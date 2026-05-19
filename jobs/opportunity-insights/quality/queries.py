"""SQL query templates for the quality-assessment step.

Both queries are restricted to opportunities updated within the last
``QUALITY_WINDOW_DAYS`` (default 5) days, anchored on the provided
``reference_date``.
"""

from __future__ import annotations

from datetime import date

from quality.required_fields import QUALITY_WINDOW_DAYS


def per_feed_completeness(opportunities_table: str, reference_date: date) -> str:
    """Per-feed completeness percentages for the last ``QUALITY_WINDOW_DAYS`` days.

    Each ``*_completeness`` column is the percentage of items (0-100) where the
    underlying column is populated and non-empty:

      * ``location``: JSON object that is not ``{}``.
      * ``startDate`` / ``endDate``: non-null (these are stored as TIMESTAMP).
      * ``activity`` / ``facility``: JSON array with at least one element.
    """
    return f"""
        WITH recent AS (
          SELECT
            dataset_url,
            feed_id,
            location,
            startDate,
            endDate,
            activity,
            facility
          FROM `{opportunities_table}`
          WHERE feed_id IS NOT NULL
            AND last_updated >= DATE_SUB(DATE '{reference_date.isoformat()}', INTERVAL {QUALITY_WINDOW_DAYS} DAY)
        )
        SELECT
          dataset_url,
          feed_id,
          COUNT(*) AS total_items,
          SAFE_DIVIDE(
            COUNTIF(location IS NOT NULL AND TO_JSON_STRING(location) != '{{}}'),
            COUNT(*)
          ) * 100 AS location_completeness,
          SAFE_DIVIDE(
            COUNTIF(startDate IS NOT NULL),
            COUNT(*)
          ) * 100 AS start_date_completeness,
          SAFE_DIVIDE(
            COUNTIF(endDate IS NOT NULL),
            COUNT(*)
          ) * 100 AS end_date_completeness,
          SAFE_DIVIDE(
            COUNTIF(activity IS NOT NULL AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(activity)) > 0),
            COUNT(*)
          ) * 100 AS activities_completeness,
          SAFE_DIVIDE(
            COUNTIF(facility IS NOT NULL AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(facility)) > 0),
            COUNT(*)
          ) * 100 AS facilities_completeness
        FROM recent
        GROUP BY dataset_url, feed_id
    """


def sampled_opportunities_by_feed_and_kind(
    opportunities_table: str,
    reference_date: date,
    samples_per_kind: int,
) -> str:
    """Up to ``samples_per_kind`` random ``json_data`` payloads per ``(dataset_url, feed_id, kind)``.

    Sampled from opportunities updated within the last ``QUALITY_WINDOW_DAYS``
    days. Used downstream to detect whether each kind's required fields appear
    in at least one sample.
    """
    return f"""
        WITH recent AS (
          SELECT dataset_url, feed_id, kind, id, json_data
          FROM `{opportunities_table}`
          WHERE last_updated >= DATE_SUB(DATE '{reference_date.isoformat()}', INTERVAL {QUALITY_WINDOW_DAYS} DAY)
            AND feed_id IS NOT NULL
            AND kind   IS NOT NULL
        ),
        sampled AS (
          SELECT
            dataset_url,
            feed_id,
            kind,
            json_data,
            ROW_NUMBER() OVER (
              PARTITION BY dataset_url, feed_id, kind
              ORDER BY FARM_FINGERPRINT(CONCAT(CAST(RAND() AS STRING), IFNULL(id, '')))
            ) AS rn
          FROM recent
        )
        SELECT dataset_url, feed_id, kind, json_data
        FROM sampled
        WHERE rn <= {samples_per_kind}
    """
