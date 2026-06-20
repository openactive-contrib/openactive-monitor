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

Performance design
------------------
This backfill targets a ~10M-row table, so it is built to stay cheap on both
memory and CPU:

- **Minimal projection.** Only the columns needed to resolve and key a row are
  read (``dataset_url, feed_id, id`` plus ``location.latitude/longitude``). The
  large ``json_data`` / ``inherited_data`` payloads are never fetched.
- **Vectorized geolocation.** All coordinates for a dataset are resolved in a
  single C-level point-in-polygon spatial join (``lookup_nhs_trust_batch``)
  instead of one Python ``lookup_nhs_trust`` call per row.
- **Lightweight write-back.** Only ``nhstrust_name`` / ``nhstrust_code`` are
  upserted (via a tiny 5-column staging table + targeted MERGE), so the heavy
  JSON columns are never re-serialized or rewritten.
- **No "largest-first" ordering.** Datasets are processed in a stable
  ``dataset_url`` order. Sorting by row-count pushed the biggest datasets to
  the front and made several workers load huge datasets into memory at once.

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
from uuid import uuid4

import click
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Make the ingest-opportunities package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boundary_lookup import lookup_nhs_trust_batch  # noqa: E402

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

# Only the columns required to resolve a coordinate and key the row back to the
# table. Crucially this excludes the large JSON payload columns.
_LOAD_COLUMNS: tuple[str, ...] = (
    "dataset_url",
    "feed_id",
    "id",
    # location.latitude / longitude is all we need from the location struct.
    "location.latitude AS _lat",
    "location.longitude AS _lng",
)


def _coerce_float(value: Any) -> float | None:
    """Return a finite float, or None if missing/malformed."""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(f):
        return None
    return f


def _get_affected_datasets(client: bigquery.Client) -> list[str]:
    """Return the distinct affected ``dataset_url`` values in a stable order.

    We deliberately do NOT order by row count: that front-loads the largest
    datasets and makes several workers hold huge result sets in memory at once.
    A stable ``dataset_url`` ordering also makes the run resumable.
    """
    query = f"""
        SELECT DISTINCT dataset_url
        FROM `{TABLE_ID}`
        WHERE {_AFFECTED_PREDICATE}
        ORDER BY dataset_url
    """
    rows = client.query(query).result()
    out = [r["dataset_url"] for r in rows if r["dataset_url"]]
    logger.info("Discovery: %d datasets with affected rows", len(out))
    return out


def _load_affected_rows(client: bigquery.Client, dataset_url: str) -> pd.DataFrame:
    """Load the minimal columns for affected rows of one ``dataset_url``."""
    selected = ", ".join(_LOAD_COLUMNS)
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


def _write_nhstrust_updates(
    client: bigquery.Client,
    dataset_url: str,
    updates_df: pd.DataFrame,
) -> int:
    """Upsert ONLY the NHS Trust columns for the given rows.

    Loads a tiny 5-column staging table and MERGEs it into the opportunities
    table, updating ``nhstrust_name`` / ``nhstrust_code`` only where they are
    still NULL (fill-only-when-empty). The large JSON columns are never touched.
    Returns the number of affected rows.
    """
    if updates_df.empty:
        return 0

    staging_table_id = (
        f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"
        f"_nhstrust_staging_{uuid4().hex[:12]}"
    )
    staging_schema = [
        bigquery.SchemaField("dataset_url", "STRING"),
        bigquery.SchemaField("feed_id", "STRING"),
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("nhstrust_name", "STRING"),
        bigquery.SchemaField("nhstrust_code", "STRING"),
    ]

    rows = updates_df[
        ["dataset_url", "feed_id", "id", "nhstrust_name", "nhstrust_code"]
    ].to_dict(orient="records")

    merge_query = f"""
        MERGE `{TABLE_ID}` AS T
        USING `{staging_table_id}` AS S
        ON  T.dataset_url = S.dataset_url
        AND T.feed_id = S.feed_id
        AND T.id = S.id
        WHEN MATCHED AND T.nhstrust_name IS NULL THEN
            UPDATE SET
                T.nhstrust_name = S.nhstrust_name,
                T.nhstrust_code = S.nhstrust_code
    """

    try:
        load_job = client.load_table_from_json(
            rows,
            staging_table_id,
            job_config=bigquery.LoadJobConfig(
                schema=staging_schema,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            ),
        )
        load_job.result()

        merge_job = client.query(merge_query)
        merge_job.result()
        affected = int(merge_job.num_dml_affected_rows or 0)
        logger.info("Updated %d NHS Trust rows for %s", affected, dataset_url)
        return affected
    finally:
        client.delete_table(staging_table_id, not_found_ok=True)


def _fix_dataset(
    dataset_url: str,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int, int]:
    """Repair affected rows for one dataset_url.

    Returns (examined, filled, unresolvable):
      - examined: rows matching the affected predicate that we loaded
      - filled: rows where we resolved an NHS Trust to write back
      - unresolvable: rows we couldn't help (no lat/lng, or outside any trust)
    """
    start = perf_counter()
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)

    client = bigquery.Client(project=GCP_PROJECT_ID)
    affected_df = _load_affected_rows(client, dataset_url)
    examined = len(affected_df)
    logger.info("[%d/%d] loaded %d affected rows for %s", index, total, examined, dataset_url)
    if examined == 0:
        return 0, 0, 0

    # Build the coordinate list aligned with the DataFrame and resolve the whole
    # batch in a single vectorized spatial join.
    coords = [
        (_coerce_float(lat), _coerce_float(lng))
        for lat, lng in zip(affected_df["_lat"], affected_df["_lng"])
    ]
    resolved = lookup_nhs_trust_batch(coords)

    affected_df["nhstrust_name"] = [r[0] for r in resolved]
    affected_df["nhstrust_code"] = [r[1] for r in resolved]

    updates_df = affected_df.loc[
        affected_df["nhstrust_name"].notna(),
        ["dataset_url", "feed_id", "id", "nhstrust_name", "nhstrust_code"],
    ].copy()
    filled = len(updates_df)
    unresolvable = examined - filled

    del affected_df, coords, resolved
    gc.collect()

    if filled and not dry_run:
        logger.info("[%d/%d] writing %d rows for %s", index, total, filled, dataset_url)
        _write_nhstrust_updates(client, dataset_url, updates_df)

    logger.info(
        "[%d/%d] DONE %s — examined=%d filled=%d unresolvable=%d in %.2fs (dry_run=%s)",
        index, total, dataset_url, examined, filled, unresolvable,
        perf_counter() - start, dry_run,
    )
    del updates_df
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
    help="Process at most this many datasets (stable dataset_url order). 0 = no limit.",
)
def main(dry_run: bool, max_workers: int, datasets: tuple[str, ...], limit: int) -> None:
    """Backfill NHS Trust columns from existing location lat/lng pairs."""
    overall_start = perf_counter()
    client = bigquery.Client(project=GCP_PROJECT_ID)

    if datasets:
        dataset_urls = list(datasets)
        logger.info("Restricting to %d explicit dataset_url(s)", len(dataset_urls))
    else:
        dataset_urls = _get_affected_datasets(client)
        if limit and limit > 0:
            dataset_urls = dataset_urls[:limit]
            logger.info("Limiting to first %d datasets", limit)

    if not dataset_urls:
        logger.info("Nothing to fix.")
        return

    total_examined = 0
    total_filled = 0
    total_unresolvable = 0
    total_datasets = len(dataset_urls)

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="nhstrust") as executor:
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
