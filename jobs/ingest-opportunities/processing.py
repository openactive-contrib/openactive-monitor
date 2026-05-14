"""Item-processing seam for ingest-opportunities.

Transforms RPDE-shaped opportunity items (``{state, kind, id, modified, data}``)
into BigQuery-ready DataFrame rows, and applies superEvent / subEvent
denormalisation. Imported by ``main.py`` and by sibling jobs (e.g.
``backfill-from-pickles``) that need to write to the same ``opportunities``
table without re-implementing this logic.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
from pandas import DataFrame

from boundary_lookup import lookup_boundaries
from geolocation import _build_location

logger = logging.getLogger(__name__)

MAX_INHERITED_MERGE_DEPTH = 6

DF_COLUMNS = [
    "dataset_url", "feed_id", "id", "data_id", "kind", "modified",
    "json_data", "inherited_data", "activity", "facility", "location",
    "district_name", "region_name",
    "startDate", "endDate", "ageRange", "level", "has_superEvent", "has_subEvent",
    "last_updated",
]


def _resolve_boundaries(location: dict[str, Any]) -> tuple[str | None, str | None]:
    """Resolve (district_name, region_name) from a built location dict."""
    if not location:
        return None, None
    return lookup_boundaries(location.get("latitude"), location.get("longitude"))


# ---------------------------------------------------------------------------
# Item flattening
# ---------------------------------------------------------------------------

def _parse_date(date_value: object) -> date | None:
    if date_value is None:
        return None
    if isinstance(date_value, datetime):
        return date_value.date()
    elif isinstance(date_value, date):
        return date_value
    elif isinstance(date_value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                dt = datetime.strptime(date_value.split("T")[0], "%Y-%m-%d")
                return dt.date()
            except (ValueError, AttributeError):
                continue
    return None


def _normalize_timestamp(value: object, default_time: str = "00:00:00") -> str | None:
    """Return a BigQuery-friendly UTC timestamp string.

    Accepts date-only or datetime-like values and fills missing time components
    with ``default_time``.
    """
    if value is None:
        return None

    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S+00:00")

    if isinstance(value, date):
        return f"{value.isoformat()} {default_time}+00:00"

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if len(raw) == 10 and raw[4] == "-" and raw[7] == "-":
            return f"{raw} {default_time}+00:00"

        parsed = pd.to_datetime(raw.replace("Z", "+00:00"), utc=True, errors="coerce")
        if pd.isna(parsed):
            logger.warning("Dropping unparseable datetime value for opportunities row: %r", value)
            return None
        return parsed.strftime("%Y-%m-%d %H:%M:%S+00:00")

    return None


def unpack_data(data: dict) -> dict:
    """Unpack nested data dicts to surface the canonical fields.

    If ``eventSchedule`` is present, derive ``startDate`` from the earliest
    schedule start and ``endDate`` from the latest schedule end so downstream
    queries don't have to traverse the schedule list themselves.
    """
    if "eventSchedule" in data and isinstance(data["eventSchedule"], list) and len(data["eventSchedule"]) > 0:
        start_dates = []
        end_dates = []
        for event_schedule in data["eventSchedule"]:
            if isinstance(event_schedule, dict):
                parsed_start = _parse_date(event_schedule.get("startDate"))
                parsed_end = _parse_date(event_schedule.get("endDate"))
                if parsed_start:
                    start_dates.append(parsed_start)
                if parsed_end:
                    end_dates.append(parsed_end)
        if start_dates:
            data["startDate"] = _normalize_timestamp(min(start_dates))
        if end_dates:
            data["endDate"] = _normalize_timestamp(max(end_dates))

    data["startDate"] = _normalize_timestamp(data.get("startDate") or data.get("date_start"))
    data["endDate"] = _normalize_timestamp(data.get("endDate") or data.get("date_end"))
    return data


def get_activity(data: dict) -> list[Any]:
    """Extract activity labels from activity or activities field."""
    # Try both singular and plural forms
    activities_field = data.get("activity") or data.get("activities")
    if activities_field:
        if isinstance(activities_field, dict):
            label = activities_field.get("prefLabel")
            return [label] if label else []
        elif isinstance(activities_field, list):
            labels = [
                item.get("prefLabel")
                for item in activities_field
                if isinstance(item, dict) and item.get("prefLabel")
            ]
            return labels
    return []


def get_facility(data: dict) -> list[Any]:
    """Extract facility labels from facilityType or facilities field."""
    # Try both singular and plural forms
    facility_field = data.get("facilityType") or data.get("facilities")
    if facility_field:
        facility_items = []
        if isinstance(facility_field, dict):
            facility_items = [facility_field]
        elif isinstance(facility_field, list):
            facility_items = facility_field

        if facility_items:
            labels = [
                item.get("prefLabel")
                for item in facility_items
                if isinstance(item, dict) and item.get("prefLabel")
            ]
            return labels
    return []


def extract_rows(dataset_url: str, feed_id: str, result: dict) -> tuple[list[dict], list[dict]]:
    """Flatten RPDE ``items`` into row dicts ready for a DataFrame.

    ``result`` is the dict returned by ``rpde.access_feed_url`` (or any
    equivalent shape — the only field used is ``items``, a list of
    ``{state, kind, id, modified, data}`` dicts).
    """
    updated: list[dict] = []
    deleted: list[dict] = []
    for item in result.get("items", []):
        if not isinstance(item, dict):
            continue

        if item.get("state") == "deleted":
            deleted.append({
                "dataset_url": dataset_url,
                "feed_id": feed_id,
                "id": item.get("id"),
                "modified": item.get("modified"),
            })
        else:
            data = item.get("data") if isinstance(item.get("data"), dict) else {}
            data = unpack_data(data)
            location = _build_location(data.get("location"))
            district_name, region_name = _resolve_boundaries(location)
            updated.append({
                "dataset_url":    dataset_url,
                "feed_id":        feed_id,
                "id":             item.get("id"),
                "data_id":        data.get("@id"),
                "kind":           data.get("@type") or data.get("type"),
                "modified":       item.get("modified"),
                "json_data":      data,
                "inherited_data": {},
                "activity":       get_activity(data),
                "facility":       get_facility(data),
                "location":       location,
                "district_name":  district_name,
                "region_name":    region_name,
                "startDate":      _normalize_timestamp(data.get("startDate") or data.get("date_start")),
                "endDate":        _normalize_timestamp(data.get("endDate") or data.get("date_end")),
                "ageRange":       data.get("ageRange"),
                "level":          data.get("level"),
                "has_superEvent": data.get("superEvent") or data.get("facilityUse"),
                "has_subEvent":   data.get("subEvent"),
                "last_updated":   datetime.now(timezone.utc).date(),
            })
    return updated, deleted


# ---------------------------------------------------------------------------
# Denormalization
# ---------------------------------------------------------------------------

def _merge_inherited_data(
    json_data: dict[str, Any],
    super_event_data: dict[str, Any],
    current_inherited: dict[str, Any],
    seen_pairs: set[tuple[int, int]] | None = None,
    depth: int = 0,
) -> dict[str, Any]:
    """Recursively merge super_event properties into inherited_data.

    Skips keys that already exist in json_data (direct data takes priority).
    Existing inherited_data values are overwritten by super_event values.
    """
    merged = dict(current_inherited)
    if seen_pairs is None:
        seen_pairs = set()

    if depth >= MAX_INHERITED_MERGE_DEPTH:
        logger.warning("Reached max inherited merge depth=%d; skipping deeper merge", MAX_INHERITED_MERGE_DEPTH)
        return merged

    merge_pair = (id(json_data), id(super_event_data))
    if merge_pair in seen_pairs:
        logger.warning("Detected cyclic inherited merge input; skipping repeated merge branch")
        return merged
    seen_pairs.add(merge_pair)

    for key, value in super_event_data.items():
        if key in json_data:
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_inherited_data(
                json_data.get(key, {}),
                value,
                merged.get(key, {}),
                seen_pairs,
                depth + 1,
            )
        else:
            merged[key] = value
    return merged


def _build_super_event_payload_by_data_id(df, df_bigquery):
    """Build data_id -> payload lookup from old then new frame; new frame overrides duplicates."""
    payload_by_data_id = {}
    for frame in (df_bigquery, df):
        if frame.empty or "data_id" not in frame.columns:
            continue
        for row in frame.itertuples(index=False):
            row_data_id = getattr(row, "data_id", None)
            if not isinstance(row_data_id, str) or not row_data_id:
                continue
            row_json = getattr(row, "json_data", None)
            row_inherited = getattr(row, "inherited_data", None)
            json_data = row_json if isinstance(row_json, dict) else {}
            inherited = row_inherited if isinstance(row_inherited, dict) else {}
            payload_by_data_id[row_data_id] = {**inherited, **json_data}
    return payload_by_data_id


def _build_df_indices_by_data_id(df: pd.DataFrame, df_bigquery: pd.DataFrame) -> dict[str, list[int]]:
    """Build data_id -> mutable df indices using old/new frame iteration; only current df adds indices."""
    index_lookup: dict[str, list[int]] = {}
    for frame in (df_bigquery, df):
        if frame.empty or "data_id" not in frame.columns:
            continue
        is_current_df = frame is df
        for idx, row_data_id in frame["data_id"].items():
            if not isinstance(row_data_id, str) or not row_data_id:
                continue
            if is_current_df:
                index_lookup.setdefault(row_data_id, []).append(idx)
            else:
                index_lookup.setdefault(row_data_id, [])
    return index_lookup


def handle_super_events(
    df: pd.DataFrame,
    super_event_payload_by_data_id: dict[str, dict[str, Any]],
) -> None:
    """For rows with a superEvent, inherit missing properties from the parent."""
    super_events_mask = df["has_superEvent"].notnull()
    super_events_indices = df[super_events_mask].index.tolist()

    for idx in super_events_indices:
        super_event_ref = df.at[idx, "has_superEvent"]
        super_event_data: dict[str, Any] | None = None

        if isinstance(super_event_ref, dict):
            super_event_data = super_event_ref
        elif isinstance(super_event_ref, str):
            super_event_id = super_event_ref
            row_data_id = df.at[idx, "data_id"]
            if isinstance(row_data_id, str) and super_event_id == row_data_id:
                logger.warning("Skipping self-referential superEvent for data_id=%s", row_data_id)
                continue
            super_event_data = super_event_payload_by_data_id.get(super_event_id)

        if super_event_data:
            super_event_data = unpack_data(super_event_data)
            current_json_data = df.at[idx, "json_data"]
            if not isinstance(current_json_data, dict):
                current_json_data = {}

            current_inherited = df.at[idx, "inherited_data"]
            if not isinstance(current_inherited, dict):
                current_inherited = {}

            updated_inherited = _merge_inherited_data(current_json_data, super_event_data, current_inherited)
            apply_inherited_data(df, idx, updated_inherited)


def apply_inherited_data(df: DataFrame, idx, inherited_data: dict[str, Any]):
    """Fill missing fields on a row from its parent's inherited data."""
    if get_activity(inherited_data) and (not df.at[idx, "activity"] or df.at[idx, "activity"] == []):
        df.at[idx, "activity"] = get_activity(inherited_data)
    if get_facility(inherited_data) and (not df.at[idx, "facility"] or df.at[idx, "facility"] == []):
        df.at[idx, "facility"] = get_facility(inherited_data)
    if "location" in inherited_data and (not df.at[idx, "location"] or df.at[idx, "location"] == {}):
        new_location = _build_location(inherited_data["location"])
        df.at[idx, "location"] = new_location
        district_name, region_name = _resolve_boundaries(new_location)
        df.at[idx, "district_name"] = district_name
        df.at[idx, "region_name"] = region_name
    if "startDate" in inherited_data and (not df.at[idx, "startDate"] or df.at[idx, "startDate"] == ""):
        df.at[idx, "startDate"] = _normalize_timestamp(inherited_data["startDate"])
    if "endDate" in inherited_data and (not df.at[idx, "endDate"] or df.at[idx, "endDate"] == ""):
        df.at[idx, "endDate"] = _normalize_timestamp(inherited_data["endDate"])
    if "ageRange" in inherited_data and (not df.at[idx, "ageRange"] or df.at[idx, "ageRange"] == {}):
        df.at[idx, "ageRange"] = inherited_data["ageRange"]
    if "level" in inherited_data and (not df.at[idx, "level"] or df.at[idx, "level"] == []):
        df.at[idx, "level"] = inherited_data["level"]


def handle_sub_events(df: pd.DataFrame, sub_event_indices_by_data_id: dict[str, list[int]]) -> None:
    """For rows with subEvents, enrich the subEvent rows from this row's data."""
    sub_events_mask = df["has_subEvent"].notnull()
    sub_events_indices = df[sub_events_mask].index.tolist()

    for idx in sub_events_indices:
        sub_event_refs = df.at[idx, "has_subEvent"]
        if isinstance(sub_event_refs, list):
            for sub_event_ref in sub_event_refs:
                if isinstance(sub_event_ref, dict):
                    continue
                elif isinstance(sub_event_ref, str):
                    sub_event_id = sub_event_ref
                    sub_event_indices = sub_event_indices_by_data_id.get(sub_event_id, [])
                    if sub_event_indices:
                        parent_json = df.at[idx, "json_data"] if isinstance(df.at[idx, "json_data"], dict) else {}
                        parent_inherited = df.at[idx, "inherited_data"] if isinstance(df.at[idx, "inherited_data"], dict) else {}
                        super_event_data = {**parent_inherited, **parent_json}
                        for sub_idx in sub_event_indices:
                            if sub_idx == idx:
                                continue
                            current_json = df.at[sub_idx, "json_data"] if isinstance(df.at[sub_idx, "json_data"], dict) else {}
                            to_inherit = {k: super_event_data[k] for k in super_event_data if k not in current_json}
                            df.at[sub_idx, "inherited_data"] = to_inherit


def denormalize_dataset(df: pd.DataFrame, df_bigquery: pd.DataFrame) -> None:
    """Apply superEvent → subEvent inheritance over a dataset's DataFrame in place."""
    super_event_payload_by_data_id = _build_super_event_payload_by_data_id(df, df_bigquery)
    sub_event_indices_by_data_id = _build_df_indices_by_data_id(df, df_bigquery)
    handle_super_events(df, super_event_payload_by_data_id)
    handle_sub_events(df, sub_event_indices_by_data_id)
