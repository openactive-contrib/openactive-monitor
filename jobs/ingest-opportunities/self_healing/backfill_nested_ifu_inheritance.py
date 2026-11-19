"""
Self-healing backfill: repair Slots that should inherit from a *nested*
IndividualFacilityUse.

Background
----------
A ``Slot``'s ``facilityUse`` reference is stored in ``has_superEvent``.  For some
publishers (observed on ``better-admin.org.uk``) that reference points at an
``IndividualFacilityUse`` ``@id`` such as::

    .../facility-uses/activity_recurrence_group:2968/individual-facility-uses/3372...

There is no opportunities row whose ``data_id`` equals that IFU ``@id`` — the IFU
exists only *nested* inside its parent FacilityUse's
``json_data.individualFacilityUse`` list.  The production denormalization used to
resolve parents only by ``data_id``, so these Slots inherited nothing and were
left with an empty ``location`` (and empty activity / facility / organisation /
boundary columns).  ~500k Slots are affected.

The production fix (``processing._build_super_event_payload_by_data_id`` expanding
nested IFUs, plus ``bigquery_ops.get_dataset_facility_uses``) heals new/updated
rows going forward.  This backfill repairs the rows already in BigQuery.

Target rows
-----------
- ``kind = 'Slot'``
- ``location`` is the empty JSON object (inheritance never ran)
- ``has_superEvent`` is a string that looks like a nested IFU reference

The script fills only-when-empty and writes back via a *targeted* MERGE that
touches only the inheritable columns (never ``json_data`` or the whole record),
so it is idempotent and safe to re-run as part of self-healing.

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python self_healing/backfill_nested_ifu_inheritance.py [--dry-run] \
        [--max-workers 8] [--dataset <url>] [--limit 0]
"""

from __future__ import annotations

import gc
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter

import click
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Make the ingest-opportunities package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigquery_ops import (  # noqa: E402
    OPPORTUNITIES_COLUMNS,
    get_dataset_facility_uses,
    get_dataset_opportunities,
    parse_opportunities_json_columns,
)
from processing import (  # noqa: E402
    _build_super_event_payload_by_data_id,
    handle_super_events,
)
from self_healing._common import (  # noqa: E402
    INHERITABLE_FIELDS,
    discover_affected_datasets,
    empty_mask as _empty_mask,
    strip_ref as _strip_ref,
    values_equal as _values_equal,
    write_inherited_updates,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backfill_nested_ifu_inheritance")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

_AFFECTED_PREDICATE = (
    "kind = 'Slot' "
    "AND TO_JSON_STRING(location) = '{}' "
    "AND has_superEvent IS NOT NULL "
)


def _load_affected_rows(dataset_url: str) -> pd.DataFrame:
    """Load every affected Slot for a single dataset, with all opportunities columns."""
    client = bigquery.Client(project=GCP_PROJECT_ID)
    selected = ", ".join(OPPORTUNITIES_COLUMNS)
    query = f"""
        SELECT {selected}
        FROM `{TABLE_ID}`
        WHERE dataset_url = @dataset_url
          AND {_AFFECTED_PREDICATE}
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url),
        ]
    )
    return client.query(query, job_config=job_config).to_dataframe()


def _fix_dataset(
    dataset_url: str,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int, int]:
    """Repair affected Slots for one dataset_url.

    Returns (examined, merged, location_filled):
      - examined: affected Slots loaded
      - merged: rows that actually received inherited data (written back)
      - location_filled: subset of merged where location went from {} to non-{}
    """
    start = perf_counter()
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)
    affected_df = _load_affected_rows(dataset_url)
    examined = len(affected_df)
    logger.info("[%d/%d] loaded %d affected rows for %s", index, total, examined, dataset_url)
    if examined == 0:
        return 0, 0, 0

    affected_df = affected_df.reset_index(drop=True)
    parse_opportunities_json_columns(affected_df)

    # Resolve parents from two sources:
    #   1. FacilityUse rows whose nested individualFacilityUse[] holds the ref
    #      (the primary nested-IFU scenario), and
    #   2. any real rows matching the ref by data_id (covers datasets that also
    #      publish IFUs as first-class rows).
    parent_ids = {p for p in (_strip_ref(r) for r in affected_df["has_superEvent"]) if p}
    parent_frames: list[pd.DataFrame] = []
    if parent_ids:
        real_parents = get_dataset_opportunities(dataset_url, required_data_ids=sorted(parent_ids))
        if not real_parents.empty:
            parent_frames.append(real_parents)
    facility_uses = get_dataset_facility_uses(dataset_url)
    if not facility_uses.empty:
        parent_frames.append(facility_uses)

    if not parent_frames:
        logger.info(
            "[%d/%d] DONE %s — examined=%d, no parents found (in %.2fs)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        del affected_df
        gc.collect()
        return examined, 0, 0

    parent_df = (
        parent_frames[0]
        if len(parent_frames) == 1
        else pd.concat(parent_frames, ignore_index=True)
    )
    payload_by_data_id = _build_super_event_payload_by_data_id(affected_df, parent_df)

    # Snapshot each inheritable field BEFORE the merge so we can detect which
    # rows actually received new data and defensively restore any populated
    # value that handle_super_events might touch (it fills only-when-empty).
    before_empty: dict[str, pd.Series] = {
        field: _empty_mask(affected_df[field]) for field in INHERITABLE_FIELDS
    }
    before_values: dict[str, pd.Series] = {
        field: affected_df[field].copy() for field in INHERITABLE_FIELDS
    }

    handle_super_events(affected_df, payload_by_data_id)

    merged_mask = pd.Series(False, index=affected_df.index)
    location_filled_mask = pd.Series(False, index=affected_df.index)
    for field in INHERITABLE_FIELDS:
        after_empty = _empty_mask(affected_df[field])
        field_filled = before_empty[field] & ~after_empty
        merged_mask = merged_mask | field_filled
        if field == "location":
            location_filled_mask = field_filled

        previously_populated = ~before_empty[field]
        if previously_populated.any():
            mismatch = previously_populated & affected_df[field].combine(
                before_values[field],
                lambda a, b: not _values_equal(a, b),
            )
            mismatch_count = int(mismatch.sum())
            if mismatch_count:
                logger.warning(
                    "[%d/%d] %s — %d rows had non-empty %s altered by handle_super_events; restoring",
                    index, total, dataset_url, mismatch_count, field,
                )
                affected_df.loc[mismatch, field] = before_values[field][mismatch]

    merged = int(merged_mask.sum())
    if merged == 0:
        logger.info(
            "[%d/%d] DONE %s — examined=%d, no parents had usable inheritable data (in %.2fs)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        del affected_df, parent_df, payload_by_data_id, before_empty, before_values
        gc.collect()
        return examined, 0, 0

    location_filled = int(location_filled_mask.sum())
    keep_columns = ["dataset_url", "feed_id", "id", *INHERITABLE_FIELDS]
    updates_df = affected_df.loc[merged_mask, keep_columns].copy()
    del affected_df, parent_df, payload_by_data_id, before_empty, before_values
    gc.collect()

    if not dry_run:
        logger.info("[%d/%d] writing %d rows for %s", index, total, len(updates_df), dataset_url)
        client = bigquery.Client(project=GCP_PROJECT_ID)
        write_inherited_updates(client, TABLE_ID, dataset_url, updates_df, label="nested_ifu")

    logger.info(
        "[%d/%d] DONE %s — examined=%d merged=%d location_filled=%d in %.2fs (dry_run=%s)",
        index, total, dataset_url, examined, merged, location_filled,
        perf_counter() - start, dry_run,
    )
    del updates_df
    gc.collect()
    return examined, merged, location_filled


def run(
    dry_run: bool = False,
    max_workers: int | None = None,
    datasets: list[str] | None = None,
    limit: int = 0,
) -> None:
    """Programmatic entry point.  Called by the self-heal step of the ingest job."""
    if max_workers is None:
        max_workers = int(os.getenv("INGEST_MAX_WORKERS", "8"))

    overall_start = perf_counter()
    client = bigquery.Client(project=GCP_PROJECT_ID)

    if datasets:
        dataset_urls = list(datasets)
        logger.info("Restricting to %d explicit dataset_url(s)", len(dataset_urls))
    else:
        affected = discover_affected_datasets(client, TABLE_ID, _AFFECTED_PREDICATE)
        total = sum(c for _, c in affected)
        logger.info("Discovery: %d datasets, %d total affected rows", len(affected), total)
        if limit and limit > 0:
            affected = affected[:limit]
            logger.info("Limiting to top %d datasets by affected-row count", limit)
        dataset_urls = [url for url, _ in affected]

    if not dataset_urls:
        logger.info("Nothing to fix.")
        return

    total_examined = 0
    total_merged = 0
    total_location_filled = 0
    total_datasets = len(dataset_urls)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="nested-ifu") as executor:
        futures = {
            executor.submit(_fix_dataset, ds, dry_run, idx, total_datasets): ds
            for idx, ds in enumerate(dataset_urls, start=1)
        }
        completed = 0
        for future in as_completed(futures):
            ds = futures[future]
            try:
                examined, merged, location_filled = future.result()
                total_examined += examined
                total_merged += merged
                total_location_filled += location_filled
            except Exception:
                logger.exception("Failed for dataset %s", ds)
            completed += 1
            logger.info(
                "Progress %d/%d datasets complete — running totals examined=%d merged=%d location_filled=%d",
                completed, total_datasets, total_examined, total_merged, total_location_filled,
            )

    logger.info(
        "DONE in %.2fs — datasets=%d examined=%d merged=%d location_filled=%d (dry_run=%s)",
        perf_counter() - overall_start,
        len(dataset_urls),
        total_examined,
        total_merged,
        total_location_filled,
        dry_run,
    )


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Compute the fixes but do not write them back to BigQuery.",
)
@click.option(
    "--max-workers",
    type=int,
    default=int(os.getenv("INGEST_MAX_WORKERS", "8")),
    show_default=True,
    help="Thread-pool size for parallel dataset processing.",
)
@click.option(
    "--dataset",
    "datasets",
    multiple=True,
    help="Restrict to specific dataset_url(s); repeat for multiple. Skips discovery.",
)
@click.option(
    "--limit",
    type=int,
    default=0,
    show_default=True,
    help="Process at most this many datasets (largest-first). 0 = no limit.",
)
def main(dry_run: bool, max_workers: int, datasets: tuple[str, ...], limit: int) -> None:
    """Backfill Slots that should inherit from a nested IndividualFacilityUse."""
    run(dry_run=dry_run, max_workers=max_workers, datasets=list(datasets) if datasets else None, limit=limit)


if __name__ == "__main__":
    main()
