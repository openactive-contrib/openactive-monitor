"""Spatial matching between Active Places sites and OpenActive location points.

Everything happens in British National Grid (EPSG:27700) metres. Both sides are
projected from WGS84 lat/lon through the *same* ``pyproj`` transformer rather
than using the eastings/northings the Active Places export ships: those came
from Sport England's own datum transformation and differ from pyproj's by a
median of ~2m (max ~5m). Using one transformer for both sides makes that
difference cancel instead of biasing every distance.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely import STRtree, distance, points

from . import names

logger = logging.getLogger(__name__)

# always_xy: inputs are (longitude, latitude), outputs are (easting, northing).
_TO_BNG = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
_FROM_BNG = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def to_bng(lat: np.ndarray, lng: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project WGS84 lat/lon arrays to EPSG:27700 eastings/northings in metres."""
    easting, northing = _TO_BNG.transform(np.asarray(lng, dtype=float), np.asarray(lat, dtype=float))
    return easting, northing


def from_bng(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project EPSG:27700 eastings/northings back to WGS84 lat/lon."""
    lng, lat = _FROM_BNG.transform(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
    return lat, lng


def _pairs_within(tree_xy: tuple[np.ndarray, np.ndarray],
                  query_xy: tuple[np.ndarray, np.ndarray],
                  metres: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """All (query index, tree index, distance) triples within ``metres``.

    Uses the ``dwithin`` predicate rather than buffering the query points: a
    buffer is a polygonal approximation of a circle and would silently drop true
    matches just inside the threshold.
    """
    tree_pts = points(tree_xy[0], tree_xy[1])
    query_pts = points(query_xy[0], query_xy[1])
    query_idx, tree_idx = STRtree(tree_pts).query(query_pts, predicate="dwithin", distance=metres)
    dists = distance(query_pts[query_idx], tree_pts[tree_idx])
    return query_idx, tree_idx, dists


class _UnionFind:
    """Minimal union-find over ``n`` integer labels, with path compression."""

    def __init__(self, n: int) -> None:
        self._parent = list(range(n))

    def find(self, a: int) -> int:
        parent = self._parent
        root = a
        while parent[root] != root:
            root = parent[root]
        while parent[a] != root:
            parent[a], a = root, parent[a]
        return root

    def union(self, a: int, b: int) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self._parent[root_b] = root_a


def cluster_points(x: np.ndarray, y: np.ndarray, radius: float) -> np.ndarray:
    """Single-link cluster points within ``radius`` metres; return a label per point.

    Single-link clustering can chain across a dense area, so the caller should
    inspect the cluster diameters this enables (see :func:`cluster_diameters`)
    rather than trusting the radius alone.
    """
    n = len(x)
    if n == 0:
        return np.empty(0, dtype=np.int64)

    query_idx, tree_idx, _ = _pairs_within((x, y), (x, y), radius)
    union_find = _UnionFind(n)
    for a, b in zip(query_idx.tolist(), tree_idx.tolist()):
        if a != b:
            union_find.union(a, b)

    roots = np.fromiter((union_find.find(i) for i in range(n)), dtype=np.int64, count=n)
    # Renumber the roots to a dense 0..k-1 range.
    _, labels = np.unique(roots, return_inverse=True)
    logger.info("Clustered %d points into %d venues at %gm", n, labels.max() + 1 if n else 0, radius)
    return labels


def cluster_diameters(x: np.ndarray, y: np.ndarray, labels: np.ndarray) -> pd.Series:
    """Bounding-box diagonal per cluster, in metres — a cheap chaining check."""
    frame = pd.DataFrame({"label": labels, "x": x, "y": y})
    extent = frame.groupby("label").agg(
        x_min=("x", "min"), x_max=("x", "max"),
        y_min=("y", "min"), y_max=("y", "max"),
    )
    return np.hypot(extent["x_max"] - extent["x_min"], extent["y_max"] - extent["y_min"])


def match_within(site_xy: tuple[np.ndarray, np.ndarray],
                 venue_xy: tuple[np.ndarray, np.ndarray],
                 buffer_metres: float) -> pd.DataFrame:
    """Every (site, venue) pair within ``buffer_metres``, with the distance."""
    site_idx, venue_idx, dists = _pairs_within(venue_xy, site_xy, buffer_metres)
    return pd.DataFrame({
        "site_idx": site_idx,
        "venue_idx": venue_idx,
        "distance_metres": dists,
    })


def normalise_postcode(series: pd.Series) -> pd.Series:
    """Strip everything but alphanumerics and upper-case, so the two sides join."""
    return (
        series.astype("string")
        .str.replace(r"[^A-Za-z0-9]", "", regex=True)
        .str.upper()
        .replace("", pd.NA)
    )


def match_by_postcode(site_postcodes: pd.Series,
                      venue_postcodes: pd.Series,
                      site_xy: tuple[np.ndarray, np.ndarray],
                      venue_xy: tuple[np.ndarray, np.ndarray],
                      max_metres: float) -> pd.DataFrame:
    """Every (site, venue) pair sharing a normalised postcode, within ``max_metres``.

    This is the channel that rescues venues whose coordinates are a postcode
    centroid: the centroid of a postcode unit is often further from the building
    than the spatial buffer allows, but the postcode itself still identifies the
    place. The distance cap keeps out pairs that share a postcode string but are
    implausibly far apart, which indicates bad data on one side or the other.
    """
    sites = pd.DataFrame({
        "site_idx": np.arange(len(site_postcodes)),
        "pc": normalise_postcode(site_postcodes).values,
    }).dropna(subset=["pc"])
    venues = pd.DataFrame({
        "venue_idx": np.arange(len(venue_postcodes)),
        "pc": normalise_postcode(venue_postcodes).values,
    }).dropna(subset=["pc"])
    pairs = sites.merge(venues, on="pc")[["site_idx", "venue_idx"]]
    if pairs.empty:
        return pd.DataFrame({"site_idx": [], "venue_idx": [], "distance_metres": []})

    site_i = pairs["site_idx"].to_numpy()
    venue_i = pairs["venue_idx"].to_numpy()
    pairs["distance_metres"] = np.hypot(
        site_xy[0][site_i] - venue_xy[0][venue_i],
        site_xy[1][site_i] - venue_xy[1][venue_i],
    )
    kept = pairs[pairs["distance_metres"] <= max_metres].reset_index(drop=True)
    logger.info(
        "Postcode channel: %d shared-postcode pairs, %d within %gm",
        len(pairs), len(kept), max_metres,
    )
    return kept


# Ordered by how much the evidence is trusted; used to pick the primary pair.
MATCH_METHOD_TIERS = {
    "spatial_and_postcode": 0,
    "spatial": 1,
    "postcode": 2,
    "spatial_centroid_only": 3,
    "name": 4,
}


def match_by_name(site_names: pd.Series,
                  venue_names: pd.Series,
                  site_xy: tuple[np.ndarray, np.ndarray],
                  venue_xy: tuple[np.ndarray, np.ndarray],
                  unmatched_sites: np.ndarray,
                  unmatched_venues: np.ndarray,
                  max_metres: float,
                  threshold: float,
                  place_tokens: frozenset[str] = frozenset()) -> pd.DataFrame:
    """Last-resort channel: pair a site and a venue whose names clearly agree.

    A pair qualifies when *either* side is still unmatched, so an unmatched venue
    can attach to a site another publisher already covers — the mapping is
    many-to-many, and a site legitimately appears under several venues. Pairs where
    both sides are already matched are skipped: they would add no coverage on either
    side and only invite false positives.

    Candidates come from within ``max_metres`` and the best-scoring one above
    ``threshold`` wins, keeping a name match anchored to a plausible location rather
    than pairing two identically-named venues at opposite ends of the country.
    """
    if len(unmatched_sites) == 0 and len(unmatched_venues) == 0:
        return _empty_name_pairs()

    site_idx, venue_idx, dists = _pairs_within(venue_xy, site_xy, max_metres)
    if len(site_idx) == 0:
        return _empty_name_pairs()

    site_open = np.zeros(len(site_names), dtype=bool)
    site_open[unmatched_sites] = True
    venue_open = np.zeros(len(venue_names), dtype=bool)
    venue_open[unmatched_venues] = True
    eligible = site_open[site_idx] | venue_open[venue_idx]
    site_idx, venue_idx, dists = site_idx[eligible], venue_idx[eligible], dists[eligible]
    if len(site_idx) == 0:
        return _empty_name_pairs()

    site_name_values = site_names.to_numpy()
    venue_name_values = venue_names.to_numpy()

    # The same (site, venue) name pairing recurs across candidates; score it once.
    cache: dict[tuple[int, int], float] = {}
    scores = np.empty(len(site_idx), dtype=float)
    for position, (s_i, v_i) in enumerate(zip(site_idx, venue_idx)):
        key = (s_i, v_i)
        score = cache.get(key)
        if score is None:
            score = names.similarity(
                venue_name_values[v_i], site_name_values[s_i], place_tokens
            )
            cache[key] = score
        scores[position] = score

    candidates = pd.DataFrame({
        "site_idx": site_idx,
        "venue_idx": venue_idx,
        "distance_metres": dists,
        "name_similarity": scores,
    })
    kept = candidates[candidates["name_similarity"] >= threshold]
    # At most one name pair per venue, and per site, so the channel cannot fan out.
    kept = kept.sort_values(["name_similarity", "distance_metres"], ascending=[False, True])
    kept = kept.drop_duplicates("venue_idx").drop_duplicates("site_idx").reset_index(drop=True)
    logger.info(
        "Name channel: %d eligible candidate pairs within %gm, %d above similarity %.2f",
        len(candidates), max_metres, len(kept), threshold,
    )
    return kept


def _empty_name_pairs() -> pd.DataFrame:
    return pd.DataFrame({"site_idx": [], "venue_idx": [], "distance_metres": [],
                         "name_similarity": []})


def combine_channels(spatial: pd.DataFrame,
                     postcode: pd.DataFrame,
                     venue_is_centroid: np.ndarray) -> pd.DataFrame:
    """Merge the two channels into one pair table with a ``match_method`` label.

    A venue whose coordinates are a postcode centroid, matched spatially but with
    no postcode agreement, is labelled ``spatial_centroid_only``: its proximity is
    an artefact of where the postcode centroid happens to fall rather than evidence
    about the venue, so it is ranked below the other methods when choosing which
    pair is primary. It still counts as a match.
    """
    spatial = spatial.assign(spatial_match=True)
    postcode = postcode.assign(postcode_match=True)
    pairs = spatial.merge(
        postcode, on=["site_idx", "venue_idx"], how="outer", suffixes=("", "_pc")
    )
    # Either side may be absent for a given pair; the distances agree where both are.
    pairs["distance_metres"] = pairs["distance_metres"].fillna(pairs["distance_metres_pc"])
    pairs = pairs.drop(columns=["distance_metres_pc"])
    pairs["spatial_match"] = pairs["spatial_match"].notna() & (pairs["spatial_match"] == True)
    pairs["postcode_match"] = pairs["postcode_match"].notna() & (pairs["postcode_match"] == True)
    pairs[["site_idx", "venue_idx"]] = pairs[["site_idx", "venue_idx"]].astype(np.int64)

    is_centroid = venue_is_centroid[pairs["venue_idx"].to_numpy()]
    pairs["match_method"] = np.select(
        [
            pairs["spatial_match"] & pairs["postcode_match"],
            pairs["spatial_match"] & ~pairs["postcode_match"] & ~is_centroid,
            pairs["spatial_match"] & ~pairs["postcode_match"] & is_centroid,
        ],
        ["spatial_and_postcode", "spatial", "spatial_centroid_only"],
        default="postcode",
    )
    pairs["match_tier"] = pairs["match_method"].map(MATCH_METHOD_TIERS)
    return add_primary_flags(pairs)


def append_name_pairs(pairs: pd.DataFrame, name_pairs: pd.DataFrame) -> pd.DataFrame:
    """Add the last-resort name pairs to the combined table and re-flag primaries."""
    if name_pairs.empty:
        pairs["name_similarity"] = np.nan
        return pairs
    name_pairs = name_pairs.assign(
        spatial_match=False,
        postcode_match=False,
        match_method="name",
        match_tier=MATCH_METHOD_TIERS["name"],
    )
    combined = pd.concat([pairs, name_pairs], ignore_index=True)
    combined["name_similarity"] = combined.get("name_similarity")
    return add_primary_flags(combined.drop(columns=[
        "is_primary_for_site", "is_primary_for_venue", "is_mutual_best",
    ], errors="ignore"))


def add_primary_flags(pairs: pd.DataFrame) -> pd.DataFrame:
    """Flag which pair to treat as the one-to-one reading for each side.

    Ranks on (tier, distance) so that a close-but-weak coincidence never outranks a
    slightly more distant pair that both channels agree on. Every pair is kept; the
    flags only mark the preferred one.
    """
    if pairs.empty:
        for column in ("is_primary_for_site", "is_primary_for_venue", "is_mutual_best"):
            pairs[column] = pd.Series(dtype=bool)
        return pairs

    # venue_idx / site_idx in the sort key make ties deterministic across runs.
    by_site = pairs.sort_values(["site_idx", "match_tier", "distance_metres", "venue_idx"])
    pairs["is_primary_for_site"] = pairs.index.isin(
        by_site.groupby("site_idx", sort=False).head(1).index
    )
    by_venue = pairs.sort_values(["venue_idx", "match_tier", "distance_metres", "site_idx"])
    pairs["is_primary_for_venue"] = pairs.index.isin(
        by_venue.groupby("venue_idx", sort=False).head(1).index
    )
    pairs["is_mutual_best"] = pairs["is_primary_for_site"] & pairs["is_primary_for_venue"]
    return pairs


def nearest_distance(from_xy: tuple[np.ndarray, np.ndarray],
                     to_xy: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """For each point in ``from_xy``, the index of and distance to its nearest neighbour.

    Unmatched entries come back as index ``-1`` and distance ``inf`` (which only
    happens when ``to_xy`` is empty). One pass of this powers both the
    distance-sensitivity table and the near-miss column in the unmatched CSVs.
    """
    n = len(from_xy[0])
    nearest_idx = np.full(n, -1, dtype=np.int64)
    nearest_m = np.full(n, np.inf, dtype=float)
    if n == 0 or len(to_xy[0]) == 0:
        return nearest_idx, nearest_m

    from_pts = points(from_xy[0], from_xy[1])
    to_pts = points(to_xy[0], to_xy[1])
    (input_idx, tree_idx), dists = STRtree(to_pts).query_nearest(
        from_pts, all_matches=False, return_distance=True
    )
    nearest_idx[input_idx] = tree_idx
    nearest_m[input_idx] = dists
    return nearest_idx, nearest_m
