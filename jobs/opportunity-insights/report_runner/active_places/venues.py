"""Collapse distinct OpenActive location points into "venues".

The same physical venue is routinely published with slightly different
coordinates — by different publishers, and sometimes by the same publisher for
different opportunity kinds. Counting raw points would inflate the OpenActive
side of the comparison and overstate how much of the data is missing from Active
Places, so points are single-link clustered and each cluster treated as one
venue.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import matching

logger = logging.getLogger(__name__)


def _join_distinct(values: pd.Series) -> str:
    """Pipe-join the distinct non-empty values of a column, sorted for stability."""
    cleaned = {str(v).strip() for v in values.dropna() if str(v).strip()}
    return "|".join(sorted(cleaned))


def _join_distinct_names(values: pd.Series) -> str:
    """Pipe-join the distinct venue names across a cluster's points.

    Each point already arrives with its own names pipe-joined by BigQuery, so they
    are split back out before being de-duplicated across the cluster.
    """
    names: set[str] = set()
    for value in values.dropna():
        names.update(part.strip() for part in str(value).split("|") if part.strip())
    return " | ".join(sorted(names))


def _first_postcode(values: pd.Series) -> object:
    """The venue's postcode key: the first non-empty value among its points."""
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _join_distinct_kinds(values: pd.Series) -> str:
    """Pipe-join the distinct kinds across members, whose values are comma-joined."""
    kinds: set[str] = set()
    for value in values.dropna():
        kinds.update(part.strip() for part in str(value).split(",") if part.strip())
    return "|".join(sorted(kinds))


def build_venues(points: pd.DataFrame, cluster_metres: float) -> tuple[pd.DataFrame, pd.Series]:
    """Cluster ``points`` into venues; return the venue frame and cluster diameters.

    ``cluster_metres`` of 0 disables clustering, making every point its own venue.
    The returned frame is indexed 0..n-1 in ``venue_id`` order so its positional
    index lines up with the coordinate arrays used for matching.
    """
    x, y = matching.to_bng(points["lat"].values, points["lng"].values)
    points = points.assign(_x=x, _y=y)

    if cluster_metres > 0:
        labels = matching.cluster_points(x, y, cluster_metres)
    else:
        labels = np.arange(len(points), dtype=np.int64)
        logger.info("Clustering disabled: %d points treated as %d venues", len(points), len(points))
    points = points.assign(venue_id=labels)

    diameters = matching.cluster_diameters(x, y, labels)

    venues = points.groupby("venue_id", sort=True).agg(
        x=("_x", "mean"),
        y=("_y", "mean"),
        oa_point_count=("dataset_url", "size"),
        oa_dataset_count=("dataset_url", "nunique"),
        oa_dataset_urls=("dataset_url", _join_distinct),
        oa_publisher_names=("publisher_name", _join_distinct),
        oa_postal_codes=("postal_code", _join_distinct),
        oa_postcode_key=("postcode_key", _first_postcode),
        oa_location_names=("location_names", _join_distinct_names),
        oa_location_json=("location_json", _join_distinct),
        oa_kinds=("kinds", _join_distinct_kinds),
        oa_opportunity_count=("opportunity_count", "sum"),
        district_code=("district_code", _join_distinct),
        district_name=("district_name", _join_distinct),
        oa_centroid_points=("is_centroid_derived", "sum"),
    ).reset_index()

    # A venue is treated as centroid-derived only when every contributing point
    # is: one real coordinate among its members is enough to locate it.
    venues["is_centroid_derived"] = venues["oa_centroid_points"] == venues["oa_point_count"]

    venue_lat, venue_lng = matching.from_bng(venues["x"].values, venues["y"].values)
    venues["oa_lat"] = venue_lat
    venues["oa_lng"] = venue_lng
    venues["venue_diameter_metres"] = diameters.reindex(venues["venue_id"]).values

    logger.info(
        "Built %d venues from %d points (max cluster diameter %.0fm, %d over 250m)",
        len(venues), len(points), diameters.max() if len(diameters) else 0.0,
        int((diameters > 250).sum()),
    )
    return venues, diameters
