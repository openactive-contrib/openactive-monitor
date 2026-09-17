"""Turn the matched site/venue pairs into the report's output frames."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import matching

logger = logging.getLogger(__name__)

DISTANCE_BUCKETS = (25, 50, 100, 250, 500, 1000)

# Rows kept for the dashboard's "what to chase next" panel; the report shows fewer.
TOP_UNMATCHED_VENUES = 50

# Local authorities below this many sites are excluded from the "worst coverage"
# ranking, where a handful of sites makes the percentage meaningless.
MIN_SITES_FOR_RANKING = 20

SITE_OUTPUT_COLUMNS = {
    "Site ID": "site_id",
    "Site Name": "site_name",
    "Postcode": "postcode",
    "Local Authority Code": "local_authority_code",
    "Local Authority Name": "local_authority_name",
    "Region Code": "region_code",
    "Region Name": "region_name",
    "Ownership Type Group": "ownership_type_group",
    "Management Type Group": "management_type_group",
    "lat": "site_lat",
    "long": "site_lng",
}


@dataclass
class CoverageResults:
    """Everything the CSV writers and the markdown renderer need."""

    mapping: pd.DataFrame
    unmatched_sites: pd.DataFrame
    unmatched_venues: pd.DataFrame
    coverage_by_la: pd.DataFrame
    coverage_by_region: pd.DataFrame
    coverage_by_ownership: pd.DataFrame
    coverage_by_management: pd.DataFrame
    coverage_by_facility_type: pd.DataFrame
    publisher_coverage: pd.DataFrame
    coordinate_provenance: pd.DataFrame
    match_methods: pd.DataFrame
    unmatched_venues_by_district: pd.DataFrame
    top_unmatched_venues: pd.DataFrame
    name_examples: pd.DataFrame
    unmatched_venues_by_publisher: pd.DataFrame
    distance_sensitivity: pd.DataFrame
    stats: dict = field(default_factory=dict)


def _coverage_by(sites: pd.DataFrame, matched: pd.Series, *group_columns: str) -> pd.DataFrame:
    """Sites total / matched / missing / coverage % grouped by the given columns."""
    grouped = sites.assign(_matched=matched).groupby(list(group_columns), dropna=False).agg(
        sites_total=("Site ID", "size"),
        sites_matched=("_matched", "sum"),
    ).reset_index()
    grouped["sites_missing"] = grouped["sites_total"] - grouped["sites_matched"]
    grouped["coverage_pct"] = (100 * grouped["sites_matched"] / grouped["sites_total"]).round(1)
    return grouped.sort_values("sites_total", ascending=False).reset_index(drop=True)


def build_results(sites: pd.DataFrame,
                  venues: pd.DataFrame,
                  pairs: pd.DataFrame,
                  site_xy: tuple[np.ndarray, np.ndarray],
                  venue_xy: tuple[np.ndarray, np.ndarray],
                  buffer_metres: float,
                  points: pd.DataFrame,
                  postcode_max_metres: float,
                  name_max_metres: float,
                  name_threshold: float) -> CoverageResults:
    """Assemble every output frame from the matched pairs."""
    sites_out = sites.rename(columns=SITE_OUTPUT_COLUMNS)
    site_matched = pd.Series(False, index=sites.index)
    site_matched.iloc[pairs["site_idx"].unique()] = True
    venue_matched = pd.Series(False, index=venues.index)
    venue_matched.iloc[pairs["venue_idx"].unique()] = True

    # --- mapping table: one row per (site, venue) pair within the buffer --------
    mapping = pd.concat(
        [
            sites_out.iloc[pairs["site_idx"].values][list(SITE_OUTPUT_COLUMNS.values())
                                                     + ["ap_facility_count", "ap_facility_types"]]
            .reset_index(drop=True),
            venues.iloc[pairs["venue_idx"].values][[
                "venue_id", "oa_location_names", "oa_lat", "oa_lng", "oa_point_count",
                "oa_dataset_count", "oa_dataset_urls", "oa_publisher_names", "oa_postal_codes",
                "oa_kinds", "oa_opportunity_count", "oa_location_json",
            ]].reset_index(drop=True),
            pairs[["distance_metres", "match_method", "name_similarity",
                   "spatial_match", "postcode_match",
                   "is_primary_for_site", "is_primary_for_venue",
                   "is_mutual_best"]].reset_index(drop=True),
        ],
        axis=1,
    )
    mapping["distance_metres"] = mapping["distance_metres"].round(1)
    mapping = mapping.sort_values(["local_authority_name", "site_name", "distance_metres"])

    # --- unmatched sides, each carrying how near the nearest miss was ----------
    nearest_venue_idx, nearest_venue_m = matching.nearest_distance(site_xy, venue_xy)
    nearest_site_idx, nearest_site_m = matching.nearest_distance(venue_xy, site_xy)

    unmatched_sites = sites_out[~site_matched.values].copy()
    unmatched_positions = np.flatnonzero(~site_matched.values)
    unmatched_sites["nearest_oa_venue_metres"] = nearest_venue_m[unmatched_positions].round(1)
    near_ids = nearest_venue_idx[unmatched_positions]
    unmatched_sites["nearest_oa_publisher_names"] = np.where(
        near_ids >= 0, venues["oa_publisher_names"].values[near_ids], "",
    )
    unmatched_sites = unmatched_sites.drop(columns=["ap_facility_subtypes"], errors="ignore")
    unmatched_sites = unmatched_sites.sort_values("nearest_oa_venue_metres")

    unmatched_venues = venues[~venue_matched.values].copy()
    unmatched_venue_positions = np.flatnonzero(~venue_matched.values)
    unmatched_venues["nearest_ap_site_metres"] = nearest_site_m[unmatched_venue_positions].round(1)
    near_site_ids = nearest_site_idx[unmatched_venue_positions]
    unmatched_venues["nearest_ap_site_name"] = np.where(
        near_site_ids >= 0, sites_out["site_name"].values[near_site_ids], "",
    )
    unmatched_venues = unmatched_venues.drop(columns=["x", "y"]).sort_values(
        "oa_opportunity_count", ascending=False
    )

    # --- coverage breakdowns ---------------------------------------------------
    coverage_by_la = _coverage_by(sites, site_matched, "Local Authority Code", "Local Authority Name")
    venues_per_district = (
        venues.assign(_matched=venue_matched.values)
        .groupby("district_code", dropna=False)
        .agg(oa_venues_in_la=("venue_id", "size"), oa_venues_matched=("_matched", "sum"))
        .reset_index()
    )
    coverage_by_la = coverage_by_la.merge(
        venues_per_district, left_on="Local Authority Code", right_on="district_code", how="left"
    ).drop(columns=["district_code"])
    coverage_by_la[["oa_venues_in_la", "oa_venues_matched"]] = (
        coverage_by_la[["oa_venues_in_la", "oa_venues_matched"]].fillna(0).astype(int)
    )
    coverage_by_la["oa_venues_unmatched"] = (
        coverage_by_la["oa_venues_in_la"] - coverage_by_la["oa_venues_matched"]
    )
    coverage_by_la = coverage_by_la.rename(columns={
        "Local Authority Code": "local_authority_code",
        "Local Authority Name": "local_authority_name",
    })

    coverage_by_region = _coverage_by(sites, site_matched, "Region Name")
    coverage_by_ownership = _coverage_by(sites, site_matched, "Ownership Type Group")
    coverage_by_management = _coverage_by(sites, site_matched, "Management Type Group")

    # A site qualifies through several facilities, so it is counted once per
    # distinct facility type it offers. Rows therefore sum to more than the site total.
    exploded = sites.assign(_matched=site_matched.values)
    exploded = exploded.assign(facility_type=exploded["ap_facility_types"].str.split("|")).explode(
        "facility_type"
    )
    coverage_by_facility_type = _coverage_by(exploded, exploded["_matched"], "facility_type")

    # --- publisher view --------------------------------------------------------
    publisher_pairs = mapping.assign(
        publisher=mapping["oa_publisher_names"].str.split("|")
    ).explode("publisher")
    publisher_pairs["publisher"] = publisher_pairs["publisher"].replace("", "<unknown>").fillna("<unknown>")
    publisher_coverage = publisher_pairs.groupby("publisher").agg(
        ap_sites_covered=("site_id", "nunique"),
        oa_venues=("venue_id", "nunique"),
        local_authorities=("local_authority_code", "nunique"),
    ).reset_index().sort_values("ap_sites_covered", ascending=False)

    publishers_per_site = publisher_pairs.groupby("site_id")["publisher"].nunique()
    sites_multi_publisher = int((publishers_per_site > 1).sum())

    name_examples = mapping[mapping["match_method"] == "name"].nlargest(
        20, "oa_opportunity_count"
    )[["site_name", "oa_location_names", "local_authority_name",
       "distance_metres", "name_similarity"]]

    top_unmatched_venues = unmatched_venues.nlargest(TOP_UNMATCHED_VENUES, "oa_opportunity_count")[[
        "oa_location_names", "oa_publisher_names", "district_name",
        "oa_opportunity_count", "nearest_ap_site_name", "nearest_ap_site_metres",
    ]]

    unmatched_venues_by_district = (
        unmatched_venues.groupby("district_name", dropna=False)
        .agg(unmatched_venues=("venue_id", "size"),
             opportunity_count=("oa_opportunity_count", "sum"))
        .reset_index().sort_values("unmatched_venues", ascending=False)
    )
    unmatched_by_publisher = unmatched_venues.assign(
        publisher=unmatched_venues["oa_publisher_names"].str.split("|")
    ).explode("publisher")
    unmatched_by_publisher["publisher"] = (
        unmatched_by_publisher["publisher"].replace("", "<unknown>").fillna("<unknown>")
    )
    unmatched_venues_by_publisher = (
        unmatched_by_publisher.groupby("publisher")
        .agg(unmatched_venues=("venue_id", "size"),
             opportunity_count=("oa_opportunity_count", "sum"))
        .reset_index().sort_values("unmatched_venues", ascending=False)
    )

    # --- match-method breakdown ------------------------------------------------
    match_methods = pairs.groupby("match_method").agg(
        pairs=("site_idx", "size"),
        sites=("site_idx", "nunique"),
        venues=("venue_idx", "nunique"),
        median_distance_metres=("distance_metres", "median"),
    ).reset_index().sort_values("pairs", ascending=False)
    match_methods["median_distance_metres"] = match_methods["median_distance_metres"].round(1)

    name_pairs = pairs[pairs["match_method"] == "name"]

    # These three must be additive, because a dashboard plots them as a waterfall.
    # A name pair may attach to a site some other channel already matched — its job
    # there was to rescue the *venue* — so only genuinely new sites are counted.
    spatial_sites = set(pairs.loc[pairs["spatial_match"], "site_idx"])
    postcode_sites = set(pairs.loc[pairs["postcode_match"], "site_idx"]).difference(spatial_sites)
    name_sites = set(name_pairs["site_idx"]).difference(spatial_sites | postcode_sites)
    spatial_only_sites = len(spatial_sites)
    postcode_added_sites = len(postcode_sites)
    name_added_sites = len(name_sites)

    stronger_venues = set(pairs.loc[pairs["match_method"] != "name", "venue_idx"])
    name_rescued_venues = len(set(name_pairs["venue_idx"]).difference(stronger_venues))

    # --- distance sensitivity --------------------------------------------------
    # Whole numbers stay ints so they render as "200" rather than "200.0".
    thresholds = sorted(set(DISTANCE_BUCKETS) | {buffer_metres})
    thresholds = [int(t) if float(t).is_integer() else t for t in thresholds]
    sensitivity = pd.DataFrame({
        "threshold_metres": thresholds,
        "sites_matched": [int((nearest_venue_m <= t).sum()) for t in thresholds],
        "is_configured_buffer": [float(t) == float(buffer_metres) for t in thresholds],
    })
    sensitivity["coverage_pct"] = (100 * sensitivity["sites_matched"] / len(sites)).round(1)

    # --- postcode diagnostic (not used for matching) ---------------------------
    # `location.postal_code` is populated by ingestion only when the feed supplied
    # no `geo` block, so a venue carrying one is precisely a venue whose coordinates
    # were derived from a postcode centroid. The count therefore doubles as a
    # measure of how much centroid imprecision could be affecting the match rate.
    oa_postcodes = set()
    for value in venues["oa_postal_codes"]:
        oa_postcodes.update(part for part in str(value).upper().replace(" ", "").split("|") if part)
    unmatched_site_postcodes = matching.normalise_postcode(unmatched_sites["postcode"])
    postcode_rescuable = int(unmatched_site_postcodes.isin(oa_postcodes).sum())
    postcode_derived_venues = int((venues["oa_postal_codes"].astype(str).str.strip() != "").sum())

    # --- coordinate provenance, per publisher ----------------------------------
    # A point sitting exactly on a postcode centroid was geocoded from a postcode
    # rather than surveyed, so it cannot be expected to fall within the buffer of
    # the building it belongs to. Splitting this by publisher shows which feeds
    # the coverage figure can and cannot speak to.
    points = points.assign(
        publisher=points["publisher_name"].fillna("").replace("", "<unknown>")
    )
    provenance = points.groupby("publisher").agg(
        points=("lat", "size"),
        centroid_points=("is_centroid_derived", "sum"),
    ).reset_index()
    provenance["centroid_pct"] = (100 * provenance["centroid_points"] / provenance["points"]).round(1)
    provenance = provenance.sort_values("points", ascending=False).reset_index(drop=True)

    centroid_points_total = int(points["is_centroid_derived"].sum())
    centroid_venues = int(venues["is_centroid_derived"].sum())
    # The headline is dominated by whichever publisher geocodes from postcodes the
    # most, so report the rate with that publisher set aside as well.
    top_centroid = provenance.sort_values("centroid_points", ascending=False).head(1)
    top_centroid_publisher = top_centroid["publisher"].iloc[0] if len(top_centroid) else ""
    rest = points[points["publisher"] != top_centroid_publisher]
    centroid_pct_excluding_top = (
        round(100 * rest["is_centroid_derived"].mean(), 1) if len(rest) else 0.0
    )

    stats = {
        "sites_total": len(sites),
        "sites_matched": int(site_matched.sum()),
        "sites_missing": int((~site_matched).sum()),
        "coverage_pct": round(100 * site_matched.sum() / len(sites), 1),
        "venues_total": len(venues),
        "venues_matched": int(venue_matched.sum()),
        "venues_unmatched": int((~venue_matched).sum()),
        "venues_unmatched_pct": round(100 * (~venue_matched).sum() / len(venues), 1),
        "pairs": len(pairs),
        "sites_multi_publisher": sites_multi_publisher,
        "postcode_rescuable": postcode_rescuable,
        "local_authorities": int(sites["Local Authority Code"].nunique()),
        "buffer_metres": buffer_metres,
        "postcode_max_metres": postcode_max_metres,
        "name_max_metres": name_max_metres,
        "name_threshold": name_threshold,
        "name_pairs": len(name_pairs),
        "name_added_sites": name_added_sites,
        "name_rescued_venues": name_rescued_venues,
        "name_median_similarity": round(float(name_pairs["name_similarity"].median()), 2)
        if len(name_pairs) else 0.0,
        "name_median_distance": round(float(name_pairs["distance_metres"].median()), 1)
        if len(name_pairs) else 0.0,
        "spatial_only_sites": spatial_only_sites,
        "spatial_only_pct": round(100 * spatial_only_sites / len(sites), 1),
        "postcode_added_sites": postcode_added_sites,
        "postcode_lift_pct": round(
            100 * postcode_added_sites / spatial_only_sites, 1
        ) if spatial_only_sites else 0.0,
        "sites_with_postcode_key": int(pd.notna(points["postcode_key"]).sum()),
        "postcode_derived_venues": postcode_derived_venues,
        "postcode_derived_pct": round(100 * postcode_derived_venues / len(venues), 1),
        "centroid_diagnostic": bool(points["centroid_diagnostic"].any()),
        "centroid_points": centroid_points_total,
        "centroid_points_pct": round(100 * centroid_points_total / len(points), 1) if len(points) else 0.0,
        "centroid_venues": centroid_venues,
        "centroid_venues_pct": round(100 * centroid_venues / len(venues), 1),
        "top_centroid_publisher": top_centroid_publisher,
        "top_centroid_publisher_points": int(top_centroid["centroid_points"].iloc[0]) if len(top_centroid) else 0,
        "centroid_pct_excluding_top": centroid_pct_excluding_top,
    }
    logger.info("Coverage: %(sites_matched)d/%(sites_total)d sites (%(coverage_pct)s%%)", stats)

    return CoverageResults(
        mapping=mapping,
        unmatched_sites=unmatched_sites,
        unmatched_venues=unmatched_venues,
        coverage_by_la=coverage_by_la,
        coverage_by_region=coverage_by_region,
        coverage_by_ownership=coverage_by_ownership,
        coverage_by_management=coverage_by_management,
        coverage_by_facility_type=coverage_by_facility_type,
        publisher_coverage=publisher_coverage,
        coordinate_provenance=provenance,
        match_methods=match_methods,
        unmatched_venues_by_district=unmatched_venues_by_district,
        top_unmatched_venues=top_unmatched_venues,
        name_examples=name_examples,
        unmatched_venues_by_publisher=unmatched_venues_by_publisher,
        distance_sensitivity=sensitivity,
        stats=stats,
    )
