"""Report on feeds that have stopped publishing opportunity changes.

Run with:
    python jobs/opportunity-insights/report_runner/inactive_feeds.py
"""

from __future__ import annotations

import logging
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)

INACTIVE_DAYS = 45
IGNORED_KINDS = ["FacilityUse"]

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
FEEDS_TABLE = os.getenv("BQ_FEEDS_TABLE")
OPPORTUNITY_INGESTION_TABLE = os.getenv("BQ_OPPORTUNITY_INGESTION_TABLE")
OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")


def query_inactive_feeds(
    inactive_days: int,
    ignored_kinds: list[str] | None = None,
) -> list[dict[str, object]]:
    """Return feeds with no updates or deletes in the last ``inactive_days`` days."""
    if (
        not BIGQUERY_PROJECT
        or not BIGQUERY_DATASET
        or not OPPORTUNITY_INGESTION_TABLE
        or not OPPORTUNITIES_TABLE
    ):
        raise RuntimeError(
            "BigQuery environment is not configured. Expected GCP_PROJECT_ID, "
            "BQ_DATASET_ID, BQ_OPPORTUNITY_INGESTION_TABLE, and "
            "BQ_OPPORTUNITIES_TABLE."
        )

    opportunity_ingestion_table_id = (
        f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITY_INGESTION_TABLE}"
    )
    feeds_table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{FEEDS_TABLE}"
    opportunities_table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"

    query = f"""
        WITH recent_runs AS (
            SELECT
                dataset_id,
                feed_id,
                kind,
                COUNT(*) AS runs_in_window,
                COUNTIF(COALESCE(updated, 0) = 0 AND COALESCE(deleted, 0) = 0) AS zero_activity_runs,
                MAX(ingestion_date) AS last_ingestion_date,
                SUM(COALESCE(updated, 0)) AS recent_updated_total,
                SUM(COALESCE(deleted, 0)) AS recent_deleted_total
            FROM `{opportunity_ingestion_table_id}`
            WHERE ingestion_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @inactive_days DAY)
            GROUP BY dataset_id, feed_id, kind
        ),
        lifetime_activity AS (
            SELECT
                dataset_id,
                feed_id,
                kind,
                MAX(
                    IF(
                        COALESCE(updated, 0) > 0 OR COALESCE(deleted, 0) > 0,
                        ingestion_date,
                        NULL
                    )
                ) AS last_published_at,
                SUM(COALESCE(updated, 0)) AS lifetime_updated_total,
                SUM(COALESCE(deleted, 0)) AS lifetime_deleted_total
            FROM `{opportunity_ingestion_table_id}`
            GROUP BY dataset_id, feed_id, kind
        ),
        dataset_impact AS (
            SELECT
                dataset_url AS dataset_id,
                COUNT(*) AS impact_opportunity_count
            FROM `{opportunities_table_id}`
            GROUP BY dataset_url
        )
        SELECT
            recent.dataset_id,
            recent.feed_id,
            recent.kind,
            feeds.publisher_name,
            feeds.dataset_name,
            feeds.url,
            recent.runs_in_window,
            recent.zero_activity_runs,
            recent.last_ingestion_date,
            lifetime.last_published_at,
            lifetime.lifetime_updated_total,
            lifetime.lifetime_deleted_total,
            COALESCE(dataset_impact.impact_opportunity_count, 0) AS impact_opportunity_count,
            TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), lifetime.last_published_at, DAY) AS days_since_last_publish
        FROM recent_runs AS recent
        JOIN lifetime_activity AS lifetime
            USING (dataset_id, feed_id, kind)
        LEFT JOIN dataset_impact
            USING (dataset_id)
        LEFT JOIN `{feeds_table_id}` AS feeds
            ON feeds.id = recent.feed_id
            AND feeds.dataset_url = recent.dataset_id
        WHERE recent.recent_updated_total = 0
          AND recent.recent_deleted_total = 0
          AND lifetime.last_published_at IS NOT NULL
          AND lifetime.last_published_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @inactive_days DAY)
        ORDER BY
            impact_opportunity_count DESC,
            recent.dataset_id,
            lifetime.last_published_at ASC,
            recent.last_ingestion_date DESC,
            recent.feed_id
    """

    client = bigquery.Client(project=BIGQUERY_PROJECT)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("inactive_days", "INT64", inactive_days),
        ]
    )
    rows = client.query(query, job_config=job_config).result()
    results = [dict(row.items()) for row in rows]

    ignored_kind_set = {
        kind for kind in (ignored_kinds or []) if kind
    }
    if not ignored_kind_set:
        return results

    return [
        row for row in results
        if str(row["kind"] or "") not in ignored_kind_set
    ]


def main() -> None:
    """Run the inactive feeds report."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    rows = query_inactive_feeds(INACTIVE_DAYS, ignored_kinds=IGNORED_KINDS)

    if not rows:
        logger.info(
            "No inactive feeds matched the criteria after ignoring kinds: %s",
            IGNORED_KINDS,
        )
        return

    dataset_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        dataset_groups[str(row["dataset_id"])].append(row)

    logger.info(
        "Found %d inactive feed(s) across %d dataset(s) in the last %d days.",
        len(rows),
        len(dataset_groups),
        INACTIVE_DAYS,
    )
    if IGNORED_KINDS:
        logger.info("Ignoring kinds: %s", IGNORED_KINDS)

    kind_counts = Counter(str(row["kind"] or "unknown") for row in rows)
    logger.info("Inactive feeds by kind: %s", dict(sorted(kind_counts.items())))

    grouped_rows = sorted(
        dataset_groups.items(),
        key=lambda item: (
            -int(item[1][0]["impact_opportunity_count"]),
            str(item[0]),
        ),
    )

    for dataset_id, dataset_rows in grouped_rows:
        impact_opportunity_count = int(dataset_rows[0]["impact_opportunity_count"])
        dataset_name = dataset_rows[0]["dataset_name"]
        publisher_name = dataset_rows[0]["publisher_name"]
        last_published_at = min(
            row["last_published_at"] for row in dataset_rows if row["last_published_at"] is not None
        )
        logger.info(
            "dataset_id=%s | dataset=%s | publisher=%s | impact_opportunity_count=%s | inactive_feeds=%s | oldest_last_published_at=%s",
            dataset_id,
            dataset_name,
            publisher_name,
            impact_opportunity_count,
            len(dataset_rows),
            last_published_at,
        )
        for row in dataset_rows:
            logger.info(
                "  feed_id=%s | kind=%s | url=%s | "
                "last_published_at=%s | last_ingestion_date=%s | runs_in_window=%s/%s zero-activity | "
                "days_since_last_publish=%s | lifetime_updated_total=%s | lifetime_deleted_total=%s",
                row["feed_id"],
                row["kind"],
                row["url"],
                row["last_published_at"],
                row["last_ingestion_date"],
                row["zero_activity_runs"],
                row["runs_in_window"],
                row["days_since_last_publish"],
                row["lifetime_updated_total"],
                row["lifetime_deleted_total"],
            )


if __name__ == "__main__":
    main()
