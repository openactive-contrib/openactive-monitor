import json
import logging
import os
import re
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE")
OPPORTUNITY_INGESTION_TABLE = os.getenv("BQ_OPPORTUNITY_INGESTION_TABLE")
OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

OPPORTUNITIES_COLUMNS = [
    "dataset_url",
    "feed_id",
    "id",
    "data_id",
    "kind",
    "modified",
    "json_data",
    "inherited_data",
    "activity",
    "location",
    "startDate",
    "endDate",
    "ageRange",
    "level",
    "has_superEvent",
    "has_subEvent",
]


def get_feeds(target_date: date | None = None, datasets: list[str] | None = None) -> dict[str, list[dict]]:
    """Fetch list of feeds collected for the given date from BigQuery."""
    if target_date is None:
        target_date = date.today()
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEEDS_TABLE}"

    query = f"""
        SELECT id, url, type, dataset_name, dataset_url
        FROM `{table_id}`
        WHERE DATE(last_access) = @target_date
        ORDER BY id
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("target_date", "DATE", target_date)
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    feeds: dict[str, list[dict]] = {}
    for row in rows:
        if datasets is None or row["dataset_url"] in datasets:
            if row["dataset_url"] not in feeds:
                feeds[row["dataset_url"]] = []
            dataset_feeds = feeds.get(row["dataset_url"])
            dataset_feeds.append(
                {
                    "id": row["id"],
                    "url": row["url"],
                    "type": row["type"],
                    "dataset_name": row["dataset_name"],
                }
            )
    return feeds


def get_last_ingestion_info(feed_id: str) -> tuple[str | None, str | None]:
    """Fetch the latest cursor values for the given feed from BigQuery."""
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITY_INGESTION_TABLE}"

    query = f"""
        SELECT afterTimestamp, afterId
        FROM `{table_id}`
        WHERE feed_id = @feed_id
        ORDER BY ingestion_date DESC
        LIMIT 1
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("feed_id", "STRING", feed_id)
        ]
    )

    rows = list(client.query(query, job_config=job_config).result())

    if not rows:
        return None, None

    row = rows[0]
    return row["afterTimestamp"], row["afterId"]


def get_dataset_opportunities(dataset_url: str) -> pd.DataFrame:
    """Fetch existing opportunities rows for a dataset_url from BigQuery."""
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    selected_columns = ", ".join(OPPORTUNITIES_COLUMNS)

    query = f"""
        SELECT {selected_columns}
        FROM `{table_id}`
        WHERE dataset_url = @dataset_url
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url)
        ]
    )

    dataset_df = client.query(query, job_config=job_config).to_dataframe()
    if dataset_df.empty:
        logger.debug(
            "Loaded %d existing opportunities from BigQuery for dataset %s",
            0,
            dataset_url,
        )
        return pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)

    normalized_df = dataset_df.reindex(columns=OPPORTUNITIES_COLUMNS)
    logger.debug(
        "Loaded %d existing opportunities from BigQuery for dataset %s",
        len(normalized_df),
        dataset_url,
    )
    return normalized_df


def delete_dataset_opportunities(delete_rows: list[dict[str, Any]]) -> int:
    """Delete opportunities rows by dataset_url + feed_id + id (ignores modified)."""
    if not delete_rows:
        logger.debug(
            "Deleted %d existing opportunities from BigQuery for dataset %s",
            0,
            "unknown",
        )
        return 0

    composite_keys: set[str] = set()
    dataset_urls: set[str] = set()
    for row in delete_rows:
        dataset_url = row.get("dataset_url")
        feed_id = row.get("feed_id")
        item_id = row.get("id")
        if not dataset_url or not feed_id or not item_id:
            continue
        dataset_urls.add(str(dataset_url))
        composite_keys.add(f"{dataset_url}|{feed_id}|{item_id}")

    if not composite_keys:
        dataset_for_log = next(iter(dataset_urls), "unknown")
        logger.debug(
            "Deleted %d existing opportunities from BigQuery for dataset %s",
            0,
            dataset_for_log,
        )
        return 0

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    query = f"""
        DELETE FROM `{table_id}`
        WHERE CONCAT(IFNULL(dataset_url, ''), '|', IFNULL(feed_id, ''), '|', IFNULL(id, '')) IN UNNEST(@composite_keys)
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    total_deleted = 0
    batch_size = 1000
    sorted_keys = sorted(composite_keys)

    for start in range(0, len(sorted_keys), batch_size):
        batch_keys = sorted_keys[start:start + batch_size]
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ArrayQueryParameter("composite_keys", "STRING", batch_keys)
            ]
        )
        job = client.query(query, job_config=job_config)
        job.result()
        total_deleted += int(job.num_dml_affected_rows or 0)

    dataset_for_log = next(iter(dataset_urls), "unknown")
    logger.debug(
        "Deleted %d existing opportunities from BigQuery for dataset %s",
        total_deleted,
        dataset_for_log,
    )

    return total_deleted


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


def _coerce_date(value: Any) -> str | None:
    if _is_missing_value(value):
        return None

    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if "T" in raw:
            return raw.split("T", 1)[0]
        if " " in raw:
            return raw.split(" ", 1)[0]
        return raw

    return str(value)


def _coerce_record(value: Any, fields: tuple[bigquery.SchemaField, ...]) -> dict[str, Any] | None:
    if _is_missing_value(value):
        return None

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return None

    if isinstance(value, list):
        dict_items = [item for item in value if isinstance(item, dict)]
        value = dict_items[0] if dict_items else None

    if not isinstance(value, dict):
        return None

    prepared: dict[str, Any] = {}
    for field in fields:
        prepared[field.name] = _normalize_for_bigquery(value.get(field.name), field)
    return prepared


def _coerce_json_value(value: Any) -> str | None:
    """Return a valid JSON literal string for BigQuery JSON columns."""
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
        # Already a JSON literal (object/array/quoted string/number/bool/null)
        try:
            json.loads(raw)
            return raw
        except (TypeError, ValueError):
            # Plain string -> encode as JSON string literal
            return json.dumps(raw, ensure_ascii=True)

    return json.dumps(value, ensure_ascii=True, default=str)


def _normalize_scalar(value: Any, field: bigquery.SchemaField) -> Any:
    field_type = field.field_type.upper()

    if _is_missing_value(value):
        return None

    if isinstance(value, tuple):
        value = list(value)

    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()

    if field_type in ("RECORD", "STRUCT"):
        return _coerce_record(value, field.fields)

    if field_type == "JSON":
        return _coerce_json_value(value)

    if field_type == "TIMESTAMP":
        return _coerce_timestamp(value)

    if field_type == "DATE":
        return _coerce_date(value)

    if field_type in ("STRING", "GEOGRAPHY"):
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=True)
        return str(value)

    if field_type in ("INTEGER", "INT64"):
        if isinstance(value, bool):
            return int(value)
        return int(value)

    if field_type in ("FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"):
        return float(value)

    if field_type in ("BOOLEAN", "BOOL"):
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "t", "yes", "y"}
        return bool(value)

    return value


def _normalize_for_bigquery(value: Any, field: bigquery.SchemaField) -> Any:
    if field.mode == "REPEATED":
        if _is_missing_value(value):
            return []
        values = value if isinstance(value, list) else [value]
        normalized = [_normalize_scalar(item, bigquery.SchemaField(field.name, field.field_type, mode="NULLABLE", fields=field.fields)) for item in values]
        return [item for item in normalized if not _is_missing_value(item)]

    if isinstance(value, list):
        if field.field_type.upper() in ("STRING", "GEOGRAPHY"):
            value = json.dumps(value, ensure_ascii=True)
        elif field.field_type.upper() == "JSON":
            # Keep full list for JSON fields.
            pass
        elif field.field_type.upper() in ("RECORD", "STRUCT"):
            dict_items = [item for item in value if isinstance(item, dict)]
            value = dict_items[0] if dict_items else None
        else:
            value = value[0] if value else None

    return _normalize_scalar(value, field)


def _prepare_row_for_bigquery(raw_row: dict[str, Any], schema_fields: list[bigquery.SchemaField]) -> dict[str, Any]:
    prepared: dict[str, Any] = {}
    for field in schema_fields:
        prepared[field.name] = _normalize_for_bigquery(raw_row.get(field.name), field)
    return prepared


def _row_identifiers(row: dict[str, Any]) -> str:
    keys = ("id", "data_id", "feed_id", "dataset_url", "dataset_id", "kind")
    parts = [f"{key}={row.get(key)}" for key in keys if row.get(key) not in (None, "")]
    return ", ".join(parts) if parts else "no-ids"


def _prettify_insert_errors(errors: list[dict[str, Any]], batch_rows: list[dict[str, Any]], batch_start: int) -> str:
    lines: list[str] = []
    for entry in errors:
        local_index = int(entry.get("index", -1))
        global_index = batch_start + local_index if local_index >= 0 else -1
        row = batch_rows[local_index] if 0 <= local_index < len(batch_rows) else {}
        ids = _row_identifiers(row)

        for err in entry.get("errors", []):
            location = err.get("location", "unknown")
            message = err.get("message", "Unknown BigQuery insert error")
            reason = err.get("reason", "unknown")
            lines.append(f"- row={global_index} ({ids}) field={location} reason={reason}: {message}")

    return "\n".join(lines)


def write_dataset_opportunities(dataset_url: str, dataset_df: pd.DataFrame) -> None:
    """Append dataset rows to the opportunities BigQuery table."""
    if dataset_df.empty:
        logger.info("No rows to write to opportunities table for dataset %s", dataset_url)
        return

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    table = client.get_table(table_id)
    logger.debug(
        "Detected opportunities schema: %s",
        {field.name: f"{field.field_type}/{field.mode}" for field in table.schema},
    )

    raw_rows = dataset_df.to_dict(orient="records")
    prepared_rows = [
        _prepare_row_for_bigquery({str(k): v for k, v in row.items()}, list(table.schema))
        for row in raw_rows
    ]

    batch_size = 500
    pretty_errors: list[str] = []

    for batch_start in range(0, len(prepared_rows), batch_size):
        batch = prepared_rows[batch_start:batch_start + batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            pretty_errors.append(_prettify_insert_errors(errors, batch, batch_start))

    if pretty_errors:
        pretty_message = "\n".join(pretty_errors)
        logger.error("Failed writing opportunities for dataset %s into %s:\n%s", dataset_url, table_id, pretty_message)
        raise RuntimeError(f"BigQuery write failed for dataset {dataset_url} into {table_id}. Details:\n{pretty_message}")

    logger.info("Inserted %d opportunities rows into %s", len(prepared_rows), table_id)


def write_opportunity_ingestion_records(records: list[dict[str, Any]]) -> None:
    """Append ingestion summary records to the opportunity_ingestion table."""
    if not records:
        logger.info("No ingestion summary rows to write.")
        return

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITY_INGESTION_TABLE}"
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    table = client.get_table(table_id)
    logger.debug(
        "Detected ingestion schema: %s",
        {field.name: f"{field.field_type}/{field.mode}" for field in table.schema},
    )

    prepared_rows = [
        _prepare_row_for_bigquery({str(k): v for k, v in row.items()}, list(table.schema))
        for row in records
    ]

    batch_size = 500
    pretty_errors: list[str] = []

    for batch_start in range(0, len(prepared_rows), batch_size):
        batch = prepared_rows[batch_start:batch_start + batch_size]
        errors = client.insert_rows_json(table_id, batch)
        if errors:
            pretty_errors.append(_prettify_insert_errors(errors, batch, batch_start))

    if pretty_errors:
        pretty_message = "\n".join(pretty_errors)
        logger.error("Failed writing opportunity ingestion rows into %s:\n%s", table_id, pretty_message)
        raise RuntimeError(f"BigQuery ingestion-summary write failed for {table_id}. Details:\n{pretty_message}")

    logger.info("Inserted %d rows into %s", len(prepared_rows), table_id)
