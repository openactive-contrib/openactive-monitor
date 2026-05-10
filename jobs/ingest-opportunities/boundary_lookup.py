"""Spatial lookup mapping (latitude, longitude) -> (district_name, region_name).

Lazily loads UK Local Authority Districts and UK Regions GeoJSON boundaries
from ``volume-1/data-analysis/`` (reprojected to WGS84) and resolves a
coordinate to ``(district_name, region_name)`` via shapely STRtree spatial
indexes.

Lookups are cached with ``lru_cache`` because many opportunities share a
venue, so the same coordinate is queried repeatedly during a run.

Pattern mirrors ``jobs/opportunity-insights/geolookup.py``.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import geopandas as gpd
from shapely import STRtree
from shapely.geometry import Point

logger = logging.getLogger(__name__)

# volume-1/data-analysis/ relative to this file (jobs/ingest-opportunities/boundary_lookup.py)
_BOUNDARY_DIR = Path(__file__).resolve().parents[2] / "volume-1" / "data-analysis"

DISTRICTS_FILENAME = "000-location-districts.geojson"
REGIONS_FILENAME = "000-location-regions.geojson"

DISTRICTS_NAME_COLUMN = "LAD24NM"
REGIONS_NAME_COLUMN = "eer18nm"


@dataclass
class _SpatialIndex:
    tree: STRtree
    geometries: object
    names: object


_districts_index: _SpatialIndex | None = None
_regions_index: _SpatialIndex | None = None
_load_lock = threading.Lock()
_load_attempted = False
_load_succeeded = False


def _build_spatial_index(gdf: gpd.GeoDataFrame, name_column: str) -> _SpatialIndex:
    tree = STRtree(gdf.geometry.values)
    return _SpatialIndex(tree=tree, geometries=gdf.geometry.values, names=gdf[name_column].values)


def _try_ensure_indexes_loaded() -> bool:
    """Load the boundary GeoDataFrames once. Returns True if indexes are usable."""
    global _districts_index, _regions_index, _load_attempted, _load_succeeded

    if _load_attempted:
        return _load_succeeded

    with _load_lock:
        if _load_attempted:
            return _load_succeeded
        try:
            logger.info("Loading boundary geojson files from %s", _BOUNDARY_DIR)
            districts_gdf = gpd.read_file(str(_BOUNDARY_DIR / DISTRICTS_FILENAME)).to_crs(4326)
            regions_gdf = gpd.read_file(str(_BOUNDARY_DIR / REGIONS_FILENAME)).to_crs(4326)
            logger.info(
                "Building boundary spatial indexes (districts=%d, regions=%d)",
                len(districts_gdf),
                len(regions_gdf),
            )
            _districts_index = _build_spatial_index(districts_gdf, DISTRICTS_NAME_COLUMN)
            _regions_index = _build_spatial_index(regions_gdf, REGIONS_NAME_COLUMN)
            _load_succeeded = True
        except Exception:
            logger.exception("Failed to load boundary indexes; boundary lookups disabled")
            _load_succeeded = False
        finally:
            _load_attempted = True
        return _load_succeeded


def _lookup_in_index(point: Point, index: _SpatialIndex) -> str | None:
    for idx in index.tree.query(point):
        try:
            if index.geometries[idx].contains(point):
                return index.names[idx]
        except Exception:
            continue
    return None


@lru_cache(maxsize=100_000)
def lookup_boundaries(
    latitude: float | None,
    longitude: float | None,
) -> tuple[str | None, str | None]:
    """Return ``(district_name, region_name)`` for a WGS84 coordinate.

    Cached on ``(latitude, longitude)``. Returns ``(None, None)`` if either
    coordinate is missing/malformed, indexes failed to load, or the point
    falls outside all UK boundaries.
    """
    if latitude is None or longitude is None:
        return None, None
    if not _try_ensure_indexes_loaded():
        return None, None
    try:
        point = Point(float(longitude), float(latitude))
    except (TypeError, ValueError):
        return None, None
    assert _districts_index is not None and _regions_index is not None
    return (
        _lookup_in_index(point, _districts_index),
        _lookup_in_index(point, _regions_index),
    )
