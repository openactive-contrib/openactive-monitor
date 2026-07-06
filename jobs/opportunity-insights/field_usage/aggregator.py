"""Streaming aggregation of field-usage observations.

``UsageAggregator`` consumes one sampled ``json_data`` payload at a time via
``add_payload`` (the payload is walked and then discarded — memory is bounded
by the number of distinct ``(type, field)`` pairs and datasets, never by the
row count) and produces structured results via ``compute_results``.

Two parallel tallies are kept:

* **Raw** ``(@type, field)`` presence — every key seen on every object
  instance. Used for provider-extension discovery, discovered-only nested
  types, and the per-dataset dump.
* **Model** ``(spec_category, model_field)`` presence — evaluated per object
  instance with alternative-field handling (so ``type`` satisfies ``@type``,
  ``facilityType`` satisfies ``FacilityUse.activity``). Used for the
  authoritative deletion-candidate percentages.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field as dc_field

from field_usage import model_catalog
from field_usage.walker import walk

# Classification labels.
UNUSED = "UNUSED"
RARE = "RARE"
LOW = "LOW"
COMMON = "COMMON"


def classify(instances_with: int, presence_pct: float, rare_threshold: float, low_threshold: float) -> str:
    if instances_with == 0:
        return UNUSED
    if presence_pct < rare_threshold:
        return RARE
    if presence_pct < low_threshold:
        return LOW
    return COMMON


@dataclass
class FieldRow:
    field: str
    model_status: str | None  # required/recommended/optional, or None for extensions
    instances_with: int
    total_instances: int
    presence_pct: float
    classification: str
    exact_pct: float | None = None  # exact full-scan %, top-level model fields only


@dataclass
class CategoryReport:
    category: str
    observed_types: list[str]
    total_instances: int
    model_fields: list[FieldRow]      # sorted ascending by presence_pct
    extension_fields: list[FieldRow]  # sorted descending by presence_pct


@dataclass
class DiscoveredTypeReport:
    type_name: str
    total_instances: int
    fields: list[FieldRow]            # sorted descending by presence_pct


@dataclass
class DatasetTypeBlock:
    type_name: str
    is_model: bool
    instances: int
    present: list[tuple[str, float]]  # (field, presence_pct within dataset)
    absent_model: list[str]           # model fields absent in this dataset (model types only)


@dataclass
class DatasetReport:
    dataset_url: str
    publisher_name: str | None
    feed_kinds: list[tuple[str, str]]            # (feed_id, kind)
    sample_counts: list[tuple[str, str, int]]    # (feed_id, kind, n_sampled)
    type_blocks: list[DatasetTypeBlock]


@dataclass
class UsageResults:
    categories: list[CategoryReport]
    discovered_types: list[DiscoveredTypeReport]
    datasets: list[DatasetReport]
    type_instances: dict[str, int] = dc_field(default_factory=dict)


def _pct(numerator: int, denominator: int) -> float:
    return (numerator / denominator * 100.0) if denominator else 0.0


class UsageAggregator:
    """Accumulates field-usage counters from a stream of payloads."""

    def __init__(self, model_version: str = model_catalog.DEFAULT_MODEL_VERSION) -> None:
        self.model_version = model_version

        # --- raw per-type tallies (global) ---
        self.type_instances: Counter[str] = Counter()
        self.field_presence: Counter[tuple[str, str]] = Counter()

        # --- model per-category tallies (global, alternative-aware) ---
        self.category_instances: Counter[str] = Counter()
        self.model_field_presence: Counter[tuple[str, str]] = Counter()

        # --- per-dataset raw tallies ---
        self.ds_type_instances: dict[str, Counter[str]] = defaultdict(Counter)
        self.ds_field_presence: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)

        # --- per-dataset provenance / sample sizes ---
        self.ds_feed_kinds: dict[str, set[tuple[str, str]]] = defaultdict(set)
        self.sampled_counts: Counter[tuple[str, str, str]] = Counter()

    def add_payload(
        self,
        dataset_url: str,
        feed_id: str | None,
        kind: str | None,
        payload: dict,
    ) -> None:
        """Walk one payload and fold its observations into the counters."""
        self.sampled_counts[(dataset_url, feed_id or "", kind or "")] += 1
        self.ds_feed_kinds[dataset_url].add((feed_id or "", kind or ""))

        ds_types = self.ds_type_instances[dataset_url]
        ds_fields = self.ds_field_presence[dataset_url]

        for entity_type, fields in walk(payload, top_level_kind=kind):
            # raw tallies
            self.type_instances[entity_type] += 1
            ds_types[entity_type] += 1
            for f in fields:
                self.field_presence[(entity_type, f)] += 1
                ds_fields[(entity_type, f)] += 1

            # model tallies (alternative-aware), only for known model entities
            if model_catalog.is_model_type(entity_type):
                category = model_catalog.spec_category_for_kind(entity_type)
                self.category_instances[category] += 1
                observed = set(fields)
                for mf in model_catalog.model_fields_for_category(category, self.model_version):
                    if model_catalog.field_is_present(category, mf, observed):
                        self.model_field_presence[(category, mf)] += 1

    # ------------------------------------------------------------------
    # Result computation
    # ------------------------------------------------------------------

    def _observed_types_for_category(self, category: str) -> list[str]:
        return sorted(
            t
            for t in self.type_instances
            if model_catalog.is_model_type(t) and model_catalog.spec_category_for_kind(t) == category
        )

    def _category_extension_fields(
        self,
        category: str,
        observed_types: list[str],
        total_instances: int,
        rare_threshold: float,
        low_threshold: float,
    ) -> list[FieldRow]:
        """Fields observed on the category's types but not in the model catalog."""
        model_fields = model_catalog.model_fields_for_category(category, self.model_version)
        # alias keys that already satisfy a model field — not extensions
        alias_keys = _alias_keys_for_category(category, self.model_version)
        # collect raw presence summed across the category's types (types partition instances)
        ext_counts: Counter[str] = Counter()
        observed_set = set(observed_types)
        for (tt, f), cnt in self.field_presence.items():
            if tt in observed_set:
                ext_counts[f] += cnt
        rows: list[FieldRow] = []
        for f, cnt in ext_counts.items():
            if f in model_fields or f in alias_keys:
                continue
            pct = _pct(cnt, total_instances)
            rows.append(
                FieldRow(
                    field=f,
                    model_status=None,
                    instances_with=cnt,
                    total_instances=total_instances,
                    presence_pct=pct,
                    classification=classify(cnt, pct, rare_threshold, low_threshold),
                )
            )
        rows.sort(key=lambda r: (-r.presence_pct, r.field))
        return rows

    def compute_results(self, rare_threshold: float, low_threshold: float) -> UsageResults:
        categories: list[CategoryReport] = []
        for category in model_catalog.SPEC_CATEGORIES:
            observed_types = self._observed_types_for_category(category)
            total = self.category_instances.get(category, 0)

            model_rows: list[FieldRow] = []
            for f, status in model_catalog.model_fields_for_category(category, self.model_version).items():
                cnt = self.model_field_presence.get((category, f), 0)
                pct = _pct(cnt, total)
                model_rows.append(
                    FieldRow(
                        field=f,
                        model_status=status,
                        instances_with=cnt,
                        total_instances=total,
                        presence_pct=pct,
                        classification=classify(cnt, pct, rare_threshold, low_threshold),
                    )
                )
            model_rows.sort(key=lambda r: (r.presence_pct, r.field))

            ext_rows = self._category_extension_fields(
                category, observed_types, total, rare_threshold, low_threshold
            )
            categories.append(
                CategoryReport(
                    category=category,
                    observed_types=observed_types,
                    total_instances=total,
                    model_fields=model_rows,
                    extension_fields=ext_rows,
                )
            )

        discovered = self._compute_discovered_types(rare_threshold, low_threshold)
        datasets = self._compute_datasets()

        return UsageResults(
            categories=categories,
            discovered_types=discovered,
            datasets=datasets,
            type_instances=dict(self.type_instances),
        )

    def _compute_discovered_types(
        self, rare_threshold: float, low_threshold: float
    ) -> list[DiscoveredTypeReport]:
        discovered_type_names = sorted(
            t for t in self.type_instances if not model_catalog.is_model_type(t)
        )
        reports: list[DiscoveredTypeReport] = []
        for t in discovered_type_names:
            total = self.type_instances[t]
            rows: list[FieldRow] = []
            for (tt, f), cnt in self.field_presence.items():
                if tt != t:
                    continue
                pct = _pct(cnt, total)
                rows.append(
                    FieldRow(
                        field=f,
                        model_status=None,
                        instances_with=cnt,
                        total_instances=total,
                        presence_pct=pct,
                        classification=classify(cnt, pct, rare_threshold, low_threshold),
                    )
                )
            rows.sort(key=lambda r: (-r.presence_pct, r.field))
            reports.append(DiscoveredTypeReport(type_name=t, total_instances=total, fields=rows))
        return reports

    def _compute_datasets(self) -> list[DatasetReport]:
        reports: list[DatasetReport] = []
        for dataset_url in sorted(self.ds_type_instances):
            ds_types = self.ds_type_instances[dataset_url]
            ds_fields = self.ds_field_presence[dataset_url]

            # observed fields per type within this dataset
            observed_by_type: dict[str, set[str]] = defaultdict(set)
            present_by_type: dict[str, list[tuple[str, float]]] = defaultdict(list)
            for (t, f), cnt in ds_fields.items():
                if cnt > 0:
                    observed_by_type[t].add(f)
                    present_by_type[t].append((f, _pct(cnt, ds_types[t])))

            blocks: list[DatasetTypeBlock] = []
            for t in sorted(ds_types):
                is_model = model_catalog.is_model_type(t)
                present = sorted(present_by_type.get(t, []), key=lambda x: (-x[1], x[0]))
                absent_model: list[str] = []
                if is_model:
                    category = model_catalog.spec_category_for_kind(t)
                    observed = observed_by_type.get(t, set())
                    absent_model = sorted(
                        mf
                        for mf in model_catalog.model_fields_for_category(category, self.model_version)
                        if not model_catalog.field_is_present(category, mf, observed)
                    )
                blocks.append(
                    DatasetTypeBlock(
                        type_name=t,
                        is_model=is_model,
                        instances=ds_types[t],
                        present=present,
                        absent_model=absent_model,
                    )
                )

            feed_kinds = sorted(self.ds_feed_kinds[dataset_url])
            sample_counts = sorted(
                (fid, knd, n)
                for (ds, fid, knd), n in self.sampled_counts.items()
                if ds == dataset_url
            )
            reports.append(
                DatasetReport(
                    dataset_url=dataset_url,
                    publisher_name=None,
                    feed_kinds=feed_kinds,
                    sample_counts=sample_counts,
                    type_blocks=blocks,
                )
            )
        return reports


def _alias_keys_for_category(category: str, model_version: str) -> set[str]:
    """All alternative-field key names that satisfy some model field of ``category``."""
    from field_usage.model_spec import get_alternatives

    keys: set[str] = set()
    for mf in model_catalog.model_fields_for_category(category, model_version):
        keys.update(get_alternatives(category, mf))
    return keys


__all__ = [
    "UsageAggregator",
    "UsageResults",
    "CategoryReport",
    "DiscoveredTypeReport",
    "DatasetReport",
    "DatasetTypeBlock",
    "FieldRow",
    "classify",
    "UNUSED",
    "RARE",
    "LOW",
    "COMMON",
]
