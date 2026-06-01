"""Spatial lookup mapping (latitude, longitude) -> (district_name, region_name).

Lazily loads UK Local Authority Districts and UK Regions GeoJSON boundaries
from ``volume-1/data-analysis/`` (reprojected to WGS84) and resolves a
coordinate to ``(district_name, region_name)`` via shapely STRtree spatial
indexes.

Also provides a JSON-based district enrichment lookup that maps district_name
to district_code, region_code, country_code, and country_name from the
``000-district-region-country.json`` file.

Lookups are cached with ``lru_cache`` because many opportunities share a
venue, so the same coordinate is queried repeatedly during a run.

Pattern mirrors ``jobs/opportunity-insights/geolookup.py``.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely import STRtree
from shapely.geometry import Point

logger = logging.getLogger(__name__)

# Boundary GeoJSONs live under ``volume-1/data-analysis/``.
#
# - On Cloud Run the ``volume-1`` GCS bucket is mounted into the container
#   and the path is provided via the ``INGEST_BOUNDARY_DIR`` env var.
# - For local development, leave ``INGEST_BOUNDARY_DIR`` unset and the path
#   resolves relative to this file at ``<repo>/volume-1/data-analysis``.
_env_boundary_dir = os.getenv("INGEST_BOUNDARY_DIR")
if _env_boundary_dir:
    _BOUNDARY_DIR = Path(_env_boundary_dir)
else:
    # jobs/ingest-opportunities/boundary_lookup.py -> repo root is parents[2].
    _BOUNDARY_DIR = Path(__file__).resolve().parents[2] / "volume-1" / "data-analysis"

DISTRICTS_FILENAME = "000-location-districts.geojson"
REGIONS_FILENAME = "000-location-regions.geojson"
DISTRICT_LOOKUP_FILENAME = "000-district-region-country.json"

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


# ---------------------------------------------------------------------------
# District -> region/country JSON lookup (loaded once, thread-safe)
# ---------------------------------------------------------------------------

_district_lookup: dict[str, dict[str, Any]] | None = None
_district_lookup_lock = threading.Lock()
_district_lookup_loaded = False


def _ensure_district_lookup_loaded() -> dict[str, dict[str, Any]]:
    """Load the district -> region/country lookup JSON once."""
    global _district_lookup, _district_lookup_loaded

    if _district_lookup_loaded:
        return _district_lookup or {}

    with _district_lookup_lock:
        if _district_lookup_loaded:
            return _district_lookup or {}

        path = _BOUNDARY_DIR / DISTRICT_LOOKUP_FILENAME
        if not path.exists():
            logger.warning(
                "District lookup %s not found; district_code/region_code/country columns will be NULL",
                path,
            )
            _district_lookup = {}
        else:
            with path.open(encoding="utf-8") as handle:
                _district_lookup = json.load(handle)
            logger.info("Loaded district lookup with %d entries from %s", len(_district_lookup), path)

        _district_lookup_loaded = True
        return _district_lookup or {}


def enrich_from_district_lookup(district_name: str | None) -> dict[str, str | None]:
    """Return enrichment fields from district_name using the JSON lookup.

    Keys returned: ``district_code``, ``region_code``, ``country_code``, ``country_name``.
    All values are ``None`` if district_name is missing or not found.
    """
    result: dict[str, str | None] = {
        "district_code": None,
        "region_code": None,
        "country_code": None,
        "country_name": None,
    }
    if not district_name:
        return result

    lookup = _ensure_district_lookup_loaded()
    info = lookup.get(district_name)
    if info:
        result["district_code"] = info.get("district_code")
        result["region_code"] = info.get("region_code")
        result["country_code"] = info.get("country_code")
        result["country_name"] = info.get("country_name")
    return result


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
