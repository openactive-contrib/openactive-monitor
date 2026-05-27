"""SQL query templates for opportunity-insights.

All queries target the ``opportunities`` and ``feeds`` tables in
``openactive_analytics``. Tables are passed in as fully-qualified
``project.dataset.table`` strings so tests can swap in staging datasets.
"""

from __future__ import annotations

from datetime import date


def _inline_subevents_cte(opportunities_table: str) -> str:
    """CTE yielding only inline JSON-object subEvents (excluding IRI strings)."""
    return f"""
        inline_subevents AS (
          SELECT
            o.dataset_url,
            o.feed_id,
            subevent
          FROM `{opportunities_table}` AS o,
               UNNEST(JSON_EXTRACT_ARRAY(o.has_subEvent)) AS subevent
          WHERE o.feed_id IS NOT NULL
            AND LOWER(JSON_TYPE(subevent)) = 'object'
        )
    """


def per_feed_base_metrics(opportunities_table: str, reference_date: date | None = None) -> str:
    reference_date_sql = f"DATE '{reference_date.isoformat()}'" if reference_date else "CURRENT_DATE()"
    return f"""
        WITH
          root AS (
            SELECT
              dataset_url,
              feed_id,
              COUNT(*) AS num_items,
              COUNTIF(startDate IS NOT NULL) AS num_opportunity_items,
              COUNTIF(
                startDate IS NOT NULL
                AND startDate >= TIMESTAMP({reference_date_sql})
              ) AS num_future_opportunity_items,
              COUNTIF(
                startDate IS NOT NULL
                AND startDate >= TIMESTAMP({reference_date_sql})
                AND startDate <  TIMESTAMP(DATE_ADD({reference_date_sql}, INTERVAL 7 DAY))
              ) AS num_future_week_opportunity_items
            FROM `{opportunities_table}`
            WHERE feed_id IS NOT NULL
            GROUP BY dataset_url, feed_id
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_dates AS (
            SELECT
              dataset_url,
              feed_id,
              COALESCE(JSON_VALUE(subevent, '$.startDate'), JSON_VALUE(subevent, '$.dateStart')) AS start_raw
            FROM inline_subevents
          ),
          inline_agg AS (
            SELECT
              dataset_url,
              feed_id,
              COUNTIF(start_ts IS NOT NULL) AS inline_num_opportunity_items,
              COUNTIF(start_ts >= TIMESTAMP({reference_date_sql})) AS inline_num_future_opportunity_items,
              COUNTIF(
                start_ts >= TIMESTAMP({reference_date_sql})
                AND start_ts < TIMESTAMP(DATE_ADD({reference_date_sql}, INTERVAL 7 DAY))
              ) AS inline_num_future_week_opportunity_items
            FROM (
              SELECT
                dataset_url,
                feed_id,
                COALESCE(
                  SAFE_CAST(start_raw AS TIMESTAMP),
                  TIMESTAMP(SAFE_CAST(start_raw AS DATE))
                ) AS start_ts
              FROM inline_dates
            )
            GROUP BY dataset_url, feed_id
          )
        SELECT
          r.dataset_url,
          r.feed_id,
          r.num_items,
          r.num_opportunity_items + COALESCE(i.inline_num_opportunity_items, 0) AS num_opportunity_items,
          r.num_future_opportunity_items + COALESCE(i.inline_num_future_opportunity_items, 0) AS num_future_opportunity_items,
          r.num_future_week_opportunity_items + COALESCE(i.inline_num_future_week_opportunity_items, 0) AS num_future_week_opportunity_items
        FROM root AS r
        LEFT JOIN inline_agg AS i
          USING (dataset_url, feed_id)
    """


def per_feed_kind_counts(opportunities_table: str) -> str:
    return f"""
        SELECT dataset_url, feed_id, kind AS value, COUNT(*) AS cnt
        FROM `{opportunities_table}`
        WHERE feed_id IS NOT NULL AND kind IS NOT NULL
        GROUP BY dataset_url, feed_id, kind
    """


def per_feed_item_type_counts(opportunities_table: str) -> str:
    return f"""
        WITH
          root_types AS (
            SELECT dataset_url, feed_id, kind AS value
            FROM `{opportunities_table}`
            WHERE feed_id IS NOT NULL AND kind IS NOT NULL
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_types AS (
            SELECT
              dataset_url,
              feed_id,
              COALESCE(
                JSON_VALUE(subevent, '$."@type"'),
                JSON_VALUE(subevent, '$.type')
              ) AS value
            FROM inline_subevents
          )
        SELECT dataset_url, feed_id, value, COUNT(*) AS cnt
        FROM (
          SELECT * FROM root_types
          UNION ALL
          SELECT * FROM inline_types
        )
        WHERE value IS NOT NULL
        GROUP BY dataset_url, feed_id, value
    """


def per_feed_activity_counts(opportunities_table: str) -> str:
    return f"""
        WITH
          root_activity AS (
            SELECT
              o.dataset_url,
              o.feed_id,
              JSON_VALUE(a) AS value
            FROM `{opportunities_table}` AS o,
                 UNNEST(JSON_EXTRACT_ARRAY(o.activity)) AS a
            WHERE o.feed_id IS NOT NULL AND JSON_VALUE(a) IS NOT NULL
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_activity AS (
            SELECT dataset_url, feed_id, JSON_VALUE(a, '$.prefLabel') AS value
            FROM inline_subevents,
                 UNNEST(JSON_EXTRACT_ARRAY(subevent, '$.activity')) AS a
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(a, '$.prefLabel') AS value
            FROM inline_subevents,
                 UNNEST(JSON_EXTRACT_ARRAY(subevent, '$.activities')) AS a
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(subevent, '$.activity.prefLabel') AS value
            FROM inline_subevents
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(subevent, '$.activities.prefLabel') AS value
            FROM inline_subevents
          )
        SELECT
          dataset_url,
          feed_id,
          value,
          COUNT(*) AS cnt
        FROM (
          SELECT * FROM root_activity
          UNION ALL
          SELECT * FROM inline_activity
        )
        WHERE value IS NOT NULL
        GROUP BY dataset_url, feed_id, value
    """


def per_feed_facility_counts(opportunities_table: str) -> str:
    return f"""
        WITH
          root_facility AS (
            SELECT
              o.dataset_url,
              o.feed_id,
              JSON_VALUE(f) AS value
            FROM `{opportunities_table}` AS o,
                 UNNEST(JSON_EXTRACT_ARRAY(o.facility)) AS f
            WHERE o.feed_id IS NOT NULL AND JSON_VALUE(f) IS NOT NULL
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_facility AS (
            SELECT dataset_url, feed_id, JSON_VALUE(f, '$.prefLabel') AS value
            FROM inline_subevents,
                 UNNEST(JSON_EXTRACT_ARRAY(subevent, '$.facilityType')) AS f
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(f, '$.prefLabel') AS value
            FROM inline_subevents,
                 UNNEST(JSON_EXTRACT_ARRAY(subevent, '$.facilities')) AS f
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(subevent, '$.facilityType.prefLabel') AS value
            FROM inline_subevents
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(subevent, '$.facilities.prefLabel') AS value
            FROM inline_subevents
          )
        SELECT
          dataset_url,
          feed_id,
          value,
          COUNT(*) AS cnt
        FROM (
          SELECT * FROM root_facility
          UNION ALL
          SELECT * FROM inline_facility
        )
        WHERE value IS NOT NULL
        GROUP BY dataset_url, feed_id, value
    """


def per_feed_accessibility_counts(opportunities_table: str) -> str:
    # accessibilitySupport is [{prefLabel, ...}, ...] under json_data or inherited_data.
    # UNNEST(NULL) is treated as an empty cross-join, so COALESCE between the two JSON
    # array sources is safe without a typed empty-array fallback.
    return f"""
        WITH
          root_acc AS (
            SELECT
              o.dataset_url,
              o.feed_id,
              JSON_VALUE(entry, '$.prefLabel') AS pref_label
            FROM `{opportunities_table}` AS o,
                 UNNEST(COALESCE(
                   JSON_EXTRACT_ARRAY(o.json_data,      '$.accessibilitySupport'),
                   JSON_EXTRACT_ARRAY(o.inherited_data, '$.accessibilitySupport')
                 )) AS entry
            WHERE o.feed_id IS NOT NULL
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_acc AS (
            SELECT dataset_url, feed_id, JSON_VALUE(entry, '$.prefLabel') AS pref_label
            FROM inline_subevents,
                 UNNEST(JSON_EXTRACT_ARRAY(subevent, '$.accessibilitySupport')) AS entry
            UNION ALL
            SELECT dataset_url, feed_id, JSON_VALUE(subevent, '$.accessibilitySupport.prefLabel') AS pref_label
            FROM inline_subevents
          ),
          acc AS (
            SELECT * FROM root_acc
            UNION ALL
            SELECT * FROM inline_acc
          )
        SELECT dataset_url, feed_id, pref_label AS value, COUNT(*) AS cnt
        FROM acc
        WHERE pref_label IS NOT NULL
        GROUP BY dataset_url, feed_id, pref_label
    """


def per_feed_organizer_counts(opportunities_table: str) -> str:
    return f"""
        WITH
          root_org AS (
            SELECT
              dataset_url,
              feed_id,
              TRIM(COALESCE(
                JSON_VALUE(json_data,      '$.organizer.name'),
                JSON_VALUE(inherited_data, '$.organizer.name')
              )) AS value
            FROM `{opportunities_table}`
            WHERE feed_id IS NOT NULL
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_org AS (
            SELECT
              dataset_url,
              feed_id,
              TRIM(JSON_VALUE(subevent, '$.organizer.name')) AS value
            FROM inline_subevents
          )
        SELECT dataset_url, feed_id, value, COUNT(*) AS cnt
        FROM (
          SELECT * FROM root_org
          UNION ALL
          SELECT * FROM inline_org
        )
        WHERE value IS NOT NULL AND value != ''
        GROUP BY dataset_url, feed_id, value
    """


def per_feed_location_points(opportunities_table: str) -> str:
    """Distinct (lat, lng) per feed with item counts for spatial lookup."""
    return f"""
        WITH
          root_points AS (
            SELECT
              dataset_url,
              feed_id,
              SAFE_CAST(JSON_VALUE(location, '$.latitude')  AS FLOAT64) AS lat,
              SAFE_CAST(JSON_VALUE(location, '$.longitude') AS FLOAT64) AS lng
            FROM `{opportunities_table}`
            WHERE feed_id IS NOT NULL
              AND location IS NOT NULL
              AND JSON_VALUE(location, '$.latitude')  IS NOT NULL
              AND JSON_VALUE(location, '$.longitude') IS NOT NULL
          ),
          {_inline_subevents_cte(opportunities_table)},
          inline_points AS (
            SELECT
              dataset_url,
              feed_id,
              SAFE_CAST(JSON_VALUE(subevent, '$.location.geo.latitude')  AS FLOAT64) AS lat,
              SAFE_CAST(JSON_VALUE(subevent, '$.location.geo.longitude') AS FLOAT64) AS lng
            FROM inline_subevents
            WHERE JSON_VALUE(subevent, '$.location.geo.latitude') IS NOT NULL
              AND JSON_VALUE(subevent, '$.location.geo.longitude') IS NOT NULL
          )
        SELECT
          dataset_url,
          feed_id,
          lat,
          lng,
          COUNT(*) AS cnt
        FROM (
          SELECT * FROM root_points
          UNION ALL
          SELECT * FROM inline_points
        )
        GROUP BY dataset_url, feed_id, lat, lng
    """


def active_opportunities_summary(
    opportunities_table: str,
    feeds_table: str,
    reference_date: date | None = None,
) -> str:
    """Active (future) opportunity counts per district / publisher / provider / activity_or_facility.

    ``activity_or_facility`` is the opportunity's facility list for facility-kind
    items (``FacilityUse`` / ``IndividualFacilityUse`` / ``Slot``) and its activity
    list otherwise, serialised as a JSON array string (e.g. ``["Football","Yoga"]``)
    so it can be both grouped on and stored in a JSON column. ``is_activity`` is
    ``TRUE`` when the value is an activity list and ``FALSE`` for facility-kind items.

    Feeds are de-duplicated to one row per ``dataset_url`` (publisher / provider are
    dataset-level attributes) to avoid fan-out inflating ``opportunity_count``.

    Rows without a (non-empty) ``district_name`` or ``publisher_name`` are excluded.
    """
    reference_date_sql = (
        f"DATE '{reference_date.isoformat()}'" if reference_date else "CURRENT_DATE()"
    )
    return f"""
        WITH feeds_dedup AS (
          SELECT dataset_url, publisher_name, provider
          FROM `{feeds_table}`
          QUALIFY ROW_NUMBER() OVER (
            PARTITION BY dataset_url ORDER BY last_access DESC
          ) = 1
        ),
        base AS (
          SELECT
            o.district_name,
            fd.publisher_name AS publisher,
            fd.provider,
            NOT COALESCE(
              o.kind IN ('FacilityUse', 'IndividualFacilityUse', 'Slot'), FALSE
            ) AS is_activity,
            CASE
              WHEN o.kind IN ('FacilityUse', 'IndividualFacilityUse', 'Slot')
                THEN JSON_VALUE_ARRAY(o.facility)
              ELSE JSON_VALUE_ARRAY(o.activity)
            END AS activity_or_facility_arr
          FROM `{opportunities_table}` AS o
          LEFT JOIN feeds_dedup AS fd
            ON o.dataset_url = fd.dataset_url
          WHERE o.startDate >= TIMESTAMP({reference_date_sql})
            AND o.district_name IS NOT NULL
            AND TRIM(o.district_name) != ''
            AND fd.publisher_name IS NOT NULL
            AND TRIM(fd.publisher_name) != ''
        )
        SELECT
          district_name,
          publisher,
          provider,
          is_activity,
          TO_JSON_STRING(activity_or_facility_arr) AS activity_or_facility,
          COUNT(*) AS opportunity_count
        FROM base
        GROUP BY district_name, publisher, provider, is_activity, activity_or_facility
    """


def latest_ingestion_status(opportunity_ingestion_table: str) -> str:
    """Latest ingestion status per feed (for the `status` column in feed_insights)."""
    return f"""
        SELECT feed_id, status
        FROM `{opportunity_ingestion_table}`
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY feed_id
          ORDER BY ingestion_date DESC
        ) = 1
    """


def feeds_metadata(feeds_table: str) -> str:
    """All feeds with their metadata (latest row per id, most recent last_access)."""
    return f"""
        SELECT
          id AS feed_id,
          url AS feed_url,
          type AS feed_type,
          dataset_name,
          dataset_url,
          publisher_name,
          license_url,
          logo_url,
          is_regular
        FROM `{feeds_table}`
        QUALIFY ROW_NUMBER() OVER (
          PARTITION BY id
          ORDER BY last_access DESC
        ) = 1
    """
