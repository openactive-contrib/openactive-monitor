"""Shared helpers for the per-dataset SQL UPDATE self-healing scripts.

Every script in ``self_healing/`` that operates by issuing a focused
``UPDATE`` against ``opportunities`` shares the same skeleton:

  1. Discover which ``dataset_url`` values contain affected rows.
  2. For each dataset_url, count affected rows (for the "examined" log line).
  3. Run the UPDATE, retrying on transient BigQuery DML errors
     (concurrent-update collisions and streaming-buffer conflicts).

The helpers below collapse those primitives into one place so the scripts
read as straight-line orchestration and pick up retry / observability
improvements uniformly. The lower-level error classifiers
(``is_concurrent_update_error``, ``is_streaming_buffer_dml_error``,
``retry_delay_seconds``) live in :mod:`bigquery_ops` because they are also
used by the MERGE / DELETE paths in the main ingest job.
"""

from __future__ import annotations

import logging
import time
from typing import Sequence

from google.cloud import bigquery

from bigquery_ops import (
    is_concurrent_update_error,
    is_streaming_buffer_dml_error,
    retry_delay_seconds,
)

logger = logging.getLogger(__name__)

# DML retry tuning. Concurrent-update collisions usually clear within seconds;
# streaming-buffer conflicts can take much longer (the BigQuery streaming
# buffer flushes on a roughly half-hour cadence) so the cap is generous.
DEFAULT_DML_RETRY_MAX_ATTEMPTS = 8
DEFAULT_DML_RETRY_BASE_SECONDS = 5
DEFAULT_DML_RETRY_MAX_SECONDS = 15 * 60


def discover_affected_datasets(
    client: bigquery.Client,
    table_id: str,
    predicate_sql: str,
    extra_query_parameters: Sequence[bigquery.ScalarQueryParameter] | None = None,
) -> list[tuple[str, int]]:
    """Return ``(dataset_url, row_count)`` for every dataset with affected rows.

    Ordered largest-first so callers can prioritise the biggest workloads
    and surface long-running outliers via per-dataset logging.
    """
    query = f"""
        SELECT dataset_url, COUNT(*) AS row_count
        FROM `{table_id}`
        WHERE {predicate_sql}
        GROUP BY dataset_url
        ORDER BY row_count DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=list(extra_query_parameters or ())
    )
    rows = client.query(query, job_config=job_config).result()
    return [(r["dataset_url"], int(r["row_count"])) for r in rows if r["dataset_url"]]


def count_dataset_rows(
    client: bigquery.Client,
    table_id: str,
    dataset_url: str,
    predicate_sql: str,
    extra_query_parameters: Sequence[bigquery.ScalarQueryParameter] | None = None,
) -> int:
    """Count rows matching ``predicate_sql`` within one ``dataset_url``."""
    query = f"""
        SELECT COUNT(*) AS n
        FROM `{table_id}`
        WHERE dataset_url = @dataset_url
          AND {predicate_sql}
    """
    params: list[bigquery.ScalarQueryParameter] = [
        bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url)
    ]
    if extra_query_parameters:
        params.extend(extra_query_parameters)
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    rows = list(client.query(query, job_config=job_config).result())
    return int(rows[0]["n"]) if rows else 0


def run_dml_with_retry(
    client: bigquery.Client,
    query: str,
    query_parameters: Sequence[bigquery.ScalarQueryParameter] | None = None,
    *,
    label: str = "",
    max_attempts: int = DEFAULT_DML_RETRY_MAX_ATTEMPTS,
    base_delay_seconds: int = DEFAULT_DML_RETRY_BASE_SECONDS,
    max_delay_seconds: int = DEFAULT_DML_RETRY_MAX_SECONDS,
) -> int:
    """Run a DML statement with exponential-backoff retry on transient errors.

    Retried errors:
      - Concurrent-update collisions (another job touched the same partition).
      - Streaming-buffer DML conflicts (the target row was just inserted and
        BigQuery hasn't flushed the streaming buffer yet).
    Any other exception bubbles up.

    Returns the count of rows the DML actually affected.
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=list(query_parameters or ())
    )
    for attempt in range(1, max_attempts + 1):
        try:
            job = client.query(query, job_config=job_config)
            job.result()
            return int(job.num_dml_affected_rows or 0)
        except Exception as exc:
            transient = (
                is_concurrent_update_error(exc)
                or is_streaming_buffer_dml_error(exc)
            )
            if not transient:
                raise
            if attempt >= max_attempts:
                logger.error(
                    "%s — exhausted %d retries on transient DML errors (%s)",
                    label or "DML", max_attempts, exc,
                )
                raise
            delay = retry_delay_seconds(attempt, base_delay_seconds, max_delay_seconds)
            kind = (
                "streaming-buffer conflict"
                if is_streaming_buffer_dml_error(exc)
                else "concurrent-update collision"
            )
            logger.warning(
                "%s — %s (attempt %d/%d), retrying in %ds",
                label or "DML", kind, attempt, max_attempts, delay,
            )
            time.sleep(delay)

    # Unreachable — the loop either returns on success or raises on exhaustion.
    return 0
