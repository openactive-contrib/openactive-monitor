import gc
import json
import logging
import os
import re
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery

# TODO reduce this to 200 on prod
DELETE_BATCH_SIZE = 50000

load_dotenv()

logger = logging.getLogger(__name__)

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE")
FEED_INGESTION_TABLE = os.getenv("BQ_FEED_INGESTION_TABLE")
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
    "facility",
    "location",
    "district_name",
    "region_name",
    "publisher_name",
    "district_code",
    "region_code",
    "country_code",
    "country_name",
    "nhstrust_name",
    "nhstrust_code",
    "startDate",
    "endDate",
    "ageRange",
    "level",
    "has_superEvent",
    "has_subEvent",
    "accessibilitySupport",
    "genderRestriction",
    "organization_name",
    "organization_json",
    "last_updated",
]

# Columns typed JSON in the opportunities BigQuery table.  ``to_dataframe()``
# returns these as raw JSON strings; downstream processing (especially
# ``processing.denormalize_dataset``) expects real Python dicts/lists, so the
# read helpers below parse them on the way in.
OPPORTUNITIES_JSON_COLUMNS = frozenset({
    "json_data",
    "inherited_data",
    "activity",
    "facility",
    "location",
    "ageRange",
    "level",
    "has_superEvent",
    "has_subEvent",
    "accessibilitySupport",
    "organization_json",
})


def _safe_json_load(value: Any) -> Any:
    if value is None or not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def parse_opportunities_json_columns(df: pd.DataFrame) -> pd.DataFrame:
    """In-place: turn raw JSON-string columns into Python objects.

    Reusable wrapper so callers that don't go through ``get_dataset_opportunities``
    (e.g. one-off migration scripts) get the same parsing semantics.
    """
    for col in df.columns:
        if col in OPPORTUNITIES_JSON_COLUMNS:
            df[col] = df[col].apply(_safe_json_load)
    return df

DEFAULT_DELETE_RETRY_BASE_SECONDS = 10
DEFAULT_DELETE_RETRY_MAX_SECONDS = 15 * 60
DATA_ID_QUERY_BATCH_SIZE = 2000

# Ingestion record insertion retry configuration
INGESTION_INSERT_RETRY_MAX_ATTEMPTS = 3
INGESTION_INSERT_RETRY_BASE_SECONDS = 2
INGESTION_INSERT_BATCH_SIZE = 500

# opportunities staging merge retry configuration
MERGE_RETRY_MAX_ATTEMPTS = 5
MERGE_RETRY_BASE_SECONDS = 5
MERGE_RETRY_MAX_SECONDS = 120

# Columns used to match existing rows for MERGE upserts.
_OPPORTUNITY_MERGE_KEYS = ("dataset_url", "feed_id", "id")
_OPPORTUNITY_UPDATE_COLS = tuple(c for c in OPPORTUNITIES_COLUMNS if c not in _OPPORTUNITY_MERGE_KEYS)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _build_composite_key(dataset_url: str, feed_id: str, item_id: str) -> str:
    return f"{dataset_url}|{feed_id}|{item_id}"


def _parse_composite_key(composite_key: str) -> tuple[str, str, str] | None:
    parts = composite_key.split("|", 2)
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def retry_delay_seconds(retry_count: int, base_delay_seconds: int, max_delay_seconds: int) -> int:
    exponent = max(retry_count - 1, 0)
    return min(max_delay_seconds, base_delay_seconds * (2 ** exponent))


def _upsert_pending_delete(
    pending_deletes: dict[str, dict[str, Any]],
    composite_key: str,
    now: datetime,
    base_delay_seconds: int,
    max_delay_seconds: int,
) -> None:
    parsed = _parse_composite_key(composite_key)
    if parsed is None:
        return

    dataset_url, feed_id, item_id = parsed
    existing = pending_deletes.get(composite_key)
    retry_count = int(existing.get("retry_count", 0) + 1) if existing else 1
    first_seen = existing.get("first_seen") if existing else now
    delay_seconds = retry_delay_seconds(retry_count, base_delay_seconds, max_delay_seconds)
    next_retry_at = now + timedelta(seconds=delay_seconds)

    pending_deletes[composite_key] = {
        "dataset_url": dataset_url,
        "feed_id": feed_id,
        "id": item_id,
        "first_seen": first_seen,
        "retry_count": retry_count,
        "next_retry_at": next_retry_at,
    }


def _get_latest_ingestion_date() -> date:
    """Return the date portion of the most recent ingestion_date in the opportunity ingestion table."""
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEED_INGESTION_TABLE}"
    query = f"SELECT MAX(ingestion_date) AS latest FROM `{table_id}`"
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    rows = list(client.query(query).result())
    latest = rows[0]["latest"] if rows else None
    if latest is None:
        return date.today()
    if isinstance(latest, datetime):
        return latest.date()
    if isinstance(latest, date):
        return latest
    return date.today()


def get_feeds(datasets: list[str] | None = None) -> dict[str, list[dict]]:
    """Fetch list of feeds collected for the latest ingestion date from BigQuery."""
    target_date = _get_latest_ingestion_date()
    logger.info("Using latest ingestion date as feed target date: %s", target_date)
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEEDS_TABLE}"

    query = f"""
        SELECT id, url, type, dataset_name, dataset_url, publisher_name, provider
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
                    "publisher_name": row["publisher_name"],
                    "provider": row["provider"],
                }
            )
    return feeds


def get_last_ingestion_info(feed_id: str) -> tuple[str | None, str | None, int | None]:
    """Fetch the latest cursor values for the given feed from BigQuery."""
    return get_last_ingestion_info_batch([feed_id]).get(feed_id, (None, None, None))


def get_last_ingestion_info_batch(feed_ids: list[str]) -> dict[str, tuple[str | None, str | None, int | None]]:
    """Fetch latest cursor values for multiple feed IDs in one BigQuery query."""
    if not feed_ids:
        return {}

    unique_feed_ids = list(dict.fromkeys(feed_ids))
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITY_INGESTION_TABLE}"

    query = f"""
        SELECT feed_id, afterTimestamp, afterId, afterChangeNumber
        FROM `{table_id}`
        WHERE feed_id IN UNNEST(@feed_ids)
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY feed_id
            ORDER BY ingestion_date DESC, afterChangeNumber DESC, afterTimestamp DESC, afterId DESC
        ) = 1
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("feed_ids", "STRING", unique_feed_ids)
        ]
    )

    rows = client.query(query, job_config=job_config).result()
    cursor_by_feed_id: dict[str, tuple[str | None, str | None, int | None]] = {
        feed_id: (None, None, None) for feed_id in unique_feed_ids
    }
    for row in rows:
        row_feed_id = row["feed_id"]
        cursor_by_feed_id[row_feed_id] = (
            row["afterTimestamp"],
            row["afterId"],
            row["afterChangeNumber"],
        )

    return cursor_by_feed_id


def get_dataset_opportunities(
    dataset_url: str,
    required_data_ids: list[str] | None = None,
    fallback_to_full_scan: bool = True,
) -> pd.DataFrame:
    """Fetch existing opportunities rows for a dataset_url from BigQuery.

    If required_data_ids is provided, only matching data_id rows are fetched.
    """
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    selected_columns = ", ".join(OPPORTUNITIES_COLUMNS)

    target_ids = _normalize_required_data_ids(required_data_ids)
    if required_data_ids is not None and not target_ids:
        logger.debug(
            "Loaded %d existing opportunities from BigQuery for dataset %s (targeted by %d ids)",
            0,
            dataset_url,
            0,
        )
        return pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    try:
        if target_ids is None:
            query = f"""
                SELECT {selected_columns}
                FROM `{table_id}`
                WHERE dataset_url = @dataset_url
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url)
                ]
            )
            dataset_df = client.query(query, job_config=job_config).to_dataframe()
        else:
            query = f"""
                SELECT {selected_columns}
                FROM `{table_id}`
                WHERE dataset_url = @dataset_url
                  AND data_id IN UNNEST(@data_ids)
            """
            chunk_frames: list[pd.DataFrame] = []
            for start in range(0, len(target_ids), DATA_ID_QUERY_BATCH_SIZE):
                chunk_ids = target_ids[start:start + DATA_ID_QUERY_BATCH_SIZE]
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url),
                        bigquery.ArrayQueryParameter("data_ids", "STRING", chunk_ids),
                    ]
                )
                chunk_df = client.query(query, job_config=job_config).to_dataframe()
                if not chunk_df.empty:
                    chunk_frames.append(chunk_df)

            if not chunk_frames:
                dataset_df = pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)
            elif len(chunk_frames) == 1:
                dataset_df = chunk_frames[0]
            else:
                dataset_df = pd.concat(chunk_frames, ignore_index=True)
    except Exception:
        if target_ids is not None and fallback_to_full_scan:
            logger.exception(
                "Targeted opportunities fetch failed for dataset %s; falling back to full dataset fetch",
                dataset_url,
            )
            return get_dataset_opportunities(
                dataset_url,
                required_data_ids=None,
                fallback_to_full_scan=False,
            )
        raise

    if dataset_df.empty:
        if target_ids is None:
            logger.debug(
                "Loaded %d existing opportunities from BigQuery for dataset %s",
                0,
                dataset_url,
            )
        else:
            logger.debug(
                "Loaded %d existing opportunities from BigQuery for dataset %s (targeted by %d ids)",
                0,
                dataset_url,
                len(target_ids),
            )
        return pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)

    # BigQuery JSON columns arrive as raw JSON strings from ``to_dataframe()``;
    # parse them so callers (denormalize_dataset etc.) see real Python objects.
    parse_opportunities_json_columns(dataset_df)
    normalized_df = dataset_df.reindex(columns=OPPORTUNITIES_COLUMNS)
    if target_ids is None:
        logger.debug(
            "Loaded %d existing opportunities from BigQuery for dataset %s",
            len(normalized_df),
            dataset_url,
        )
    else:
        logger.debug(
            "Loaded %d existing opportunities from BigQuery for dataset %s (targeted by %d ids)",
            len(normalized_df),
            dataset_url,
            len(target_ids),
        )
    return normalized_df


def get_dataset_facility_uses(dataset_url: str) -> pd.DataFrame:
    """Fetch all ``kind='FacilityUse'`` rows for a dataset_url from BigQuery.

    FacilityUse rows can embed their ``IndividualFacilityUse`` children inline
    (``json_data.individualFacilityUse``).  When a Slot's ``facilityUse``
    reference points at one of those nested IFU ``@id``s, the parent FacilityUse
    is needed for inheritance but is never returned by the ``data_id``-keyed
    ``get_dataset_opportunities`` (the nested IFU ``@id`` is not any row's
    ``data_id``).  FacilityUse rows are few per dataset, so loading them all is
    cheap and avoids any assumption about the IFU URL structure.
    """
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    selected_columns = ", ".join(OPPORTUNITIES_COLUMNS)
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    query = f"""
        SELECT {selected_columns}
        FROM `{table_id}`
        WHERE dataset_url = @dataset_url
          AND kind = 'FacilityUse'
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url)
        ]
    )
    dataset_df = client.query(query, job_config=job_config).to_dataframe()
    if dataset_df.empty:
        return pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)
    # JSON columns arrive as raw JSON strings from ``to_dataframe()``; parse them
    # so denormalize_dataset sees real Python dicts/lists.
    parse_opportunities_json_columns(dataset_df)
    return dataset_df.reindex(columns=OPPORTUNITIES_COLUMNS)


def _normalize_required_data_ids(required_data_ids: list[str] | None) -> list[str] | None:
    if required_data_ids is None:
        return None

    normalized: list[str] = []
    seen: set[str] = set()
    for item in required_data_ids:
        if not isinstance(item, str):
            continue
        value = item.strip("\"").strip("'").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def delete_dataset_opportunities(
    delete_rows: list[dict[str, Any]],
    pending_deletes: dict[str, dict[str, Any]] | None = None,
    now: datetime | None = None,
    base_delay_seconds: int = DEFAULT_DELETE_RETRY_BASE_SECONDS,
    max_delay_seconds: int = DEFAULT_DELETE_RETRY_MAX_SECONDS,
) -> int:
    """Delete opportunities rows by dataset_url + feed_id + id (ignores modified)."""
    if pending_deletes is None:
        pending_deletes = {}
    if now is None:
        now = _utc_now()

    if not delete_rows:
        logger.info(
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
        composite_keys.add(_build_composite_key(str(dataset_url), str(feed_id), str(item_id)))

    if not composite_keys:
        dataset_for_log = next(iter(dataset_urls), "unknown")
        logger.info(
            "Deleted %d existing opportunities from BigQuery for dataset %s (with %s pending deletes)",
            0,
            dataset_for_log,
            len(pending_deletes),
        )
        return 0

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    query = f"""
        DELETE FROM `{table_id}`
        WHERE CONCAT(IFNULL(dataset_url, ''), '|', IFNULL(feed_id, ''), '|', IFNULL(id, '')) IN UNNEST(@composite_keys)
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    total_deleted = 0
    deferred_keys: set[str] = set()
    batch_size = DELETE_BATCH_SIZE
    sorted_keys = sorted(composite_keys)

    for start in range(0, len(sorted_keys), batch_size):
        logger.debug("Processing batch delete %d of %d", len(sorted_keys), batch_size)
        batch_keys = sorted_keys[start:start + batch_size]
        deleted_count, deferred_count = _delete_batch_with_streaming_buffer_fallback(
            client,
            query,
            batch_keys,
        )
        total_deleted += deleted_count
        deferred_keys.update(deferred_count)

    attempted_keys = set(sorted_keys)
    resolved_keys = attempted_keys - deferred_keys
    for resolved_key in resolved_keys:
        pending_deletes.pop(resolved_key, None)

    for deferred_key in deferred_keys:
        _upsert_pending_delete(
            pending_deletes,
            deferred_key,
            now,
            base_delay_seconds,
            max_delay_seconds,
        )

    dataset_for_log = next(iter(dataset_urls), "unknown")
    logger.info(
        "Deleted %d existing opportunities from BigQuery for dataset %s (with %s pending deletes)",
        total_deleted,
        dataset_for_log,
        len(pending_deletes),
    )
    if deferred_keys:
        logger.warning(
            "Deferred %d deletes for dataset %s because matching rows are in BigQuery streaming buffer",
            len(deferred_keys),
            dataset_for_log,
        )

    return total_deleted


def is_streaming_buffer_dml_error(exc: Exception) -> bool:
    if not isinstance(exc, google_exceptions.BadRequest):
        return False

    message = str(exc).lower()
    return "update or delete statement" in message and "streaming buffer" in message


def _delete_batch_with_streaming_buffer_fallback(
    client: bigquery.Client,
    query: str,
    composite_keys: list[str],
) -> tuple[int, set[str]]:
    """
    Delete keys in one batch.
    If BigQuery reports streaming-buffer conflicts, split recursively to isolate
    blocked keys and delete everything else now.
    Returns: (deleted_count, deferred_keys)
    """
    if not composite_keys:
        return 0, set()

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("composite_keys", "STRING", composite_keys)
        ]
    )

    try:
        job = client.query(query, job_config=job_config)
        job.result()
        return int(job.num_dml_affected_rows or 0), set()
    except Exception as exc:
        if not is_streaming_buffer_dml_error(exc):
            raise

        logger.debug(
            "Deferring entire delete batch (%d keys) due to streaming buffer conflict",
            len(composite_keys),
        )
        return 0, set(composite_keys)


def retry_deferred_deletes(
    pending_deletes: dict[str, dict[str, Any]],
    now: datetime | None = None,
    base_delay_seconds: int = DEFAULT_DELETE_RETRY_BASE_SECONDS,
    max_delay_seconds: int = DEFAULT_DELETE_RETRY_MAX_SECONDS,
) -> int:
    """
    Retry due deferred deletes and update pending_deletes in place. To overcome BQ streaming buffer issue.
    """
    if now is None:
        now = _utc_now()

    due_rows: list[dict[str, Any]] = []
    for composite_key, metadata in pending_deletes.items():
        next_retry_at = metadata.get("next_retry_at")
        if isinstance(next_retry_at, datetime) and next_retry_at > now:
            continue

        parsed = _parse_composite_key(composite_key)
        if parsed is None:
            continue
        dataset_url, feed_id, item_id = parsed
        due_rows.append({"dataset_url": dataset_url, "feed_id": feed_id, "id": item_id})

    if not due_rows:
        return 0

    logger.info("Retrying %d deferred deletes", len(due_rows))
    return delete_dataset_opportunities(
        due_rows,
        pending_deletes=pending_deletes,
        now=now,
        base_delay_seconds=base_delay_seconds,
        max_delay_seconds=max_delay_seconds,
    )


def drain_deferred_deletes_until_timeout(
    pending_deletes: dict[str, dict[str, Any]],
    max_total_wait_seconds: int = 90 * 60,
    base_delay_seconds: int = DEFAULT_DELETE_RETRY_BASE_SECONDS,
    max_delay_seconds: int = DEFAULT_DELETE_RETRY_MAX_SECONDS,
) -> None:
    """
    Keep retrying deferred deletes with exponential backoff up to timeout.
    """
    if not pending_deletes:
        return

    deadline = time.monotonic() + max_total_wait_seconds

    while pending_deletes and time.monotonic() < deadline:
        now = _utc_now()
        retry_deferred_deletes(
            pending_deletes,
            now=now,
            base_delay_seconds=base_delay_seconds,
            max_delay_seconds=max_delay_seconds,
        )

        if not pending_deletes:
            break

        next_due_candidates = [
            meta.get("next_retry_at")
            for meta in pending_deletes.values()
            if isinstance(meta.get("next_retry_at"), datetime)
        ]

        if not next_due_candidates:
            wait_seconds = 1
        else:
            next_due = min(next_due_candidates)
            wait_seconds = max(1.0, (next_due - _utc_now()).total_seconds())

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break

        sleep_seconds = min(wait_seconds, remaining)
        logger.info(
            "Pending deferred deletes=%d; waiting %.1f seconds before next retry",
            len(pending_deletes),
            sleep_seconds,
        )
        time.sleep(sleep_seconds)

    if pending_deletes:
        logger.error(
            "Deferred deletes still pending after %.0f minutes: %d",
            max_total_wait_seconds / 60,
            len(pending_deletes),
        )


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
        candidate = raw.replace("Z", "+00:00")
        # Validate the string actually parses as a timestamp; some legacy data
        # contains malformed values like "T00:00:00" (no date) which BigQuery
        # rejects on load. Drop those rather than failing the whole batch.
        try:
            parsed = pd.to_datetime(candidate, utc=True, errors="raise")
        except Exception:
            logger.warning("Dropping unparseable timestamp value: %r", value)
            return None
        if pd.isna(parsed):
            logger.warning("Dropping unparseable timestamp value: %r", value)
            return None
        return parsed.isoformat()

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


def _build_upsert_merge_query(main_table_id: str, staging_table_id: str) -> str:
    """
    Build a BigQuery MERGE statement that upserts rows from the staging table into the main table.
    Matching is done on (dataset_url, feed_id, id)
    """
    on_clause = (
        "S.dataset_url = T.dataset_url"
        " AND S.feed_id = T.feed_id"
        " AND S.id = T.id"
    )
    update_set = ", ".join(f"T.{col} = S.{col}" for col in _OPPORTUNITY_UPDATE_COLS)
    insert_cols = ", ".join(OPPORTUNITIES_COLUMNS)
    insert_vals = ", ".join(f"S.{col}" for col in OPPORTUNITIES_COLUMNS)
    return f"""
        MERGE `{main_table_id}` AS T
        USING `{staging_table_id}` AS S
        ON {on_clause}
        WHEN MATCHED THEN
            UPDATE SET {update_set}
        WHEN NOT MATCHED BY TARGET THEN
            INSERT ({insert_cols}) VALUES ({insert_vals})
    """


def _unwrap_json_fields_for_load(
    rows: list[dict[str, Any]],
    schema_fields: list[bigquery.SchemaField],
) -> list[dict[str, Any]]:
    """
    `_prepare_row_for_bigquery` serialises BigQuery JSON-type columns to strings (suitable for
    insert_rows_json).  `load_table_from_json` expects the actual Python object for JSON-type
    columns, otherwise the value is stored as a JSON string literal.  This function reverses that
    coercion for JSON-typed fields only.
    """
    json_col_names = {f.name for f in schema_fields if f.field_type.upper() == "JSON"}
    if not json_col_names:
        return rows

    result: list[dict[str, Any]] = []
    for row in rows:
        new_row = dict(row)
        for col in json_col_names:
            val = new_row.get(col)
            if isinstance(val, str):
                try:
                    new_row[col] = json.loads(val)
                except (TypeError, ValueError):
                    pass  # keep the original string if it is not valid JSON
        result.append(new_row)
    return result


def _dedup_on_merge_keys(dataset_df: pd.DataFrame, dataset_url: str) -> pd.DataFrame:
    """
    Drop rows with duplicate MERGE keys, keeping the last occurrence.

    Guards against malformed RPDE feeds (e.g. a self-loop that returns the same items
    on multiple pages) which would otherwise cause BigQuery MERGE to fail with
    "UPDATE/MERGE must match at most one source row for each target row".
    """
    merge_key_cols = [c for c in _OPPORTUNITY_MERGE_KEYS if c in dataset_df.columns]
    deduped = dataset_df.drop_duplicates(subset=merge_key_cols, keep="last")
    dropped = len(dataset_df) - len(deduped)
    if dropped:
        logger.warning(
            "Dropped %d duplicate rows (on merge keys %s) before staging for dataset %s",
            dropped,
            merge_key_cols,
            dataset_url,
        )
    return deduped


def _prepare_rows_for_staging(
    dataset_df: pd.DataFrame,
    schema_fields: list[bigquery.SchemaField],
) -> list[dict[str, Any]]:
    """
    Coerce DataFrame rows into dicts ready for ``load_table_from_json``.

    ``_prepare_row_for_bigquery`` serialises JSON-typed columns to strings, but
    ``load_table_from_json`` expects real Python objects for those columns, so the
    string coercion is reversed here.
    """
    json_col_names = {f.name for f in schema_fields if f.field_type.upper() == "JSON"}
    prepared_rows: list[dict[str, Any]] = []
    for row in dataset_df.to_dict(orient="records"):
        prepared = _prepare_row_for_bigquery({str(k): v for k, v in row.items()}, schema_fields)
        for col in json_col_names:
            val = prepared.get(col)
            if isinstance(val, str):
                try:
                    prepared[col] = json.loads(val)
                except (TypeError, ValueError):
                    pass  # keep the original string if it is not valid JSON
        prepared_rows.append(prepared)
    return prepared_rows


def _load_staging_table(
    client: bigquery.Client,
    prepared_rows: list[dict[str, Any]],
    staging_table_id: str,
    table_schema: list[bigquery.SchemaField],
    dataset_url: str,
) -> None:
    """Load prepared rows into a staging table via a load job so they are immediately DML-queryable."""
    load_job_config = bigquery.LoadJobConfig(
        schema=table_schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    load_job = client.load_table_from_json(
        prepared_rows, staging_table_id, job_config=load_job_config
    )
    load_job.result()
    logger.info(
        "Staged %d rows in %s for dataset %s",
        len(prepared_rows),
        staging_table_id,
        dataset_url,
    )


def _merge_staging_to_main(
        client: bigquery.Client,
        table_id: str,
        staging_table_id: str,
        dataset_url: str,
        max_attempts: int = MERGE_RETRY_MAX_ATTEMPTS,
        base_delay_seconds: int = MERGE_RETRY_BASE_SECONDS,
        max_delay_seconds: int = MERGE_RETRY_MAX_SECONDS,
) -> None:
    """Run the MERGE statement that upserts rows from the staging table into the main table.

    Retries on concurrent update errors with exponential backoff.
    """
    merge_query = _build_upsert_merge_query(table_id, staging_table_id)

    for attempt in range(max_attempts):
        try:
            merge_job = client.query(merge_query)
            merge_job.result()
            logger.info(
                "Upserted %d rows into %s for dataset %s (inserted+updated)",
                merge_job.num_dml_affected_rows or 0,
                table_id,
                dataset_url,
            )
            return
        except Exception as exc:
            if not is_concurrent_update_error(exc):
                raise

            if attempt >= max_attempts - 1:
                logger.error(
                    "MERGE failed after %d attempts due to concurrent updates for dataset %s",
                    max_attempts,
                    dataset_url,
                )
                raise

            delay = retry_delay_seconds(attempt, base_delay_seconds, max_delay_seconds)
            logger.warning(
                "Concurrent update on MERGE attempt %d/%d for dataset %s; retrying in %d seconds",
                attempt + 1,
                max_attempts,
                dataset_url,
                delay,
            )
            time.sleep(delay)

def is_concurrent_update_error(exc: Exception) -> bool:
    if not isinstance(exc, google_exceptions.BadRequest):
        return False
    message = str(exc).lower()
    return "could not serialize access" in message and "concurrent update" in message

def write_dataset_opportunities(dataset_url: str, dataset_df: pd.DataFrame) -> None:
    """
    Upsert dataset rows into the opportunities BigQuery table.

    Rows whose (dataset_url, feed_id, id) already exist in the table are updated;
    new combinations are inserted.  This makes the operation idempotent so re-runs are safe.

    Steps:
        1. Deduplicate on merge keys to guard against malformed RPDE feeds.
        2. Coerce rows into dicts ready for BigQuery.
        3. Load rows into a short-lived staging table via a load job (immediately DML-queryable).
        4. MERGE staging into the main table (update matched rows, insert new ones).
        5. Drop the staging table regardless of outcome.
    """
    if dataset_df.empty:
        logger.info("No rows to write to opportunities table for dataset %s", dataset_url)
        return

    dataset_df = _dedup_on_merge_keys(dataset_df, dataset_url)

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"
    staging_table_id = (
        f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}_staging_{uuid4().hex[:12]}"
    )
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    table = client.get_table(table_id)
    schema_fields = list(table.schema)
    logger.debug(
        "Detected opportunities schema: %s",
        {field.name: f"{field.field_type}/{field.mode}" for field in schema_fields},
    )

    prepared_rows = _prepare_rows_for_staging(dataset_df, schema_fields)
    del dataset_df
    gc.collect()

    try:
        _load_staging_table(client, prepared_rows, staging_table_id, table.schema, dataset_url)
        _merge_staging_to_main(client, table_id, staging_table_id, dataset_url)
    except Exception:
        logger.exception(
            "Failed upserting opportunities for dataset %s into %s",
            dataset_url,
            table_id,
        )
        raise
    finally:
        client.delete_table(staging_table_id, not_found_ok=True)
        logger.debug("Dropped staging table %s", staging_table_id)


def _calculate_insert_retry_delay(attempt: int, base_delay_seconds: int) -> int:
    """
    Calculate exponential backoff delay in seconds.

    Args:
        attempt: 0-based attempt number
        base_delay_seconds: Base delay for first retry

    Returns:
        Delay in seconds
    """
    exponent = min(attempt, 5)  # Cap exponent to prevent excessive delays
    return base_delay_seconds * (2 ** exponent)


def _insert_batch_with_retry(
    client: bigquery.Client,
    table_id: str,
    batch: list[dict[str, Any]],
    max_attempts: int = INGESTION_INSERT_RETRY_MAX_ATTEMPTS,
    base_delay_seconds: int = INGESTION_INSERT_RETRY_BASE_SECONDS,
) -> list[dict[str, Any]]:
    """
    Insert a batch of rows into BigQuery with exponential backoff retry logic.

    Retries on transient errors (e.g., 404 NotFound). Non-transient errors are
    raised immediately.

    Args:
        client: BigQuery client
        table_id: Target table ID
        batch: Rows to insert
        max_attempts: Maximum number of insertion attempts
        base_delay_seconds: Base delay for exponential backoff

    Returns:
        List of errors from insert_rows_json (may be empty)
    """
    last_exception: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return client.insert_rows_json(table_id, batch)
        except Exception as exc:
            last_exception = exc

            # Non-transient errors should be raised immediately
            if not isinstance(exc, google_exceptions.NotFound):
                raise

            # Don't retry on last attempt
            if attempt >= max_attempts - 1:
                logger.error(
                    "Failed to insert batch after %d attempts. Raising error: %s",
                    max_attempts,
                    str(exc),
                )
                raise

            # Wait before retrying
            delay_seconds = _calculate_insert_retry_delay(attempt, base_delay_seconds)
            logger.warning(
                "Transient insert error on attempt %d/%d (will retry in %.1f seconds): %s",
                attempt + 1,
                max_attempts,
                delay_seconds,
                str(exc),
            )
            time.sleep(delay_seconds)

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    return []


def _prepare_ingestion_rows(
    records: list[dict[str, Any]],
    schema_fields: list[bigquery.SchemaField],
) -> list[dict[str, Any]]:
    """
    Prepare ingestion records for BigQuery insertion.

    Args:
        records: Raw ingestion records
        schema_fields: BigQuery table schema fields

    Returns:
        Normalized rows ready for BigQuery insert_rows_json
    """
    return [
        _prepare_row_for_bigquery({str(k): v for k, v in row.items()}, schema_fields)
        for row in records
    ]


def _insert_ingestion_batches(
    client: bigquery.Client,
    table_id: str,
    prepared_rows: list[dict[str, Any]],
) -> list[str]:
    """
    Insert prepared rows in batches, collecting any insertion errors.

    Args:
        client: BigQuery client
        table_id: Target table ID
        prepared_rows: Prepared rows ready for insertion

    Returns:
        List of formatted error messages (empty if no errors)
    """
    pretty_errors: list[str] = []

    for batch_start in range(0, len(prepared_rows), INGESTION_INSERT_BATCH_SIZE):
        batch_end = min(batch_start + INGESTION_INSERT_BATCH_SIZE, len(prepared_rows))
        batch = prepared_rows[batch_start:batch_end]

        logger.debug(
            "Inserting batch %d-%d of %d rows",
            batch_start,
            batch_end,
            len(prepared_rows),
        )

        errors = _insert_batch_with_retry(client, table_id, batch)

        if errors:
            pretty_errors.append(_prettify_insert_errors(errors, batch, batch_start))

    return pretty_errors


def write_opportunity_ingestion_records(records: list[dict[str, Any]]) -> None:
    """
    Append ingestion summary records to the opportunity_ingestion table.

    Handles transient BigQuery errors (e.g., 404) with exponential backoff retry logic.
    Non-transient errors are raised immediately. Data validation errors are logged
    and re-raised.
    """
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

    # Prepare rows for insertion
    prepared_rows = _prepare_ingestion_rows(records, list(table.schema))

    # Insert rows in batches with retry logic
    pretty_errors = _insert_ingestion_batches(client, table_id, prepared_rows)

    # Raise if any data validation errors occurred
    if pretty_errors:
        pretty_message = "\n".join(pretty_errors)
        logger.error("Failed writing opportunity ingestion rows into %s:\n%s", table_id, pretty_message)
        raise RuntimeError(f"BigQuery ingestion-summary write failed for {table_id}. Details:\n{pretty_message}")

    logger.info("Inserted %d rows into %s", len(prepared_rows), table_id)
