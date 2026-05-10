"""Fast, backfill-only writer for the BigQuery ``opportunities`` table.

The live ``ingest-opportunities`` job uses a staging table + MERGE upsert so
deltas are idempotent. For a one-shot backfill into a freshly TRUNCATEd table
that's pure overhead — we already deduplicate per-dataset on the merge keys
before loading, and the destination has no rows to merge against. So we bypass
``bigquery_ops.write_dataset_opportunities`` and load NDJSON directly with
``WRITE_APPEND``.

This module is intentionally self-contained inside ``backfill-from-pickles``
so the imported ``ingest-opportunities`` code stays untouched.
"""

from __future__ import annotations

import json
import logging
import math
import os
from datetime import date, datetime
from typing import Any
from uuid import uuid4

import pandas as pd
from google.cloud import bigquery

logger = logging.getLogger(__name__)

# One client + one cached schema per worker process. Populated lazily on first
# call so it works under both the parent process and ProcessPoolExecutor workers.
_CLIENT: bigquery.Client | None = None
_TABLE_ID: str | None = None
_SCHEMA: list[bigquery.SchemaField] | None = None
_JSON_COLS: set[str] = set()
_REPEATED_COLS: set[str] = set()
_RECORD_COLS: set[str] = set()
_TIMESTAMP_COLS: set[str] = set()
_DATE_COLS: set[str] = set()
_INTEGER_COLS: set[str] = set()


def _get_client_and_schema() -> tuple[bigquery.Client, str, list[bigquery.SchemaField]]:
    global _CLIENT, _TABLE_ID, _SCHEMA
    global _JSON_COLS, _REPEATED_COLS, _RECORD_COLS, _TIMESTAMP_COLS, _DATE_COLS, _INTEGER_COLS
    if _CLIENT is None or _SCHEMA is None or _TABLE_ID is None:
        project = os.environ["GCP_PROJECT_ID"]
        dataset = os.environ["BQ_DATASET_ID"]
        table = os.getenv("BQ_OPPORTUNITIES_TABLE", "opportunities")
        _TABLE_ID = f"{project}.{dataset}.{table}"
        _CLIENT = bigquery.Client(project=project)
        table_ref = _CLIENT.get_table(_TABLE_ID)
        _SCHEMA = list(table_ref.schema)
        _JSON_COLS = {f.name for f in _SCHEMA if f.field_type.upper() == "JSON"}
        _REPEATED_COLS = {f.name for f in _SCHEMA if f.mode == "REPEATED"}
        _RECORD_COLS = {f.name for f in _SCHEMA if f.field_type.upper() in ("RECORD", "STRUCT")}
        _TIMESTAMP_COLS = {f.name for f in _SCHEMA if f.field_type.upper() == "TIMESTAMP"}
        _DATE_COLS = {f.name for f in _SCHEMA if f.field_type.upper() == "DATE"}
        _INTEGER_COLS = {f.name for f in _SCHEMA if f.field_type.upper() in ("INTEGER", "INT64")}
        logger.info("Cached opportunities schema (%d fields) for backfill writer", len(_SCHEMA))
    return _CLIENT, _TABLE_ID, _SCHEMA


def _is_missing(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, float):
        return math.isnan(v)
    return False


def _coerce_integer(value: Any) -> int | None:
    """Coerce integer-like values and strip trailing .0 from float-like strings."""
    if _is_missing(value):
        return None

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        if value.is_integer():
            return int(value)
        logger.warning("Dropping non-integral float for INTEGER column: %r", value)
        return None

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None

        # Fast path for plain integer strings.
        if raw.lstrip("+-").isdigit():
            return int(raw)

        # Handle legacy float-like values such as "1747723419.0".
        try:
            as_float = float(raw)
        except ValueError:
            logger.warning("Dropping unparseable INTEGER value: %r", value)
            return None

        if not math.isfinite(as_float):
            return None
        if as_float.is_integer():
            return int(as_float)

        logger.warning("Dropping non-integral numeric string for INTEGER column: %r", value)
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("Dropping unparseable INTEGER value: %r", value)
        return None


def _coerce_value(col: str, value: Any) -> Any:
    """Coerce a single cell into something ``load_table_from_json`` accepts.

    Backfill data comes from ``processing.extract_rows``, which already produces
    clean Python types matching the schema, so this is intentionally minimal.
    """
    if _is_missing(value):
        return None

    if col in _JSON_COLS:
        # JSON BQ columns: pass dict/list straight through. If we got a JSON-encoded
        # string, decode it; if it's a plain string, wrap it as a JSON string literal
        # by passing the string itself (BQ JSON accepts scalar JSON values too).
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return None
            try:
                return json.loads(s)
            except (TypeError, ValueError):
                return s
        return value

    if col in _REPEATED_COLS:
        if isinstance(value, list):
            return [v for v in value if not _is_missing(v)]
        return [value]

    if col in _TIMESTAMP_COLS:
        if isinstance(value, datetime):
            return value.isoformat()
        return value  # already a string from extract_rows

    if col in _DATE_COLS:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return value

    if col in _INTEGER_COLS:
        return _coerce_integer(value)

    if col in _RECORD_COLS:
        if isinstance(value, dict):
            return value
        return None

    # STRING / scalar — keep as-is (extract_rows already gave us str/None).
    return value


def _df_to_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    records = df.to_dict(orient="records")
    for r in records:
        out: dict[str, Any] = {}
        for col, val in r.items():
            coerced = _coerce_value(str(col), val)
            if coerced is None:
                continue
            out[str(col)] = coerced
        rows.append(out)
    return rows


def _dedup_on_merge_keys(df: pd.DataFrame) -> pd.DataFrame:
    keys = [c for c in ("dataset_url", "feed_id", "id") if c in df.columns]
    if not keys:
        return df
    before = len(df)
    deduped = df.drop_duplicates(subset=keys, keep="last")
    dropped = before - len(deduped)
    if dropped:
        logger.warning("Dropped %d duplicate rows on merge keys before load", dropped)
    return deduped


def write_dataset_opportunities_append(dataset_url: str, df: pd.DataFrame) -> int:
    """Append ``df`` to the opportunities table via a single load job.

    Returns the number of rows written. Caller is responsible for ensuring the
    target table was TRUNCATEd before the backfill so this append-only path is
    safe (no duplicate keys vs pre-existing rows).
    """
    if df.empty:
        logger.info("Dataset %s — no rows to load", dataset_url)
        return 0

    df = _dedup_on_merge_keys(df)
    client, table_id, schema = _get_client_and_schema()

    rows = _df_to_rows(df)
    n_rows = len(rows)
    if n_rows == 0:
        return 0

    # Use a unique load_job id so we can spot/retry it server-side if needed.
    job_id_prefix = f"backfill_{uuid4().hex[:12]}_"
    load_cfg = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        # Ignore unknown values defensively (shouldn't happen, but cheap insurance).
        ignore_unknown_values=True,
    )

    logger.info("Dataset %s — loading %d rows to %s (WRITE_APPEND)", dataset_url, n_rows, table_id)
    job = client.load_table_from_json(
        rows, table_id, job_config=load_cfg, job_id_prefix=job_id_prefix,
    )
    job.result()
    logger.info("Dataset %s — loaded %d rows (job %s)", dataset_url, n_rows, job.job_id)
    return n_rows

