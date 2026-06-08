---
name: geolocation-boundaries
description: Use this skill when working on UK geolocation boundary files (districts, parishes, regions) for spatial analysis or joining opportunity locations to administrative areas.
---

# Skill: UK Geolocation Boundaries

## When to use
Use this skill when working on spatial joins, boundary lookups, or any analysis that maps opportunity locations to UK administrative areas (districts, parishes, regions).

## Boundary files

All files are located in `volume-1/data-analysis/`.

| File | Description | CRS | Count | Use Case |
|------|-------------|-----|-------|----------|
| `000-location-districts.geojson` | UK Local Authority Districts | EPSG:27700 | ~300 | Primary boundary for most analyses |
| `000-location-parishes.geojson` | UK Civil Parishes | EPSG:27700 | ~10,000 | Fine-grained analysis |
| `000-location-regions.geojson` | UK Regions | EPSG:27700 | ~12 | High-level regional analysis |
| `000-district-region-country.json` | District -> region/country lookup | n/a | ~300 | Fast name-based enrichment for BigQuery columns |

## ⚠️ Coordinate reference system

All GeoJSON files use **British National Grid (EPSG:27700)** and **must be reprojected to WGS84 (EPSG:4326)** before matching against opportunity location data (which stores `latitude`/`longitude` in WGS84).

```python
import geopandas as gpd

gdf = gpd.read_file("volume-1/data-analysis/000-location-districts.geojson")
gdf = gdf.to_crs(epsg=4326)
```

## Feature properties

### Districts (`000-location-districts.geojson`)
| Property | Description | Usage |
|----------|-------------|-------|
| `LAD24CD` | Local Authority District code | Unique identifier — use for joins |
| `LAD24NM` | Local Authority District name | Human-readable — use for display |

### Regions (`000-location-regions.geojson`)
| Property | Description | Usage |
|----------|-------------|-------|
| `eer18cd` | Region code | Unique identifier — use for joins |
| `eer18nm` | Region name | Human-readable — use for display |

### Parishes (`000-location-parishes.geojson`)
| Property | Description | Usage |
|----------|-------------|-------|
| `PARNCP25CD` | Parish/non-civil parish code | Unique identifier — use for joins |
| `PARNCP25NM` | Parish/non-civil parish name | Human-readable — use for display |

## Typical spatial join pattern

```python
import geopandas as gpd
from shapely.geometry import Point

# Load and reproject boundaries
districts = gpd.read_file("volume-1/data-analysis/000-location-districts.geojson")
districts = districts.to_crs(epsg=4326)

# Build GeoDataFrame from opportunity locations (lat/lon already WGS84)
points = gpd.GeoDataFrame(
    opportunities_df,
    geometry=gpd.points_from_xy(
        opportunities_df["longitude"],
        opportunities_df["latitude"],
    ),
    crs="EPSG:4326",
)

# Spatial join
joined = gpd.sjoin(points, districts[["LAD24CD", "LAD24NM", "geometry"]], how="left", predicate="within")
```

## Choosing the right boundary level

- **Districts** — default choice for most analyses; ~300 areas, good balance of granularity and coverage.
- **Regions** — use when you need high-level England/Wales/Scotland breakdowns (~12 areas).
- **Parishes** — use only when very fine-grained local detail is required; ~10,000 areas, slower joins.

keeps RPDE ingestion fast.
