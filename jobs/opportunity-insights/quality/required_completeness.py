"""Per-feed completeness of spec-REQUIRED properties.

For every opportunity updated in the last ``QUALITY_WINDOW_DAYS`` days, checks
which of its kind's REQUIRED properties (``field_usage.model_catalog``, OpenActive
Modelling Opportunity Data V2.0 with per-sub-type overrides) are present, then
rolls the result up per feed.

A property counts as present when the item's ``json_data`` holds a non-empty
value for it, or for one of its alternative keys (``model_spec.get_alternatives``,
e.g. ``type`` for ``@type``). For Event-family items, except for properties in
``model_spec.INHERITANCE_EXCLUDED`` (spec 5.6.7), it also counts as present
when an ancestor holds it, up to two levels up:

* inline ``json_data.superEvent`` and ``json_data.superEvent.superEvent``
  objects (many ScheduledSessions embed a SessionSeries that embeds the
  EventSeries carrying ``activity``), or
* the parent's own row, found via a superEvent URI (``dataset_url`` +
  ``data_id``), together with that row's inline ``superEvent``.

Feed score (item-weighted)::

    100 * Σ_items (required present / required total) / number of items

The feed's kinds are pooled, so the per-item ratio is weighted by item count.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

import pandas as pd

from field_usage import model_catalog
from field_usage.model_spec import INHERITANCE_EXCLUDED, get_alternatives
from quality.queries import QUALITY_WINDOW_DAYS

MODEL_VERSION = model_catalog.DEFAULT_MODEL_VERSION

# Event-family kinds that can be the superEvent of another item.
# ScheduledSession is excluded: it MUST NOT have subEvents (spec 5.6.8.1).
PARENT_KINDS: tuple[str, ...] = tuple(
    kind
    for kind in model_catalog.SCORED_KINDS
    if model_catalog.spec_category_for_kind(kind) == "Event"
    and kind not in ("ScheduledSession", "ScheduledSessions")
)

_EMPTY_JSON_LITERALS = "('null', '\"\"', '[]', '{}')"

# Inline ancestors checked on the item itself (parent, grandparent).
_INLINE_ANCESTOR_PATHS: tuple[tuple[str, ...], ...] = (
    ("superEvent",),
    ("superEvent", "superEvent"),
)
# Paths checked on a URI-referenced parent row: its own value, then its inline
# superEvent (the item's grandparent).
_PARENT_PATHS: tuple[tuple[str, ...], ...] = ((), ("superEvent",))


# ---------------------------------------------------------------------------
# SQL generation
# ---------------------------------------------------------------------------

def _sql_str(value: str) -> str:
    """Single-quoted SQL string literal for a constant from the model spec."""
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _json_path(*keys: str) -> str:
    """JSONPath literal such as ``'$.superEvent."name"'`` (keys double-quoted)."""
    parts = "".join(f'."{k}"' for k in keys)
    return _sql_str("$" + parts)


def _present(doc: str, *keys: str) -> str:
    """SQL: ``doc`` has a non-empty value at the nested ``keys`` path."""
    return (
        f"IFNULL(TO_JSON_STRING(JSON_QUERY({doc}, {_json_path(*keys)})) "
        f"NOT IN {_EMPTY_JSON_LITERALS}, FALSE)"
    )


def _keys_for(category: str, field: str) -> list[str]:
    return [field, *get_alternatives(category, field)]


def _parent_flag(category: str, field: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z]+", "_", f"{category}_{field}").strip("_")
    return f"p_{slug}"


def _inherits(category: str, field: str) -> bool:
    """True if ``field`` can be inherited from a superEvent for ``category``.

    Only the Event family has superEvent/subEvent links (spec 5.6.7), and some
    properties are never inherited (``INHERITANCE_EXCLUDED``).
    """
    return category == "Event" and field not in INHERITANCE_EXCLUDED


def required_fields_by_kind() -> dict[str, list[str]]:
    """``{kind: [required field, ...]}`` for every scored kind."""
    return {
        kind: model_catalog.required_fields_for_kind(kind, MODEL_VERSION)
        for kind in model_catalog.SCORED_KINDS
    }


def build_query(opportunities_tbl: str, reference_date: date) -> str:
    """SQL yielding ``(dataset_url, feed_id, kind, field, items, present)`` rows."""
    required = required_fields_by_kind()

    # One parent presence flag per (category, inheritable field) in use.
    parent_flags: dict[tuple[str, str], str] = {}
    for kind, fields in required.items():
        category = model_catalog.spec_category_for_kind(kind)
        for field in fields:
            if _inherits(category, field):
                parent_flags[(category, field)] = _parent_flag(category, field)

    parent_cols = ",\n            ".join(
        "("
        + " OR ".join(
            _present("json_data", *prefix, k)
            for prefix in _PARENT_PATHS
            for k in _keys_for(cat, f)
        )
        + f") AS {flag}"
        for (cat, f), flag in sorted(parent_flags.items())
    )

    case_branches = []
    for kind, fields in required.items():
        category = model_catalog.spec_category_for_kind(kind)
        structs = []
        for field in fields:
            keys = _keys_for(category, field)
            checks = [_present("i.json_data", k) for k in keys]
            if _inherits(category, field):
                checks += [
                    _present("i.json_data", *prefix, k)
                    for prefix in _INLINE_ANCESTOR_PATHS
                    for k in keys
                ]
                checks.append(f"IFNULL(p.{parent_flags[(category, field)]}, FALSE)")
            structs.append(
                f"STRUCT({_sql_str(field)} AS field, ({' OR '.join(checks)}) AS present)"
            )
        case_branches.append(
            f"WHEN {_sql_str(kind)} THEN [\n              "
            + ",\n              ".join(structs)
            + "\n            ]"
        )

    scored_kinds = ", ".join(_sql_str(k) for k in required)
    parent_kinds = ", ".join(_sql_str(k) for k in PARENT_KINDS)

    return f"""
        WITH items AS (
          SELECT
            dataset_url,
            feed_id,
            TRIM(kind) AS kind,
            json_data,
            IF(
              JSON_TYPE(JSON_QUERY(json_data, '$.superEvent')) = 'string',
              JSON_VALUE(json_data, '$.superEvent'),
              NULL
            ) AS se_ref
          FROM `{opportunities_tbl}`
          WHERE last_updated >= DATE_SUB(DATE '{reference_date.isoformat()}', INTERVAL {QUALITY_WINDOW_DAYS} DAY)
            AND feed_id IS NOT NULL
            AND TRIM(kind) IN ({scored_kinds})
        ),
        parents AS (
          SELECT
            dataset_url,
            data_id,
            {parent_cols}
          FROM `{opportunities_tbl}`
          WHERE data_id IS NOT NULL
            AND TRIM(kind) IN ({parent_kinds})
          QUALIFY ROW_NUMBER() OVER (
            PARTITION BY dataset_url, data_id ORDER BY last_updated DESC
          ) = 1
        ),
        checked AS (
          SELECT
            i.dataset_url,
            i.feed_id,
            i.kind,
            CASE i.kind
            {chr(10).join('            ' + b for b in case_branches)}
            END AS checks
          FROM items AS i
          LEFT JOIN parents AS p
            ON p.dataset_url = i.dataset_url
           AND p.data_id = i.se_ref
        )
        SELECT
          dataset_url,
          feed_id,
          kind,
          c.field AS field,
          COUNT(*) AS items,
          COUNTIF(c.present) AS present
        FROM checked, UNNEST(checks) AS c
        GROUP BY dataset_url, feed_id, kind, field
    """


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _pct(numerator: float, denominator: float) -> float:
    return round(100.0 * numerator / denominator, 2) if denominator else 0.0


def summarise(
    df: pd.DataFrame,
) -> dict[tuple[str | None, str], tuple[float | None, dict[str, Any] | None]]:
    """Fold ``build_query`` rows into ``{(dataset_url, feed_id): (pct, breakdown)}``.

    ``pct`` is the item-weighted mean of each item's required-present ratio.
    ``breakdown`` is ``{"model_version", "items", "kinds": {kind: {"items",
    "pct", "fields": {field: pct}}}}``.
    """
    out: dict[tuple[str | None, str], tuple[float | None, dict[str, Any] | None]] = {}
    if df is None or df.empty:
        return out

    for (dataset_url, feed_id), feed_df in df.groupby(
        ["dataset_url", "feed_id"], dropna=False, sort=False
    ):
        if not feed_id:
            continue
        total_items = 0
        weighted_ratio_sum = 0.0  # Σ over items of present/required
        kinds: dict[str, Any] = {}

        for kind, kind_df in feed_df.groupby("kind", sort=True):
            n_items = int(kind_df["items"].max())
            n_fields = len(kind_df)
            if n_items == 0 or n_fields == 0:
                continue
            present_total = float(kind_df["present"].sum())
            weighted_ratio_sum += present_total / n_fields
            total_items += n_items
            kinds[kind] = {
                "items": n_items,
                "pct": _pct(present_total, n_items * n_fields),
                "fields": {
                    str(r.field): _pct(float(r.present), n_items)
                    for r in kind_df.sort_values("field").itertuples(index=False)
                },
            }

        if total_items == 0:
            continue
        key = (None if pd.isna(dataset_url) else dataset_url, feed_id)
        out[key] = (
            _pct(weighted_ratio_sum, total_items),
            {"model_version": MODEL_VERSION, "items": total_items, "kinds": kinds},
        )
    return out
