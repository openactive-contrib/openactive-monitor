"""Build a UK Local Authority District -> Region -> Country lookup as JSON.

Reads district names/codes from ``000-location-districts.geojson`` (the same
boundary file used by ``jobs/ingest-opportunities/boundary_lookup.py``) and
enriches them with region and country information from the ONS Open Geography
Portal "April 2025" lookups.

The boundary directory is resolved the same way as ``boundary_lookup.py`` so the
code runs both on Google Cloud (``volume-1`` GCS bucket mounted, path provided
via ``INSIGHTS_GEO_DIR``) and locally (path resolved relative to this file).

Two ``click`` commands are exposed:

* ``download`` -- fetch the two ONS ArcGIS lookups and merge them into
  ``nspl.json`` (keyed by ``LAD25CD``).
* ``build`` -- read the districts geojson + ``nspl.json`` and write the enriched
  ``{district_name: {district_code, region_code, region_name, country_code,
  country_name}}`` dict to ``district_region_country.json``.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import click
import geopandas as gpd
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Reference data lives under ``volume-1/data-analysis/``.
#
# - On Cloud Run the ``volume-1`` GCS bucket is mounted into the container and
#   the path is provided via the ``INSIGHTS_GEO_DIR`` env var.
# - For local development, leave ``INSIGHTS_GEO_DIR`` unset and the path resolves
#   relative to this file at ``<repo>/volume-1/data-analysis``.
_env_geo_dir = os.getenv("INSIGHTS_GEO_DIR")
if _env_geo_dir:
    DEFAULT_GEO_DIR = Path(_env_geo_dir)
else:
    # jobs/opportunity-insights/district_region_country.py -> repo root is parents[2].
    DEFAULT_GEO_DIR = Path(__file__).resolve().parents[2] / "volume-1" / "data-analysis"

DISTRICTS_FILENAME = "000-location-districts.geojson"
DISTRICTS_NAME_COLUMN = "LAD24NM"
DISTRICTS_CODE_COLUMN = "LAD24CD"

NSPL_FILENAME = "000-nspl.json"
DEFAULT_OUTPUT_FILENAME = "000-district-region-country.json"

# ONS Open Geography Portal ArcGIS FeatureServer "/query" endpoints (April 2025).
REGION_LOOKUP_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "LAD25_RGN25_EN_LU_v2/FeatureServer/0/query"
)
COUNTRY_LOOKUP_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "LAD25_CTRY25_UK_LU/FeatureServer/0/query"
)
ARCGIS_PAGE_SIZE = 2000
REQUEST_TIMEOUT = 60


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# ArcGIS download
# ---------------------------------------------------------------------------

def _fetch_arcgis_table(query_url: str, out_fields: list[str]) -> list[dict[str, Any]]:
    """Page through an ArcGIS FeatureServer ``/query`` endpoint, returning rows.

    Each returned dict is the ``attributes`` payload of one feature. Geometry is
    not requested (these are non-spatial lookup tables).
    """
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": ",".join(out_fields),
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": ARCGIS_PAGE_SIZE,
        }
        logger.debug("Querying %s offset=%d", query_url, offset)
        response = requests.get(query_url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise RuntimeError(f"ArcGIS query failed for {query_url}: {data['error']}")

        features = data.get("features", [])
        rows.extend(feature["attributes"] for feature in features)

        if not data.get("exceededTransferLimit") or not features:
            break
        offset += len(features)

    logger.info("Fetched %d rows from %s", len(rows), query_url)
    return rows


def download_lookup(output_path: Path) -> dict[str, dict[str, Any]]:
    """Download + merge the ONS region and country lookups into ``output_path``.

    Returns the merged lookup keyed by ``LAD25CD``.
    """
    country_rows = _fetch_arcgis_table(
        COUNTRY_LOOKUP_URL, ["LAD25CD", "LAD25NM", "CTRY25CD", "CTRY25NM"]
    )
    region_rows = _fetch_arcgis_table(
        REGION_LOOKUP_URL, ["LAD25CD", "LAD25NM", "RGN25CD", "RGN25NM"]
    )

    # Country lookup is UK-wide, so seed the merged dict from it. Region lookup is
    # England-only; overlay region fields where present.
    merged: dict[str, dict[str, Any]] = {}
    for row in country_rows:
        code = row.get("LAD25CD")
        if not code:
            continue
        merged[code] = {
            "LAD25NM": row.get("LAD25NM"),
            "RGN25CD": None,
            "RGN25NM": None,
            "CTRY25CD": row.get("CTRY25CD"),
            "CTRY25NM": row.get("CTRY25NM"),
        }

    for row in region_rows:
        code = row.get("LAD25CD")
        if not code:
            continue
        entry = merged.setdefault(
            code,
            {"LAD25NM": row.get("LAD25NM"), "CTRY25CD": None, "CTRY25NM": None},
        )
        entry["RGN25CD"] = row.get("RGN25CD")
        entry["RGN25NM"] = row.get("RGN25NM")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(merged, handle, indent=2, ensure_ascii=False)
    logger.info("Wrote %d district lookups to %s", len(merged), output_path)

    return merged


# ---------------------------------------------------------------------------
# Build the enriched district dict
# ---------------------------------------------------------------------------

def _load_lookup(lookup_path: Path) -> dict[str, dict[str, Any]]:
    with lookup_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_district_dict(
    geo_dir: Path, lookup: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Build ``{district_name: {district_code, region_*, country_*}}``.

    District names/codes come from the boundary geojson; region and country are
    taken from ``lookup`` (keyed by district code). The join is by district code;
    where the boundary geojson carries an older code than the 2025 lookup (e.g.
    the South Yorkshire metropolitan districts) it falls back to matching on
    district name. Districts with no match at all keep only ``district_code``
    (region/country left ``None``).
    """
    districts_path = geo_dir / DISTRICTS_FILENAME
    logger.info("Reading districts geojson from %s", districts_path)
    gdf = gpd.read_file(str(districts_path))

    # Name index used as a fallback when the geojson code predates the lookup.
    lookup_by_name = {
        info["LAD25NM"]: info for info in lookup.values() if info.get("LAD25NM")
    }

    result: dict[str, dict[str, Any]] = {}
    unmatched = 0
    name_matched = 0
    region_matched = 0
    country_matched = 0

    for name, code in zip(gdf[DISTRICTS_NAME_COLUMN], gdf[DISTRICTS_CODE_COLUMN]):
        entry: dict[str, Any] = {
            "district_code": code,
            "region_code": None,
            "region_name": None,
            "country_code": None,
            "country_name": None,
        }
        info = lookup.get(code)
        if info is None:
            info = lookup_by_name.get(name)
            if info is not None:
                name_matched += 1
                logger.debug("Matched %s by name (geojson code %s)", name, code)
        if info is None:
            unmatched += 1
            logger.debug("No region/country lookup for %s (%s)", name, code)
        else:
            entry["region_code"] = info.get("RGN25CD")
            entry["region_name"] = info.get("RGN25NM")
            entry["country_code"] = info.get("CTRY25CD")
            entry["country_name"] = info.get("CTRY25NM")
            if entry["region_name"]:
                region_matched += 1
            if entry["country_name"]:
                country_matched += 1
        result[name] = entry

    logger.info(
        "Built %d districts (region matched=%d, country matched=%d, "
        "matched by name=%d, unmatched=%d)",
        len(result),
        region_matched,
        country_matched,
        name_matched,
        unmatched,
    )
    return result


def main(
    geo_dir: Path,
    lookup_path: Path,
    output_path: Path,
    download: bool = False,
) -> None:
    """Build the enriched district dict and write it to ``output_path``."""
    if download or not lookup_path.exists():
        if download:
            logger.info("Refreshing lookup from ArcGIS (--download).")
        else:
            logger.info("Lookup %s not found; downloading from ArcGIS.", lookup_path)
        download_lookup(lookup_path)

    lookup = _load_lookup(lookup_path)
    district_dict = build_district_dict(geo_dir, lookup)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(district_dict, handle, indent=2, ensure_ascii=False)
    logger.info("Wrote %d districts to %s", len(district_dict), output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
def cli() -> None:
    """Build the UK district -> region -> country lookup."""


@cli.command("download")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help=f"Path to write the merged lookup (default: <geo-dir>/{NSPL_FILENAME}).",
)
@click.option("--verbose", is_flag=True, default=False, help="Enable DEBUG logging.")
def download_cmd(output: Path | None, verbose: bool) -> None:
    """Download + merge the ONS region/country lookups into nspl.json."""
    _configure_logging(verbose)
    download_lookup(output or DEFAULT_GEO_DIR / NSPL_FILENAME)


@cli.command("build")
@click.option(
    "--geo-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_GEO_DIR,
    help="Directory containing the boundary geojson and lookup files.",
)
@click.option(
    "--lookup",
    "lookup_path",
    type=click.Path(path_type=Path),
    default=None,
    help=f"Path to the merged lookup (default: <geo-dir>/{NSPL_FILENAME}).",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help=f"Path to write the enriched dict (default: <geo-dir>/{DEFAULT_OUTPUT_FILENAME}).",
)
@click.option(
    "--download/--no-download",
    default=False,
    help="Download a fresh lookup from ArcGIS before building.",
)
@click.option("--verbose", is_flag=True, default=False, help="Enable DEBUG logging.")
def build_cmd(
    geo_dir: Path,
    lookup_path: Path | None,
    output: Path | None,
    download: bool,
    verbose: bool,
) -> None:
    """Build district_region_country.json from the geojson + lookup."""
    _configure_logging(verbose)
    main(
        geo_dir=geo_dir,
        lookup_path=lookup_path or geo_dir / NSPL_FILENAME,
        output_path=output or geo_dir / DEFAULT_OUTPUT_FILENAME,
        download=download,
    )


if __name__ == "__main__":
    cli()
