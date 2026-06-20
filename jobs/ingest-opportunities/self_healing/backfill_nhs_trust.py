"""
Self-healing backfill: populate the NHS Trust columns (nhstrust_name,
nhstrust_code) for opportunities rows that already carry a usable ``location``
(with at least a latitude / longitude pair) but never had an NHS Trust
resolved against them.

Target rows
-----------
- ``nhstrust_name IS NULL`` (proxy for "NHS Trust lookup hasn't been run")
- ``location`` is not the empty JSON object
- ``location.latitude IS NOT NULL``

The script fills only-when-empty; it never overwrites an already-populated
column. Rows whose location lacks latitude/longitude (or whose coordinates
fall outside any known NHS Trust boundary) are skipped and counted as
``unresolvable``.

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python self_healing/backfill_nhs_trust.py [--dry-run] \
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
    parse_opportunities_json_columns,
    write_dataset_opportunities,
)
from boundary_lookup import lookup_nhs_trust  # noqa: E402

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backfill_nhs_trust")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

_AFFECTED_PREDICATE = (
    "nhstrust_name IS NULL "
    "AND TO_JSON_STRING(location) != '{}'"
    "AND location.latitude IS NOT NULL"
)

# Columns we may populate on each affected row. We snapshot these before
# enrichment so we can guarantee fill-only-when-empty semantics and pick out
# which rows actually need to be written back.
NHSTRUST_COLUMNS: tuple[str, ...] = (
    "nhstrust_name",
    "nhstrust_code",
)


def _is_empty_value(value: Any) -> bool:
    """True if a DataFrame cell should be treated as 'missing'."""
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


def _location_coords(location: Any) -> tuple[float, float] | None:
    """Return (lat, lng) if both are present and finite, else None."""
    if not isinstance(location, dict):
        return None
    lat = location.get("latitude")
    lng = location.get("longitude")
    if lat is None or lng is None:
        return None
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None
    return lat_f, lng_f


def _get_affected_datasets(client: bigquery.Client) -> list[tuple[str, int]]:
    """Return (dataset_url, row_count) tuples ordered by row_count desc."""
    query = f"""
        SELECT dataset_url, COUNT(*) AS row_count
        FROM `{TABLE_ID}`
        WHERE {_AFFECTED_PREDICATE}
        GROUP BY dataset_url
        ORDER BY row_count DESC
    """
    rows = client.query(query).result()
    out = [(r["dataset_url"], int(r["row_count"])) for r in rows if r["dataset_url"]]
    total = sum(c for _, c in out)
    logger.info("Discovery: %d datasets, %d total affected rows", len(out), total)
    return out


def _load_affected_rows(dataset_url: str) -> pd.DataFrame:
    """Load all affected rows for one dataset_url with the full opportunities schema."""
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


def _enrich_row(
    df: pd.DataFrame,
    idx,
) -> bool:
    """Compute NHS Trust for one row's location and fill empty cells.

    Returns True iff at least one NHS Trust cell on this row was populated.
    """
    coords = _location_coords(df.at[idx, "location"])
    if coords is None:
        return False
    lat, lng = coords

    nhstrust_name, nhstrust_code = lookup_nhs_trust(lat, lng)
    if not nhstrust_name:
        # Outside any NHS Trust boundary / unresolvable.
        return False

    new_values = {
        "nhstrust_name": nhstrust_name,
        "nhstrust_code": nhstrust_code,
    }

    changed = False
    for col, val in new_values.items():
        if val is None:
            continue
        if _is_empty_value(df.at[idx, col]):
            df.at[idx, col] = val
            changed = True
    return changed


def _fix_dataset(
    dataset_url: str,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int, int]:
    """Repair affected rows for one dataset_url.

    Returns (examined, filled, unresolvable):
      - examined: rows matching the affected predicate that we loaded
      - filled: rows where we populated at least one NHS Trust column
      - unresolvable: rows we couldn't help (no lat/lng, or outside any trust)
    """
    start = perf_counter()
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)
    affected_df = _load_affected_rows(dataset_url)
    examined = len(affected_df)
    logger.info("[%d/%d] loaded %d affected rows for %s", index, total, examined, dataset_url)
    if examined == 0:
        return 0, 0, 0

    affected_df = affected_df.reset_index(drop=True)
    # Parse JSON-typed columns (location especially) into real Python objects.
    parse_opportunities_json_columns(affected_df)

    filled_indices: list[int] = []
    unresolvable = 0
    for idx in affected_df.index:
        if _enrich_row(affected_df, idx):
            filled_indices.append(idx)
        else:
            unresolvable += 1

    filled = len(filled_indices)
    if filled == 0:
        logger.info(
            "[%d/%d] DONE %s — examined=%d unresolvable=%d (in %.2fs)",
            index, total, dataset_url, examined, unresolvable, perf_counter() - start,
        )
        del affected_df
        gc.collect()
        return examined, 0, unresolvable

    rows_to_write = affected_df.loc[filled_indices].copy()
    del affected_df
    gc.collect()

    if not dry_run:
        logger.info(
            "[%d/%d] writing %d rows for %s",
            index, total, len(rows_to_write), dataset_url,
        )
        write_dataset_opportunities(dataset_url, rows_to_write)

    logger.info(
        "[%d/%d] DONE %s — examined=%d filled=%d unresolvable=%d in %.2fs (dry_run=%s)",
        index, total, dataset_url, examined, filled, unresolvable, perf_counter() - start, dry_run,
    )
    del rows_to_write
    gc.collect()
    return examined, filled, unresolvable


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
    """Backfill NHS Trust columns from existing location lat/lng pairs."""
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
    total_filled = 0
    total_unresolvable = 0
    total_datasets = len(dataset_urls)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="nhstrust") as executor:
        futures = {
            executor.submit(_fix_dataset, ds, dry_run, idx, total_datasets): ds
            for idx, ds in enumerate(dataset_urls, start=1)
        }
        completed = 0
        for future in as_completed(futures):
            ds = futures[future]
            try:
                examined, filled, unresolvable = future.result()
                total_examined += examined
                total_filled += filled
                total_unresolvable += unresolvable
            except Exception:
                logger.exception("Failed for dataset %s", ds)
            completed += 1
            logger.info(
                "Progress %d/%d datasets complete — running totals examined=%d filled=%d unresolvable=%d",
                completed, total_datasets, total_examined, total_filled, total_unresolvable,
            )

    logger.info(
        "DONE in %.2fs — datasets=%d examined=%d filled=%d unresolvable=%d (dry_run=%s)",
        perf_counter() - overall_start,
        len(dataset_urls),
        total_examined,
        total_filled,
        total_unresolvable,
        dry_run,
    )


if __name__ == "__main__":
    main()
