"""
Self-healing backfill: populate ``accessibilitySupport`` and
``genderRestriction`` for rows whose ``json_data`` exposes those fields but
the corresponding top-level columns are NULL.

Both columns are filled via a single per-dataset SQL ``UPDATE`` (mirrors
``backfill_data_id.py``).  The UPDATE uses ``COALESCE`` so it never
overwrites an already-populated cell — safe to re-run as part of
self-healing.

Shape of the new columns (matches what the live extractor in
``processing.py`` writes today):

- ``accessibilitySupport``: JSON array of ``prefLabel`` strings (e.g.
  ``["Hearing impairment", "Visual impairment"]``).  Real-world feeds carry
  ``accessibilitySupport`` as a ``Concept[]`` of dicts; this script extracts
  the ``prefLabel`` from each Concept.  An empty prefLabel array collapses
  to SQL ``NULL``.
- ``genderRestriction``: STRING, raw URI value (e.g.
  ``https://openactive.io/FemaleOnly``).  ``""`` is treated as missing.

Target rows
-----------
A row is affected if either of the following holds:

- ``accessibilitySupport IS NULL`` AND ``json_data.accessibilitySupport``
  is a non-empty array/object.
- ``genderRestriction IS NULL`` AND ``json_data.genderRestriction`` is a
  non-empty string.

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python self_healing/backfill_accessibility_gender.py [--dry-run] \
        [--max-workers 8] [--dataset <url>] [--limit 0]
"""

from __future__ import annotations

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter

import click
from dotenv import load_dotenv
from google.cloud import bigquery

# Make the ingest-opportunities package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from self_healing._common import (  # noqa: E402
    count_dataset_rows,
    discover_affected_datasets,
    run_dml_with_retry,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backfill_accessibility_gender")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

# Predicate: either the accessibilitySupport column is unfilled and json_data
# carries a non-empty array/object for it, OR the genderRestriction column is
# unfilled and json_data has a non-empty string for it.  Empty `[]` arrays,
# JSON `null` literals and empty `""` strings are excluded so we don't write
# meaningless placeholder values.
_AFFECTED_PREDICATE = (
    "("
    " (accessibilitySupport IS NULL"
    "    AND JSON_QUERY(json_data, '$.accessibilitySupport') IS NOT NULL"
    "    AND TO_JSON_STRING(JSON_QUERY(json_data, '$.accessibilitySupport')) NOT IN ('null', '[]'))"
    " OR"
    " (genderRestriction IS NULL"
    "    AND JSON_VALUE(json_data, '$.genderRestriction') IS NOT NULL"
    "    AND JSON_VALUE(json_data, '$.genderRestriction') != '')"
    ")"
)

# UPDATE statement.
#
# ``accessibilitySupport``: COALESCE keeps an existing value; otherwise build
# an ARRAY<STRING> of prefLabels and TO_JSON it.  Real feeds always pass an
# array of Concept dicts, but some legacy feeds use a single Concept dict —
# the inner COALESCE wraps that case into a one-element array so the same
# UNNEST works.  An all-empty result collapses to NULL (via the outer
# CASE WHEN ARRAY_LENGTH=0).
#
# ``genderRestriction``: COALESCE the raw JSON_VALUE — null/empty are
# excluded by the WHERE clause, so a non-null COALESCE input is a real value.
_UPDATE_QUERY = f"""
    UPDATE `{TABLE_ID}`
    SET
      accessibilitySupport = COALESCE(
        accessibilitySupport,
        (
          SELECT CASE WHEN ARRAY_LENGTH(labels) = 0 THEN NULL ELSE TO_JSON(labels) END
          FROM (
            SELECT ARRAY(
              SELECT JSON_VALUE(item, '$.prefLabel')
              FROM UNNEST(COALESCE(
                JSON_QUERY_ARRAY(json_data, '$.accessibilitySupport'),
                CASE
                  WHEN JSON_VALUE(json_data, '$.accessibilitySupport.prefLabel') IS NOT NULL
                    THEN [JSON_QUERY(json_data, '$.accessibilitySupport')]
                  ELSE []
                END
              )) AS item
              WHERE JSON_VALUE(item, '$.prefLabel') IS NOT NULL
                AND JSON_VALUE(item, '$.prefLabel') != ''
            ) AS labels
          )
        )
      ),
      genderRestriction = COALESCE(
        genderRestriction,
        JSON_VALUE(json_data, '$.genderRestriction')
      )
    WHERE dataset_url = @dataset_url
      AND {_AFFECTED_PREDICATE}
"""


def _get_affected_datasets(client: bigquery.Client) -> list[tuple[str, int]]:
    """Return (dataset_url, row_count) tuples ordered by row_count desc."""
    out = discover_affected_datasets(client, TABLE_ID, _AFFECTED_PREDICATE)
    total = sum(c for _, c in out)
    logger.info("Discovery: %d datasets, %d total affected rows", len(out), total)
    return out


def _fix_dataset(
    dataset_url: str,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int]:
    """Backfill the two new columns for one dataset_url.

    Returns (examined, updated):
      - examined: rows matching the affected predicate at scan time
      - updated:  rows actually modified by the UPDATE (0 in dry-run)
    """
    start = perf_counter()
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)
    client = bigquery.Client(project=GCP_PROJECT_ID)

    examined = count_dataset_rows(client, TABLE_ID, dataset_url, _AFFECTED_PREDICATE)
    logger.info("[%d/%d] %s has %d affected rows", index, total, dataset_url, examined)

    if examined == 0:
        return 0, 0

    if dry_run:
        logger.info(
            "[%d/%d] DONE %s — would update %d rows in %.2fs (dry_run=True)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        return examined, 0

    updated = run_dml_with_retry(
        client,
        _UPDATE_QUERY,
        [bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url)],
        label=dataset_url,
    )
    logger.info(
        "[%d/%d] DONE %s — examined=%d updated=%d in %.2fs",
        index, total, dataset_url, examined, updated, perf_counter() - start,
    )
    return examined, updated


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Count affected rows but do not run the UPDATE.",
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
    """Backfill accessibilitySupport and genderRestriction from json_data."""
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
    total_updated = 0
    total_datasets = len(dataset_urls)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="acc_gender") as executor:
        futures = {
            executor.submit(_fix_dataset, ds, dry_run, idx, total_datasets): ds
            for idx, ds in enumerate(dataset_urls, start=1)
        }
        completed = 0
        for future in as_completed(futures):
            ds = futures[future]
            try:
                examined, updated = future.result()
                total_examined += examined
                total_updated += updated
            except Exception:
                logger.exception("Failed for dataset %s", ds)
            completed += 1
            logger.info(
                "Progress %d/%d datasets complete — running totals examined=%d updated=%d",
                completed, total_datasets, total_examined, total_updated,
            )

    logger.info(
        "DONE in %.2fs — datasets=%d examined=%d updated=%d (dry_run=%s)",
        perf_counter() - overall_start,
        len(dataset_urls),
        total_examined,
        total_updated,
        dry_run,
    )


if __name__ == "__main__":
    main()
