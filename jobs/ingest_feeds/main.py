"""Ingest OpenActive data feeds into BigQuery.

Collects feed metadata from the OpenActive catalog collection (regular and
preview), then merges the results into the BigQuery table
``openactive-monitor.openactive_analytics.feeds`` using the ``id`` column as
the merge key.  The ``last_access`` date is updated on every run.

Can be executed locally or as a Google Cloud Run job.
"""

import os
import json
import logging
from datetime import date, datetime, timezone
from time import sleep
from typing import Any

import pandas as pd
import pandas_gbq
import requests
from bs4 import BeautifulSoup
from google.cloud import bigquery
from dotenv import load_dotenv
from request_client import build_session, get_json, get_text

load_dotenv()

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE")
FEED_INGESTION_TABLE = os.getenv("BQ_FEED_INGESTION_TABLE")

CATALOG_COLLECTION_URLS = {
    "regular": "https://openactive.io/data-catalogs/data-catalog-collection.jsonld",
    "preview": "https://openactive.io/data-catalogs/data-catalog-collection-preview.jsonld",
}

SECONDS_WAIT_BETWEEN_REQUESTS = 0.2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feed collection logic
# ---------------------------------------------------------------------------


def get_catalogue_urls(
    session: requests.Session,
    collection_url: str,
) -> list[str]:
    """
    Fetch catalog URLs from the given *collection_url*.
    Args:
        session: A requests.Session with retries configured.
        collection_url: URL of the catalog collection (regular or preview).
    Returns:
        A list of catalog URLs, or an empty list on failure.
    """
    data = get_json(session, collection_url, timeout=180)
    if data is None:
        logger.error("Cannot get collection: %s", collection_url)
        return []

    if not "hasPart" in data:
        logger.error("Missing hasPart in collection: %s", collection_url)
        return []

    parts = data.get("hasPart", [])
    if not all(isinstance(p, str) for p in parts):
        logger.error("Invalid hasPart entries in: %s", collection_url)
        return []

    return parts


def get_dataset_urls(
    session: requests.Session,
    catalogue_urls: list[str],
) -> list[str]:
    """Fetch dataset URLs from each catalogue URL."""
    dataset_urls: list[str] = []

    for idx, catalogue_url in enumerate(catalogue_urls):
        data = get_json(session, catalogue_url, timeout=180)
        if data is None:
            logger.error("Cannot get catalogue: %s", catalogue_url)
        else:
            datasets = data.get("dataset", [])
            if all(isinstance(d, str) for d in datasets):
                dataset_urls.extend(datasets)
            else:
                logger.error("Invalid dataset entries in: %s", catalogue_url)

        if idx < len(catalogue_urls) - 1:
            sleep(SECONDS_WAIT_BETWEEN_REQUESTS)

    return dataset_urls


def _parse_feeds_from_dataset(
    session: requests.Session,
    dataset_url: str,
    catalogue_url: str = "",
) -> list[dict]:
    """Scrape the JSON-LD metadata from *dataset_url* and return a list of
    feed dicts.

    Args:
        session: A requests.Session with retries configured.
        dataset_url: The URL of the dataset page to scrape.
        catalogue_url: The parent catalogue URL (used to derive provider).
    """
    html = get_text(session, dataset_url, timeout=60)
    if html is None:
        logger.error("Cannot get dataset: %s", dataset_url)
        return []

    feeds: list[dict] = []

    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            jsonld = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        for feed_in in jsonld.get("distribution", []):
            feed_out = {
                "type": get_feed_type(feed_in),
                "url": feed_in.get("contentUrl", ""),
                "dataset_name": jsonld.get("name", ""),
                "dataset_url": dataset_url,
                "catalogue_url": catalogue_url,
                "license_url": jsonld.get("license", ""),
                "logo_url": _nested_get(jsonld, "publisher", "logo", "url"),
                "publisher_name": _nested_get(jsonld, "publisher", "name"),
            }
            feeds.append(feed_out)

    return feeds

expected_feed_names = ["HeadlineEvent", "Event", "OnDemandEvent", "FacilityUse", "IndividualFacilityUse", "Slot", "SessionSeries", "ScheduledSession", "CourseInstance", ""]

def get_feed_type(feed_in) -> Any:
    feed_type = feed_in.get("name", "")
    if feed_type in expected_feed_names:
        return feed_type
    else:
        # handle non-standard (error) feed names
        if "slot" in str(feed_type).lower():
            return "Slot"
        elif "scheduled" in str(feed_type).lower():
            return "ScheduledSession"
        elif "session" in str(feed_type).lower():
            return "SessionSeries"
    return ""


def _nested_get(d: dict, *keys: str, default: str = "") -> str:
    """Safely traverse nested dicts and return *default* on any miss."""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d if isinstance(d, str) else default


def collect_feeds(
    session: requests.Session, label: str = "regular"
) -> dict:
    """Collect all feeds for the given mode.

    Args:
        session: A requests.Session with retries configured.
        label: Either ``"regular"`` or ``"preview"``.

    Returns:
        A dict with keys:
            - ``feeds``: list of feed dicts
            - ``catalogue_urls``: list of catalogue URLs fetched
            - ``dataset_urls``: list of dataset URLs fetched
    """
    collection_url = CATALOG_COLLECTION_URLS[label]

    logger.info("Collecting %s feeds from %s", label, collection_url)

    catalogue_urls = get_catalogue_urls(session, collection_url)

    # Build a map of dataset_url -> catalogue_url
    dataset_to_catalogue: dict[str, str] = {}

    for catalogue_url in catalogue_urls:
        data = get_json(session, catalogue_url, timeout=180)
        if data is None:
            logger.error("Cannot get catalogue: %s", catalogue_url)
        else:
            datasets = data.get("dataset", [])
            if all(isinstance(d, str) for d in datasets):
                for dataset_url in datasets:
                    dataset_to_catalogue[dataset_url] = catalogue_url
            else:
                logger.error("Invalid dataset entries in: %s", catalogue_url)

    dataset_urls = list(dataset_to_catalogue.keys())
    logger.info("Found %d datasets for %s feeds", len(dataset_urls), label)

    feeds: list[dict] = []
    for idx, dataset_url in enumerate(dataset_urls):
        catalogue_url_for_dataset = dataset_to_catalogue.get(dataset_url, "")
        feeds.extend(_parse_feeds_from_dataset(session, dataset_url, catalogue_url=catalogue_url_for_dataset))
        if idx < len(dataset_urls) - 1:
            sleep(SECONDS_WAIT_BETWEEN_REQUESTS)

    logger.info("Collected %d %s feeds", len(feeds), label)
    return {
        "feeds": feeds,
        "catalogue_urls": catalogue_urls,
        "dataset_urls": dataset_urls,
    }


# ---------------------------------------------------------------------------
# ID & Provider helpers
# ---------------------------------------------------------------------------


def _make_feed_id(url: str) -> str:
    """Derive a stable, human-readable id from a feed URL.

    Mirrors the logic in the original ``get-feeds`` job.
    """
    return (
        url.replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .replace(".", "-")
        .replace("/", "-")
        .strip("-")
    )


def _extract_provider(url: str) -> str:
    """Extract the domain (provider) from a URL.

    Args:
        url: A full URL (e.g., 'https://example.com/path/to/resource').

    Returns:
        The domain name (e.g., 'example.com'), or empty string on parse failure.
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove 'www.' prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# BigQuery helpers
# ---------------------------------------------------------------------------


def _feeds_to_dataframe(feeds: list[dict]) -> pd.DataFrame:
    """
    Convert collected feeds to a DataFrame matching the BQ schema.
    Args:
        feeds: List of feed dicts with keys: url, type, dataset_name, dataset_url,
               catalogue_url, license_url, logo_url, publisher_name.
    Returns:
        A pandas DataFrame with BQ table columns.
    """
    columns = [
        "id",
        "url",
        "type",
        "dataset_name",
        "dataset_url",
        "provider",
        "license_url",
        "logo_url",
        "publisher_name",
        "last_access",
    ]
    today = date.today()

    rows = []
    for feed in feeds:
        # Extract provider from catalogue_url
        catalogue_url = feed.get("catalogue_url", "")
        provider = _extract_provider(catalogue_url) if catalogue_url else ""

        rows.append(
            {
                "id": _make_feed_id(feed["url"]),
                "url": feed["url"],
                "type": feed["type"],
                "dataset_name": feed["dataset_name"],
                "dataset_url": feed["dataset_url"],
                "provider": provider,
                "license_url": feed["license_url"],
                "logo_url": feed["logo_url"],
                "publisher_name": feed["publisher_name"],
                "last_access": today,
            }
        )

    df = pd.DataFrame(rows, columns=columns)
    # De-duplicate: keep last occurrence (same id may appear in regular + preview)
    df = df.drop_duplicates(subset="id", keep="last").reset_index(drop=True)
    return df


def merge_to_bigquery(df_new: pd.DataFrame) -> None:
    """Merge *df_new* into the BigQuery feeds table.

    * Rows whose ``id`` already exists are **updated** (all columns
      overwritten, ``last_access`` refreshed).
    * Rows with a new ``id`` are **inserted**.

    Args:
        df_new: DataFrame of new feed data to merge in. Must contain an ``id``
            column and match the BQ schema.
    """
    logger.info("Loading existing feeds from BigQuery …")

    try:
        df_existing = pandas_gbq.read_gbq(
            f"SELECT * FROM `{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEEDS_TABLE}`",
            project_id=BIGQUERY_PROJECT,
        )
    except Exception:
        logger.info("Could not read existing table – will create it from scratch.")
        df_existing = pd.DataFrame()

    df_merged: pd.DataFrame
    if df_existing.empty:
        df_merged = df_new
    else:
        # Ensure consistent date type
        if "last_access" in df_existing.columns:
            last_access = pd.to_datetime(df_existing["last_access"], errors="coerce")
            df_existing = df_existing.assign(
                last_access=last_access.apply(
                    lambda ts: ts.date() if pd.notna(ts) else None
                )
            )

        # New rows take precedence for matching ids
        combined: pd.DataFrame = pd.DataFrame(
            pd.concat([df_existing, df_new], ignore_index=True)
        )
        df_merged = combined.drop_duplicates(subset="id", keep="last").reset_index(
            drop=True
        )

    logger.info("Writing %d rows to BigQuery …", len(df_merged))

    pandas_gbq.to_gbq(
        df_merged,
        destination_table=f'{BIGQUERY_DATASET}.{FEEDS_TABLE}',
        project_id=BIGQUERY_PROJECT,
        if_exists="replace",
    )

    logger.info("BigQuery table updated successfully.")


def write_ingestion_record(
    feed_ids: list[str],
    catalogue_urls: list[str],
    dataset_urls: list[str],
    ingestion_ts: datetime,
) -> None:
    """Append a single summary row to the feed_ingestion table.

    Uses the google-cloud-bigquery client directly because pandas-gbq does not
    support JSON column types.

    Args:
        feed_ids: Ordered list of all ingested feed ids.
        catalogue_urls: All catalogue URLs visited during this run.
        dataset_urls: All dataset URLs visited during this run.
        ingestion_ts: UTC timestamp marking the start of this ingestion run.
    """
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEED_INGESTION_TABLE}"

    row = {
        "ingestion_date": ingestion_ts.isoformat(),
        "number_of_catalogues": len(catalogue_urls),
        "catalogues": json.dumps(catalogue_urls),
        "number_of_datasets": len(dataset_urls),
        "datasets": json.dumps(dataset_urls),
        "number_of_feeds": len(feed_ids),
        "feed_ids": json.dumps(feed_ids),
    }

    logger.info(
        "Writing ingestion record: %d feeds, %d catalogues, %d datasets …",
        len(feed_ids),
        len(catalogue_urls),
        len(dataset_urls),
    )

    errors = client.insert_rows_json(table_id, [row])
    if errors:
        logger.error("BigQuery insert errors: %s", errors)
        raise RuntimeError(f"Failed to insert ingestion record: {errors}")

    logger.info("Ingestion record written successfully.")


def main() -> None:
    ingestion_ts = datetime.now(tz=timezone.utc)
    session = build_session()

    all_feeds: list[dict] = []
    all_catalogue_urls: list[str] = []
    all_dataset_urls: list[str] = []

    for label in ("preview", "regular"):
        try:
            result = collect_feeds(session, label=label)
            all_feeds.extend(result["feeds"])
            all_catalogue_urls.extend(result["catalogue_urls"])
            all_dataset_urls.extend(result["dataset_urls"])
        except Exception as e:
            logger.error("Error collecting %s feeds: %s", label, e, exc_info=True)

    if not all_feeds:
        logger.warning("No feeds collected – nothing to write.")
        return

    df = _feeds_to_dataframe(all_feeds)
    merge_to_bigquery(df)

    write_ingestion_record(
        feed_ids=df["id"].tolist(),
        catalogue_urls=all_catalogue_urls,
        dataset_urls=all_dataset_urls,
        ingestion_ts=ingestion_ts,
    )

    logger.info("Finished.")


if __name__ == "__main__":
    main()

