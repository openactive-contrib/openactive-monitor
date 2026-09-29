"""Detect custom (non-schema) properties used by each feed.

A property is *known* when it is a term of the official OpenActive JSON-LD
context (``oa.jsonld``, fetched at runtime like the taxonomies in
``main.py``) or a field of the local model catalog
(``field_usage.model_spec`` plus ``_SUPPLEMENTARY_MODEL_FIELDS``). The model catalog also covers plain schema.org
properties (``name``, ``url``, ``startDate``, …) that ``oa.jsonld`` only maps
through ``@vocab``, and is the offline fallback when the fetch fails.

Every other key is reported as custom, classified as:

* ``beta``       — ``beta:`` namespace (OpenActive beta vocabulary)
* ``prefixed``   — any other namespace (``ext:foo``, ``imin:bar``) or full URI
* ``unprefixed`` — a bare, unknown key (not spec-conformant)

Payloads are sampled per ``(dataset_url, feed_id, kind)`` via
``field_usage.queries.sampled_json_data`` and walked with
``field_usage.walker.walk`` so each key is attributed to the ``@type`` of the
object it sits on. Output is one row per sampled feed for the
``custom_properties`` BigQuery table; the properties live in a REPEATED
RECORD so new properties/types never require schema changes.
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import date, datetime
from typing import Any

import pandas as pd

import bigquery_ops
from field_usage import queries as field_usage_queries
from field_usage.model_spec import (
    ALTERNATIVE_FIELDS,
    GLOBAL_ALTERNATIVE_FIELDS,
    VERSION_SPECS,
)
from field_usage.walker import coerce_payload, walk
from report_runner.taxonomy_adherence.openactive_vocab import (
    BETA_CONTEXT_URL,
    OA_CONTEXT_URL,
    fetch_vocabulary_terms,
)

logger = logging.getLogger(__name__)

BETA = "beta"
PREFIXED = "prefixed"
UNPREFIXED = "unprefixed"

_JSONLD_KEYWORDS: frozenset[str] = frozenset({"@context", "@type", "@id", "type", "id"})

# OpenActive model fields (schema.org terms, so absent from oa.jsonld) that
# ``field_usage.model_spec`` does not list. Diffed against the opportunity-related
# models of ``@openactive/data-models`` 3.0.9 (versions/2.x/models/*.json).
_SUPPLEMENTARY_MODEL_FIELDS: frozenset[str] = frozenset({
    "minValue", "maxValue",                  # QuantitativeValue (ageRange, …)
    "propertyID", "value",                   # PropertyValue / LocationFeatureSpecification
    "givenName", "familyName",               # Person
    "author",                                # Course
    "contentUrl", "embedUrl",                # MediaObject
    "workFeatured",                          # OnDemandEvent
    "specialOpeningHoursSpecification",      # Place
    "accessCode",                            # VirtualLocation
})

FeedKey = tuple[str, str]  # (dataset_url, feed_id)


# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

def _model_spec_fields() -> set[str]:
    """All field names across every model_spec category and version, plus alternatives."""
    fields: set[str] = set()
    for per_version in VERSION_SPECS.values():
        for spec in per_version.values():
            fields.update(spec)
    for alts in ALTERNATIVE_FIELDS.values():
        fields.update(alts)
    for alts in GLOBAL_ALTERNATIVE_FIELDS.values():
        fields.update(alts)
    return fields


def load_known_properties() -> tuple[set[str], str]:
    """Return ``(known_property_names, vocab_source)``."""
    known = set(_JSONLD_KEYWORDS) | _SUPPLEMENTARY_MODEL_FIELDS | _model_spec_fields()
    oa_terms = fetch_vocabulary_terms(OA_CONTEXT_URL)
    if oa_terms:
        known |= oa_terms
        vocab_source = "oa.jsonld+model_spec"
    else:
        logger.warning(
            "Could not load %s; falling back to field_usage.model_spec only", OA_CONTEXT_URL
        )
        vocab_source = "model_spec (fallback)"
    logger.info("Known property set: %d names (%s)", len(known), vocab_source)
    return known, vocab_source


def classify_property(key: str, known: set[str]) -> str | None:
    """Return the custom-property kind of ``key``, or ``None`` if it is known."""
    if key in known or key.startswith("@"):
        return None
    if key.startswith("beta:"):
        return BETA
    if ":" in key or key.startswith("http"):
        return PREFIXED
    return UNPREFIXED


def _namespace(key: str) -> str | None:
    if key.startswith("http"):
        return None
    prefix, sep, _ = key.partition(":")
    return prefix if sep else None


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

class CustomPropertyAggregator:
    """Streaming per-feed counters of custom-property usage."""

    def __init__(self, known: set[str]) -> None:
        self.known = known
        self._kind_cache: dict[str, str | None] = {}
        self.sampled_items: Counter[FeedKey] = Counter()
        self.entity_instances: Counter[tuple[FeedKey, str]] = Counter()
        self.occurrences: Counter[tuple[FeedKey, str, str]] = Counter()

    def _classify(self, key: str) -> str | None:
        if key not in self._kind_cache:
            self._kind_cache[key] = classify_property(key, self.known)
        return self._kind_cache[key]

    def add_payload(
        self,
        dataset_url: str,
        feed_id: str,
        kind: str | None,
        payload: dict[str, Any],
    ) -> None:
        feed: FeedKey = (dataset_url, feed_id)
        self.sampled_items[feed] += 1
        for entity_type, keys in walk(payload, top_level_kind=kind):
            self.entity_instances[(feed, entity_type)] += 1
            for key in keys:
                if self._classify(key) is not None:
                    self.occurrences[(feed, entity_type, key)] += 1

    def observed_custom_properties(self) -> set[str]:
        return {key for (_, _, key) in self.occurrences}

    def build_rows(
        self,
        run_date: datetime,
        df_feeds: pd.DataFrame,
        vocab_source: str,
    ) -> list[dict[str, Any]]:
        """One row per sampled feed; feeds without custom properties get an empty array."""
        meta_by_feed = {
            rec["feed_id"]: rec for rec in df_feeds.to_dict("records") if rec.get("feed_id")
        }

        structs_by_feed: dict[FeedKey, list[dict[str, Any]]] = {}
        for (feed, entity_type, key), count in self.occurrences.items():
            instances = self.entity_instances[(feed, entity_type)]
            structs_by_feed.setdefault(feed, []).append({
                "property": key,
                "property_kind": self._kind_cache[key],
                "namespace": _namespace(key),
                "entity_type": entity_type,
                "occurrences": int(count),
                "entity_instances": int(instances),
                "presence_pct": round(count / instances * 100.0, 2) if instances else 0.0,
            })

        rows: list[dict[str, Any]] = []
        for feed in sorted(self.sampled_items):
            dataset_url, feed_id = feed
            meta = meta_by_feed.get(feed_id, {})
            structs = sorted(
                structs_by_feed.get(feed, []),
                key=lambda s: (-s["occurrences"], s["property"], s["entity_type"]),
            )
            rows.append({
                "dataset_url": dataset_url,
                "dataset_name": meta.get("dataset_name"),
                "publisher_name": meta.get("publisher_name"),
                "feed_id": feed_id,
                "feed_url": meta.get("feed_url"),
                "feed_type": meta.get("feed_type"),
                "is_regular": meta.get("is_regular"),
                "sampled_items": int(self.sampled_items[feed]),
                "num_custom_properties": len({s["property"] for s in structs}),
                "num_custom_property_usages": len(structs),
                "custom_properties": structs,
                "vocab_source": vocab_source,
                "last_assessed": run_date,
            })
        return rows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def assess_custom_properties(
    run_date: datetime,
    df_feeds: pd.DataFrame,
    opportunities_tbl: str,
    reference_date: date,
    samples_per_kind: int = field_usage_queries.DEFAULT_SAMPLES_PER_KIND,
) -> list[dict[str, Any]]:
    """Sample ``json_data`` per feed/kind and build ``custom_properties`` rows."""
    known, vocab_source = load_known_properties()
    agg = CustomPropertyAggregator(known)

    sql = field_usage_queries.sampled_json_data(
        opportunities_tbl, reference_date, window_days=None, samples_per_kind=samples_per_kind
    )
    logger.info("Running custom-property sampling query (samples_per_kind=%s)", samples_per_kind)
    rows_seen = 0
    for row in bigquery_ops._client().query(sql).result():
        payload = coerce_payload(row["json_data"])
        if payload is None or not row["dataset_url"]:
            continue
        agg.add_payload(row["dataset_url"], row["feed_id"], row["kind"], payload)
        rows_seen += 1
        if rows_seen % 50_000 == 0:
            logger.info("  processed %s sampled rows", f"{rows_seen:,}")
    logger.info("Custom-property sampling complete: %s payloads", f"{rows_seen:,}")

    beta_terms = fetch_vocabulary_terms(BETA_CONTEXT_URL)
    if beta_terms:
        unofficial_beta = sorted(
            k for k in agg.observed_custom_properties()
            if k.startswith("beta:") and k not in beta_terms
        )
        if unofficial_beta:
            logger.info(
                "%d observed beta: properties are not in the beta vocabulary: %s",
                len(unofficial_beta), ", ".join(unofficial_beta[:20]),
            )

    return agg.build_rows(run_date, df_feeds, vocab_source)


__all__ = [
    "BETA",
    "PREFIXED",
    "UNPREFIXED",
    "CustomPropertyAggregator",
    "assess_custom_properties",
    "classify_property",
    "load_known_properties",
]
