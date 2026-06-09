"""One-time backfill: recover rows the has_superEvent quote bug left empty.

Background
----------
For a period before commit 3140d28, ``has_superEvent`` values were stored in
BigQuery with literal surrounding double-quotes (e.g. ``"https://..."``). The
ingestion lookup in ``_extract_denormalization_reference_ids`` and
``get_dataset_opportunities`` then failed to find the matching parent (parents'
``data_id`` values have no quotes), so super-event inheritance was skipped and
the affected rows ended up with ``location = {}`` (and missing activity /
facility / dates / ageRange / level).

The forward code paths now strip quotes on both write and read sides. This
script repairs the rows that were already persisted with the bug.

Target rows (per user spec)
---------------------------
- ``startDate > 2026-03-01``
- ``has_superEvent IS NOT NULL``
- ``location`` is the empty JSON object (``{}``)

For each target row this script looks up the parent by ``data_id`` (after
stripping quotes from ``has_superEvent``) and reuses
``processing.handle_super_events`` to apply ``apply_inherited_data`` — the
exact same merge logic the live pipeline runs. Only rows whose
``inherited_data`` actually grew as a result of the merge are written back.

Efficiency notes
----------------
- Discovery is a single ``GROUP BY dataset_url`` query — datasets are then
  processed by a thread pool (one dataset per worker) so the slow MERGE/load
  steps overlap across datasets.
- The largest datasets are scheduled first so a long-running outlier doesn't
  hold up the tail of the pool.
- Inside each dataset we only fetch parents for the ``has_superEvent`` IDs that
  actually appear, and ``get_dataset_opportunities`` already batches its
  ``data_id`` UNNEST at 2000 IDs per query.
- Only rows that were actually filled are sent through
  ``write_dataset_opportunities`` (staging table + MERGE), so MERGE work is
  proportional to fixes, not to rows examined.

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python migrations/backfill_super_event_location.py [--dry-run] \
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
from typing import Any

import click
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Make the ingest-opportunities package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigquery_ops import (  # noqa: E402
    OPPORTUNITIES_COLUMNS,
    get_dataset_opportunities,
    parse_opportunities_json_columns,
    write_dataset_opportunities,
)
from processing import (  # noqa: E402
    _build_super_event_payload_by_data_id,
    handle_super_events,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backfill_super_event_location")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

CUTOFF_DATE = "2026-03-01"

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

_AFFECTED_PREDICATE = (
    "startDate > TIMESTAMP(@cutoff) "
    "AND has_superEvent IS NOT NULL "
    "AND TO_JSON_STRING(location) = '{}'"
)


# Columns that ``apply_inherited_data`` may fill from a parent. We snapshot
# each of these BEFORE running ``handle_super_events`` and compare AFTER to
# detect which rows actually received new data — ``inherited_data`` is
# intentionally never written back to opportunities (it would explode the
# table size with redundant data), so we cannot use it as a change signal.
INHERITABLE_FIELDS: tuple[str, ...] = (
    "activity",
    "facility",
    "location",
    "startDate",
    "endDate",
    "ageRange",
    "level",
    "district_name",
    "region_name",
    "district_code",
    "region_code",
    "country_code",
    "country_name",
)


def _is_empty_value(value: Any) -> bool:
    """True if ``apply_inherited_data`` would consider this slot 'missing'."""
    if isinstance(value, (list, dict)):
        return len(value) == 0
    if isinstance(value, str):
        return value.strip() == ""
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _empty_mask(series: pd.Series) -> pd.Series:
    return series.apply(_is_empty_value)


def _values_equal(a: Any, b: Any) -> bool:
    """Lenient equality check that handles dicts/lists/timestamps/NaN safely."""
    # Treat both-empty as equal regardless of type (None vs NaT vs "" all match here).
    if _is_empty_value(a) and _is_empty_value(b):
        return True
    if isinstance(a, (list, dict)) or isinstance(b, (list, dict)):
        return a == b
    try:
        return bool(a == b)
    except (TypeError, ValueError):
        return False


def _strip_ref(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip('"').strip("'").strip()
    return cleaned or None


def _get_affected_datasets(client: bigquery.Client) -> list[tuple[str, int]]:
    """Return (dataset_url, row_count) tuples ordered by row_count desc."""
    query = f"""
        SELECT dataset_url, COUNT(*) AS row_count
        FROM `{TABLE_ID}`
        WHERE {_AFFECTED_PREDICATE}
        GROUP BY dataset_url
        ORDER BY row_count DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("cutoff", "DATE", CUTOFF_DATE)]
    )
    rows = client.query(query, job_config=job_config).result()
    out = [(r["dataset_url"], int(r["row_count"])) for r in rows if r["dataset_url"]]
    total = sum(c for _, c in out)
    logger.info("Discovery: %d datasets, %d total affected rows", len(out), total)
    return out


def _load_affected_rows(dataset_url: str) -> pd.DataFrame:
    """Load every affected row for a single dataset, with all opportunities columns."""
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
            bigquery.ScalarQueryParameter("cutoff", "DATE", CUTOFF_DATE),
        ]
    )
    return client.query(query, job_config=job_config).to_dataframe()


def _fix_dataset(
    dataset_url: str,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int, int]:
    """Repair affected rows for one dataset_url.

    Returns (examined, merged, location_filled):
      - examined: rows matching the affected predicate that we loaded
      - merged: rows whose inherited_data actually grew (parent was found,
                apply_inherited_data ran). These are the rows written back.
      - location_filled: subset of merged where location went from {} to non-{}.
    """
    start = perf_counter()
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)
    affected_df = _load_affected_rows(dataset_url)
    examined = len(affected_df)
    logger.info("[%d/%d] loaded %d affected rows for %s", index, total, examined, dataset_url)
    if examined == 0:
        return 0, 0, 0

    affected_df = affected_df.reset_index(drop=True)
    # BQ JSON columns arrive from to_dataframe() as raw JSON strings; parse them
    # so the downstream processing helpers see real dicts/lists/None.
    parse_opportunities_json_columns(affected_df)

    parent_ids: set[str] = set()
    for ref in affected_df["has_superEvent"]:
        cleaned = _strip_ref(ref)
        if cleaned:
            parent_ids.add(cleaned)

    if not parent_ids:
        logger.info(
            "[%d/%d] DONE %s — examined=%d, no parent references (in %.2fs)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        del affected_df
        gc.collect()
        return examined, 0, 0

    parent_df = get_dataset_opportunities(dataset_url, required_data_ids=sorted(parent_ids))
    if parent_df.empty:
        logger.info(
            "[%d/%d] DONE %s — examined=%d, no parent rows found in BigQuery (in %.2fs)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        del affected_df, parent_df
        gc.collect()
        return examined, 0, 0

    # ``get_dataset_opportunities`` already parses JSON columns since the
    # production fix landed; this call is a no-op safety net in case the
    # function is invoked through an older path.
    parse_opportunities_json_columns(parent_df)

    payload_by_data_id = _build_super_event_payload_by_data_id(affected_df, parent_df)

    # Snapshot each inheritable field BEFORE the merge so we can:
    #   1. detect which rows actually received new data, and
    #   2. defensively assert that no previously-populated value was overwritten
    #      (apply_inherited_data fills only when empty; this is a belt-and-braces
    #      check in case that contract ever changes).
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

        # Safety: if a previously non-empty value somehow changed, restore it and warn.
        previously_populated = ~before_empty[field]
        if previously_populated.any():
            mismatch = previously_populated & affected_df[field].combine(
                before_values[field],
                lambda a, b: not _values_equal(a, b),
            )
            mismatch_count = int(mismatch.sum())
            if mismatch_count:
                logger.warning(
                    "[%d/%d] %s — %d rows had non-empty %s value altered by handle_super_events; restoring",
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

    rows_to_write = affected_df.loc[merged_mask].copy()
    del affected_df, parent_df, payload_by_data_id, before_empty, before_values
    gc.collect()

    if not dry_run:
        logger.info(
            "[%d/%d] writing %d rows for %s",
            index, total, len(rows_to_write), dataset_url,
        )
        write_dataset_opportunities(dataset_url, rows_to_write)

    logger.info(
        "[%d/%d] DONE %s — examined=%d merged=%d location_filled=%d in %.2fs (dry_run=%s)",
        index, total, dataset_url, examined, merged, location_filled, perf_counter() - start, dry_run,
    )
    del rows_to_write
    gc.collect()
    return examined, merged, location_filled


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
    help="Restrict to specific dataset_url(s); repeat for multiple. "
         "Skips the discovery query.",
)
@click.option(
    "--limit",
    type=int,
    default=0,
    show_default=True,
    help="Process at most this many datasets (largest-first). 0 = no limit.",
)
def main(dry_run: bool, max_workers: int, datasets: tuple[str, ...], limit: int) -> None:
    """Backfill missing inherited columns for rows hit by the has_superEvent quote bug."""
    overall_start = perf_counter()
    client = bigquery.Client(project=GCP_PROJECT_ID)

    if datasets:
        dataset_urls = list(datasets)
        logger.info("Restricting to %d explicit dataset_url(s)", len(dataset_urls))
    else:
        affected = _get_affected_datasets(client)
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

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="backfill") as executor:
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


if __name__ == "__main__":
    main()
