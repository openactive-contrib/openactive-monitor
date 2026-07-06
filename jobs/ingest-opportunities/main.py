import gc
import logging
import os
import threading
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import click
import pandas as pd
from dotenv import load_dotenv

from bigquery_ops import (
    delete_dataset_opportunities,
    drain_deferred_deletes_until_timeout,
    get_dataset_facility_uses,
    get_dataset_opportunities,
    get_feeds,
    get_last_ingestion_info_batch,
    retry_deferred_deletes,
    write_dataset_opportunities,
    write_opportunity_ingestion_records,
)
from processing import DF_COLUMNS, denormalize_dataset, extract_rows
from rpde import access_feed_url
from self_healing import (
    backfill_location_boundaries,
    backfill_nested_ifu_inheritance,
    backfill_nhs_trust,
    backfill_super_event_inheritance,
)

load_dotenv()

INGEST_MAX_WORKERS = int(os.getenv("INGEST_MAX_WORKERS", "8"))

# For Debugging True
# TODO
PERSIST_CSV=False
CSV_OUTPUT_DIR = os.getenv("OPPORTUNITY_CSV_OUTPUT_DIR", "./opportunities/csv")

FEED_EXECUTION_ORDER = ["HeadlineEvent", "Event", "OnDemandEvent", "FacilityUse", "IndividualFacilityUse", "Slot", "SessionSeries", "ScheduledSession", "CourseInstance", ""]
FIRST_BATCH_FEED_TYPES = {"FacilityUse", "IndividualFacilityUse", "Slot"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  [%(threadName)s] [dataset=%(dataset_context)s]  %(message)s",
)
logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    """Configure app logging and set component loggers to DEBUG in verbose mode."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.getLogger().setLevel(level)
    logging.getLogger("rpde").setLevel(level)
    logging.getLogger("bigquery_ops").setLevel(level)
    logging.getLogger("geolocation").setLevel(level)
    logging.getLogger("request_client").setLevel(level)


_LOG_CONTEXT = threading.local()


def _set_log_dataset_context(dataset_url: str) -> None:
    _LOG_CONTEXT.dataset_context = dataset_url


def _clear_log_dataset_context() -> None:
    if hasattr(_LOG_CONTEXT, "dataset_context"):
        delattr(_LOG_CONTEXT, "dataset_context")


# Ensure every log record always has dataset_context to satisfy formatter fields.
_previous_factory = logging.getLogRecordFactory()


def _record_factory(*args, **kwargs):
    record = _previous_factory(*args, **kwargs)
    record.dataset_context = getattr(_LOG_CONTEXT, "dataset_context", "-")
    return record


logging.setLogRecordFactory(_record_factory)


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
            "previous_afterChangeNumber": None,
            "next_afterTimestamp": None,
            "next_afterId": None,
            "next_afterChangeNumber": None,
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
    feed_ids = [dataset_feed["id"] for dataset_feed in dataset_feeds]
    latest_cursor_by_feed_id = get_last_ingestion_info_batch(feed_ids)

    for dataset_feed in dataset_feeds:
        feed_id = dataset_feed["id"]
        after_timestamp, after_id, after_change_number = latest_cursor_by_feed_id.get(feed_id, (None, None, None))
        feed_states[feed_id]["previous_afterTimestamp"] = after_timestamp
        feed_states[feed_id]["previous_afterId"] = after_id
        feed_states[feed_id]["previous_afterChangeNumber"] = after_change_number

        result = access_feed_url(dataset_feed, after_timestamp, after_id, after_change_number, PERSIST_CSV)
        if result is None:
            raise RuntimeError(f"RPDE returned no result for feed {feed_id}")

        publisher_name = dataset_feed.get("publisher_name")
        updates, deletes = extract_rows(dataset_url, feed_id, result, publisher_name=publisher_name)
        dataset_updates.extend(updates)
        dataset_deletes.extend(deletes)
        logger.info("Collected %d items from feed %s", len(updates), feed_id)

        feed_states[feed_id]["updated"] = len(updates)
        feed_states[feed_id]["deleted"] = len(deletes)
        feed_states[feed_id]["next_afterTimestamp"] = result.get("after_timestamp")
        feed_states[feed_id]["next_afterId"] = result.get("after_id")
        feed_states[feed_id]["next_afterChangeNumber"] = result.get("after_change_number")
        feed_states[feed_id]["status"] = result.get("status")

    return dataset_updates, dataset_deletes


def _partition_dataset_feeds(
    dataset_feeds: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split dataset feeds into two batches to reduce peak memory usage."""
    first_batch: list[dict[str, Any]] = []
    second_batch: list[dict[str, Any]] = []

    for dataset_feed in dataset_feeds:
        if dataset_feed.get("type") in FIRST_BATCH_FEED_TYPES:
            first_batch.append(dataset_feed)
        else:
            second_batch.append(dataset_feed)

    return first_batch, second_batch


def _persist_dataset_results(
    dataset_url: str,
    dataset_updates: list[dict],
    dataset_deletes: list[dict[str, Any]],
    pending_deletes: dict[str, dict[str, Any]],
    pending_deletes_lock: threading.Lock,
) -> None:
    """
    Persist collected dataset rows to BigQuery opportunities after denormalization.
    Args:
        dataset_url: URL pointing to the dataset feed.
        dataset_updates: List of dataset rows.
        dataset_deletes: List of dataset deletes.
        pending_deletes: List of pending deletes.
    """
    total_start = perf_counter()
    logger.info(
        "Persist start for dataset %s: updates=%d deletes=%d",
        dataset_url,
        len(dataset_updates),
        len(dataset_deletes),
    )

    attempted_delete_keys = {
        f"{row.get('dataset_url')}|{row.get('feed_id')}|{row.get('id')}"
        for row in dataset_deletes
        if row.get("dataset_url") and row.get("feed_id") and row.get("id")
    }

    # Keep lock scope small: snapshot relevant pending state, run slow BQ delete work unlocked,
    # then merge only this batch's key updates back into the shared pending map.
    with pending_deletes_lock:
        local_pending_deletes = {
            key: dict(value)
            for key, value in pending_deletes.items()
            if key in attempted_delete_keys
        }

    phase_start = perf_counter()
    delete_dataset_opportunities(dataset_deletes, pending_deletes=local_pending_deletes)

    with pending_deletes_lock:
        for key in attempted_delete_keys:
            if key in local_pending_deletes:
                pending_deletes[key] = local_pending_deletes[key]
            else:
                pending_deletes.pop(key, None)

    logger.info("Persist phase delete_dataset_opportunities completed in %.2fs", perf_counter() - phase_start)
    del dataset_deletes
    gc.collect()

    phase_start = perf_counter()
    dataset_new_df = pd.DataFrame(dataset_updates, columns=DF_COLUMNS)
    logger.info("Persist phase build_dataset_new_df completed in %.2fs (rows=%d)", perf_counter() - phase_start, len(dataset_new_df))
    del dataset_updates
    gc.collect()

    phase_start = perf_counter()
    denormalization_reference_ids = _extract_denormalization_reference_ids(dataset_new_df)
    logger.info(
        "Persist phase extract_denormalization_reference_ids completed in %.2fs (reference_ids=%d)",
        perf_counter() - phase_start,
        len(denormalization_reference_ids),
    )

    phase_start = perf_counter()
    dataset_referred_df = get_dataset_opportunities(dataset_url, required_data_ids=denormalization_reference_ids)
    logger.info("Persist phase get_dataset_opportunities completed in %.2fs (rows=%d)", perf_counter() - phase_start, len(dataset_referred_df))

    # A Slot's ``facilityUse`` reference may point at an IndividualFacilityUse
    # embedded inside its parent FacilityUse (``json_data.individualFacilityUse``)
    # rather than existing as its own row.  Such refs don't resolve via the
    # data_id-keyed fetch above, so when unresolved Slot refs remain we also load
    # the dataset's FacilityUse rows and let denormalize_dataset expand their
    # nested IFUs.  Gated on unresolved Slot refs so it is a no-op for datasets
    # without the nested-IFU pattern.
    facility_use_df = _fetch_facility_uses_for_unresolved_slots(
        dataset_url, dataset_new_df, dataset_referred_df
    )
    if facility_use_df is not None and not facility_use_df.empty:
        dataset_referred_df = pd.concat(
            [dataset_referred_df, facility_use_df], ignore_index=True
        )
        logger.info(
            "Persist phase fetched %d FacilityUse rows for nested-IFU inheritance",
            len(facility_use_df),
        )
    del facility_use_df

    phase_start = perf_counter()
    denormalize_dataset(dataset_new_df, dataset_referred_df)
    logger.info("Persist phase denormalize_dataset completed in %.2fs", perf_counter() - phase_start)

    del dataset_referred_df
    gc.collect()

    if PERSIST_CSV:
        phase_start = perf_counter()
        _write_dataset_csv(dataset_url, dataset_new_df)
        logger.info("Persist phase write_dataset_csv completed in %.2fs", perf_counter() - phase_start)

    logger.info("Persist complete for dataset %s in %.2fs", dataset_url, perf_counter() - total_start)
    write_dataset_opportunities(dataset_url, dataset_new_df)


def _extract_denormalization_reference_ids(dataset_new_df: pd.DataFrame) -> list[str]:
    """Collect unique super/sub references not already present in this batch's data_id values."""
    if dataset_new_df.empty:
        return []

    reference_ids: list[str] = []
    seen: set[str] = set()
    existing_data_ids: set[str] = set()
    for data_id in dataset_new_df["data_id"].tolist():
        if isinstance(data_id, str) and data_id:
            existing_data_ids.add(data_id)

    def add_reference(value: Any) -> None:
        if isinstance(value, str):
            value = value.replace("\"", "").strip()
            if value and value not in existing_data_ids and value not in seen:
                seen.add(value)
                reference_ids.append(value)
            return

        if isinstance(value, list):
            for item in value:
                if (
                    isinstance(item, str)
                    and item
                    and item not in existing_data_ids
                    and item not in seen
                ):
                    item = item.replace("\"", "").strip()
                    seen.add(item)
                    reference_ids.append(item)

    for super_event_ref, sub_event_ref in dataset_new_df[["has_superEvent", "has_subEvent"]].itertuples(index=False, name=None):
        add_reference(super_event_ref)
        add_reference(sub_event_ref)

    return reference_ids


def _fetch_facility_uses_for_unresolved_slots(
    dataset_url: str,
    dataset_new_df: pd.DataFrame,
    dataset_referred_df: pd.DataFrame,
) -> pd.DataFrame | None:
    """Load the dataset's FacilityUse rows iff some Slot's superEvent ref is unresolved.

    A Slot's ``facilityUse`` reference is stored in ``has_superEvent``.  When it
    points at an IndividualFacilityUse nested inside a FacilityUse (rather than a
    standalone row), the ref won't match any ``data_id`` already in the new batch
    or the targeted fetch.  In that case we return the dataset's FacilityUse rows
    so ``denormalize_dataset`` can expand their nested IFUs; otherwise ``None``.
    """
    if dataset_new_df.empty or "kind" not in dataset_new_df.columns:
        return None

    slot_refs = dataset_new_df.loc[dataset_new_df["kind"] == "Slot", "has_superEvent"]
    if slot_refs.empty:
        return None

    resolved_data_ids: set[str] = set()
    for frame in (dataset_new_df, dataset_referred_df):
        if not frame.empty and "data_id" in frame.columns:
            resolved_data_ids.update(
                d for d in frame["data_id"].tolist() if isinstance(d, str) and d
            )

    for ref in slot_refs.tolist():
        if not isinstance(ref, str):
            continue  # inline dicts resolve on their own; only string refs need a lookup
        cleaned = ref.replace('"', "").strip()
        if cleaned and cleaned not in resolved_data_ids:
            return get_dataset_facility_uses(dataset_url)

    return None


def _build_ingestion_records(
    dataset_url: str,
    dataset_feeds: list[dict[str, Any]],
    feed_states: dict[str, dict[str, Any]],
    persisted_feed_ids: set[str],
    failed_feed_ids: set[str],
) -> list[dict[str, Any]]:
    """
    Build ingestion-summary rows based on per-feed batch outcomes.
    Feeds whose batch was persisted keep next cursors and counters; all others retain previous cursors with ERROR.
    Args:
        dataset_url: URL pointing to the dataset feed.
        dataset_feeds: List of dataset feeds.
        feed_states: Dictionary of feed states.
        persisted_feed_ids: Feed IDs for batches that were fully persisted.
        failed_feed_ids: Feed IDs for the batch that failed (safe fallback marks those as ERROR).
    Returns:
        List of opportunity_ingestion record dicts to write to BigQuery.
    """
    records_to_write: list[dict[str, Any]] = []

    for dataset_feed in dataset_feeds:
        feed_id = dataset_feed["id"]
        state = feed_states.get(feed_id, {})

        if feed_id in persisted_feed_ids and feed_id not in failed_feed_ids:
            record = {
                "dataset_id": dataset_url,
                "feed_id": feed_id,
                "kind": dataset_feed.get("type"),
                "ingestion_date": datetime.now(timezone.utc),
                "updated": state.get("updated", 0),
                "deleted": state.get("deleted", 0),
                "afterTimestamp": state.get("next_afterTimestamp"),
                "afterId": state.get("next_afterId"),
                "afterChangeNumber": state.get("next_afterChangeNumber"),
                "status": state.get("status"),
            }
        else:
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
                "afterChangeNumber": state.get("previous_afterChangeNumber"),
                "status": "ERROR",
            }

        records_to_write.append(record)

    return records_to_write

def _process_single_dataset(
    dataset_url: str,
    dataset_feeds: list[dict[str, Any]],
    pending_deletes: dict[str, dict[str, Any]],
    pending_deletes_lock: threading.Lock,
    index: int,
    total: int,
) -> None:
    """Process one dataset: fetch feeds, persist results, write ingestion records."""
    _set_log_dataset_context(dataset_url)
    try:
        # Workaround to handle BQ streaming buffer
        with pending_deletes_lock:
            retry_deferred_deletes(pending_deletes)

        logger.info("[%d/%d] Processing dataset: %s", index, total, dataset_url)
        dataset_feeds.sort(key=lambda feed: FEED_EXECUTION_ORDER.index(feed["type"]))

        persisted_feed_ids: set[str] = set()
        failed_feed_ids: set[str] = set()
        current_batch_feed_ids: set[str] = set()
        feed_states = _initialize_feed_states(dataset_url, dataset_feeds)

        try:
            first_batch_feeds, second_batch_feeds = _partition_dataset_feeds(dataset_feeds)
            feed_batches = [
                ("FacilityUse/IndividualFacilityUse/Slot", first_batch_feeds),
                ("remaining", second_batch_feeds),
            ]

            for batch_label, batch_feeds in feed_batches:
                if not batch_feeds:
                    continue
                current_batch_feed_ids = {feed["id"] for feed in batch_feeds}
                logger.info(
                    "Processing %s feed batch for dataset %s (%d feeds)",
                    batch_label,
                    dataset_url,
                    len(batch_feeds),
                )
                dataset_updates, dataset_deletes = _collect_dataset_feed_rows(dataset_url, batch_feeds, feed_states)
                _persist_dataset_results(
                    dataset_url,
                    dataset_updates,
                    dataset_deletes,
                    pending_deletes,
                    pending_deletes_lock,
                )
                persisted_feed_ids.update(current_batch_feed_ids)
                current_batch_feed_ids = set()
                gc.collect()
        except Exception:
            failed_feed_ids.update(current_batch_feed_ids)
            logger.exception(
                "Dataset processing failed for %s; writing ERROR ingestion status and continuing",
                dataset_url,
            )
        finally:
            records_to_write = _build_ingestion_records(
                dataset_url,
                dataset_feeds,
                feed_states,
                persisted_feed_ids,
                failed_feed_ids,
            )
            try:
                write_opportunity_ingestion_records(records_to_write)
            except Exception:
                logger.exception("Failed writing ingestion records for dataset %s", dataset_url)
    finally:
        _clear_log_dataset_context()

def _order_datasets_by_provider(feeds: dict[str, list[dict]]) -> list[str]:
    """Order dataset URLs round-robin across infrastructure providers.

    Datasets published on the same provider share the same server, so running
    many of them concurrently raises the chance of provider-side 403 / rate-limit
    responses. Interleaving the submission order so consecutive datasets rotate
    through different providers spreads the in-flight load across servers instead
    of clustering workers on one provider.
    """
    buckets: dict[str, deque[str]] = defaultdict(deque)
    for dataset_url, dataset_feeds in feeds.items():
        provider = ""
        for feed in dataset_feeds:
            provider = feed.get("provider") or ""
            if provider:
                break
        buckets[provider].append(dataset_url)

    ordered: list[str] = []
    queues = list(buckets.values())
    while queues:
        for queue in queues:
            if queue:
                ordered.append(queue.popleft())
        queues = [queue for queue in queues if queue]
    return ordered


def ingest_opportunities(
    datasets: list[str] | None = None,
    verbose: bool = False,
) -> None:
    _configure_logging(verbose)
    pending_deletes: dict[str, dict[str, Any]] = {}
    pending_deletes_lock = threading.Lock()

    feeds = get_feeds(datasets)
    logger.info("Loaded %d datasets", len(feeds))
    total = len(feeds)

    # order datasets so not overload to single provider at once
    ordered_datasets = _order_datasets_by_provider(feeds)

    with ThreadPoolExecutor(max_workers=INGEST_MAX_WORKERS, thread_name_prefix="ingest-worker") as executor:
        futures = {
            executor.submit(
                _process_single_dataset,
                dataset_url,
                feeds[dataset_url],
                pending_deletes,
                pending_deletes_lock,
                idx,
                total,
            ): dataset_url
            for idx, dataset_url in enumerate(ordered_datasets, start=1)
        }

        for future in as_completed(futures):
            dataset_url = futures[future]
            try:
                future.result()
            except Exception:
                logger.exception("Unhandled error processing dataset %s", dataset_url)

    # Flush any remaining deferred deletes, waiting up to 120 minutes for BigQuery streaming buffer to clear if needed.
    drain_deferred_deletes_until_timeout(
        pending_deletes,
        max_total_wait_seconds=120 * 60,
    )

    # Self-heal: repair data issues left by previous ingestion runs.
    run_self_heal()


def run_self_heal() -> None:
    """
    Run self-healing routines to fix data issues from prior ingestion runs.
    Data can be updated out of order (Slot exists in the db but FacilityUse
    updated afterward etc.), so run these backfills to identify and solve common issues.
    """
    logger.info("Starting self-heal step")
    start = perf_counter()

    backfill_super_event_inheritance()
    backfill_nested_ifu_inheritance()
    backfill_location_boundaries()
    backfill_nhs_trust()

    logger.info("Self-heal step completed in %.2fs", perf_counter() - start)


@click.command()
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
def cli(datasets: tuple[str, ...], verbose: bool) -> None:
    """Ingest opportunities from RPDE feeds."""
    parsed_datasets = list(datasets) if datasets else None

    # parsed_datasets = ["https://leisurecentre-openactive.legendonlineservices.co.uk/OpenActive"]
    # parsed_datasets = ["https://data.bookwhen.com/",
    #                    "https://activehartlepool.gs-signature.cloud/OpenActive/",
    #                    "https://wymondhamtownunitedfc.bookteq.com/api/open-active",
    #                    "https://leisurefocus-openactive.legendonlineservices.co.uk/OpenActive"]
    # verbose = True

    ingest_opportunities(parsed_datasets, verbose)


if __name__ == "__main__":
    cli()
