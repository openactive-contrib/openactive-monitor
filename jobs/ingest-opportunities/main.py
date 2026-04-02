import logging
import os
from datetime import date, datetime

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE", "feeds")

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


def ingest_opportunities(target_date: date | None = None, datasets: list[str] | None = None) -> None:
    feeds = get_feeds(target_date, datasets)
    logger.info("Loaded %d feeds for date=%s", len(feeds), target_date)
    print(feeds[:5])

    for feed in feeds:
        logger.info("Processing feed: %s (type: %s, dataset: %s)", feed["url"], feed["type"], feed["dataset_name"])
        get_last_ingestion_info(feed["id"])


if __name__ == "__main__":
    logger.info("Starting Opportunities Ingestion Job")

    # DEBUG: Use custom date and dataset for testing
    custom_date = datetime.strptime("2026-04-01", "%Y-%m-%d").date()
    ingest_opportunities(custom_date, ["Active Leeds Sessions and Facilities"])

    # PROD:
    # ingest_opportunities()