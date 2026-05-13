"""Write the BigQuery `feeds` and `feed_ingestion` tables from legacy pickles.

The legacy feed dicts have 9 keys that map cleanly onto the BigQuery `feeds`
schema; ``provider``, ``rpde_version`` and ``model_version`` are not stored in
the legacy pickles and are left ``NULL`` (the next ``ingest_feeds`` run will
fill them in). ``is_regular`` and ``last_access`` are derived from the source
pickle's filename.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime
from typing import Any

import pandas as pd
from google.cloud import bigquery

from pickle_reader import FeedsPickle

logger = logging.getLogger(__name__)

# Catalogue collection URLs used by ingest_feeds (mirrored here so the synthetic
# feed_ingestion record looks like the new pipeline's output).
CATALOG_COLLECTION_URLS = {
    "regular": "https://openactive.io/data-catalogs/data-catalog-collection.jsonld",
    "preview": "https://openactive.io/data-catalogs/data-catalog-collection-preview.jsonld",
}

FEEDS_COLUMNS = [
    "id", "url", "type", "dataset_name", "dataset_url", "license_url",
    "logo_url", "publisher_name", "is_regular", "last_access",
    "provider", "rpde_version", "model_version",
]


def _feed_to_row(feed: dict, is_regular: bool, last_access: date) -> dict[str, Any]:
    return {
        "id":             feed.get("id"),
        "url":            feed.get("url"),
        "type":           feed.get("type"),
        "dataset_name":   feed.get("dataset_name"),
        "dataset_url":    feed.get("dataset_url"),
        "license_url":    feed.get("license_url"),
        "logo_url":       feed.get("logo_url"),
        "publisher_name": feed.get("publisher_name"),
        "is_regular":     is_regular,
        "last_access":    last_access,
        "provider":       None,
        "rpde_version":   None,
        "model_version":  None,
    }


def write_feeds(
    regular_pickle: FeedsPickle | None,
    preview_pickle: FeedsPickle | None,
) -> int:
    """Append all feeds to the BigQuery feeds table. Returns row count written.

    Caller is expected to have TRUNCATEd the table first; we use append mode
    rather than replace so we don't accidentally clobber any other data.
    """
    project = os.environ["GCP_PROJECT_ID"]
    dataset = os.environ["BQ_DATASET_ID"]
    table = os.getenv("BQ_FEEDS_TABLE", "feeds")
    table_id = f"{project}.{dataset}.{table}"

    rows: list[dict[str, Any]] = []
    for src in (regular_pickle, preview_pickle):
        if src is None:
            continue
        last_access = src.time_finish.date()
        for feed in src.feeds:
            if not isinstance(feed, dict) or not feed.get("id"):
                continue
            rows.append(_feed_to_row(feed, src.is_regular, last_access))

    if not rows:
        logger.warning("No feed rows to write")
        return 0

    df = pd.DataFrame(rows, columns=FEEDS_COLUMNS)
    df = df.drop_duplicates(subset="id", keep="last").reset_index(drop=True)
    # Convert is_regular to nullable boolean and last_access to a proper date column.
    df["is_regular"] = df["is_regular"].astype("boolean")
    df["last_access"] = pd.to_datetime(df["last_access"]).dt.date

    schema = [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("dataset_name", "STRING"),
        bigquery.SchemaField("dataset_url", "STRING"),
        bigquery.SchemaField("license_url", "STRING"),
        bigquery.SchemaField("logo_url", "STRING"),
        bigquery.SchemaField("publisher_name", "STRING"),
        bigquery.SchemaField("is_regular", "BOOL"),
        bigquery.SchemaField("last_access", "DATE"),
        bigquery.SchemaField("provider", "STRING"),
        bigquery.SchemaField("rpde_version", "STRING"),
        bigquery.SchemaField("model_version", "STRING"),
    ]
    client = bigquery.Client(project=project)
    job = client.load_table_from_dataframe(
        df, table_id,
        job_config=bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ),
    )
    job.result()
    logger.info("Wrote %d rows to %s", len(df), table_id)
    return len(df)


def write_feed_ingestion(
    regular_pickle: FeedsPickle | None,
    preview_pickle: FeedsPickle | None,
) -> None:
    """Insert a single synthetic feed_ingestion row covering the backfilled snapshot."""
    project = os.environ["GCP_PROJECT_ID"]
    dataset = os.environ["BQ_DATASET_ID"]
    table = os.getenv("BQ_FEED_INGESTION_TABLE", "feed_ingestion")
    table_id = f"{project}.{dataset}.{table}"

    feeds: list[dict] = []
    catalogues: list[str] = []
    if regular_pickle is not None:
        feeds.extend(regular_pickle.feeds)
        catalogues.append(CATALOG_COLLECTION_URLS["regular"])
    if preview_pickle is not None:
        feeds.extend(preview_pickle.feeds)
        catalogues.append(CATALOG_COLLECTION_URLS["preview"])

    feed_ids = sorted({f["id"] for f in feeds if isinstance(f, dict) and f.get("id")})
    dataset_urls = sorted({f["dataset_url"] for f in feeds if isinstance(f, dict) and f.get("dataset_url")})

    candidates = [p.time_finish for p in (regular_pickle, preview_pickle) if p is not None]
    ingestion_date = max(candidates) if candidates else datetime.utcnow()

    row = {
        "ingestion_date":       ingestion_date.isoformat(),
        "number_of_feeds":      len(feed_ids),
        "feed_ids":             json.dumps(feed_ids),
        "number_of_catalogues": len(catalogues),
        "catalogues":           json.dumps(catalogues),
        "number_of_datasets":   len(dataset_urls),
        "datasets":             json.dumps(dataset_urls),
    }

    client = bigquery.Client(project=project)
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"feed_ingestion insert errors: {errors}")
    logger.info("Wrote 1 row to %s (%d feeds, %d datasets)", table_id, len(feed_ids), len(dataset_urls))
