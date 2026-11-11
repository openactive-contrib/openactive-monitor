"""Vocabulary adherence of activity / facility values to the OpenActive SKOS lists.

The ``opportunities`` table stores the raw published payload of each item's
``activity`` (``activity_json``) and ``facilityType`` (``facility_json``),
including values inherited from a superEvent / FacilityUse.  The OpenActive
model allows these to be either a ``Concept`` referencing a vocabulary or a
plain string; this module measures how often publishers actually reference the
official vocabulary:

* Activity List — https://openactive.io/activity-list/activity-list.jsonld
* Facility Types — https://openactive.io/facility-types/facility-types.jsonld

Every value is classified into one category (best first):

=====================  ======================================================
``valid_id``           ``id`` / ``@id`` (or a URI string) resolving to a
                       concept in the vocabulary — the only adherent category
``invalid_id``         URI in the OpenActive vocabulary namespace that does not
                       resolve to a concept (typo, retired id, ...)
``other_scheme``       URI in another namespace (e.g. a publisher's own list)
``label_match_only``   no usable id, but the ``prefLabel`` / plain string
                       matches a vocabulary ``prefLabel`` / ``altLabel``
                       (case-insensitive)
``unrecognised``       anything else
=====================  ======================================================

An item (one opportunity row) takes the best category among its values, so
each item is counted in exactly one bucket and the buckets sum to ``items``.
``adherence_pct`` is the share of items in ``valid_id``.

All functions are pure (no network / BigQuery access) to keep them testable.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from typing import Any

import pandas as pd

from report_runner.taxonomy_adherence.openactive_vocab import (
    ConceptScheme,
    normalise_concept_id,
)

logger = logging.getLogger(__name__)

VALID_ID = "valid_id"
INVALID_ID = "invalid_id"
OTHER_SCHEME = "other_scheme"
LABEL_MATCH_ONLY = "label_match_only"
UNRECOGNISED = "unrecognised"

# Best first: an item's category is the highest-ranked category among its values.
CATEGORIES: tuple[str, ...] = (VALID_ID, INVALID_ID, OTHER_SCHEME, LABEL_MATCH_ONLY, UNRECOGNISED)
_RANK = {category: rank for rank, category in enumerate(CATEGORIES)}

TOP_UNMATCHED_LIMIT = 10

# Field names as emitted by ``quality.queries.per_feed_vocabulary_values``.
ACTIVITY_FIELD = "activity"
FACILITY_FIELD = "facility"


def _is_uri(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def _classify_uri(uri: str, scheme: ConceptScheme) -> str:
    normalised = normalise_concept_id(uri)
    if normalised in scheme.ids:
        return VALID_ID
    base = normalised.partition("#")[0]
    if base == scheme.namespace:
        return INVALID_ID
    return OTHER_SCHEME


def _first_label(value: Any) -> str | None:
    """First non-blank string from a SKOS label (str, list, or language map)."""
    if isinstance(value, str):
        return value.strip() or None
    candidates: list[Any] = []
    if isinstance(value, list):
        candidates = value
    elif isinstance(value, dict):
        candidates = list(value.values())
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _classify_label(label: str | None, scheme: ConceptScheme) -> str:
    if label and label.lower() in scheme.labels:
        return LABEL_MATCH_ONLY
    return UNRECOGNISED


def classify_value(value: Any, scheme: ConceptScheme) -> tuple[str, str | None]:
    """Classify a single activity / facility value.

    Returns ``(category, token)`` where ``token`` is a lower-cased label (or the
    id when there is no label) describing the value, used for the
    ``top_unmatched`` list.  ``token`` is ``None`` for ``valid_id`` values.
    """
    if isinstance(value, dict):
        raw_id = value.get("id") or value.get("@id")
        label = _first_label(value.get("prefLabel"))
        if isinstance(raw_id, str) and _is_uri(raw_id):
            category = _classify_uri(raw_id, scheme)
            if category == VALID_ID:
                return VALID_ID, None
            return category, (label or raw_id.strip()).lower()
        # No usable URI id: judge on the label alone.
        return _classify_label(label, scheme), label.lower() if label else None

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return UNRECOGNISED, None
        if _is_uri(stripped):
            category = _classify_uri(stripped, scheme)
            return category, None if category == VALID_ID else stripped.lower()
        return _classify_label(stripped, scheme), stripped.lower()

    return UNRECOGNISED, None


def classify_item(raw_value: Any, scheme: ConceptScheme) -> tuple[str, list[str]] | None:
    """Classify one item's raw activity / facility payload.

    ``raw_value`` may be a dict, a string, or a list of either.  Returns
    ``(category, unmatched_tokens)`` where ``category`` is the best category
    among the item's values and ``unmatched_tokens`` lists the tokens of the
    item's values when the item is *not* adherent (empty for ``valid_id``).
    Returns ``None`` when the payload holds no values at all.
    """
    values = raw_value if isinstance(raw_value, list) else [raw_value]
    values = [v for v in values if v not in (None, "", [], {})]
    if not values:
        return None

    classified = [classify_value(v, scheme) for v in values]
    best = min((category for category, _ in classified), key=_RANK.__getitem__)
    if best == VALID_ID:
        return VALID_ID, []
    tokens = [token for _, token in classified if token]
    return best, tokens


def summarise(
    category_counts: Counter[str],
    unmatched_counts: Counter[str],
) -> dict[str, Any] | None:
    """Build the JSON breakdown stored in ``feed_quality``; ``None`` if no items."""
    items = sum(category_counts[c] for c in CATEGORIES)
    if items == 0:
        return None
    summary: dict[str, Any] = {
        "adherence_pct": round(category_counts[VALID_ID] / items * 100, 2),
        "items": items,
    }
    for category in CATEGORIES:
        summary[category] = category_counts[category]
    summary["top_unmatched"] = [
        token for token, _ in unmatched_counts.most_common(TOP_UNMATCHED_LIMIT)
    ]
    return summary


def _parse_raw(raw: Any) -> Any:
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return raw
    return raw


def build_adherence_by_feed(
    df: pd.DataFrame,
    schemes: dict[str, ConceptScheme | None],
) -> dict[tuple[str | None, str], dict[str, dict[str, Any] | None]]:
    """Aggregate grouped raw values into per-feed adherence summaries.

    ``df`` has columns ``dataset_url, feed_id, field, raw_value, n`` where
    ``raw_value`` is the ``TO_JSON_STRING`` of one distinct payload and ``n``
    the number of items carrying it.  ``schemes`` maps a field name
    (``activity`` / ``facility``) to its vocabulary; fields whose scheme is
    ``None`` (fetch failed) are skipped.

    Returns ``{(dataset_url, feed_id): {field: summary | None}}``.
    """
    category_counts: dict[tuple[str | None, str, str], Counter[str]] = {}
    unmatched_counts: dict[tuple[str | None, str, str], Counter[str]] = {}
    cache: dict[tuple[str, str], tuple[str, list[str]] | None] = {}

    for row in df.itertuples(index=False):
        feed_id = getattr(row, "feed_id", None)
        field = getattr(row, "field", None)
        scheme = schemes.get(field) if field else None
        if not feed_id or scheme is None:
            continue
        raw = getattr(row, "raw_value", None)
        count = int(getattr(row, "n", 0) or 0)
        if raw is None or count <= 0:
            continue

        cache_key = (field, raw if isinstance(raw, str) else json.dumps(raw, sort_keys=True))
        if cache_key not in cache:
            cache[cache_key] = classify_item(_parse_raw(raw), scheme)
        result = cache[cache_key]
        if result is None:
            continue

        category, tokens = result
        key = (getattr(row, "dataset_url", None), feed_id, field)
        category_counts.setdefault(key, Counter())[category] += count
        unmatched = unmatched_counts.setdefault(key, Counter())
        for token in tokens:
            unmatched[token] += count

    out: dict[tuple[str | None, str], dict[str, dict[str, Any] | None]] = {}
    for (dataset_url, feed_id, field), counts in category_counts.items():
        out.setdefault((dataset_url, feed_id), {})[field] = summarise(
            counts, unmatched_counts.get((dataset_url, feed_id, field), Counter()),
        )
    return out


__all__ = [
    "ACTIVITY_FIELD",
    "FACILITY_FIELD",
    "CATEGORIES",
    "VALID_ID",
    "INVALID_ID",
    "OTHER_SCHEME",
    "LABEL_MATCH_ONLY",
    "UNRECOGNISED",
    "classify_value",
    "classify_item",
    "summarise",
    "build_adherence_by_feed",
]
