"""opportunity-insights — BigQuery-based analysis job.

Reads from the ``opportunities`` table produced by ``ingest-opportunities`` and
writes per-feed and aggregate insights into a set of ``insight_*`` tables.
Replaces the pickle-based ``analyse-opportunities`` job while keeping the same
overall metric definitions.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import click
import pandas as pd
from dotenv import load_dotenv

import bigquery_ops
import geolookup
import queries
from sad_mapping import run_sad_matching

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_GEO_DIR = Path(os.getenv("INSIGHTS_GEO_DIR", "../../volume-1/data-analysis")).resolve()
DEFAULT_PUBLIC_DIR = Path(os.getenv("INSIGHTS_PUBLIC_DIR", "../../volume-1/public")).resolve()


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Data assembly helpers
# ---------------------------------------------------------------------------

def _pivot_counts_to_dicts(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    """Pivot a per-feed category-count DataFrame into ``{feed_id: {value: count}}``."""
    out: dict[str, dict[str, int]] = defaultdict(dict)
    for feed_id, value, cnt in zip(df["feed_id"], df["value"], df["cnt"]):
        if feed_id is None or value is None:
            continue
        out[feed_id][str(value)] = int(cnt)
    return out


def _resolve_geo_counts(
    df_points: pd.DataFrame,
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """Group location points per feed into ``regions_counts`` / ``districts_counts`` / ``trusts_counts`` dicts."""
    regions: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    districts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    trusts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for feed_id, lat, lng, cnt in zip(df_points["feed_id"], df_points["lat"], df_points["lng"], df_points["cnt"]):
        if feed_id is None:
            continue
        region, district, trust = geolookup.lookup(lng, lat)
        if region:
            regions[feed_id][region] += int(cnt)
        if district:
            districts[feed_id][district] += int(cnt)
        if trust:
            trusts[feed_id][trust] += int(cnt)

    return (
        {fid: dict(d) for fid, d in regions.items()},
        {fid: dict(d) for fid, d in districts.items()},
        {fid: dict(d) for fid, d in trusts.items()},
    )


def _collect_per_feed_dicts(opportunities_tbl: str) -> dict[str, dict[str, dict[str, int]]]:
    """Run one query per categorical dimension and pivot each into per-feed dicts."""
    return {
        "item_kinds_counts":      _pivot_counts_to_dicts(bigquery_ops.run_query(queries.per_feed_kind_counts(opportunities_tbl))),
        "item_types_counts":      _pivot_counts_to_dicts(bigquery_ops.run_query(queries.per_feed_item_type_counts(opportunities_tbl))),
        "activities_counts":      _pivot_counts_to_dicts(bigquery_ops.run_query(queries.per_feed_activity_counts(opportunities_tbl))),
        "facilities_counts":      _pivot_counts_to_dicts(bigquery_ops.run_query(queries.per_feed_facility_counts(opportunities_tbl))),
        "accessibilities_counts": _pivot_counts_to_dicts(bigquery_ops.run_query(queries.per_feed_accessibility_counts(opportunities_tbl))),
        "organizer_names_counts": _pivot_counts_to_dicts(bigquery_ops.run_query(queries.per_feed_organizer_counts(opportunities_tbl))),
    }


# ---------------------------------------------------------------------------
# Per-feed assembly
# ---------------------------------------------------------------------------

def _build_feed_insights_rows(
    run_date: datetime,
    df_feeds: pd.DataFrame,
    df_base: pd.DataFrame,
    df_status: pd.DataFrame,
    per_feed_dicts: dict[str, dict[str, dict[str, int]]],
    regions_counts: dict[str, dict[str, int]],
    districts_counts: dict[str, dict[str, int]],
    trusts_counts: dict[str, dict[str, int]],
) -> list[dict[str, Any]]:
    base_by_feed = {row["feed_id"]: row for _, row in df_base.iterrows() if row["feed_id"]}
    status_by_feed = {row["feed_id"]: row["status"] for _, row in df_status.iterrows() if row["feed_id"]}

    feed_ids_with_data = set(base_by_feed.keys())
    # Only emit rows for feeds that have at least one opportunity row in the window.
    # This matches legacy semantics (feeds_with_analysed_data).
    rows: list[dict[str, Any]] = []

    feed_meta_by_id = {row["feed_id"]: row for _, row in df_feeds.iterrows() if row["feed_id"]}

    for feed_id in feed_ids_with_data:
        meta = feed_meta_by_id.get(feed_id, pd.Series(dtype=object))
        base = base_by_feed[feed_id]
        feed_type = meta.get("feed_type") if not meta.empty else None
        num_items = int(base.get("num_items") or 0)

        row = {
            "run_date": run_date,
            "feed_id": feed_id,
            "dataset_url": meta.get("dataset_url"),
            "dataset_name": meta.get("dataset_name"),
            "publisher_name": meta.get("publisher_name"),
            "feed_url": meta.get("feed_url"),
            "license_url": meta.get("license_url"),
            "logo_url": meta.get("logo_url"),
            "feed_type": feed_type,
            "event_type": None,  # Not derivable cheaply from new schema; left NULL.
            "is_regular": _coerce_bool(meta.get("is_regular")) if not meta.empty else None,
            "status": status_by_feed.get(feed_id),
            "num_items": num_items,
            "num_analysis_items": num_items,
            "num_opportunity_items": int(base.get("num_opportunity_items") or 0),
            "num_future_opportunity_items": int(base.get("num_future_opportunity_items") or 0),
            "num_future_week_opportunity_items": int(base.get("num_future_week_opportunity_items") or 0),
            "num_opportunity_start_dates": int(base.get("num_opportunity_items") or 0),
            "num_future_opportunity_start_dates": int(base.get("num_future_opportunity_items") or 0),
            "num_future_week_opportunity_start_dates": int(base.get("num_future_week_opportunity_items") or 0),
            "item_kinds_counts":      per_feed_dicts["item_kinds_counts"].get(feed_id, {}),
            "item_types_counts":      per_feed_dicts["item_types_counts"].get(feed_id, {}),
            "organizer_names_counts": per_feed_dicts["organizer_names_counts"].get(feed_id, {}),
            "activities_counts":      per_feed_dicts["activities_counts"].get(feed_id, {}),
            "facilities_counts":      per_feed_dicts["facilities_counts"].get(feed_id, {}),
            "accessibilities_counts": per_feed_dicts["accessibilities_counts"].get(feed_id, {}),
            "regions_counts":         regions_counts.get(feed_id, {}),
            "districts_counts":       districts_counts.get(feed_id, {}),
            "trusts_counts":          trusts_counts.get(feed_id, {}),
        }
        rows.append(row)

    logger.info("Built %d feed_insights rows", len(rows))
    return rows


def _coerce_bool(value: Any) -> bool | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in {"true", "t", "yes", "y", "1"}:
            return True
        if s in {"false", "f", "no", "n", "0"}:
            return False
    return None


# ---------------------------------------------------------------------------
# Aggregates
# ---------------------------------------------------------------------------

_SCOPES = ("all", "regular", "preview")


def _feeds_in_scope(df_feeds: pd.DataFrame, scope: str) -> pd.DataFrame:
    if scope == "all":
        return df_feeds
    if scope == "regular":
        return df_feeds[df_feeds["is_regular"] == True]
    if scope == "preview":
        return df_feeds[df_feeds["is_regular"] == False]
    raise ValueError(f"Unknown scope: {scope}")


def _count_distinct_non_empty(df: pd.DataFrame, column: str) -> int:
    """Count distinct non-empty values in a metadata column."""
    if column not in df.columns:
        return 0
    series = df[column].dropna().astype(str).str.strip()
    return int(series[series != ""].nunique())


def _aggregate_category(
    rows: list[dict[str, Any]],
    feed_id_col: str,
    value_col: str,
    count_col: str,
    scope_feed_ids: dict[str, set[str]],
) -> dict[str, list[dict[str, Any]]]:
    """Collapse a per-feed SQL result into one aggregated count list per scope."""
    out: dict[str, list[dict[str, Any]]] = {}
    for scope in _SCOPES:
        feed_ids = scope_feed_ids[scope]
        totals: dict[str, int] = defaultdict(int)
        for row in rows:
            if row[feed_id_col] in feed_ids and row[value_col] is not None:
                totals[str(row[value_col])] += int(row[count_col])
        grand_total = sum(totals.values())
        scope_rows: list[dict[str, Any]] = []
        for value, count in sorted(totals.items(), key=lambda x: -x[1]):
            scope_rows.append({
                "value": value,
                "count": count,
                "percentage": (count / grand_total * 100) if grand_total else 0.0,
            })
        out[scope] = scope_rows
    return out


def _sum_counts(rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge two already-aggregated count lists by value, recomputing percentage."""
    totals: dict[str, int] = defaultdict(int)
    for row in (*rows_a, *rows_b):
        totals[row["value"]] += row["count"]
    grand = sum(totals.values())
    merged = [
        {"value": v, "count": c, "percentage": (c / grand * 100) if grand else 0.0}
        for v, c in sorted(totals.items(), key=lambda x: -x[1])
    ]
    return merged


def _category_rows_for_bq(
    run_date: datetime,
    category: str,
    per_scope: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for scope, rows in per_scope.items():
        for row in rows:
            out.append({
                "run_date": run_date,
                "category": category,
                "scope": scope,
                "value": row["value"],
                "count": row["count"],
                "percentage": row["percentage"],
            })
    return out


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

class _SourceData:
    """Bundle of raw inputs loaded from BigQuery + spatial counts."""

    def __init__(
        self,
        df_feeds: pd.DataFrame,
        df_status: pd.DataFrame,
        df_base: pd.DataFrame,
        df_points: pd.DataFrame,
        per_feed_dicts: dict[str, dict[str, dict[str, int]]],
        regions_counts: dict[str, dict[str, int]],
        districts_counts: dict[str, dict[str, int]],
        trusts_counts: dict[str, dict[str, int]],
    ) -> None:
        self.df_feeds = df_feeds
        self.df_status = df_status
        self.df_base = df_base
        self.df_points = df_points
        self.per_feed_dicts = per_feed_dicts
        self.regions_counts = regions_counts
        self.districts_counts = districts_counts
        self.trusts_counts = trusts_counts


def _load_source_data(opportunities_tbl: str, feeds_tbl: str,
                      opportunity_ingestion_tbl: str, reference_date: date) -> _SourceData:
    """Load all raw BigQuery inputs and resolve geolocation counts."""
    logger.info("Loading feed metadata")
    df_feeds = bigquery_ops.run_query(queries.feeds_metadata(feeds_tbl))

    logger.info("Loading latest ingestion status per feed")
    df_status = bigquery_ops.run_query(queries.latest_ingestion_status(opportunity_ingestion_tbl))

    logger.info("Computing per-feed base metrics")
    df_base = bigquery_ops.run_query(
        queries.per_feed_base_metrics(opportunities_tbl, reference_date)
    )

    logger.info("Computing per-feed categorical counts")
    per_feed_dicts = _collect_per_feed_dicts(opportunities_tbl)

    logger.info("Loading location points for spatial lookup")
    df_points = bigquery_ops.run_query(queries.per_feed_location_points(opportunities_tbl))

    logger.info("Building spatial indexes from %s", DEFAULT_GEO_DIR)
    geolookup.load_indexes(DEFAULT_GEO_DIR)

    logger.info("Resolving %d location points into region/district/trust counts", len(df_points))
    regions_counts, districts_counts, trusts_counts = _resolve_geo_counts(df_points)

    return _SourceData(
        df_feeds=df_feeds,
        df_status=df_status,
        df_base=df_base,
        df_points=df_points,
        per_feed_dicts=per_feed_dicts,
        regions_counts=regions_counts,
        districts_counts=districts_counts,
        trusts_counts=trusts_counts,
    )


def _build_scope_feed_ids(feed_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    """Build feed-id sets per scope from the analysed feed rows."""
    return {
        "all":     {r["feed_id"] for r in feed_rows},
        "regular": {r["feed_id"] for r in feed_rows if r["is_regular"] is True},
        "preview": {r["feed_id"] for r in feed_rows if r["is_regular"] is False},
    }


def _aggregate_geo_category(
    per_feed: dict[str, dict[str, int]],
    scope_feed_ids: dict[str, set[str]],
) -> dict[str, list[dict[str, Any]]]:
    """Roll a per-feed geo-count dict up into the standard per-scope aggregate format."""
    per_scope: dict[str, list[dict[str, Any]]] = {}
    for scope in _SCOPES:
        totals: dict[str, int] = defaultdict(int)
        for feed_id, values in per_feed.items():
            if feed_id in scope_feed_ids[scope]:
                for v, c in values.items():
                    totals[v] += c
        grand = sum(totals.values())
        per_scope[scope] = [
            {"value": v, "count": c, "percentage": (c / grand * 100) if grand else 0.0}
            for v, c in sorted(totals.items(), key=lambda x: -x[1])
        ]
    return per_scope


def _aggregate_all_categories(
    opportunities_tbl: str,
    source: _SourceData,
    scope_feed_ids: dict[str, set[str]],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Compute every aggregate category (categorical + geo + activity_facility)."""
    categories: dict[str, dict[str, list[dict[str, Any]]]] = {}

    def agg_simple(category: str, sql: str) -> None:
        rows = bigquery_ops.run_query(sql).to_dict("records")
        categories[category] = _aggregate_category(rows, "feed_id", "value", "cnt", scope_feed_ids)

    agg_simple("item_kind",     queries.per_feed_kind_counts(opportunities_tbl))
    agg_simple("item_type",     queries.per_feed_item_type_counts(opportunities_tbl))
    agg_simple("activity",      queries.per_feed_activity_counts(opportunities_tbl))
    agg_simple("facility",      queries.per_feed_facility_counts(opportunities_tbl))
    agg_simple("accessibility", queries.per_feed_accessibility_counts(opportunities_tbl))
    agg_simple("organizer",     queries.per_feed_organizer_counts(opportunities_tbl))

    categories["activity_facility"] = {
        scope: _sum_counts(categories["activity"][scope], categories["facility"][scope])
        for scope in _SCOPES
    }

    for category, per_feed in (
        ("region", source.regions_counts),
        ("district", source.districts_counts),
        ("trust", source.trusts_counts),
    ):
        categories[category] = _aggregate_geo_category(per_feed, scope_feed_ids)

    return categories


def _compute_scope_totals(
    df_feeds: pd.DataFrame,
    feed_rows: list[dict[str, Any]],
    scope_feed_ids: dict[str, set[str]],
) -> dict[str, dict[str, int]]:
    """Compute per-scope scalar totals used in the run summary row."""
    def scalar_by_scope(predicate) -> dict[str, int]:
        return {scope: sum(1 for r in feed_rows
                           if r["feed_id"] in scope_feed_ids[scope] and predicate(r))
                for scope in _SCOPES}

    def sum_by_scope(col: str) -> dict[str, int]:
        return {scope: sum(int(r.get(col) or 0) for r in feed_rows
                           if r["feed_id"] in scope_feed_ids[scope])
                for scope in _SCOPES}

    return {
        # Publisher/dataset counts reflect the full feed catalogue snapshot
        # (including feeds with zero opportunity rows).
        "num_publishers": {
            scope: _count_distinct_non_empty(_feeds_in_scope(df_feeds, scope), "publisher_name")
            for scope in _SCOPES
        },
        "num_datasets": {
            scope: _count_distinct_non_empty(_feeds_in_scope(df_feeds, scope), "dataset_url")
            for scope in _SCOPES
        },
        "num_feeds": {scope: len(_feeds_in_scope(df_feeds, scope)) for scope in _SCOPES},
        "num_feeds_with_data": {scope: len(scope_feed_ids[scope]) for scope in _SCOPES},
        "num_feeds_with_future": scalar_by_scope(
            lambda r: (r.get("num_future_opportunity_items") or 0) > 0
        ),
        "total_items": sum_by_scope("num_items"),
        "total_future": sum_by_scope("num_future_opportunity_items"),
        "total_future_week": sum_by_scope("num_future_week_opportunity_items"),
    }


def _run_sad(categories: dict[str, dict[str, list[dict[str, Any]]]]):
    """Build the SAD (sport & discipline) input frame and run matching."""
    act_fac_all = categories["activity_facility"]["all"]
    df_act_fac_all = pd.DataFrame(act_fac_all, columns=["value", "count", "percentage"]).rename(
        columns={"value": "activity"}
    )
    return run_sad_matching(df_act_fac_all, DEFAULT_GEO_DIR)


def _build_summary_row(
    run_date: datetime,
    totals: dict[str, dict[str, int]],
    categories: dict[str, dict[str, list[dict[str, Any]]]],
    sad,
) -> dict[str, Any]:
    """Assemble the single run-summary row."""
    total_num_items_with = {
        cat: sum(r["count"] for r in categories[cat]["all"])
        for cat in ("item_kind", "item_type", "organizer", "activity", "facility",
                    "accessibility", "region", "district", "trust")
    }

    num_publishers = totals["num_publishers"]
    num_datasets = totals["num_datasets"]
    num_feeds = totals["num_feeds"]
    num_feeds_with_data = totals["num_feeds_with_data"]
    num_feeds_with_future = totals["num_feeds_with_future"]
    total_items = totals["total_items"]
    total_future = totals["total_future"]
    total_future_week = totals["total_future_week"]

    return {
        "run_date": run_date,
        "num_publishers":                                    num_publishers["all"],
        "num_publishers_regular":                            num_publishers["regular"],
        "num_publishers_preview":                            num_publishers["preview"],
        "num_datasets":                                      num_datasets["all"],
        "num_datasets_regular":                              num_datasets["regular"],
        "num_datasets_preview":                              num_datasets["preview"],
        "num_feeds":                                         num_feeds["all"],
        "num_feeds_regular":                                 num_feeds["regular"],
        "num_feeds_preview":                                 num_feeds["preview"],
        "num_feeds_with_analysed_data":                      num_feeds_with_data["all"],
        "num_feeds_with_analysed_data_regular":              num_feeds_with_data["regular"],
        "num_feeds_with_analysed_data_preview":              num_feeds_with_data["preview"],
        "num_feeds_with_future_opportunity_items":           num_feeds_with_future["all"],
        "num_feeds_with_future_opportunity_items_regular":   num_feeds_with_future["regular"],
        "num_feeds_with_future_opportunity_items_preview":   num_feeds_with_future["preview"],
        "total_num_items":                                   total_items["all"],
        "total_num_items_regular":                           total_items["regular"],
        "total_num_items_preview":                           total_items["preview"],
        "total_num_future_opportunity_items":                total_future["all"],
        "total_num_future_opportunity_items_regular":        total_future["regular"],
        "total_num_future_opportunity_items_preview":        total_future["preview"],
        "total_num_future_week_opportunity_items":           total_future_week["all"],
        "total_num_future_week_opportunity_items_regular":   total_future_week["regular"],
        "total_num_future_week_opportunity_items_preview":   total_future_week["preview"],
        "total_num_item_kinds":                              len(categories["item_kind"]["all"]),
        "total_num_item_types":                              len(categories["item_type"]["all"]),
        "total_num_organizer_names":                         len(categories["organizer"]["all"]),
        "total_num_activities":                              len(categories["activity"]["all"]),
        "total_num_facilities":                              len(categories["facility"]["all"]),
        "total_num_accessibilities":                         len(categories["accessibility"]["all"]),
        "total_num_regions":                                 len(categories["region"]["all"]),
        "total_num_districts":                               len(categories["district"]["all"]),
        "total_num_trusts":                                  len(categories["trust"]["all"]),
        "total_num_items_with_kinds":                        total_num_items_with["item_kind"],
        "total_num_items_with_types":                        total_num_items_with["item_type"],
        "total_num_items_with_organizer_names":              total_num_items_with["organizer"],
        "total_num_items_with_activities":                   total_num_items_with["activity"],
        "total_num_items_with_facilities":                   total_num_items_with["facility"],
        "total_num_items_with_accessibilities":              total_num_items_with["accessibility"],
        "total_num_items_with_regions":                      total_num_items_with["region"],
        "total_num_items_with_districts":                    total_num_items_with["district"],
        "total_num_items_with_trusts":                       total_num_items_with["trust"],
        "total_num_items_with_sad":                          sad.total_num_items_with_sad,
        "total_num_items_without_sad":                       sad.total_num_items_without_sad,
        "total_num_activities_with_sad":                     sad.total_num_activities_with_sad,
        "total_num_activities_without_sad":                  sad.total_num_activities_without_sad,
        "num_sad":                                           sad.num_sad,
        "num_sad_matched":                                   sad.num_sad_matched,
        "num_sad_unmatched":                                 sad.num_sad_unmatched,
        "percentage_sad_matched":                            sad.percentage_sad_matched,
        "percentage_sad_unmatched":                          sad.percentage_sad_unmatched,
    }


def _build_category_rows(
    run_date: datetime,
    categories: dict[str, dict[str, list[dict[str, Any]]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cat, per_scope in categories.items():
        rows.extend(_category_rows_for_bq(run_date, cat, per_scope))
    return rows


def _build_sad_rows(run_date: datetime, sad) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, row in sad.matched.iterrows():
        rows.append({
            "run_date": run_date,
            "sport_and_discipline": row["sport_and_discipline"],
            "activity": row["activity"],
            "is_matched": True,
            "count_items": int(row["count_items"]),
            "count_activities": int(row["count_activities"]),
            "percentage_items": float(row["percentage_items"]),
            "percentage_activities": float(row["percentage_activities"]),
        })
    for _, row in sad.unmatched.iterrows():
        rows.append({
            "run_date": run_date,
            "sport_and_discipline": row["sport_and_discipline"],
            "activity": row["activity"],
            "is_matched": False,
            "count_items": int(row["count_items"]),
            "count_activities": None,
            "percentage_items": float(row["percentage_items"]),
            "percentage_activities": None,
        })
    return rows


def _build_sad_master_rows(run_date: datetime, sad) -> list[dict[str, Any]]:
    return [
        {
            "run_date": run_date,
            "sport": row.get("sport"),
            "discipline": row.get("discipline"),
            "sport_and_discipline": row.get("sport_and_discipline"),
            "is_matched_by_any_feed": bool(row["is_matched_by_any_feed"]),
        }
        for _, row in sad.master.iterrows()
    ]


def _persist_outputs(
    feed_rows: list[dict[str, Any]],
    summary_row: dict[str, Any],
    category_rows: list[dict[str, Any]],
    sad_rows: list[dict[str, Any]],
    master_rows: list[dict[str, Any]],
) -> None:
    logger.info("Writing outputs to BigQuery")
    bigquery_ops.upsert_feed_insights(feed_rows)
    bigquery_ops.append_run_summary(summary_row)
    bigquery_ops.append_category_counts(category_rows)
    bigquery_ops.append_sport_discipline(sad_rows)
    bigquery_ops.append_sport_discipline_master(master_rows)


def _run_quality_assessment(
    run_date: datetime,
    source: _SourceData,
    feed_rows: list[dict[str, Any]],
    opportunities_tbl: str,
    opportunity_ingestion_tbl: str,
    reference_date: date,
) -> None:
    from quality.assess import assess_feed_quality

    active_df_feeds = _filter_active_feeds(
        source.df_feeds, opportunity_ingestion_tbl, reference_date,
    )

    logger.info(
        "Running per-feed data-quality assessment on %d active feeds",
        len(active_df_feeds),
    )
    quality_rows = assess_feed_quality(
        run_date=run_date,
        df_feeds=active_df_feeds,
        df_status=source.df_status,
        feed_rows=feed_rows,
        opportunities_tbl=opportunities_tbl,
        reference_date=reference_date,
        max_workers=int(os.getenv("INGEST_MAX_WORKERS", "4")),
    )
    bigquery_ops.write_feed_quality(quality_rows)


def _filter_active_feeds(
    df_feeds: pd.DataFrame,
    opportunity_ingestion_tbl: str,
    reference_date: date,
) -> pd.DataFrame:
    """Drop stale feeds while keeping every dataset visible.

    A feed is "active" when its ``opportunity_ingestion`` rows in the last
    ``QUALITY_FEED_STALE_DAYS`` days include at least one with ``updated > 0``
    or ``deleted > 0``.

    A stale feed is dropped only if **another feed in the same dataset** is
    active.  When every feed in a dataset is stale, all of them are kept so
    the dataset still produces ``feed_quality`` rows — losing entire
    datasets from the assessment is worse than having a few "stale" rows
    that surface why nothing is moving.
    """
    from quality import queries as quality_queries

    df_active = bigquery_ops.run_query(
        quality_queries.active_feed_ids(opportunity_ingestion_tbl, reference_date)
    )
    active_ids = set(df_active["feed_id"].dropna().tolist())

    is_active = df_feeds["feed_id"].isin(active_ids)
    # Datasets that contain at least one active feed.  Any stale feed in a
    # dataset NOT in this set is preserved (so the dataset still produces
    # ``feed_quality`` rows).  ``isin`` returns False for NULL dataset_urls,
    # which naturally falls through to the "no active sibling" branch and
    # preserves orphan feeds too.
    active_datasets = set(
        df_feeds.loc[is_active, "dataset_url"].dropna().tolist()
    )
    has_active_sibling = df_feeds["dataset_url"].isin(active_datasets)
    keep_mask = is_active | ~has_active_sibling
    kept = df_feeds[keep_mask].copy()

    active_count = int(is_active.sum())
    stale_kept = int((~is_active & ~has_active_sibling).sum())
    skipped = len(df_feeds) - len(kept)

    if skipped or stale_kept:
        logger.info(
            "Quality assessment: keeping %d feeds (%d active + %d stale "
            "preserved for dataset visibility); skipping %d stale feeds with "
            "no updated/deleted items in the last %d days",
            len(kept), active_count, stale_kept, skipped,
            quality_queries.QUALITY_FEED_STALE_DAYS,
        )
    return kept


DISTRICT_LOOKUP_FILENAME = "000-district-region-country.json"


def _load_district_lookup(geo_dir: Path) -> dict[str, dict[str, Any]]:
    """Load the district -> region/country lookup keyed by district name (LAD24NM).

    Produced by ``district_region_country.py``. Returns an empty dict (so the
    enrichment columns stay NULL) if the file is missing.
    """
    path = geo_dir / DISTRICT_LOOKUP_FILENAME
    if not path.exists():
        logger.warning(
            "District lookup %s not found; region/country columns will be NULL", path
        )
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _run_api_tables_export(
    opportunities_tbl: str,
    feeds_tbl: str,
    reference_date: date,
    geo_dir: Path = DEFAULT_GEO_DIR,
) -> None:
    """Build the ``active_opportunities_summary`` table.

    One row per (district, publisher, provider, activity_or_facility) for active
    (future) opportunities, enriched with district/region/country codes and names
    from ``000-district-region-country.json``.
    """
    logger.info("Building active_opportunities_summary (reference_date=%s)", reference_date)
    df = bigquery_ops.run_query(
        queries.active_opportunities_summary(opportunities_tbl, feeds_tbl, reference_date)
    )
    lookup = _load_district_lookup(geo_dir)

    rows: list[dict[str, Any]] = []
    for rec in df.to_dict("records"):
        district_name = rec.get("district_name")
        info = lookup.get(district_name) if district_name else None
        info = info or {}
        rows.append({
            "district_name": district_name,
            "publisher": rec.get("publisher"),
            "provider": rec.get("provider"),
            "opportunity_count": int(rec.get("opportunity_count") or 0),
            "is_activity": rec.get("is_activity"),
            # JSON array string from TO_JSON_STRING(...) -> stored as JSON column.
            "activity_or_facility": rec.get("activity_or_facility"),
            "district_code": info.get("district_code"),
            "region_code": info.get("region_code"),
            "region_name": info.get("region_name"),
            "country_code": info.get("country_code"),
            "country_name": info.get("country_name"),
        })

    bigquery_ops.write_active_opportunities_summary(rows)
    logger.info("Wrote %d rows to active_opportunities_summary", len(rows))


def run(
    verbose: bool = False,
    init_tables: bool = False,
    reference_date: date | None = None,
    skip_quality: bool = False,
    skip_export: bool = False,
) -> None:
    run_date = datetime.now(timezone.utc)
    effective_reference_date = reference_date or run_date.date()
    logger.info("opportunity-insights run starting (run_date=%s)", run_date.isoformat())
    logger.info("Using reference date %s for future opportunity metrics", effective_reference_date.isoformat())

    if init_tables:
        logger.info("Ensuring output tables exist")
        bigquery_ops.ensure_tables()

    opportunities_tbl = bigquery_ops.table_id(bigquery_ops.OPPORTUNITIES_TABLE)
    feeds_tbl = bigquery_ops.table_id(bigquery_ops.FEEDS_TABLE)
    opportunity_ingestion_tbl = bigquery_ops.table_id(bigquery_ops.OPPORTUNITY_INGESTION_TABLE)

    # ---------- Load + per-feed assembly ---------- #
    source = _load_source_data(
        opportunities_tbl, feeds_tbl, opportunity_ingestion_tbl, effective_reference_date
    )

    feed_rows = _build_feed_insights_rows(
        run_date, source.df_feeds, source.df_base, source.df_status,
        source.per_feed_dicts,
        source.regions_counts, source.districts_counts, source.trusts_counts,
    )

    # ---------- Aggregate pass ---------- #
    scope_feed_ids = _build_scope_feed_ids(feed_rows)
    categories = _aggregate_all_categories(opportunities_tbl, source, scope_feed_ids)
    totals = _compute_scope_totals(source.df_feeds, feed_rows, scope_feed_ids)

    # ---------- SAD matching + output assembly ---------- #
    sad = _run_sad(categories)
    summary_row = _build_summary_row(run_date, totals, categories, sad)
    category_rows = _build_category_rows(run_date, categories)
    sad_rows = _build_sad_rows(run_date, sad)
    master_rows = _build_sad_master_rows(run_date, sad)

    # ---------- Persist ---------- #
    # TODO disabled for debugging
    # _persist_outputs(feed_rows, summary_row, category_rows, sad_rows, master_rows)

    # ---------- Data quality assessment ---------- #
    if not skip_quality:
        _run_quality_assessment(
            run_date, source, feed_rows, opportunities_tbl,
            opportunity_ingestion_tbl, effective_reference_date,
        )
    else:
        logger.info("Skipping data-quality assessment (--skip-quality)")

    # ---------- API tables export ---------- #
    if not skip_export:
        _run_api_tables_export(
            opportunities_tbl, feeds_tbl, effective_reference_date, DEFAULT_GEO_DIR,
        )
    else:
        logger.info("Skipping API tables export (--skip-export)")

    logger.info("opportunity-insights run complete")


@click.command()
@click.option("--verbose", is_flag=True, default=False, help="Enable DEBUG logging.")
@click.option("--init-tables", is_flag=True, default=False, help="Ensure output tables exist before running (idempotent).")
@click.option(
    "--reference-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Optional date (YYYY-MM-DD) used to calculate future opportunity metrics.",
)
@click.option(
    "--skip-quality",
    is_flag=True,
    default=False,
    help="Skip the per-feed data-quality assessment step (feed_quality table is not updated).",
)
@click.option(
    "--skip-export",
    is_flag=True,
    default=False,
    help="Skip the API tables export step (active_opportunities_summary is not written).",
)
def cli(
    verbose: bool,
    init_tables: bool,
    reference_date: datetime | None,
    skip_quality: bool,
    skip_export: bool,
) -> None:
    _configure_logging(verbose)
    run(
        verbose=verbose,
        init_tables=init_tables,
        reference_date=reference_date.date() if reference_date else None,
        skip_quality=skip_quality,
        skip_export=skip_export,
    )


if __name__ == "__main__":
    cli()
