"""Spatial lookup for opportunity coordinates.

Ported from jobs/analyse-opportunities/analyse_separate_opportunities.py:20-84.
Builds STRtree indexes for UK regions, districts, and NHS trusts, then resolves
(longitude, latitude) pairs to (region, district, trust) name tuples with LRU
caching on the input coordinates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import geopandas as gpd
from shapely import STRtree
from shapely.geometry import Point

logger = logging.getLogger(__name__)

REGIONS_FILENAME = "000-location-regions.geojson"
DISTRICTS_FILENAME = "000-location-districts.geojson"
TRUSTS_FILENAME = "000-location-nhstrusts.geojson"

REGIONS_NAME_COLUMN = "eer18nm"
DISTRICTS_NAME_COLUMN = "LAD24NM"
TRUSTS_NAME_COLUMN = "TrustName"


@dataclass
class SpatialIndex:
    tree: STRtree
    geometries: object
    names: object


_regions_index: SpatialIndex | None = None
_districts_index: SpatialIndex | None = None
_trusts_index: SpatialIndex | None = None


def _build_spatial_index(gdf: gpd.GeoDataFrame, name_column: str) -> SpatialIndex:
    tree = STRtree(gdf.geometry.values)
    return SpatialIndex(tree=tree, geometries=gdf.geometry.values, names=gdf[name_column].values)


def _lookup_location(point: Point, index: SpatialIndex) -> str | None:
    candidates = index.tree.query(point)
    for idx in candidates:
        try:
            if index.geometries[idx].contains(point):
                return index.names[idx]
        except Exception:
            continue
    return None


def load_indexes(geo_dir: Path) -> None:
    """Load the three geojson shapefiles and build spatial indexes.

    Must be called once before :func:`lookup` is used. Re-calling rebuilds the
    indexes and clears the lookup cache.
    """
    global _regions_index, _districts_index, _trusts_index

    logger.info("Loading geojson shapefiles from %s", geo_dir)
    gdf_regions = gpd.read_file(str(geo_dir / REGIONS_FILENAME)).to_crs(4326)
    gdf_districts = gpd.read_file(str(geo_dir / DISTRICTS_FILENAME)).to_crs(4326)
    gdf_trusts = gpd.read_file(str(geo_dir / TRUSTS_FILENAME)).to_crs(4326)

    logger.info(
        "Building spatial indexes (regions=%d, districts=%d, trusts=%d)",
        len(gdf_regions), len(gdf_districts), len(gdf_trusts),
    )
    _regions_index = _build_spatial_index(gdf_regions, REGIONS_NAME_COLUMN)
    _districts_index = _build_spatial_index(gdf_districts, DISTRICTS_NAME_COLUMN)
    _trusts_index = _build_spatial_index(gdf_trusts, TRUSTS_NAME_COLUMN)
    lookup.cache_clear()


@lru_cache(maxsize=200_000)
def lookup(longitude: float | None, latitude: float | None) -> tuple[str | None, str | None, str | None]:
    """Return ``(region, district, trust)`` names for a coordinate.

    Any of the returned names can be ``None``. Returns ``(None, None, None)``
    if either coordinate is missing or point construction fails.
    """
    if longitude is None or latitude is None:
        return None, None, None
    if _regions_index is None or _districts_index is None or _trusts_index is None:
        raise RuntimeError("Spatial indexes not loaded — call load_indexes() first")
    try:
        point = Point(float(longitude), float(latitude))
    except (TypeError, ValueError):
        return None, None, None
    return (
        _lookup_location(point, _regions_index),
        _lookup_location(point, _districts_index),
        _lookup_location(point, _trusts_index),
    )
