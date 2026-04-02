import logging
import os
from datetime import date, datetime

from dotenv import load_dotenv
from google.cloud import bigquery

from rpde import access_feed_url

load_dotenv()

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE", "feeds")
OPPORTUNITY_INGESTION_TABLE = os.getenv("BQ_OPPORTUNITY_INGESTION_TABLE", "opportunity_ingestion")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


def get_feeds(target_date: date | None = None, datasets: list[str] | None = None) -> list[dict]:
    """
    Fetch list of the feeds collected for the given date from BigQuery.
    Args:
        target_date: Optional date to filter feeds by last_access date. Defaults to None (today's date).
        datasets: Optional list of dataset names to filter feeds. Defaults to None (no dataset filter).
    Returns:
        List of feed dictionaries with keys: id, url, type, dataset_name.
    """
    if target_date is None:
        target_date = date.today()
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEEDS_TABLE}"

    query = f"""
        SELECT id, url, type, dataset_name
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

    feeds = []
    for row in rows:
        if datasets is None or row["dataset_name"] in datasets:
            feeds.append({"id": row["id"], "url": row["url"], "type": row["type"], "dataset_name": row["dataset_name"]})
    return feeds


def get_last_ingestion_info(feed_id: str) -> tuple[str | None, str | None]:
    """
    Fetch the latest ingestion record for a given feed_id from the opportunity_ingestion table.
    Args:
        feed_id: The feed ID to query.
    Returns:
        Tuple of (afterTimestamp, afterId) from the latest ingestion record, or (None, None) if no record exists.
    """
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



def ingest_opportunities(target_date: date | None = None, datasets: list[str] | None = None) -> None:
    feeds = get_feeds(target_date, datasets)
    logger.info("Loaded %d feeds for date=%s", len(feeds), target_date or date.today())

    for idx, feed in enumerate(feeds, 1):
        logger.info(f"[{idx}/{len(feeds)}] Processing feed: {feed['url']} (type: {feed['type']}, dataset: {feed['dataset_name']})")
        afterTimestamp, afterId = get_last_ingestion_info(feed["id"])
        result = access_feed_url(feed, afterTimestamp, afterId)

        if result:
            logger.info(f"Completed feed {feed['id']}: {result['items_count']} items in {result['pages_fetched']} pages [{result['status']}]")
        else:
            logger.error(f"Failed to process feed {feed['id']}")


if __name__ == "__main__":
    logger.info("Starting Opportunities Ingestion Job")

    # DEBUG: Use custom date and dataset for testing
    custom_date = datetime.strptime("2026-04-01", "%Y-%m-%d").date()
    ingest_opportunities(custom_date, ["Active Leeds Sessions and Facilities"])

    # PROD:
    # ingest_opportunities()