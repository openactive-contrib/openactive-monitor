---
name: geolocation
description: Use this skill when working on location extraction, UK postcode geocoding, or the geolocation.py module.
---

# Skill: Geolocation & UK Postcodes

## When to use
Use this skill when working on location extraction, postcode geocoding, or the `geolocation.py` module.

## Key file
- `jobs/ingest-opportunities/geolocation.py`

## How location extraction works
The `_build_location()` function tries multiple strategies in order:

1. **Direct geo coordinates:** `location.geo.latitude` / `location.geo.longitude`
2. **Address with postcode:** Extract UK postcode from `location.address` (string or dict), then geocode
3. **containsPlace fallback:** Recurse into `location.containsPlace`
4. **Name-only fallback:** Store `place_name` for future geocoding

## UK postcode geocoding
- Uses `uklookup` library (`lookup_postcode_lat_long`)
- Results are cached with `@lru_cache(maxsize=50_000)`
- Postcode extraction uses the official UK postcode regex pattern

## Output format
```python
{
    "latitude": 51.5074,
    "longitude": -0.1278,
    "postal_code": "SW1A 1AA",
    "address": "10 Downing Street, London",  # only if from string address
    "place_name": "Some Venue"  # only if no geo found
}
```

