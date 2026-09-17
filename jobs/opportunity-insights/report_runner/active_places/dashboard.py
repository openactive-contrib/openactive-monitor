"""Build the JSON payload that feeds the Active Places coverage dashboard.

The markdown report is written for a person reading it top to bottom; this is the
same run reduced to the figures a dashboard plots. The two are generated from one
set of results, so they cannot drift apart.

Design notes for anyone consuming this file:

* ``schema_version`` changes whenever a key is removed or its meaning changes, so
  a dashboard can refuse a payload it does not understand.
* ``run_date`` keys the run. Appending successive payloads gives a coverage trend
  without anything here needing to know about history.
* Every local authority is included, not just the worst, because the natural view
  is a choropleth and a partial list would leave holes in the map. The per-record
  ``local_authority_code`` is the ONS code to join boundaries on.
* Lists that exist to drive a "what should we chase next" panel are truncated —
  the full detail is in the CSVs alongside.
* Numbers are numbers, never strings, and anything missing is ``null`` rather than
  ``NaN``, which is not valid JSON.
"""

from __future__ import annotations

import json
import logging
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .analysis import CoverageResults

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# Enough rows to act on, without turning the payload into a data dump.
TOP_UNMATCHED_VENUES = 50
TOP_UNMATCHED_DISTRICTS = 50


def _scalar(value: Any) -> Any:
    """Convert one pandas/numpy value into something ``json.dump`` accepts."""
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return None if math.isnan(number) or math.isinf(number) else round(number, 4)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if value is pd.NA or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _records(frame: pd.DataFrame, rename: dict[str, str] | None = None,
             limit: int | None = None) -> list[dict[str, Any]]:
    """Render a DataFrame as JSON-safe records, optionally renaming and truncating."""
    if frame.empty:
        return []
    if limit is not None:
        frame = frame.head(limit)
    if rename:
        frame = frame.rename(columns=rename)[list(rename.values())]
    return [{key: _scalar(value) for key, value in row.items()}
            for row in frame.to_dict("records")]


def build_payload(results: CoverageResults,
                  points_frame: pd.DataFrame,
                  scope_counts: dict[str, int],
                  data_version: str,
                  opportunities_table: str,
                  diameters: pd.Series,
                  cluster_metres: float) -> dict[str, Any]:
    """Assemble the dashboard payload from a completed run."""
    stats = results.stats

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_date": date.today().isoformat(),
        "source": {
            "opportunities_table": opportunities_table,
            "active_places_data_version": data_version,
            "geography_scope": "England",
            "excluded_kinds": ["Slot"],
        },
        "parameters": {
            "buffer_metres": _scalar(stats["buffer_metres"]),
            "postcode_max_metres": _scalar(stats["postcode_max_metres"]),
            "name_max_metres": _scalar(stats["name_max_metres"]),
            "name_threshold": _scalar(stats["name_threshold"]),
            "venue_cluster_metres": _scalar(cluster_metres),
        },
        # The single number the dashboard leads with, plus the counts behind it.
        "headline": {
            "coverage_pct": _scalar(stats["coverage_pct"]),
            "sites_total": _scalar(stats["sites_total"]),
            "sites_matched": _scalar(stats["sites_matched"]),
            "sites_missing": _scalar(stats["sites_missing"]),
            "local_authorities": _scalar(stats["local_authorities"]),
            "venues_total": _scalar(stats["venues_total"]),
            "venues_matched": _scalar(stats["venues_matched"]),
            "venues_unmatched": _scalar(stats["venues_unmatched"]),
            "venues_unmatched_pct": _scalar(stats["venues_unmatched_pct"]),
            "pairs": _scalar(stats["pairs"]),
        },
        # How the coverage was arrived at — the natural donut / waterfall.
        "channels": {
            "sites_by_proximity": _scalar(stats["spatial_only_sites"]),
            "sites_added_by_postcode": _scalar(stats["postcode_added_sites"]),
            "sites_added_by_name": _scalar(stats["name_added_sites"]),
            "name_pairs": _scalar(stats["name_pairs"]),
            "venues_rescued_by_name": _scalar(stats["name_rescued_venues"]),
            "postcode_lift_pct": _scalar(stats["postcode_lift_pct"]),
            "name_median_similarity": _scalar(stats["name_median_similarity"]),
            "name_median_distance_metres": _scalar(stats["name_median_distance"]),
            "breakdown": _records(results.match_methods, {
                "match_method": "method",
                "pairs": "pairs",
                "sites": "sites",
                "venues": "venues",
                "median_distance_metres": "median_distance_metres",
            }),
        },
        # Spatial channel only: what each threshold would buy. Plots as a curve, and
        # is the honest way to show that the headline depends on a chosen number.
        "distance_sensitivity": _records(results.distance_sensitivity, {
            "threshold_metres": "threshold_metres",
            "sites_matched": "sites_matched",
            "coverage_pct": "coverage_pct",
            "is_configured_buffer": "is_configured_buffer",
        }),
        "coverage_by_region": _records(results.coverage_by_region, {
            "Region Name": "region_name",
            "sites_total": "sites_total",
            "sites_matched": "sites_matched",
            "sites_missing": "sites_missing",
            "coverage_pct": "coverage_pct",
        }),
        # Every authority, for the map. Sorted worst-covered first so a dashboard
        # that simply takes the head gets the actionable end.
        "coverage_by_local_authority": _records(
            results.coverage_by_la.sort_values(["coverage_pct", "sites_missing"],
                                               ascending=[True, False]),
            {
                "local_authority_code": "local_authority_code",
                "local_authority_name": "local_authority_name",
                "sites_total": "sites_total",
                "sites_matched": "sites_matched",
                "sites_missing": "sites_missing",
                "coverage_pct": "coverage_pct",
                "oa_venues_in_la": "oa_venues",
                "oa_venues_unmatched": "oa_venues_unmatched",
            },
        ),
        "coverage_by_ownership": _records(results.coverage_by_ownership, {
            "Ownership Type Group": "group",
            "sites_total": "sites_total",
            "sites_matched": "sites_matched",
            "sites_missing": "sites_missing",
            "coverage_pct": "coverage_pct",
        }),
        "coverage_by_management": _records(results.coverage_by_management, {
            "Management Type Group": "group",
            "sites_total": "sites_total",
            "sites_matched": "sites_matched",
            "sites_missing": "sites_missing",
            "coverage_pct": "coverage_pct",
        }),
        # Facility type codes are raw: the export ships no code-to-label lookup.
        "coverage_by_facility_type": _records(results.coverage_by_facility_type, {
            "facility_type": "facility_type_code",
            "sites_total": "sites_total",
            "sites_matched": "sites_matched",
            "sites_missing": "sites_missing",
            "coverage_pct": "coverage_pct",
        }),
        "publishers": _records(results.publisher_coverage, {
            "publisher": "publisher",
            "ap_sites_covered": "ap_sites_covered",
            "oa_venues": "oa_venues",
            "local_authorities": "local_authorities",
        }),
        # Why coverage is a floor: points geocoded from a postcode cannot be
        # expected to sit on the building.
        "coordinate_provenance": {
            "diagnostic_available": _scalar(stats["centroid_diagnostic"]),
            "centroid_points": _scalar(stats["centroid_points"]),
            "centroid_points_pct": _scalar(stats["centroid_points_pct"]),
            "centroid_venues": _scalar(stats["centroid_venues"]),
            "top_centroid_publisher": stats["top_centroid_publisher"],
            "centroid_pct_excluding_top_publisher": _scalar(stats["centroid_pct_excluding_top"]),
            "by_publisher": _records(results.coordinate_provenance, {
                "publisher": "publisher",
                "points": "points",
                "centroid_points": "centroid_points",
                "centroid_pct": "centroid_pct",
            }),
        },
        "unmatched": {
            "venues_by_district": _records(results.unmatched_venues_by_district, {
                "district_name": "district_name",
                "unmatched_venues": "unmatched_venues",
                "opportunity_count": "opportunity_count",
            }, limit=TOP_UNMATCHED_DISTRICTS),
            "venues_by_publisher": _records(results.unmatched_venues_by_publisher, {
                "publisher": "publisher",
                "unmatched_venues": "unmatched_venues",
                "opportunity_count": "opportunity_count",
            }),
            "top_venues": _records(results.top_unmatched_venues, {
                "oa_location_names": "venue_name",
                "oa_publisher_names": "publisher",
                "district_name": "district_name",
                "oa_opportunity_count": "opportunity_count",
                "nearest_ap_site_name": "nearest_site_name",
                "nearest_ap_site_metres": "nearest_site_metres",
            }, limit=TOP_UNMATCHED_VENUES),
        },
        # What was set aside before matching, so a reader can see the denominator.
        "data_quality": {
            "oa_points_fetched": _scalar(scope_counts["total_points"]),
            "excluded_out_of_gb_envelope": _scalar(scope_counts["out_of_envelope"]),
            "excluded_other_country": _scalar(scope_counts["other_country"]),
            "excluded_unknown_country": _scalar(scope_counts["unknown_country"]),
            "oa_points_in_scope": _scalar(scope_counts["england"]),
            "oa_venues_after_clustering": _scalar(stats["venues_total"]),
            "max_cluster_diameter_metres": _scalar(diameters.max() if len(diameters) else 0.0),
            "clusters_over_250m": _scalar(int((diameters > 250).sum()) if len(diameters) else 0),
            "points_with_postcode": _scalar(stats["sites_with_postcode_key"]),
            "points_with_name": _scalar(
                int(points_frame["location_names"].notna().sum())
                if "location_names" in points_frame else 0
            ),
        },
    }
    return payload


def validate_payload(payload: dict[str, Any], sites_total: int) -> None:
    """Check the payload before it reaches a dashboard that cannot argue back."""
    headline = payload["headline"]
    channels = payload["channels"]
    assert (channels["sites_by_proximity"] + channels["sites_added_by_postcode"]
            + channels["sites_added_by_name"]) == headline["sites_matched"], \
        "channel waterfall does not reconcile to the headline"
    assert headline["sites_matched"] + headline["sites_missing"] == headline["sites_total"], \
        "headline counts do not add up"
    assert headline["sites_total"] == sites_total, "headline disagrees with the site universe"

    authorities = payload["coverage_by_local_authority"]
    assert sum(row["sites_total"] for row in authorities) == sites_total, \
        "per-authority totals do not sum to the universe"
    assert all(row["local_authority_code"] for row in authorities), \
        "an authority is missing its ONS code, which the map joins on"

    thresholds = [row["sites_matched"] for row in payload["distance_sensitivity"]]
    assert thresholds == sorted(thresholds), "sensitivity curve is not monotonic"
    assert any(row["is_configured_buffer"] for row in payload["distance_sensitivity"]), \
        "sensitivity curve has no point at the configured buffer"
    logger.info("Dashboard payload checks passed")


def write_payload(payload: dict[str, Any], path: Path) -> None:
    """Write the payload, refusing to emit NaN/Infinity so the file is valid JSON."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    logger.info("Wrote %s (%.0f KB)", path, path.stat().st_size / 1024)
