import logging
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import click
import pandas as pd
from dotenv import load_dotenv
from pandas import DataFrame

from bigquery_ops import (
    delete_dataset_opportunities,
    drain_deferred_deletes_until_timeout,
    get_dataset_opportunities,
    get_feeds,
    get_last_ingestion_info,
    retry_deferred_deletes,
    write_dataset_opportunities,
    write_opportunity_ingestion_records,
)
from geolocation import _build_location
from rpde import access_feed_url

load_dotenv()

CSV_OUTPUT_DIR = os.getenv("OPPORTUNITY_CSV_OUTPUT_DIR", "./opportunities/csv")

FEED_EXECUTION_ORDER = ["HeadlineEvent", "Event", "OnDemandEvent", "FacilityUse", "IndividualFacilityUse", "Slot", "SessionSeries", "ScheduledSession", "CourseInstance", ""]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    """Configure app logging and set RPDE logger to DEBUG in verbose mode."""
    logging.getLogger().setLevel(logging.DEBUG if verbose else logging.INFO)
    logging.getLogger("rpde").setLevel(logging.DEBUG if verbose else logging.INFO)


DF_COLUMNS = [
    "dataset_url", "feed_id", "id", "data_id", "kind", "modified",
    "json_data", "inherited_data", "activity", "location", "startDate", "endDate", "ageRange", "level", "has_superEvent", "has_subEvent"
]


def _parse_date(date_value: object) -> date | None:
    """
    Parse a date value (string or datetime) and return a date object.
    Supports common date formats: YYYY-MM-DD, ISO datetime strings, etc.
    Returns None if parsing fails.
    """
    if date_value is None:
        return None

    if isinstance(date_value, datetime):
        return date_value.date()
    elif isinstance(date_value, date):
        return date_value
    elif isinstance(date_value, str):
        # Try common date formats
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                dt = datetime.strptime(date_value.split("T")[0], "%Y-%m-%d")
                return dt.date()
            except (ValueError, AttributeError):
                continue

    return None


def unpack_data(data: dict) -> dict:
    """
    Unpack some nested 'data' dicts until we get to the core data.
    This is needed to handle cases where the same data may exist in different locations. Such as Event.startDate vs Event.eventSchedule.startDate.
    If eventSchedule exists, extract the earliest startDate and latest endDate from all items.
    Dates are parsed to handle string dates correctly.
    """
    if "eventSchedule" in data and isinstance(data["eventSchedule"], list) and len(data["eventSchedule"]) > 0:
        start_dates = []
        end_dates = []

        for event_schedule in data["eventSchedule"]:
            if isinstance(event_schedule, dict):
                start = event_schedule.get("startDate")
                end = event_schedule.get("endDate")

                # Parse dates safely
                parsed_start = _parse_date(start)
                parsed_end = _parse_date(end)

                if parsed_start:
                    start_dates.append(parsed_start)
                if parsed_end:
                    end_dates.append(parsed_end)

        # Use the earliest start date and latest end date
        if start_dates:
            data["startDate"] = str(min(start_dates))
        if end_dates:
            data["endDate"] = str(max(end_dates))

    return data

def _extract_rows(dataset_url: str, feed_id: str, result: dict) -> tuple[list[dict], list[dict]]:
    """
    Flatten opportunity *items* into row dicts ready for a DataFrame.
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
            updated.append({
                "dataset_url":    dataset_url,
                "feed_id":        feed_id,
                "id":             item.get("id"),
                "data_id":        data.get("@id"),
                "kind":           data.get("@type"),
                "modified":       item.get("modified"),
                "json_data":      data,
                "inherited_data": {},
                "activity":         get_activity(data),
                "location":       _build_location(data.get("location")),
                "startDate":      data.get("startDate"),
                "endDate":        data.get("endDate"),
                "ageRange":       data.get("ageRange", {}),
                "level":          data.get("level", {}),
                "has_superEvent": data.get("superEvent") or data.get("facilityUse"),
                "has_subEvent":     data.get("subEvent"),
            })
    return updated, deleted


def get_activity(data: dict) -> list[Any]:
    """
    Extract a clean activity list from an opportunity data.
    FacilityUse may have a category instead of activity, and some older datasets may have activity nested in different ways. Try to extract activity from common locations.
    Args:
        data: opportunity data dict.
    Returns:
        list of activities
    """
    if data.get("activity"):
        if isinstance(data["activity"], dict):
            return [data["activity"].get("prefLabel")]
        elif isinstance(data["activity"], list):
            return [activity.get("prefLabel") for activity in data["activity"]]
    if data.get("facilityType"):
        facility_type = ""
        if isinstance(data["facilityType"], dict):
            facility_type = data["facilityType"]
        elif isinstance(data["facilityType"], list) and len(data["facilityType"]) > 0:
            facility_type = data["facilityType"][0]
        if facility_type and facility_type.get("prefLabel"):
            return facility_type.get("prefLabel")
    if data.get("category"):
        if isinstance(data["category"], dict):
            return [data["category"]]
        elif isinstance(data["category"], list):
            return data["category"]
    if data.get("name"):
        return [data["name"]]
    return []


def _write_dataset_csv(dataset_url: str, dataset_df: pd.DataFrame) -> None:
    """
    For debugging only.
    Write all collected rows for one dataset_url to a single CSV.
    """
    Path(CSV_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    safe_name = "".join(
        ch if ch.isalnum() or ch in ("-", "_") else "_"
        for ch in dataset_url
    )
    output_path = Path(CSV_OUTPUT_DIR) / f"{safe_name}.csv"

    dataset_df.to_csv(output_path, index=False)
    logger.info("Wrote %d rows to %s", len(dataset_df), output_path)

def _merge_inherited_data(json_data: dict[str, Any], super_event_data: dict[str, Any], current_inherited: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge super_event properties into inherited_data, excluding keys that exist in json_data.
    Existing inherited_data values are overwritten by super_event values.

    Args:
        json_data: Current row's direct data.
        super_event_data: Data from the superEvent row.
        current_inherited: Existing inherited_data dict.

    Returns:
        Updated inherited_data dict with new properties from super_event_data.
    """
    merged = dict(current_inherited)  # Start with existing inherited data

    for key, value in super_event_data.items():
        # Skip keys that exist in json_data (prioritize direct data)
        if key in json_data:
            continue

        # For nested dicts, recursively merge
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_inherited_data(
                json_data.get(key, {}),
                value,
                merged.get(key, {})
            )
        else:
            # Overwrite with super_event value
            merged[key] = value

    return merged


def handle_super_events(df: pd.DataFrame, df_bigquery: pd.DataFrame) -> None:
    """
    For rows with a superEvent, find the corresponding superEvent row and inherit properties.
    Updates inherited_data to contain only properties from superEvent that don't exist in json_data.
    Nested dict properties are recursively merged.
    Df is modified in place.
    Args:
        df: DataFrame containing the dataset rows newly collected.
        df_bigquery: DataFrame containing the rows from bigquery table.
    """
    super_events_mask = df["has_superEvent"].notnull()
    super_events_indices = df[super_events_mask].index.tolist()

    # merge df and df_bigquery to have holistic view of all rows for superEvent lookup, prioritizing df for any overlapping rows
    combined_df = pd.concat([df_bigquery, df]).drop_duplicates(subset=["data_id"], keep="last").reset_index(drop=True)

    for idx in super_events_indices:
        super_event_ref = df.at[idx, "has_superEvent"]
        super_event_data: dict[str, Any] | None = None

        # Resolve superEvent reference: can be inline dict or @id string reference
        if isinstance(super_event_ref, dict):
            # inline dict
            super_event_data = super_event_ref
        elif isinstance(super_event_ref, str):
            # super event reference
            super_event_id = super_event_ref
            super_event_rows = combined_df[combined_df["data_id"] == super_event_id]
            if not super_event_rows.empty:
                # Extract and merge json_data and inherited_data from the superEvent row
                super_event_json = super_event_rows.iloc[0]["json_data"]
                super_event_inherited = super_event_rows.iloc[0]["inherited_data"]

                json_data_dict = super_event_json if isinstance(super_event_json, dict) else {}
                inherited_dict = super_event_inherited if isinstance(super_event_inherited, dict) else {}

                # Merge inherited into json_data (json_data takes precedence)
                super_event_data = {**inherited_dict, **json_data_dict}

        if super_event_data:
            super_event_data = unpack_data(super_event_data)
            current_json_data = df.at[idx, "json_data"]
            if not isinstance(current_json_data, dict):
                current_json_data = {}

            current_inherited = df.at[idx, "inherited_data"]
            if not isinstance(current_inherited, dict):
                current_inherited = {}

            # Merge inherited properties
            updated_inherited = _merge_inherited_data(current_json_data, super_event_data, current_inherited)
            df.at[idx, "inherited_data"] = updated_inherited
            apply_inherited_data(df, idx, updated_inherited)


def apply_inherited_data(df: DataFrame, idx, inherited_data: dict[str, Any]):
    """
    Applies inherited properties to the current row if they don't exist in the row's own json_data.
        df: DataFrame containing the dataset rows.
        idx: Index of the current row to apply inherited data to.
        inherited_data: Inherited properties from the superEvent to apply to the current row. Only applied if the current row doesn't have these properties in its own json_data.

    Returns:
        None. The DataFrame is modified in place.
    """
    if get_activity(inherited_data) and (not df.at[idx, "activity"] or df.at[idx, "activity"] == {}):
        df.at[idx, "activity"] = get_activity(inherited_data)
    if "location" in inherited_data and (not df.at[idx, "location"] or df.at[idx, "location"] == {}):
        df.at[idx, "location"] = _build_location(inherited_data["location"])
    if "startDate" in inherited_data and (not df.at[idx, "startDate"] or df.at[idx, "startDate"] == ""):
        df.at[idx, "startDate"] = inherited_data["startDate"]
    if "endDate" in inherited_data and (not df.at[idx, "endDate"] or df.at[idx, "endDate"] == ""):
        df.at[idx, "endDate"] = inherited_data["endDate"]
    if "ageRange" in inherited_data and (not df.at[idx, "ageRange"] or df.at[idx, "ageRange"] == {}):
        df.at[idx, "ageRange"] = inherited_data["ageRange"]
    if "level" in inherited_data and (not df.at[idx, "level"] or df.at[idx, "level"] == {}):
        df.at[idx, "level"] = inherited_data["level"]



def handle_sub_events(df: pd.DataFrame, df_bigquery: pd.DataFrame) -> None:
    """
    For rows with a subEvent, find the corresponding subEvent rows and enrich them with properties from the current row.
    This is the inverse of superEvent handling - we want to enrich subEvents with properties from the parent event where they don't have them directly.
    Df is modified in place.
    Args:
        df: DataFrame containing the dataset rows newly collected.
        df_bigquery: DataFrame containing the rows from bigquery table. [Not used yet, don't know how to handle subEvents referencing BQ]
    """
    sub_events_mask = df["has_subEvent"].notnull()
    sub_events_indices = df[sub_events_mask].index.tolist()

    for idx in sub_events_indices:
        sub_event_refs = df.at[idx, "has_subEvent"]
        if isinstance(sub_event_refs, list):
            for sub_event_ref in sub_event_refs:
                if isinstance(sub_event_ref, dict):
                    continue  # inline dict subEvent - we won't be able to enrich this so skip
                elif isinstance(sub_event_ref, str):
                    sub_event_id = sub_event_ref
                    sub_event_rows = df[df["data_id"] == sub_event_id]
                    if not sub_event_rows.empty:
                        # Enrich inherited_data of the subEvent row with properties from the current row
                        parent_json = df.at[idx, "json_data"] if isinstance(df.at[idx, "json_data"], dict) else {}
                        parent_inherited = df.at[idx, "inherited_data"] if isinstance(df.at[idx, "inherited_data"], dict) else {}
                        super_event_data = {**parent_inherited, **parent_json}

                        for sub_idx in sub_event_rows.index:
                            current_json = df.at[sub_idx, "json_data"] if isinstance(df.at[sub_idx, "json_data"], dict) else {}
                            # only inherit properties that don't exist in the subEvent's own json_data
                            to_inherit = {super_event_data_key: super_event_data[super_event_data_key] for super_event_data_key in super_event_data if super_event_data_key not in current_json}
                            df.at[sub_idx, "inherited_data"] = to_inherit


def denormalize_dataset(df: pd.DataFrame, df_bigquery: pd.DataFrame) -> None:
    """
    Denormalize dataset rows by inheriting properties from superEvent to subEvent where applicable and enriching location etc.
    Df is modified in place.
    Args:
        df: DataFrame containing the collected rows for a dataset.
        df_bigquery: DataFrame containing the rows from bigquery table.
    """
    handle_super_events(df, df_bigquery)
    handle_sub_events(df, df_bigquery)


def _initialize_feed_states(dataset_url: str, dataset_feeds: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Initialize per-feed state used for cursor handling and ingestion summaries.
    Args:
        dataset_url: URL pointing to the dataset to query.
        dataset_feeds: list of dictionaries containing feed information.
    Returns:
        Dictionary containing per-feed state for cursor handling and ingestion summaries.
    """
    return {
        dataset_feed["id"]: {
            "dataset_id": dataset_url,
            "feed_id": dataset_feed["id"],
            "kind": dataset_feed.get("type"),
            "previous_afterTimestamp": None,
            "previous_afterId": None,
            "next_afterTimestamp": None,
            "next_afterId": None,
            "status": None,
            "updated": 0,
            "deleted": 0,
        }
        for dataset_feed in dataset_feeds
    }


def _collect_dataset_feed_rows(
    dataset_url: str,
    dataset_feeds: list[dict[str, Any]],
    feed_states: dict[str, dict[str, Any]],
) -> tuple[list[dict], list[dict[str, Any]]]:
    """
    Traverse dataset feeds and collect update/delete rows while tracking feed cursor state.
    Args:
        dataset_url: URL pointing to the dataset feed.
        dataset_feeds: List of dataset feeds.
        feed_states: Dictionary of feed states.
    Returns:
        Updated and deleted rows.
    """
    dataset_updates: list[dict] = []
    dataset_deletes: list[dict[str, Any]] = []

    for dataset_feed in dataset_feeds:
        feed_id = dataset_feed["id"]
        after_timestamp, after_id = get_last_ingestion_info(feed_id)
        feed_states[feed_id]["previous_afterTimestamp"] = after_timestamp
        feed_states[feed_id]["previous_afterId"] = after_id

        result = access_feed_url(dataset_feed, after_timestamp, after_id)
        if result is None:
            raise RuntimeError(f"RPDE returned no result for feed {feed_id}")

        updates, deletes = _extract_rows(dataset_url, feed_id, result)
        dataset_updates.extend(updates)
        dataset_deletes.extend(deletes)
        logger.info("Collected %d items from feed %s", len(updates), feed_id)

        feed_states[feed_id]["updated"] = len(updates)
        feed_states[feed_id]["deleted"] = len(deletes)
        feed_states[feed_id]["next_afterTimestamp"] = result.get("after_timestamp")
        feed_states[feed_id]["next_afterId"] = result.get("after_id")
        feed_states[feed_id]["status"] = result.get("status")

    return dataset_updates, dataset_deletes


def _persist_dataset_results(
    dataset_url: str,
    dataset_updates: list[dict],
    dataset_deletes: list[dict[str, Any]],
    pending_deletes: dict[str, dict[str, Any]],
) -> None:
    """
    Persist collected dataset rows to BigQuery opportunities after denormalization.
    Args:
        dataset_url: URL pointing to the dataset feed.
        dataset_updates: List of dataset rows.
        dataset_deletes: List of dataset deletes.
        pending_deletes: List of pending deletes.
    """
    delete_dataset_opportunities(dataset_deletes, pending_deletes=pending_deletes)

    dataset_old_df = get_dataset_opportunities(dataset_url)
    dataset_new_df = pd.DataFrame(dataset_updates, columns=DF_COLUMNS)
    denormalize_dataset(dataset_new_df, dataset_old_df)
    # _write_dataset_csv(dataset_url, dataset_new_df)
    write_dataset_opportunities(dataset_url, dataset_new_df)


def _build_ingestion_records(
    dataset_url: str,
    dataset_feeds: list[dict[str, Any]],
    feed_states: dict[str, dict[str, Any]],
    dataset_failed: bool,
) -> list[dict[str, Any]]:
    """
    Build ingestion-summary rows based on success/failure cursor semantics. If any of the feeds failed, the entire
    dataset is marked as ERROR and the previous cursor is retained for all feeds to enable retry from last successful
    state. If successful, the next cursor is saved for all feeds.
    Args:
        dataset_url: URL pointing to the dataset feed.
        dataset_feeds: List of dataset feeds.
        feed_states: Dictionary of feed states.
        dataset_failed: Boolean indicating if the dataset processing failed.
    Returns:
        List of opportunity_ingestion record dicts to write to BigQuery.
    """
    records_to_write: list[dict[str, Any]] = []

    for dataset_feed in dataset_feeds:
        feed_id = dataset_feed["id"]
        state = feed_states.get(feed_id, {})

        if dataset_failed:
            # Keep the previous cursor so consecutive runs retry from the last successful state.
            record = {
                "dataset_id": dataset_url,
                "feed_id": feed_id,
                "kind": dataset_feed.get("type"),
                "ingestion_date": datetime.now(timezone.utc),
                "updated": 0,
                "deleted": 0,
                "afterTimestamp": state.get("previous_afterTimestamp"),
                "afterId": state.get("previous_afterId"),
                "status": "ERROR",
            }
        else:
            record = {
                "dataset_id": dataset_url,
                "feed_id": feed_id,
                "kind": dataset_feed.get("type"),
                "ingestion_date": datetime.now(timezone.utc),
                "updated": state.get("updated", 0),
                "deleted": state.get("deleted", 0),
                "afterTimestamp": state.get("next_afterTimestamp"),
                "afterId": state.get("next_afterId"),
                "status": state.get("status"),
            }

        records_to_write.append(record)

    return records_to_write


def ingest_opportunities(
    target_date: date | None = None,
    datasets: list[str] | None = None,
    verbose: bool = False,
) -> None:
    _configure_logging(verbose)
    pending_deletes: dict[str, dict[str, Any]] = {}

    feeds = get_feeds(target_date, datasets)
    logger.info("Loaded %d feeds for date=%s", len(feeds), target_date or date.today())

    count = 1
    for dataset_url in feeds:
        # Workaround to handle BQ streaming buffer
        retry_deferred_deletes(pending_deletes)

        dataset_feeds = feeds[dataset_url]
        logger.info(
            "[%d/%d] Processing dataset: %s",
            count,
            len(feeds),
            dataset_url,
        )
        dataset_feeds.sort(key=lambda feed: FEED_EXECUTION_ORDER.index(feed["type"]))

        dataset_failed = False
        feed_states = _initialize_feed_states(dataset_url, dataset_feeds)

        try:
            dataset_updates, dataset_deletes = _collect_dataset_feed_rows(dataset_url, dataset_feeds, feed_states)
            _persist_dataset_results(dataset_url, dataset_updates, dataset_deletes, pending_deletes)
        except Exception:
            dataset_failed = True
            logger.exception(
                "Dataset processing failed for %s; writing ERROR ingestion status and continuing",
                dataset_url,
            )
        finally:
            records_to_write = _build_ingestion_records(dataset_url, dataset_feeds, feed_states, dataset_failed)
            try:
                write_opportunity_ingestion_records(records_to_write)
            except Exception:
                logger.exception("Failed writing ingestion records for dataset %s", dataset_url)

        count += 1

    # Flush any remaining deferred deletes, waiting up to 90 minutes for BigQuery streaming buffer to clear if needed.
    drain_deferred_deletes_until_timeout(
        pending_deletes,
        max_total_wait_seconds=90 * 60,
    )


@click.command()
@click.option(
    "--target-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Optional feed date in yyyy-mm-dd. Defaults to today.",
)
@click.option(
    "--dataset",
    "datasets",
    multiple=True,
    help="Optional dataset filter. Repeat for multiple datasets.",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose logging (includes RPDE traversal logs).",
)
def cli(target_date: datetime | None, datasets: tuple[str, ...], verbose: bool) -> None:
    """Ingest opportunities from RPDE feeds."""
    parsed_target_date = target_date.date() if target_date else None
    parsed_datasets = list(datasets) if datasets else None

    parsed_target_date = datetime.strptime("2026-04-10", "%Y-%m-%d").date()
    # parsed_datasets = ["https://leisurefocus-openactive.legendonlineservices.co.uk/OpenActive"]
    parsed_datasets = ["https://data.bookwhen.com/",
                       "https://activehartlepool.gs-signature.cloud/OpenActive/",
                       "https://wymondhamtownunitedfc.bookteq.com/api/open-active",
                       "https://leisurefocus-openactive.legendonlineservices.co.uk/OpenActive"]
    # verbose = True

    ingest_opportunities(parsed_target_date, parsed_datasets, verbose)


if __name__ == "__main__":
    cli()
