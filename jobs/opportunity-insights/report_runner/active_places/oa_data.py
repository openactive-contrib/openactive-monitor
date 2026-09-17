"""Fetch distinct OpenActive location points from BigQuery.

OpenActive publishes opportunities, not sites, so the closest analogue to an
Active Places site is a distinct location point within a dataset. ``Slot`` items
are excluded: they carry no location of their own and inherit it from their
parent ``FacilityUse``, so including them would only duplicate points already
contributed by the parent.
"""

from __future__ import annotations

import logging

import pandas as pd

import bigquery_ops

logger = logging.getLogger(__name__)

# Generous envelope around Great Britain and Northern Ireland. The existing
# missing-location analysis documents transposed and plainly wrong coordinates in
# the feeds; anything outside this box cannot be matched against an English site.
GB_LAT_MIN, GB_LAT_MAX = 49.0, 61.0
GB_LNG_MIN, GB_LNG_MAX = -9.0, 2.0

ENGLAND = "England"


def build_query(opportunities_table: str) -> str:
    """Distinct (dataset_url, lat, lng) points with publisher, geography and postcode.

    ``publisher_name`` is read straight off ``opportunities`` — it is populated on
    100% of rows, so joining ``feeds`` would only risk fan-out for no gain. It is
    not grouped on, because 14 datasets carry two spellings of their publisher and
    grouping would split a single location into two points.

    Where a point carries several candidate values for a single-valued column, ``MIN``
    picks one deterministically. ``APPROX_TOP_COUNT`` is the obvious alternative and is
    wrong here twice over: it is approximate, returning different postcodes for 27
    points across two runs of the same query, and — worse — it counts NULL as a
    candidate value, so it returns NULL whenever most rows at a point happen to lack a
    postcode. That silently discarded a real postcode for 1,414 points. ``MIN`` ignores
    NULLs, which lifts postcode coverage from 57.9% to 65.1% of points. Where a point
    genuinely straddles two postcodes there is no single right answer to lose.

    The postcode is taken from the ingestion-resolved ``location.postal_code``
    first, falling back to whatever the publisher declared in ``json_data``.
    ``location_json`` is the raw ``location`` payload, kept so a row in the output
    can be traced back to the opportunities that produced it:
    ``WHERE TO_JSON_STRING(location) = '<value>'``. It is effectively invariant per
    point — 2 of 19,507 points carry a second variant.
    ``location_names`` collects every distinct ``json_data.location.name`` at the
    point, because one coordinate often carries several named spaces — up to 11.
    They are joined with `` | `` rather than the default comma, since venue names
    routinely contain commas ("Sports Hall, Main Building").

    Reading ``json_data`` is what makes this query cost ~6.7GB rather than ~0.7GB;
    it roughly quadruples postcode coverage, which the postcode matching channel
    depends on, and supplies the venue names. Only scalar paths are read, never the
    whole payload.
    """
    return f"""
        SELECT
          o.dataset_url,
          MIN(o.publisher_name) AS publisher_name,
          SAFE_CAST(JSON_VALUE(o.location, '$.latitude')  AS FLOAT64) AS lat,
          SAFE_CAST(JSON_VALUE(o.location, '$.longitude') AS FLOAT64) AS lng,
          MIN(
            COALESCE(
              JSON_VALUE(o.location,  '$.postal_code'),
              JSON_VALUE(o.json_data, '$.location.address.postalCode')
            )
          ) AS postal_code,
          MIN(TO_JSON_STRING(o.location)) AS location_json,
          STRING_AGG(
            DISTINCT JSON_VALUE(o.json_data, '$.location.name'), ' | '
            ORDER BY JSON_VALUE(o.json_data, '$.location.name')
          ) AS location_names,
          ANY_VALUE(o.country_name)  AS country_name,
          ANY_VALUE(o.district_code) AS district_code,
          ANY_VALUE(o.district_name) AS district_name,
          STRING_AGG(DISTINCT o.kind ORDER BY o.kind) AS kinds,
          COUNT(*) AS opportunity_count
        FROM `{opportunities_table}` o
        WHERE COALESCE(o.kind, '') != 'Slot'
          AND o.location IS NOT NULL
          AND SAFE_CAST(JSON_VALUE(o.location, '$.latitude')  AS FLOAT64) IS NOT NULL
          AND SAFE_CAST(JSON_VALUE(o.location, '$.longitude') AS FLOAT64) IS NOT NULL
        GROUP BY o.dataset_url, lat, lng
    """


def fetch_oa_points() -> pd.DataFrame:
    """Run the point query and return the raw result frame."""
    sql = build_query(bigquery_ops.table_id(bigquery_ops.OPPORTUNITIES_TABLE))
    logger.info("Querying distinct OpenActive location points")
    points = bigquery_ops.run_query(sql)
    logger.info("Fetched %d distinct (dataset_url, lat, lng) points", len(points))
    return points


def split_by_scope(points: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Reduce the raw points to the England in-scope set, returning scope counts.

    Active Places covers England only, so the headline coverage figures need both
    sides on the same denominator. The excluded counts come back alongside so the
    report can state what was set aside rather than quietly dropping it.
    """
    total = len(points)

    in_envelope = (
        points["lat"].between(GB_LAT_MIN, GB_LAT_MAX)
        & points["lng"].between(GB_LNG_MIN, GB_LNG_MAX)
    )
    out_of_envelope = int((~in_envelope).sum())
    points = points[in_envelope]

    country = points["country_name"].fillna("").str.strip()
    is_england = country == ENGLAND
    unknown_country = int((country == "").sum())
    other_country = int((~is_england & (country != "")).sum())

    england = points[is_england].reset_index(drop=True)
    counts = {
        "total_points": total,
        "out_of_envelope": out_of_envelope,
        "other_country": other_country,
        "unknown_country": unknown_country,
        "england": len(england),
    }
    logger.info(
        "OA points: %d total, %d out of GB envelope, %d non-England, "
        "%d unknown country, %d in scope (England)",
        total, out_of_envelope, other_country, unknown_country, len(england),
    )
    return england, counts
