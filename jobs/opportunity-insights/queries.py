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
              ) AS num_future_week_opportunity_items,
              -- Narrow variants: exclude bookable Slot rows (their parent facility
              -- is credited separately via slot_super_agg below).
              COUNTIF(kind != 'Slot') AS num_items_nonslot,
              COUNTIF(
                kind != 'Slot'
                AND startDate IS NOT NULL
                AND startDate >= TIMESTAMP({reference_date_sql})
              ) AS num_future_nonslot,
              COUNTIF(
                kind != 'Slot'
                AND startDate IS NOT NULL
                AND startDate >= TIMESTAMP({reference_date_sql})
                AND startDate <  TIMESTAMP(DATE_ADD({reference_date_sql}, INTERVAL 7 DAY))
              ) AS num_future_week_nonslot
            FROM `{opportunities_table}`
            WHERE feed_id IS NOT NULL
            GROUP BY dataset_url, feed_id
          ),
          slot_super AS (
            -- A Slot's parent facility reference lives in the JSON ``has_superEvent``
            -- column. In practice it is a scalar URI string (the facilityUse @id),
            -- but it may also be an inline object (carrying an ``@id`` or ``id``) or
            -- an array of those. Normalise to one row per referenced facility so both
            -- the items-narrow (inline objects only) and future-narrow (all refs)
            -- terms can be derived.
            SELECT
              o.dataset_url,
              o.feed_id,
              o.startDate,
              JSON_TYPE(ref) AS ref_type,
              CASE JSON_TYPE(ref)
                WHEN 'object' THEN COALESCE(
                  JSON_VALUE(ref, '$."@id"'), JSON_VALUE(ref, '$.id')
                )
                WHEN 'string' THEN JSON_VALUE(ref)
                ELSE NULL
              END AS facility_ref
            FROM `{opportunities_table}` AS o
            LEFT JOIN UNNEST(
              CASE JSON_TYPE(o.has_superEvent)
                WHEN 'array' THEN JSON_QUERY_ARRAY(o.has_superEvent)
                ELSE [o.has_superEvent]
              END
            ) AS ref
            WHERE o.feed_id IS NOT NULL
              AND o.kind = 'Slot'
          ),
          slot_super_agg AS (
            SELECT
              dataset_url,
              feed_id,
              -- Items-narrow term: inline (object) superEvents only. Facilities
              -- referenced by a string @id already exist as their own FacilityUse /
              -- IndividualFacilityUse rows and are counted in num_items_nonslot, so
              -- including them here would double-count.
              COUNT(DISTINCT IF(ref_type = 'object', facility_ref, NULL)) AS num_super_items,
              -- Future terms: any distinct facility referenced by a future Slot.
              -- Facility rows carry no startDate, so they are absent from
              -- num_future_nonslot and there is no double-count.
              COUNT(DISTINCT IF(
                startDate IS NOT NULL
                AND startDate >= TIMESTAMP({reference_date_sql}),
                facility_ref, NULL
              )) AS num_future_super_items,
              COUNT(DISTINCT IF(
                startDate IS NOT NULL
                AND startDate >= TIMESTAMP({reference_date_sql})
                AND startDate <  TIMESTAMP(DATE_ADD({reference_date_sql}, INTERVAL 7 DAY)),
                facility_ref, NULL
              )) AS num_future_week_super_items
            FROM slot_super
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
          r.num_future_week_opportunity_items + COALESCE(i.inline_num_future_week_opportunity_items, 0) AS num_future_week_opportunity_items,
          r.num_items_nonslot + COALESCE(s.num_super_items, 0) AS num_items_narrow,
          r.num_future_nonslot
            + COALESCE(i.inline_num_future_opportunity_items, 0)
            + COALESCE(s.num_future_super_items, 0) AS num_future_opportunity_items_narrow,
          r.num_future_week_nonslot
            + COALESCE(i.inline_num_future_week_opportunity_items, 0)
            + COALESCE(s.num_future_week_super_items, 0) AS num_future_week_opportunity_items_narrow
        FROM root AS r
        LEFT JOIN inline_agg AS i
          USING (dataset_url, feed_id)
        LEFT JOIN slot_super_agg AS s
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
            o.nhstrust_name,
            o.nhstrust_code,
            fd.publisher_name AS publisher,
            fd.provider,
            o.organization_name,
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
          nhstrust_name,
          nhstrust_code,
          publisher,
          provider,
          is_activity,
          TO_JSON_STRING(activity_or_facility_arr) AS activity_or_facility,
          COUNT(*) AS opportunity_count,
          TO_JSON_STRING(ARRAY_AGG(DISTINCT organization_name IGNORE NULLS ORDER BY organization_name)) AS organization_names
        FROM base
        GROUP BY district_name, nhstrust_name, nhstrust_code, publisher, provider, is_activity, activity_or_facility
    """


def active_opportunities_summary_narrow_counts(
    opportunities_table: str,
    feeds_table: str,
    reference_date: date | None = None,
) -> str:
    """Narrow active-opportunity counts per the same group as ``active_opportunities_summary``.

    Computes ``opportunity_count_narrow``: ``Slot`` rows are excluded and instead
    each Slot's referenced facility (``FacilityUse`` / ``IndividualFacilityUse``) is
    credited once, de-duplicated by facility ``@id`` within each output group. The
    net effect for facility groups (``is_activity = FALSE``) is *the number of
    distinct future FacilityUse / IndividualFacilityUse* — i.e. facilities that have
    at least one future ``Slot`` — rather than the raw future ``Slot`` count.

    A Slot's parent facility reference is stored in the JSON ``has_superEvent``
    column (populated from ``facilityUse`` / ``superEvent`` during ingest). It may be
    a JSON **array** of URI strings (the common shape), a scalar URI **string**, or
    an inline **object** carrying an ``@id``. All three shapes are handled here; the
    earlier ``JSON_VALUE(has_superEvent, '$."@id"')`` only matched inline objects and
    so produced 0 for the array/string shapes.

    ``FacilityUse`` / ``IndividualFacilityUse`` rows themselves carry no ``startDate``
    and are therefore excluded by the future filter, which is why they must be
    counted via their future Slots rather than directly.

    Grouping keys and filters mirror ``active_opportunities_summary`` exactly so the
    result can be joined back onto it one-to-one. Kept as a separate function to
    avoid complicating the primary query.
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
            o.nhstrust_name,
            o.nhstrust_code,
            fd.publisher_name AS publisher,
            fd.provider,
            NOT COALESCE(
              o.kind IN ('FacilityUse', 'IndividualFacilityUse', 'Slot'), FALSE
            ) AS is_activity,
            CASE
              WHEN o.kind IN ('FacilityUse', 'IndividualFacilityUse', 'Slot')
                THEN JSON_VALUE_ARRAY(o.facility)
              ELSE JSON_VALUE_ARRAY(o.activity)
            END AS activity_or_facility_arr,
            o.kind AS kind,
            -- Normalise a Slot's facility reference(s) to an array of JSON values so
            -- array / scalar-string / object shapes can all be handled uniformly.
            CASE
              WHEN o.kind = 'Slot' THEN
                CASE JSON_TYPE(o.has_superEvent)
                  WHEN 'array' THEN JSON_QUERY_ARRAY(o.has_superEvent)
                  ELSE [o.has_superEvent]
                END
              ELSE []
            END AS super_refs
          FROM `{opportunities_table}` AS o
          LEFT JOIN feeds_dedup AS fd
            ON o.dataset_url = fd.dataset_url
          WHERE o.startDate >= TIMESTAMP({reference_date_sql})
            AND o.district_name IS NOT NULL
            AND TRIM(o.district_name) != ''
            AND fd.publisher_name IS NOT NULL
            AND TRIM(fd.publisher_name) != ''
        ),
        exploded AS (
          -- LEFT JOIN UNNEST keeps non-Slot rows (empty super_refs -> single NULL ref).
          SELECT
            district_name,
            nhstrust_name,
            nhstrust_code,
            publisher,
            provider,
            is_activity,
            activity_or_facility_arr,
            kind,
            CASE JSON_TYPE(super_ref)
              WHEN 'object' THEN COALESCE(
                JSON_VALUE(super_ref, '$."@id"'), JSON_VALUE(super_ref, '$.id')
              )
              WHEN 'string' THEN JSON_VALUE(super_ref)
              ELSE NULL
            END AS slot_facility_id
          FROM base
          LEFT JOIN UNNEST(super_refs) AS super_ref
        )
        SELECT
          district_name,
          nhstrust_name,
          nhstrust_code,
          publisher,
          provider,
          is_activity,
          TO_JSON_STRING(activity_or_facility_arr) AS activity_or_facility,
          COUNTIF(kind != 'Slot')
            + COUNT(DISTINCT slot_facility_id) AS opportunity_count_narrow
        FROM exploded
        GROUP BY district_name, nhstrust_name, nhstrust_code, publisher, provider, is_activity, activity_or_facility
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
