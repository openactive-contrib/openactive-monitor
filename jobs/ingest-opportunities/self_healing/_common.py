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
from datetime import datetime
from typing import Any, Sequence
from uuid import uuid4

import pandas as pd
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


# ---------------------------------------------------------------------------
# Inheritance backfills (superEvent / nested IFU): shared field lists, diffing
# and the slim fill-only-when-empty MERGE writer.
# ---------------------------------------------------------------------------

# Columns ``processing.apply_inherited_data`` may fill from a parent, partitioned
# by BigQuery type for the slim staging table.  ``inherited_data`` is
# intentionally never written back to ``opportunities`` (it would explode the
# table with redundant data), so backfills detect changes by diffing these.
INHERITABLE_JSON_COLUMNS: tuple[str, ...] = (
    "activity",
    "facility",
    "activity_json",
    "facility_json",
    "location",
    "ageRange",
    "level",
    "accessibilitySupport",
)
INHERITABLE_TIMESTAMP_COLUMNS: tuple[str, ...] = ("startDate", "endDate")
INHERITABLE_BOOL_COLUMNS: tuple[str, ...] = ("isAccessibleForFree",)
INHERITABLE_STRING_COLUMNS: tuple[str, ...] = (
    "genderRestriction",
    "organization_name",
    "district_name",
    "region_name",
    "district_code",
    "region_code",
    "country_code",
    "country_name",
    "nhstrust_name",
    "nhstrust_code",
)
INHERITABLE_FIELDS: tuple[str, ...] = (
    *INHERITABLE_JSON_COLUMNS,
    *INHERITABLE_TIMESTAMP_COLUMNS,
    *INHERITABLE_BOOL_COLUMNS,
    *INHERITABLE_STRING_COLUMNS,
)


def is_empty_value(value: Any) -> bool:
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


def empty_mask(series: pd.Series) -> pd.Series:
    return series.apply(is_empty_value)


def values_equal(a: Any, b: Any) -> bool:
    """Lenient equality check that handles dicts/lists/timestamps/NaN safely."""
    if is_empty_value(a) and is_empty_value(b):
        return True
    if isinstance(a, (list, dict)) or isinstance(b, (list, dict)):
        return a == b
    try:
        return bool(a == b)
    except (TypeError, ValueError):
        return False


def strip_ref(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip('"').strip("'").strip()
    return cleaned or None


def snapshot_inheritable(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Copy every inheritable column before running inheritance on ``df``."""
    return {field: df[field].copy() for field in INHERITABLE_FIELDS}


def inherited_changes_mask(
    df: pd.DataFrame,
    before: dict[str, pd.Series],
    log_prefix: str = "",
) -> tuple[pd.Series, dict[str, int]]:
    """Return (rows that gained data, per-field fill counts) after inheritance.

    Belt-and-braces: ``apply_inherited_data`` only fills empty cells, but if a
    previously populated value was altered it is restored here and logged.
    """
    changed = pd.Series(False, index=df.index)
    filled_counts: dict[str, int] = {}
    for field in INHERITABLE_FIELDS:
        before_empty = empty_mask(before[field])
        field_filled = before_empty & ~empty_mask(df[field])
        filled_counts[field] = int(field_filled.sum())
        changed |= field_filled

        populated = ~before_empty
        if populated.any():
            mismatch = populated & df[field].combine(
                before[field], lambda a, b: not values_equal(a, b)
            )
            mismatch_count = int(mismatch.sum())
            if mismatch_count:
                logger.warning(
                    "%s %d rows had non-empty %s altered by inheritance; restoring",
                    log_prefix, mismatch_count, field,
                )
                df.loc[mismatch, field] = before[field][mismatch]
    return changed, filled_counts


def _coerce_json(value: Any) -> Any:
    """Return a JSON-loadable Python value, or None for empty cells."""
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        return value.strip() or None
    return value


def _coerce_timestamp(value: Any) -> str | None:
    """Return a BigQuery TIMESTAMP-friendly string, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat(sep=" ")
    return None


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return bool(value)
    except (TypeError, ValueError):
        return None


def _coerce_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return str(value)


def _inherited_staging_schema() -> list[bigquery.SchemaField]:
    fields = [
        bigquery.SchemaField("dataset_url", "STRING"),
        bigquery.SchemaField("feed_id", "STRING"),
        bigquery.SchemaField("id", "STRING"),
    ]
    fields += [bigquery.SchemaField(c, "JSON") for c in INHERITABLE_JSON_COLUMNS]
    fields += [bigquery.SchemaField(c, "TIMESTAMP") for c in INHERITABLE_TIMESTAMP_COLUMNS]
    fields += [bigquery.SchemaField(c, "BOOLEAN") for c in INHERITABLE_BOOL_COLUMNS]
    fields += [bigquery.SchemaField(c, "STRING") for c in INHERITABLE_STRING_COLUMNS]
    return fields


def _empty_check_sql(col: str) -> str:
    """SQL predicate that is TRUE when the target column is 'missing'."""
    if col in INHERITABLE_JSON_COLUMNS:
        return f"(T.{col} IS NULL OR TO_JSON_STRING(T.{col}) IN ('{{}}', '[]', 'null'))"
    if col in INHERITABLE_TIMESTAMP_COLUMNS or col in INHERITABLE_BOOL_COLUMNS:
        return f"T.{col} IS NULL"
    return f"(T.{col} IS NULL OR T.{col} = '')"


def _build_inherited_merge(table_id: str, staging_table_id: str) -> str:
    """MERGE that fills only-when-empty and touches only the inheritable columns."""
    update_set = ",\n                ".join(
        f"T.{col} = IF({_empty_check_sql(col)}, S.{col}, T.{col})"
        for col in INHERITABLE_FIELDS
    )
    return f"""
        MERGE `{table_id}` AS T
        USING `{staging_table_id}` AS S
        ON  T.dataset_url = S.dataset_url
        AND T.feed_id = S.feed_id
        AND T.id = S.id
        WHEN MATCHED THEN
            UPDATE SET
                {update_set}
    """


def _build_inherited_staging_rows(updates_df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in updates_df.to_dict(orient="records"):
        row: dict[str, Any] = {
            "dataset_url": record.get("dataset_url"),
            "feed_id": record.get("feed_id"),
            "id": record.get("id"),
        }
        for col in INHERITABLE_JSON_COLUMNS:
            row[col] = _coerce_json(record.get(col))
        for col in INHERITABLE_TIMESTAMP_COLUMNS:
            row[col] = _coerce_timestamp(record.get(col))
        for col in INHERITABLE_BOOL_COLUMNS:
            row[col] = _coerce_bool(record.get(col))
        for col in INHERITABLE_STRING_COLUMNS:
            row[col] = _coerce_str(record.get(col))
        rows.append(row)
    return rows


def write_inherited_updates(
    client: bigquery.Client,
    table_id: str,
    dataset_url: str,
    updates_df: pd.DataFrame,
    label: str = "inheritance",
) -> int:
    """Upsert ONLY the inheritable columns for the given rows via a slim MERGE.

    Loads a staging table (merge keys + inheritable columns) and MERGEs with
    per-column fill-only-when-empty guards, so already-populated columns and the
    heavy ``json_data`` payload are never rewritten.  Returns rows affected.
    """
    if updates_df.empty:
        return 0

    staging_table_id = f"{table_id}_{label.replace('-', '_')}_staging_{uuid4().hex[:12]}"
    staging_rows = _build_inherited_staging_rows(updates_df)
    try:
        load_job = client.load_table_from_json(
            staging_rows,
            staging_table_id,
            job_config=bigquery.LoadJobConfig(
                schema=_inherited_staging_schema(),
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            ),
        )
        load_job.result()
        affected = run_dml_with_retry(
            client,
            _build_inherited_merge(table_id, staging_table_id),
            label=f"{label} MERGE {dataset_url}",
        )
        logger.info("Updated %d rows for %s", affected, dataset_url)
        return affected
    finally:
        client.delete_table(staging_table_id, not_found_ok=True)
