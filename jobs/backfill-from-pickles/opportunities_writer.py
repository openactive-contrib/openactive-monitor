"""Backfill the BigQuery `opportunities` and `opportunity_ingestion` tables.

Performance & layout notes
--------------------------
* Pickles are grouped by ``dataset_url`` using the **feeds pickles** loaded in
  phase 1 — zero opportunities pickles are decoded just to discover their
  dataset.
* Dataset workers run in a ``ProcessPoolExecutor`` so CPU-heavy work
  parallelises past the GIL. Workers are named ``worker_1``, ``worker_2``, …
  via a shared counter passed to the pool initializer.
* The largest datasets are submitted first so the long tail starts running in
  parallel with everything else.
* Each dataset is processed in **two batches** — mirroring
  ``jobs/ingest-opportunities/main.py:_process_single_dataset``:

  1. ``FacilityUse`` / ``IndividualFacilityUse`` / ``Slot`` feeds first.
  2. Everything else (``HeadlineEvent``, ``Event``, ``OnDemandEvent``,
     ``SessionSeries``, ``ScheduledSession``, ``CourseInstance``, …).

  Each batch is fully extracted → denormalised → loaded to BigQuery before
  the next batch starts, which keeps peak memory bounded.
* Writes go through a direct ``WRITE_APPEND`` load job (see
  ``bq_backfill_writer``) — no MERGE.
"""

from __future__ import annotations

import gc
import logging
import multiprocessing
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd

# The backfill imports modules from the sibling ``jobs/ingest-opportunities/``
# project. ``main.py`` adds that directory to sys.path before importing this
# module, but ``ProcessPoolExecutor`` with the default ``spawn`` start method
# (used on macOS) re-imports this module from scratch in each worker — so the
# worker never ran ``main.py`` and ``sys.path`` is back to its default. We
# re-add the path here so ``import processing`` / ``from rpde import …`` work
# everywhere.
_INGEST_DIR = (Path(__file__).resolve().parent.parent / "ingest-opportunities").as_posix()
if _INGEST_DIR not in sys.path:
    sys.path.insert(0, _INGEST_DIR)

import processing  # noqa: E402  (sys.path mutation above)
from rpde import _extract_cursor_from_url  # noqa: E402

from bq_backfill_writer import write_dataset_opportunities_append  # noqa: E402
from pickle_reader import OpportunityPickle  # noqa: E402

logger = logging.getLogger(__name__)


# Mirrors jobs/ingest-opportunities/main.py
FIRST_BATCH_FEED_TYPES = {"FacilityUse", "IndividualFacilityUse", "Slot"}


# ---------------------------------------------------------------------------
# Grouping & partitioning (parent process; no pickle decode)
# ---------------------------------------------------------------------------

def _group_and_partition(
    pickles: list[OpportunityPickle],
    feed_info: dict[str, dict[str, str]],
) -> tuple[
    dict[str, tuple[list[OpportunityPickle], list[OpportunityPickle]]],
    list[OpportunityPickle],
]:
    """Group pickles by ``dataset_url`` and split each group into two batches.

    ``feed_info`` maps ``feed_id`` → ``{"dataset_url": …, "type": …}`` and is
    built from the feeds pickles in ``main.py``.

    For pickles whose ``feed_id`` is **not** in ``feed_info`` (e.g. feeds
    dropped from the catalog snapshot between the last ``get-feeds`` run and
    the last ``get-opportunities`` run), we fall back to decoding that one
    pickle to recover ``dataset_url`` / ``type`` from its embedded
    ``feed`` metadata. This is intentionally rare and pickles are released
    immediately afterwards so memory stays low.

    Returns
    -------
    (grouped, skipped)
        ``grouped`` is ``{dataset_url: (first_batch, second_batch)}``;
        ``skipped`` is a list of pickles that could neither be looked up nor
        decoded (truly unreadable / malformed).
    """
    grouped: dict[str, tuple[list[OpportunityPickle], list[OpportunityPickle]]] = {}
    skipped: list[OpportunityPickle] = []
    fallback_decoded = 0

    for pkl in pickles:
        info = feed_info.get(pkl.feed_id)
        dataset_url: str | None = info.get("dataset_url") if info else None
        feed_type: str = (info.get("type") if info else "") or ""

        if not dataset_url:
            # Fallback: decode this pickle to recover dataset_url + type from
            # the embedded feed metadata. We don't want to silently drop these
            # — they still represent real opportunities to backfill.
            try:
                payload = pkl.load()
            except Exception:
                logger.exception("Failed to decode %s for fallback grouping", pkl.path.name)
                skipped.append(pkl)
                continue

            feed_meta = payload.get("feed") if isinstance(payload, dict) else None
            if isinstance(feed_meta, dict):
                dataset_url = feed_meta.get("dataset_url") or None
                feed_type = (feed_meta.get("type") or "") if not feed_type else feed_type
            pkl.release()
            fallback_decoded += 1

            if not dataset_url:
                logger.warning(
                    "Cannot determine dataset_url for %s — skipping",
                    pkl.path.name,
                )
                skipped.append(pkl)
                continue

        first, second = grouped.setdefault(dataset_url, ([], []))
        if feed_type in FIRST_BATCH_FEED_TYPES:
            first.append(pkl)
        else:
            second.append(pkl)

    if fallback_decoded:
        logger.info(
            "Decoded %d pickles for fallback dataset_url/type lookup",
            fallback_decoded,
        )
    if skipped:
        logger.warning(
            "Could not group %d pickles (unreadable or no embedded dataset_url)",
            len(skipped),
        )
    return grouped, skipped


# ---------------------------------------------------------------------------
# Per-batch worker helper (runs in a ProcessPoolExecutor child)
# ---------------------------------------------------------------------------

def _process_batch(
    dataset_url: str,
    batch: list[OpportunityPickle],
) -> tuple[int, list[dict[str, Any]]]:
    """Extract → denormalise → load one batch of pickles for a dataset.

    Mirrors ``_collect_dataset_feed_rows`` + ``_persist_dataset_results`` from
    ``jobs/ingest-opportunities/main.py`` but adapted to read from pickles
    rather than RPDE.
    """
    all_updated_rows: list[dict[str, Any]] = []
    ingestion_records: list[dict[str, Any]] = []

    for pkl in batch:
        try:
            payload = pkl.load()
        except Exception:
            logger.exception("Failed to decode %s", pkl.path.name)
            continue

        feed_meta = payload.get("feed", {}) if isinstance(payload, dict) else {}
        feed_id = feed_meta.get("id") or pkl.feed_id

        items_dict = payload.get("items", {}) if isinstance(payload, dict) else {}
        items = list(items_dict.values()) if isinstance(items_dict, dict) else list(items_dict or [])
        rpde_result = {"items": items}
        updated, _deleted = processing.extract_rows(dataset_url, feed_id, rpde_result)
        all_updated_rows.extend(updated)

        next_url = payload.get("next_url", "") if isinstance(payload, dict) else ""
        aft_ts, aft_id, aft_change = _extract_cursor_from_url(next_url) if next_url else (None, None, None)

        ingestion_records.append({
            "dataset_id":        dataset_url,
            "feed_id":           feed_id,
            "kind":              feed_meta.get("type"),
            "ingestion_date":    pkl.time_finish.isoformat(),
            "afterTimestamp":    aft_ts,
            "afterId":           aft_id,
            "afterChangeNumber": aft_change,
            "updated":           len(updated),
            "deleted":           0,  # legacy pickle's items already represent post-delete state
            "status":            pkl.status,
        })
        pkl.release()

    if not all_updated_rows:
        return 0, ingestion_records

    df = pd.DataFrame(all_updated_rows, columns=processing.DF_COLUMNS)
    # Free the intermediate row dicts before denormalisation builds parallel
    # lookup structures — keeps peak memory down.
    all_updated_rows.clear()
    empty_bq = pd.DataFrame(columns=processing.DF_COLUMNS)
    processing.denormalize_dataset(df, empty_bq)

    rows_written = write_dataset_opportunities_append(dataset_url, df)
    del df
    gc.collect()
    return rows_written, ingestion_records


# ---------------------------------------------------------------------------
# Per-dataset worker entry point
# ---------------------------------------------------------------------------

def _process_one_dataset(
    dataset_url: str,
    first_batch: list[OpportunityPickle],
    second_batch: list[OpportunityPickle],
    index: int,
    total: int,
) -> tuple[int, list[dict[str, Any]]]:
    """Process one dataset: two batches, each fully persisted before the next."""
    logger.info("[%d/%d] Processing dataset %s", index, total, dataset_url)

    rows_written_total = 0
    ingestion_records: list[dict[str, Any]] = []

    for batch_label, batch in (
        ("FacilityUse/IndividualFacilityUse/Slot", first_batch),
        ("remaining", second_batch),
    ):
        if not batch:
            continue
        logger.info(
            "[%d/%d] %s — %s batch (%d feeds)",
            index, total, dataset_url, batch_label, len(batch),
        )
        rows, records = _process_batch(dataset_url, batch)
        rows_written_total += rows
        ingestion_records.extend(records)
        gc.collect()

    return rows_written_total, ingestion_records


# ---------------------------------------------------------------------------
# Worker process setup (spawn-safe)
# ---------------------------------------------------------------------------

def _worker_init(log_level: int, counter, counter_lock) -> None:
    """Configure each worker process: stable ``worker_N`` name + logging.

    ``counter`` is a ``multiprocessing.Value('i', 0)`` shared across workers,
    so each child gets a unique sequential index regardless of when it is
    spawned. The process is renamed so ``%(processName)s`` in the log format
    yields ``worker_1``, ``worker_2``, … instead of ``SpawnProcess-N``.
    """
    with counter_lock:
        counter.value += 1
        worker_id = counter.value
    multiprocessing.current_process().name = f"worker_{worker_id}"

    import logging as _logging
    _logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)-8s [%(processName)s] %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )
    _logging.getLogger("google").setLevel(_logging.WARNING)
    _logging.getLogger("urllib3").setLevel(_logging.WARNING)


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def write_opportunities(
    pickles: list[OpportunityPickle],
    max_workers: int,
    feed_info: dict[str, dict[str, str]],
    dataset_filter: set[str] | None = None,
) -> dict[str, Any]:
    """Top-level backfill driver. Returns a summary dict for logging."""
    grouped, _skipped = _group_and_partition(pickles, feed_info)
    if dataset_filter:
        grouped = {k: v for k, v in grouped.items() if k in dataset_filter}

    # Submit datasets in their natural (insertion) order — deliberately *not*
    # sorted by size. Loading all the giant datasets at once would spike peak
    # memory across workers; leaving the order alone interleaves big and small
    # datasets so total RAM usage stays bounded.
    ordered_datasets = list(grouped.items())

    total_datasets = len(ordered_datasets)
    total_feeds = sum(len(b1) + len(b2) for _, (b1, b2) in ordered_datasets)
    logger.info(
        "Processing %d datasets / %d feeds with %d worker processes",
        total_datasets, total_feeds, max_workers,
    )

    rows_written_total = 0
    all_ingestion_records: list[dict[str, Any]] = []
    failed_datasets: list[str] = []
    completed = 0

    log_level = logger.getEffectiveLevel()
    worker_counter = multiprocessing.Value("i", 0)
    worker_counter_lock = multiprocessing.Lock()

    with ProcessPoolExecutor(
        max_workers=max_workers,
        initializer=_worker_init,
        initargs=(log_level, worker_counter, worker_counter_lock),
    ) as ex:
        futures = {
            ex.submit(
                _process_one_dataset,
                dataset_url,
                first_batch,
                second_batch,
                idx,
                total_datasets,
            ): dataset_url
            for idx, (dataset_url, (first_batch, second_batch)) in enumerate(ordered_datasets, start=1)
        }
        for fut in as_completed(futures):
            dataset_url = futures[fut]
            completed += 1
            try:
                rows_written, records = fut.result()
            except Exception:
                logger.exception(
                    "[%d/%d] Dataset %s FAILED", completed, total_datasets, dataset_url,
                )
                failed_datasets.append(dataset_url)
                continue
            rows_written_total += rows_written
            all_ingestion_records.extend(records)
            logger.info(
                "[%d/%d] Dataset %s — wrote %d rows (cumulative: %d)",
                completed, total_datasets, dataset_url, rows_written, rows_written_total,
            )

    # opportunity_ingestion is small — write it from the parent process.
    if all_ingestion_records:
        import bigquery_ops  # lazy import; not needed in worker processes
        bigquery_ops.write_opportunity_ingestion_records(all_ingestion_records)
        logger.info("Wrote %d opportunity_ingestion rows", len(all_ingestion_records))

    return {
        "datasets_processed": total_datasets - len(failed_datasets),
        "datasets_failed":    len(failed_datasets),
        "feeds_processed":    total_feeds,
        "rows_written":       rows_written_total,
        "ingestion_records":  len(all_ingestion_records),
        "failed_datasets":    failed_datasets,
    }
