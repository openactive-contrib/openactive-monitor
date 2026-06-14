"""SQL query templates for the quality-assessment step.

Both queries are restricted to opportunities updated within the last
``QUALITY_WINDOW_DAYS`` (default 5) days, anchored on the provided
``reference_date``.
"""

from __future__ import annotations

from datetime import date

SAMPLES_PER_KIND = 100
QUALITY_WINDOW_DAYS = 5

def per_feed_completeness(opportunities_table: str, reference_date: date) -> str:
    """Per-feed completeness percentages for the last ``QUALITY_WINDOW_DAYS`` days.

    Each ``*_completeness`` column is the percentage of items (0-100) where the
    underlying column is populated and non-empty:

      * ``location`` / ``ageRange``: JSON object that is not the JSON literal
        ``null`` and not ``{}``.
      * ``level``: JSON scalar/array/object that is not the JSON literal
        ``null`` and not an empty form (``""`` / ``{}`` / ``[]``).
      * ``startDate`` / ``endDate``: non-null (these are stored as TIMESTAMP).
      * ``activity`` / ``facility`` / ``accessibilitySupport``: JSON array with
        at least one element. ``ARRAY_LENGTH(JSON_EXTRACT_ARRAY(...))`` is
        already safe against JSON ``null`` (returns NULL → not counted).
      * ``genderRestriction``: non-null STRING that is not empty.
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
            facility,
            ageRange,
            level,
            accessibilitySupport,
            genderRestriction
          FROM `{opportunities_table}`
          WHERE feed_id IS NOT NULL
            AND last_updated >= DATE_SUB(DATE '{reference_date.isoformat()}', INTERVAL {QUALITY_WINDOW_DAYS} DAY)
        )
        SELECT
          dataset_url,
          feed_id,
          COUNT(*) AS total_items,
          SAFE_DIVIDE(
            COUNTIF(location IS NOT NULL AND TO_JSON_STRING(location) NOT IN ('null', '{{}}')),
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
          ) * 100 AS facilities_completeness,
          SAFE_DIVIDE(
            COUNTIF(ageRange IS NOT NULL AND TO_JSON_STRING(ageRange) NOT IN ('null', '{{}}')),
            COUNT(*)
          ) * 100 AS age_range_completeness,
          SAFE_DIVIDE(
            COUNTIF(level IS NOT NULL AND TO_JSON_STRING(level) NOT IN ('null', '""', '{{}}', '[]')),
            COUNT(*)
          ) * 100 AS level_completeness,
          SAFE_DIVIDE(
            COUNTIF(accessibilitySupport IS NOT NULL AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(accessibilitySupport)) > 0),
            COUNT(*)
          ) * 100 AS accessibility_support_completeness,
          SAFE_DIVIDE(
            COUNTIF(genderRestriction IS NOT NULL AND genderRestriction != ''),
            COUNT(*)
          ) * 100 AS gender_restriction_completeness
        FROM recent
        GROUP BY dataset_url, feed_id
    """


def sampled_opportunities_by_feed_and_kind(
    opportunities_table: str,
    reference_date: date,
    samples_per_kind: int = SAMPLES_PER_KIND,
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
