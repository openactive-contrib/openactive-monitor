"""
Self-healing backfill: populate ``organization_name`` and ``organization_json``
for rows whose ``json_data`` exposes an ``organizer`` or ``provider`` block
but the corresponding top-level columns are NULL.

Both columns are filled via a single per-dataset SQL ``UPDATE`` (mirrors
``backfill_accessibility_gender.py``).  The UPDATE uses ``COALESCE`` so it
never overwrites an already-populated cell — safe to re-run as part of
self-healing.

Shape of the new columns (matches what the live extractor in
``processing.py`` writes today):

- ``organization_json``: JSON, the raw ``organizer`` (or ``provider``)
  payload from ``json_data`` with its original shape preserved — dict,
  list of dicts, or a URI string.  ``organizer`` wins when both are
  present (Event types use ``organizer``; FacilityUse types use
  ``provider``, and the two never co-exist meaningfully on the same row).
- ``organization_name``: STRING, the first non-empty ``name`` found in
  the payload.  Returns NULL for URI-only references that carry no
  embedded ``name``.

Target rows
-----------
A row is affected if either of the following holds:

- ``organization_json IS NULL`` AND ``json_data.organizer`` or
  ``json_data.provider`` is a non-empty array / object / string.
- ``organization_name IS NULL`` AND ``json_data.organizer`` or
  ``json_data.provider`` exposes a non-empty ``name`` (as a dict
  ``payload.name`` or as the first array element ``payload[0].name``).

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python self_healing/backfill_organization.py [--dry-run] \
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
logger = logging.getLogger("backfill_organization")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

# Predicate: a row is affected if EITHER column has a fillable source.
#
# The ``_json`` and ``_name`` halves are intentionally kept separate so that
# a row whose only ``organizer`` is a URI string (no embedded name) becomes
# non-affected after a single pass — ``organization_json`` is filled, the
# ``_json`` half stops matching, and the ``_name`` half never matches for
# URI-only sources.  This is what gives the backfill its idempotency.
_HAS_SOURCE_OBJECT = (
    "("
    "(JSON_QUERY(json_data, '$.organizer') IS NOT NULL"
    "   AND TO_JSON_STRING(JSON_QUERY(json_data, '$.organizer')) NOT IN ('null', '[]', '\"\"'))"
    " OR"
    " (JSON_QUERY(json_data, '$.provider') IS NOT NULL"
    "   AND TO_JSON_STRING(JSON_QUERY(json_data, '$.provider')) NOT IN ('null', '[]', '\"\"'))"
    ")"
)
_HAS_EXTRACTABLE_NAME = (
    "("
    " (JSON_VALUE(json_data, '$.organizer.name') IS NOT NULL"
    "    AND JSON_VALUE(json_data, '$.organizer.name') != '')"
    " OR (JSON_VALUE(json_data, '$.organizer[0].name') IS NOT NULL"
    "    AND JSON_VALUE(json_data, '$.organizer[0].name') != '')"
    " OR (JSON_VALUE(json_data, '$.provider.name') IS NOT NULL"
    "    AND JSON_VALUE(json_data, '$.provider.name') != '')"
    " OR (JSON_VALUE(json_data, '$.provider[0].name') IS NOT NULL"
    "    AND JSON_VALUE(json_data, '$.provider[0].name') != '')"
    ")"
)
_AFFECTED_PREDICATE = (
    "("
    f" (organization_json IS NULL AND {_HAS_SOURCE_OBJECT})"
    f" OR (organization_name IS NULL AND {_HAS_EXTRACTABLE_NAME})"
    ")"
)

# UPDATE statement.
#
# ``organization_json``: COALESCE keeps an existing value; otherwise pick the
# first non-empty source (organizer first, then provider).  The explicit
# CASE guards against the BigQuery JSON-null trap — a literal ``"x": null``
# in ``json_data`` returns a JSON ``null`` value (not SQL NULL) which would
# otherwise be selected by COALESCE.
#
# ``organization_name``: COALESCE keeps an existing value; otherwise run two
# UNNEST subqueries (organizer, then provider) and pick the first non-empty
# ``$.name``.  ``JSON_QUERY_ARRAY`` handles the list case directly; the
# inner CASE wraps a single dict into a one-element array so the same
# UNNEST works.  URI-string sources flow through as ``ELSE []`` → empty
# result → NULL.
_UPDATE_QUERY = f"""
    UPDATE `{TABLE_ID}`
    SET
      organization_json = COALESCE(
        organization_json,
        CASE
          WHEN JSON_QUERY(json_data, '$.organizer') IS NOT NULL
               AND TO_JSON_STRING(JSON_QUERY(json_data, '$.organizer')) NOT IN ('null', '[]', '""')
            THEN JSON_QUERY(json_data, '$.organizer')
          WHEN JSON_QUERY(json_data, '$.provider') IS NOT NULL
               AND TO_JSON_STRING(JSON_QUERY(json_data, '$.provider')) NOT IN ('null', '[]', '""')
            THEN JSON_QUERY(json_data, '$.provider')
          ELSE NULL
        END
      ),
      organization_name = COALESCE(
        organization_name,
        (
          SELECT JSON_VALUE(item, '$.name')
          FROM UNNEST(COALESCE(
            JSON_QUERY_ARRAY(json_data, '$.organizer'),
            CASE
              WHEN JSON_VALUE(json_data, '$.organizer.name') IS NOT NULL
                THEN [JSON_QUERY(json_data, '$.organizer')]
              ELSE []
            END
          )) AS item WITH OFFSET AS pos
          WHERE JSON_VALUE(item, '$.name') IS NOT NULL
            AND JSON_VALUE(item, '$.name') != ''
          ORDER BY pos
          LIMIT 1
        ),
        (
          SELECT JSON_VALUE(item, '$.name')
          FROM UNNEST(COALESCE(
            JSON_QUERY_ARRAY(json_data, '$.provider'),
            CASE
              WHEN JSON_VALUE(json_data, '$.provider.name') IS NOT NULL
                THEN [JSON_QUERY(json_data, '$.provider')]
              ELSE []
            END
          )) AS item WITH OFFSET AS pos
          WHERE JSON_VALUE(item, '$.name') IS NOT NULL
            AND JSON_VALUE(item, '$.name') != ''
          ORDER BY pos
          LIMIT 1
        )
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
    """Backfill the two organisation columns for one dataset_url.

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
    """Backfill organization_name and organization_json from json_data."""
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

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="org_backfill") as executor:
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
