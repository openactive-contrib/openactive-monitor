import logging
import os
from datetime import date, datetime

import click
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


def _configure_logging(verbose: bool) -> None:
    """Configure app logging and set RPDE logger to DEBUG in verbose mode."""
    logging.getLogger().setLevel(logging.DEBUG if verbose else logging.INFO)
    logging.getLogger("rpde").setLevel(logging.DEBUG if verbose else logging.INFO)


def get_feeds(target_date: date | None = None, datasets: list[str] | None = None) -> dict[str, list[dict]]:
    """
    Fetch list of the feeds collected for the given date from BigQuery.
    Args:
        target_date: Optional date to filter feeds by last_access date. Defaults to None (today's date).
        datasets: Optional list of dataset names to filter feeds. Defaults to None (no dataset filter).
    Returns:
        Dict of feeds grouped by dataset_url. Key is dataset_url, value is list of dataset feed dicts with id, url, type, and dataset_name.
    """
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

    feeds = {}
    for row in rows:
        if datasets is None or row["dataset_url"] in datasets:
            if row["dataset_url"] not in feeds:
                feeds[row["dataset_url"]] = []
            dataset_feeds = feeds.get(row["dataset_url"])
            dataset_feeds.append({"id": row["id"], "url": row["url"], "type": row["type"], "dataset_name": row["dataset_name"]})
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



def ingest_opportunities(
    target_date: date | None = None,
    datasets: list[str] | None = None,
    verbose: bool = False,
) -> None:
    _configure_logging(verbose)
    feeds = get_feeds(target_date, datasets)
    logger.info("Loaded %d feeds for date=%s", len(feeds), target_date or date.today())

    count = 0
    for dataset_url in feeds:
        dataset_feeds = feeds[dataset_url]
        logger.info(
            "[%d/%d] Processing feed: %s",
            count,
            len(feeds),
            dataset_url
        )
        for dataset_feed in dataset_feeds:
            after_timestamp, after_id = get_last_ingestion_info(dataset_feed["id"])
            result = access_feed_url(dataset_feed, after_timestamp, after_id)




@click.command()
@click.option(
    "--target-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Optional feed date in yyyy-mm-dd. Defaults to today.",
)
@click.option(
    "--dataset",
    "datasets",
    multiple=True,
    help="Optional dataset filter. Repeat for multiple datasets.",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose logging (includes RPDE traversal logs).",
)
def cli(target_date: datetime | None, datasets: tuple[str, ...], verbose: bool) -> None:
    """Ingest opportunities from RPDE feeds."""
    parsed_target_date = target_date.date() if target_date else None
    parsed_datasets = list(datasets) if datasets else None

    parsed_target_date = datetime.strptime("2026-04-01", "%Y-%m-%d").date()
    parsed_datasets = ["https://activehartlepool.gs-signature.cloud/OpenActive/"]
    # verbose = True

    ingest_opportunities(parsed_target_date, parsed_datasets, verbose)


if __name__ == "__main__":
    cli()
