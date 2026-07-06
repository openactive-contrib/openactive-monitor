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
from typing import Any, Iterator

import pandas as pd
from pandas import DataFrame

from boundary_lookup import enrich_from_district_lookup, lookup_boundaries, lookup_nhs_trust
from geolocation import _build_location

logger = logging.getLogger(__name__)

MAX_INHERITED_MERGE_DEPTH = 6

DF_COLUMNS = [
    "dataset_url", "feed_id", "id", "data_id", "kind", "modified",
    "json_data", "inherited_data", "activity", "facility", "location",
    "district_name", "region_name",
    "publisher_name", "district_code", "region_code", "country_code", "country_name",
    "nhstrust_name", "nhstrust_code",
    "startDate", "endDate", "ageRange", "level", "has_superEvent", "has_subEvent",
    "accessibilitySupport", "genderRestriction",
    "organization_name", "organization_json",
    "last_updated",
]

# Boundary columns derived from ``location``.  Inherited from a super event
# either indirectly (when the super event's raw ``location`` is inherited and
# its boundaries are recomputed) or directly (when the super event has the
# boundary columns set but no usable ``location``).
_BOUNDARY_COLUMNS: tuple[str, ...] = (
    "district_name",
    "region_name",
    "district_code",
    "region_code",
    "country_code",
    "country_name",
    "nhstrust_name",
    "nhstrust_code",
)



def _resolve_boundaries(location: dict[str, Any]) -> tuple[str | None, str | None]:
    """Resolve (district_name, region_name) from a built location dict."""
    if not location:
        return None, None
    return lookup_boundaries(location.get("latitude"), location.get("longitude"))


def _resolve_nhs_trust(location: dict[str, Any]) -> tuple[str | None, str | None]:
    """Resolve (nhstrust_name, nhstrust_code) from a built location dict."""
    if not location:
        return None, None
    return lookup_nhs_trust(location.get("latitude"), location.get("longitude"))


def _strip_quotes(value: Any) -> Any:
    """Strip surrounding double-quote characters from a string value."""
    if isinstance(value, str):
        return value.strip('"')
    return value


def _strip_quotes_list(value: Any) -> Any:
    """Strip surrounding double-quote characters from string items in a list."""
    if isinstance(value, list):
        return [item.strip('"') if isinstance(item, str) else item for item in value]
    if isinstance(value, str):
        return value.strip('"')
    return value


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


def get_accessibility_support(data: dict) -> list[str] | None:
    """Normalise ``accessibilitySupport`` into a list of ``prefLabel`` strings.

    OpenActive feeds may present ``accessibilitySupport`` as a list of
    ``Concept`` dicts (the common case), a single ``Concept`` dict, or even
    as plain strings.  This helper returns the prefLabels (or the strings
    themselves) as a clean ``list[str]``.

    Returns ``None`` when no labels can be resolved.
    """
    field = data.get("accessibilitySupport")
    if not field:
        return None
    if isinstance(field, dict):
        items: list[Any] = [field]
    elif isinstance(field, list):
        items = field
    else:
        return None
    labels: list[str] = []
    for item in items:
        if isinstance(item, dict):
            label = item.get("prefLabel")
        elif isinstance(item, str):
            label = item
        else:
            label = None
        if isinstance(label, str) and label.strip():
            labels.append(label.strip())
    return labels or None


def get_organization_payload(data: dict) -> Any | None:
    """Return the raw organisation payload from an opportunity.

    Events expose ``organizer`` (Organization, list of Organizations, or URI
    string); FacilityUses expose ``provider`` (Organization).  ``organizer``
    takes priority — when both are present we keep the event's organiser as
    the more specific signal.

    The original shape is preserved so the downstream ``organization_json``
    column reflects the source feed verbatim.  Returns ``None`` for empty
    containers and for blank strings.
    """
    for field in ("organizer", "provider"):
        value = data.get(field)
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        if isinstance(value, (dict, list)) and value:
            return value
    return None


def get_organization_name(data: dict) -> str | None:
    """Resolve the organisation's ``name`` from ``organizer`` / ``provider``.

    Returns the first non-empty ``name`` string found:
      - dict payload → ``payload.name``
      - list payload → first list entry with a non-empty ``name``
      - URI string payload → no embedded name, returns ``None``
    """
    payload = get_organization_payload(data)
    if payload is None:
        return None
    if isinstance(payload, dict):
        candidates: list[Any] = [payload]
    elif isinstance(payload, list):
        candidates = payload
    else:
        return None
    for item in candidates:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def extract_rows(dataset_url: str, feed_id: str, result: dict, publisher_name: str | None = None) -> tuple[list[dict], list[dict]]:
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
            enriched = enrich_from_district_lookup(district_name)
            nhstrust_name, nhstrust_code = _resolve_nhs_trust(location)
            updated.append({
                "dataset_url":    dataset_url,
                "feed_id":        feed_id,
                "id":             item.get("id"),
                "data_id":        data.get("@id") or data.get("id"),
                "kind":           data.get("@type") or data.get("type"),
                "modified":       item.get("modified"),
                "json_data":      data,
                "inherited_data": {},
                "activity":       get_activity(data),
                "facility":       get_facility(data),
                "location":       location,
                "district_name":  district_name,
                "region_name":    region_name,
                "publisher_name": publisher_name,
                "district_code":  enriched["district_code"],
                "region_code":    enriched["region_code"],
                "country_code":   enriched["country_code"],
                "country_name":   enriched["country_name"],
                "nhstrust_name":  nhstrust_name,
                "nhstrust_code":  nhstrust_code,
                "startDate":      _normalize_timestamp(data.get("startDate") or data.get("date_start")),
                "endDate":        _normalize_timestamp(data.get("endDate") or data.get("date_end")),
                "ageRange":       data.get("ageRange"),
                "level":          data.get("level"),
                "has_superEvent":       _strip_quotes(data.get("superEvent") or data.get("facilityUse")),
                "has_subEvent":         _strip_quotes_list(data.get("subEvent")),
                "accessibilitySupport": get_accessibility_support(data),
                "genderRestriction":    (data.get("genderRestriction") or None),
                "organization_name":    get_organization_name(data),
                "organization_json":    get_organization_payload(data),
                "last_updated":         datetime.now(timezone.utc).date(),
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


def _iter_nested_ifus(json_data: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield ``(ifu_@id, ifu_item)`` for each nested IndividualFacilityUse.

    A ``FacilityUse`` may embed its ``IndividualFacilityUse`` children inline in
    a ``individualFacilityUse`` list rather than publishing them as standalone
    opportunities.  A ``Slot``'s ``facilityUse`` reference can then point at one
    of those nested IFU ``@id``s, which never appears as any row's ``data_id``.
    This helper surfaces those ``(id, item)`` pairs so the parent-payload lookup
    can register a virtual entry for each, letting the Slot inherit from the
    IFU (which in turn inherits from its containing FacilityUse).
    """
    if not isinstance(json_data, dict):
        return
    ifus = json_data.get("individualFacilityUse")
    if not isinstance(ifus, list):
        return
    for item in ifus:
        if not isinstance(item, dict):
            continue
        ifu_id = item.get("@id") or item.get("id")
        if isinstance(ifu_id, str) and ifu_id:
            yield ifu_id, item


def _build_super_event_payload_by_data_id(df, df_bigquery):
    """Build data_id -> payload lookup from old then new frame; new frame overrides duplicates.

    The payload combines the parent's ``inherited_data`` and ``json_data`` so
    that ``apply_inherited_data`` can read raw OpenActive fields (location,
    activity, etc.).  We also surface the parent's pre-computed boundary
    columns (district/region/country names + codes) on the payload so children
    can inherit them directly when the parent's raw ``location`` is missing.

    In addition to keying each row by its own ``data_id``, we register a
    *virtual* payload for every IndividualFacilityUse embedded inline in a
    FacilityUse's ``json_data.individualFacilityUse`` list.  The virtual payload
    is the FacilityUse payload overlaid with that specific IFU item's own fields
    (IFU-specific values win), so a Slot pointing at a nested IFU ``@id`` can
    inherit correctly.  Virtual entries never clobber a real row: they are only
    folded in for IFU ``@id``s that no real ``data_id`` claims.
    """
    payload_by_data_id = {}
    # Kept separate so real rows always win — a dataset may also publish the same
    # IFU as a first-class row via a dedicated IndividualFacilityUse feed.
    virtual_ifu_payloads: dict[str, dict[str, Any]] = {}
    for frame in (df_bigquery, df):
        if frame.empty or "data_id" not in frame.columns:
            continue
        for row in frame.itertuples(index=False):
            row_data_id = getattr(row, "data_id", None)
            row_json = getattr(row, "json_data", None)
            row_inherited = getattr(row, "inherited_data", None)
            json_data = row_json if isinstance(row_json, dict) else {}
            inherited = row_inherited if isinstance(row_inherited, dict) else {}
            payload = {**inherited, **json_data}
            for col in _BOUNDARY_COLUMNS:
                val = getattr(row, col, None)
                if isinstance(val, str) and val:
                    payload[col] = val
            if isinstance(row_data_id, str) and row_data_id:
                payload_by_data_id[row_data_id] = payload
            # Register virtual payloads for any inline IndividualFacilityUse
            # children.  The new frame is iterated last, so its FacilityUse rows
            # override older BigQuery copies here too.
            for ifu_id, ifu_item in _iter_nested_ifus(json_data):
                virtual_ifu_payloads[ifu_id] = {**payload, **ifu_item}

    for ifu_id, virtual_payload in virtual_ifu_payloads.items():
        if ifu_id not in payload_by_data_id:
            payload_by_data_id[ifu_id] = virtual_payload
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
            super_event_id = super_event_ref.strip('"')
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


def _is_slot_empty(value: Any) -> bool:
    """True if a DataFrame cell should be treated as 'missing' for inheritance."""
    if value is None:
        return True
    if isinstance(value, (list, dict)):
        return len(value) == 0
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _set_if_empty(df: DataFrame, idx, col: str, value: Any) -> None:
    """Assign ``value`` to ``df.at[idx, col]`` only when the current cell is empty
    and ``value`` is non-empty. Keeps the 'fill only, never overwrite' policy."""
    if _is_slot_empty(value):
        return
    if _is_slot_empty(df.at[idx, col]):
        df.at[idx, col] = value


def apply_inherited_data(df: DataFrame, idx, inherited_data: dict[str, Any]):
    """Fill missing fields on a row from its parent's inherited data.

    Every assignment is guarded so that an already-populated cell is never
    overwritten — the only side effect is filling in cells that were empty.
    """
    if get_activity(inherited_data) and (not df.at[idx, "activity"] or df.at[idx, "activity"] == []):
        df.at[idx, "activity"] = get_activity(inherited_data)
    if get_facility(inherited_data) and (not df.at[idx, "facility"] or df.at[idx, "facility"] == []):
        df.at[idx, "facility"] = get_facility(inherited_data)
    if "location" in inherited_data and (not df.at[idx, "location"] or df.at[idx, "location"] == {}):
        new_location = _build_location(inherited_data["location"])
        df.at[idx, "location"] = new_location
        district_name, region_name = _resolve_boundaries(new_location)
        enriched = enrich_from_district_lookup(district_name)
        nhstrust_name, nhstrust_code = _resolve_nhs_trust(new_location)
        # Fill only-when-empty so an existing boundary value isn't overwritten.
        _set_if_empty(df, idx, "district_name", district_name)
        _set_if_empty(df, idx, "region_name", region_name)
        _set_if_empty(df, idx, "district_code", enriched["district_code"])
        _set_if_empty(df, idx, "region_code", enriched["region_code"])
        _set_if_empty(df, idx, "country_code", enriched["country_code"])
        _set_if_empty(df, idx, "country_name", enriched["country_name"])
        _set_if_empty(df, idx, "nhstrust_name", nhstrust_name)
        _set_if_empty(df, idx, "nhstrust_code", nhstrust_code)
    # Direct inheritance of boundary columns from the super event row — covers
    # the case where the parent has these populated but no usable raw
    # ``location`` (e.g. it inherited them from its own super event).
    for col in _BOUNDARY_COLUMNS:
        _set_if_empty(df, idx, col, inherited_data.get(col))
    if "startDate" in inherited_data and (not df.at[idx, "startDate"] or df.at[idx, "startDate"] == ""):
        df.at[idx, "startDate"] = _normalize_timestamp(inherited_data["startDate"])
    if "endDate" in inherited_data and (not df.at[idx, "endDate"] or df.at[idx, "endDate"] == ""):
        df.at[idx, "endDate"] = _normalize_timestamp(inherited_data["endDate"])
    if "ageRange" in inherited_data and (not df.at[idx, "ageRange"] or df.at[idx, "ageRange"] == {}):
        df.at[idx, "ageRange"] = inherited_data["ageRange"]
    if "level" in inherited_data and (not df.at[idx, "level"] or df.at[idx, "level"] == []):
        df.at[idx, "level"] = inherited_data["level"]
    inherited_access = get_accessibility_support(inherited_data)
    if inherited_access and _is_slot_empty(df.at[idx, "accessibilitySupport"]):
        df.at[idx, "accessibilitySupport"] = inherited_access
    inherited_gender = inherited_data.get("genderRestriction")
    if (
        isinstance(inherited_gender, str)
        and inherited_gender.strip()
        and _is_slot_empty(df.at[idx, "genderRestriction"])
    ):
        df.at[idx, "genderRestriction"] = inherited_gender
    inherited_org_name = get_organization_name(inherited_data)
    if inherited_org_name and _is_slot_empty(df.at[idx, "organization_name"]):
        df.at[idx, "organization_name"] = inherited_org_name


def _row_super_event_payload(df: pd.DataFrame, idx) -> dict[str, Any]:
    """Build the inheritable payload for a 'parent' row, including its
    pre-computed boundary columns."""
    parent_json = df.at[idx, "json_data"] if isinstance(df.at[idx, "json_data"], dict) else {}
    parent_inherited = df.at[idx, "inherited_data"] if isinstance(df.at[idx, "inherited_data"], dict) else {}
    payload: dict[str, Any] = {**parent_inherited, **parent_json}
    for col in _BOUNDARY_COLUMNS:
        if col in df.columns:
            val = df.at[idx, col]
            if isinstance(val, str) and val:
                payload[col] = val
    return payload


def handle_sub_events(df: pd.DataFrame, sub_event_indices_by_data_id: dict[str, list[int]]) -> None:
    """For rows that list subEvents, push the parent's inheritable fields into
    each subEvent row using the same fill-only-when-empty rules as
    ``handle_super_events``."""
    sub_events_mask = df["has_subEvent"].notnull()
    sub_events_indices = df[sub_events_mask].index.tolist()

    for idx in sub_events_indices:
        sub_event_refs = df.at[idx, "has_subEvent"]
        if not isinstance(sub_event_refs, list):
            continue
        super_event_data: dict[str, Any] | None = None
        for sub_event_ref in sub_event_refs:
            if isinstance(sub_event_ref, dict):
                continue
            if not isinstance(sub_event_ref, str):
                continue
            sub_event_id = sub_event_ref.strip('"')
            sub_event_target_indices = sub_event_indices_by_data_id.get(sub_event_id, [])
            if not sub_event_target_indices:
                continue
            if super_event_data is None:
                super_event_data = _row_super_event_payload(df, idx)
                super_event_data = unpack_data(super_event_data)
            for sub_idx in sub_event_target_indices:
                if sub_idx == idx:
                    continue
                current_json_data = df.at[sub_idx, "json_data"]
                if not isinstance(current_json_data, dict):
                    current_json_data = {}
                current_inherited = df.at[sub_idx, "inherited_data"]
                if not isinstance(current_inherited, dict):
                    current_inherited = {}
                updated_inherited = _merge_inherited_data(
                    current_json_data, super_event_data, current_inherited
                )
                apply_inherited_data(df, sub_idx, updated_inherited)


def denormalize_dataset(df: pd.DataFrame, df_bigquery: pd.DataFrame) -> None:
    """Apply superEvent → subEvent inheritance over a dataset's DataFrame in place."""
    super_event_payload_by_data_id = _build_super_event_payload_by_data_id(df, df_bigquery)
    sub_event_indices_by_data_id = _build_df_indices_by_data_id(df, df_bigquery)
    handle_super_events(df, super_event_payload_by_data_id)
    handle_sub_events(df, sub_event_indices_by_data_id)
