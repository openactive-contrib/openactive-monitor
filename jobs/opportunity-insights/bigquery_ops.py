"""BigQuery read/write operations for opportunity-insights.

Row-coercion helpers and staging+MERGE patterns are ported from
``jobs/ingest-opportunities/bigquery_ops.py``. The insights job writes to
several small tables (a few thousand rows max per run), so this module only
needs:

* ``ensure_tables()`` — idempotent CREATE from JSON schema files.
* ``load_feeds_metadata()``, ``run_query()`` — read helpers.
* ``upsert_feed_insights()`` — stage + MERGE on ``(run_date, feed_id)``.
* ``append_*()`` — load-job INSERTs for the append-only summary tables.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)

GCP_PROJECT = os.getenv("GCP_PROJECT_ID")
BQ_DATASET = os.getenv("BQ_DATASET_ID")

FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE", "feeds")
OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE", "opportunities")
OPPORTUNITY_INGESTION_TABLE = os.getenv("BQ_OPPORTUNITY_INGESTION_TABLE", "opportunity_ingestion")

FEED_INSIGHTS_TABLE = os.getenv("BQ_FEED_INSIGHTS_TABLE", "feed_insights")
INSIGHT_RUN_SUMMARY_TABLE = os.getenv("BQ_INSIGHT_RUN_SUMMARY_TABLE", "insight_run_summary")
INSIGHT_CATEGORY_COUNTS_TABLE = os.getenv("BQ_INSIGHT_CATEGORY_COUNTS_TABLE", "insight_category_counts")
INSIGHT_SPORT_DISCIPLINE_TABLE = os.getenv("BQ_INSIGHT_SPORT_DISCIPLINE_TABLE", "insight_sport_discipline")
INSIGHT_SPORT_DISCIPLINE_MASTER_TABLE = os.getenv(
    "BQ_INSIGHT_SPORT_DISCIPLINE_MASTER_TABLE", "insight_sport_discipline_master"
)
FEED_QUALITY_TABLE = os.getenv("BQ_FEED_QUALITY_TABLE", "feed_quality")

MERGE_RETRY_MAX_ATTEMPTS = 5
MERGE_RETRY_BASE_SECONDS = 5
MERGE_RETRY_MAX_SECONDS = 120

_SCHEMAS_DIR = Path(__file__).parent / "schemas"

# Clustering and partitioning config for each output table.
# Each entry: (schema_filename, clustering_cols, partition_field).
# partition_field is None for tables that should not be time-partitioned (e.g. current-state tables).
_TABLE_CONFIGS: dict[str, tuple[str, list[str], str | None]] = {
    FEED_INSIGHTS_TABLE:                   ("feed_insights.json",                  ["run_date", "dataset_url", "feed_id"], "run_date"),
    INSIGHT_RUN_SUMMARY_TABLE:             ("insight_run_summary.json",            ["run_date"],                            "run_date"),
    INSIGHT_CATEGORY_COUNTS_TABLE:         ("insight_category_counts.json",        ["run_date", "category", "scope"],       "run_date"),
    INSIGHT_SPORT_DISCIPLINE_TABLE:        ("insight_sport_discipline.json",       ["run_date", "is_matched"],              "run_date"),
    INSIGHT_SPORT_DISCIPLINE_MASTER_TABLE: ("insight_sport_discipline_master.json", ["run_date"],                            "run_date"),
    FEED_QUALITY_TABLE:                    ("feed_quality.json",                   ["dataset_url", "feed_id", "grade"],     None),
}

_FEED_INSIGHTS_MERGE_KEYS = ("run_date", "feed_id")


# ---------------------------------------------------------------------------
# Client / table id helpers
# ---------------------------------------------------------------------------

def _client() -> bigquery.Client:
    return bigquery.Client(project=GCP_PROJECT)


def table_id(table_name: str) -> str:
    return f"{GCP_PROJECT}.{BQ_DATASET}.{table_name}"


def _load_schema_json(filename: str) -> list[bigquery.SchemaField]:
    path = _SCHEMAS_DIR / filename
    with path.open() as f:
        raw = json.load(f)
    return [bigquery.SchemaField.from_api_repr(field) for field in raw]


# ---------------------------------------------------------------------------
# ensure_tables
# ---------------------------------------------------------------------------

def ensure_tables() -> None:
    """Create any missing output tables from the JSON schemas under ``schemas/``.

    Idempotent: existing tables are left untouched. Uses the configured
    ``partition_field`` (if any) and clustering list from ``_TABLE_CONFIGS``.
    """
    client = _client()
    for name, (schema_file, clustering, partition_field) in _TABLE_CONFIGS.items():
        full_id = table_id(name)
        try:
            client.get_table(full_id)
            logger.info("Table exists: %s", full_id)
            continue
        except google_exceptions.NotFound:
            pass

        schema = _load_schema_json(schema_file)
        table = bigquery.Table(full_id, schema=schema)
        if partition_field is not None:
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field,
            )
        table.clustering_fields = clustering
        client.create_table(table)
        logger.info(
            "Created table: %s (clustering=%s, partition=%s)",
            full_id, clustering, partition_field,
        )


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def run_query(sql: str) -> pd.DataFrame:
    logger.debug("Running BigQuery query:\n%s", sql)
    return _client().query(sql).to_dataframe()


# ---------------------------------------------------------------------------
# Row coercion (ported from ingest-opportunities/bigquery_ops.py)
# ---------------------------------------------------------------------------

def _is_missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (dict, list, tuple)):
        return False
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def _coerce_timestamp(value: Any) -> str | None:
    if _is_missing_value(value):
        return None
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc).isoformat()
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            return f"{raw} 00:00:00+00:00"
        return raw.replace("Z", "+00:00")
    return str(value)


def _coerce_json_value(value: Any) -> str | None:
    if _is_missing_value(value):
        return None
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, (datetime, date)):
        value = value.isoformat()
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            json.loads(raw)
            return raw
        except (TypeError, ValueError):
            return json.dumps(raw, ensure_ascii=True)
    return json.dumps(value, ensure_ascii=True, default=str)


def _normalize_scalar(value: Any, field: bigquery.SchemaField) -> Any:
    ft = field.field_type.upper()
    if _is_missing_value(value):
        return None
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if ft == "JSON":
        return _coerce_json_value(value)
    if ft == "TIMESTAMP":
        return _coerce_timestamp(value)
    if ft == "STRING":
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=True)
        return str(value)
    if ft in ("INTEGER", "INT64"):
        if isinstance(value, bool):
            return int(value)
        return int(value)
    if ft in ("FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"):
        return float(value)
    if ft in ("BOOLEAN", "BOOL"):
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "t", "yes", "y"}
        return bool(value)
    return value


def _prepare_rows(rows: list[dict[str, Any]], schema: list[bigquery.SchemaField]) -> list[dict[str, Any]]:
    """Coerce raw dicts to load-job-ready dicts; JSON fields become Python objects."""
    json_names = {f.name for f in schema if f.field_type.upper() == "JSON"}
    prepared: list[dict[str, Any]] = []
    for row in rows:
        out: dict[str, Any] = {}
        for field in schema:
            out[field.name] = _normalize_scalar(row.get(field.name), field)
        for name in json_names:
            val = out.get(name)
            if isinstance(val, str):
                try:
                    out[name] = json.loads(val)
                except (TypeError, ValueError):
                    pass
        prepared.append(out)
    return prepared


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def _load_job(rows: list[dict[str, Any]], destination: str, schema: list[bigquery.SchemaField], write_disposition: str) -> None:
    if not rows:
        logger.info("No rows to load into %s", destination)
        return
    config = bigquery.LoadJobConfig(schema=schema, write_disposition=write_disposition)
    client = _client()
    job = client.load_table_from_json(rows, destination, job_config=config)
    job.result()
    logger.info("Loaded %d rows into %s (disposition=%s)", len(rows), destination, write_disposition)


def _append_rows(table_name: str, rows: list[dict[str, Any]]) -> None:
    schema_file, _, _ = _TABLE_CONFIGS[table_name]
    schema = _load_schema_json(schema_file)
    prepared = _prepare_rows(rows, schema)
    _load_job(prepared, table_id(table_name), schema, bigquery.WriteDisposition.WRITE_APPEND)


def append_run_summary(row: dict[str, Any]) -> None:
    _append_rows(INSIGHT_RUN_SUMMARY_TABLE, [row])


def append_category_counts(rows: list[dict[str, Any]]) -> None:
    _append_rows(INSIGHT_CATEGORY_COUNTS_TABLE, rows)


def append_sport_discipline(rows: list[dict[str, Any]]) -> None:
    _append_rows(INSIGHT_SPORT_DISCIPLINE_TABLE, rows)


def append_sport_discipline_master(rows: list[dict[str, Any]]) -> None:
    _append_rows(INSIGHT_SPORT_DISCIPLINE_MASTER_TABLE, rows)


def write_feed_quality(rows: list[dict[str, Any]]) -> None:
    """Replace the entire ``feed_quality`` table with ``rows`` (WRITE_TRUNCATE).

    The quality table is a current-state view (one row per feed), so each run
    fully overwrites the previous contents. No staging / MERGE is needed.
    """
    schema_file, _, _ = _TABLE_CONFIGS[FEED_QUALITY_TABLE]
    schema = _load_schema_json(schema_file)
    prepared = _prepare_rows(rows, schema)
    _load_job(prepared, table_id(FEED_QUALITY_TABLE), schema, bigquery.WriteDisposition.WRITE_TRUNCATE)


def upsert_feed_insights(rows: list[dict[str, Any]]) -> None:
    """Upsert per-feed insight rows via stage + MERGE on ``(run_date, feed_id)``.

    Idempotent so a second run at the same ``run_date`` overwrites the first.
    """
    if not rows:
        logger.info("No feed_insights rows to write")
        return

    schema_file, _, _ = _TABLE_CONFIGS[FEED_INSIGHTS_TABLE]
    schema = _load_schema_json(schema_file)
    prepared = _prepare_rows(rows, schema)

    client = _client()
    main_id = table_id(FEED_INSIGHTS_TABLE)
    staging_id = f"{main_id}__stg_{uuid4().hex[:8]}"

    try:
        _load_job(prepared, staging_id, schema, bigquery.WriteDisposition.WRITE_TRUNCATE)
        _merge_feed_insights(client, main_id, staging_id)
    finally:
        try:
            client.delete_table(staging_id, not_found_ok=True)
        except Exception:
            logger.exception("Failed to drop staging table %s", staging_id)


def _merge_feed_insights(client: bigquery.Client, main_id: str, staging_id: str) -> None:
    schema_file, _, _ = _TABLE_CONFIGS[FEED_INSIGHTS_TABLE]
    schema = _load_schema_json(schema_file)
    all_cols = [f.name for f in schema]
    update_cols = [c for c in all_cols if c not in _FEED_INSIGHTS_MERGE_KEYS]

    on_clause = " AND ".join(f"S.{k} = T.{k}" for k in _FEED_INSIGHTS_MERGE_KEYS)
    update_set = ", ".join(f"T.{c} = S.{c}" for c in update_cols)
    insert_cols = ", ".join(all_cols)
    insert_vals = ", ".join(f"S.{c}" for c in all_cols)

    query = f"""
        MERGE `{main_id}` AS T
        USING `{staging_id}` AS S
        ON {on_clause}
        WHEN MATCHED THEN UPDATE SET {update_set}
        WHEN NOT MATCHED BY TARGET THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """

    last_error: Exception | None = None
    for attempt in range(1, MERGE_RETRY_MAX_ATTEMPTS + 1):
        try:
            client.query(query).result()
            logger.info("MERGE complete for %s (attempt %d)", main_id, attempt)
            return
        except google_exceptions.BadRequest as err:
            last_error = err
            msg = str(err).lower()
            if "could not serialize access" in msg and "concurrent update" in msg:
                delay = min(
                    MERGE_RETRY_MAX_SECONDS,
                    MERGE_RETRY_BASE_SECONDS * (2 ** (attempt - 1)),
                )
                logger.warning(
                    "MERGE concurrent-update error (attempt %d/%d); retrying in %ds",
                    attempt, MERGE_RETRY_MAX_ATTEMPTS, delay,
                )
                time.sleep(delay)
                continue
            raise
    assert last_error is not None
    raise last_error
