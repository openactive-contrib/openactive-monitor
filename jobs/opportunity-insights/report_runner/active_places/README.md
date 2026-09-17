# Active Places coverage report

Ad-hoc report answering **"what percentage of Active Places sites are in the OpenActive data?"**

Standalone — not part of the `opportunity-insights` main flow (`main.py`), and it writes nothing to
BigQuery.

## Running it

```bash
cd jobs/opportunity-insights
source virt/bin/activate
python -m report_runner.active_places.run --verbose
```

Takes about 10 seconds and bills ~6.7 GB of BigQuery scan. Most of that is reading the
publisher-declared postcode and venue name out of `json_data`; without them the query would cost
~0.7 GB, but postcode coverage would fall from 65% of points to 3%, gutting the postcode channel,
and no venue names would be available for manual checking.

| Flag | Default | Purpose |
|---|---|---|
| `--data-dir` | `data/active_places` | Where `facilities.csv` / `sites.csv` / `information.txt` live |
| `--output-dir` | `reports/active_places` | Where the CSVs and the markdown report are written |
| `--buffer-metres` | `200` | Spatial channel: a venue this close counts as a match |
| `--postcode-max-metres` | `1000` | Postcode channel: cap beyond which a shared postcode is treated as bad data |
| `--name-max-metres` | `500` | Name channel: how far apart a site and venue may be to be name-matched |
| `--name-threshold` | `0.8` | Name similarity required. Below ~0.8 it starts matching on shared town names |
| `--venue-cluster-metres` | `50` | Radius for collapsing near-duplicate OpenActive points into one venue |
| `--no-cluster` | off | Treat every distinct OpenActive point as its own venue |
| `--points-cache` | none | Parquet file to cache the BigQuery result in, so reruns skip the query |
| `--codepoint-dir` | from `uklookup` | Code-Point Open CSVs for the coordinate-provenance diagnostic |
| `--verbose` | off | Debug logging |

`--points-cache` is the one to use while iterating on the report text — it turns a rerun into a
no-query, few-second loop.

## What it does

1. **Active Places universe** — facilities with `Operational Status` in (3 Operational,
   4 Temporarily Closed) and `Accessibility Type Group (Text)` != `Private`, joined to their sites,
   excluding sites with a `Closed Date`. 27,857 sites across 296 local authorities.
2. **OpenActive points** — distinct `(dataset_url, location)` for every kind except `Slot` (which has
   no location of its own and inherits from its parent `FacilityUse`). `publisher_name` is read
   straight off `opportunities`, where it is populated on 100% of rows; it is deliberately *not*
   grouped on, because 14 datasets carry two spellings of their publisher and grouping would split a
   single location into two points. Restricted to England, because Active Places is England-only.
3. **Venues** — near-duplicate points are single-link clustered at 50m *across publishers*, since the
   same venue is routinely published by several of them.
4. **Matching** — two channels, combined:
   - **Spatial** — both sides projected to EPSG:27700 through one shared `pyproj` transformer, then
     `STRtree.query(predicate="dwithin")` for the exact all-pairs join within the buffer.
   - **Postcode** — sites and venues sharing a normalised postcode, capped at
     `--postcode-max-metres`. The venue's postcode is what the feed declared, or — for a point that
     snaps to a postcode centroid — the postcode recovered from that snap.
   - **Name** — the last resort, run after the others and only on pairs that rescue a still-unmatched
     site or venue, so it can add coverage but never override stronger evidence. See below.

   Every pair is labelled `spatial`, `spatial_and_postcode`, `postcode`, `spatial_centroid_only` or
   `name`, and the `is_primary_for_site` flag ranks on that label before distance, so a close-but-weak
   centroid coincidence never outranks a pair the stronger channels agree on.

### Name matching

Bridges `Whitwick & Coalville Lc` to `WHITWICK AND COALVILLE LEISURE CENTRE`. Normalisation folds
case, unifies `&`/`and`, expands sector abbreviations (`Lc`, `SC`, `RFC`, `CC`, `GC`), strips embedded
postcodes, and splits off the address publishers append to the name. Scoring averages Jaccard with
containment over the distinctive tokens — token-based rather than edit-distance, because word order
differs between the two registers and an address glued to a name makes edit distance meaningless.

Two guards keep it honest, both calibrated by hand against the real data:

- **Threshold 0.8.** Below it, pairs sharing only a town creep in (`Suffolk Rd, Andover` against
  `ANDOVER LEISURE CENTRE`).
- **Place-name guard.** Publishers often put a bare location in the name field, and since generic
  words like "leisure centre" are stripped, `Wetherby` would score a perfect 1.0 against
  `WETHERBY LEISURE CENTRE`. When every shared word is a place name — vocabulary built from the
  export's own `Town`/`Local Authority`/`County`/`Region` columns, not an external gazetteer — the
  pair survives only if the whole names agree *and* the site name adds no distinctive word of its own.
  That keeps `Whitwick & Coalville Lc` (whose tokens are themselves town names) while rejecting
  `Clacton-on-Sea, UK` against `PUREGYM (CLACTON-ON-SEA)`.

`report_runner/active_places/names.py` holds the logic; the calibration cases are worth re-running if
the thresholds are ever changed.

## Design notes

Three choices are load-bearing and easy to get wrong if this is ever rewritten:

- **Project both sides from lat/lon with the same transformer.** Do *not* use the `Easting`/`Northing`
  columns Active Places ships. Those came from Sport England's OSTN15 transformation, while pyproj
  here falls back to a Helmert approximation; mixing them injects a regionally systematic bias
  (measured: median 1.94m, max 4.75m). Using one transformer for both sides cancels it exactly.
- **Use `dwithin`, not `sjoin_nearest` or a buffer.** `geopandas.sjoin_nearest(max_distance=...)`
  treats the distance as a *search cutoff* and returns only the nearest match, silently dropping the
  other neighbours — wrong for a many-to-many mapping table. `buffer(100)` is a 32-gon inscribed in
  the circle, so it under-selects by ~0.5m. `dwithin` is exact and fast (0.03s at this scale).
- **The postcode channel is not optional garnish.** 31% of in-scope OpenActive points sit exactly on
  a postcode centroid because the publisher geocoded from a postcode, and a centroid is routinely
  further from the building than the spatial buffer allows. The channel adds ~24% more matched sites
  on top of the spatial result. The report quantifies provenance per publisher rather than hiding it.
- **Coverage is still a lower bound**, because Active Places records one point per site while
  OpenActive records where a session happens, and a campus or golf course outruns any tight buffer.
  The spatial buffer is 200m for exactly this reason; the sensitivity table in the report shows what
  each threshold buys.

## Outputs

| File | Contents |
|---|---|
| `active_places_coverage.md` | The narrative report |
| `site_oa_mapping.csv` | One row per (site, venue) pair, with `match_method` and primary-pair flags |
| `unmatched_sites.csv` | Active Places sites with no venue in range, plus how near the nearest was |
| `unmatched_oa_venues.csv` | OpenActive venues with no Active Places site in range |
| `coverage_by_local_authority.csv` | Per-LA totals, matched, missing and coverage % |

Both venue-bearing CSVs carry two columns for manual investigation:

- **`oa_location_names`** — every distinct `json_data.location.name` at the venue, ` | `-separated.
  Present for 46% of points, and the quickest way to eyeball whether a match is real
  ("ALFRETON LEISURE CENTRE" ↔ "Alfreton Leisure Centre").
- **`oa_location_json`** — the raw `location` payload, so a row traces straight back to the
  opportunities behind it:

  ```sql
  SELECT * FROM `openactive-monitor.openactive_analytics.opportunities`
  WHERE TO_JSON_STRING(location) = '{"latitude":53.096955,"longitude":-1.39317}'
  ```

  Needed because the `oa_lat`/`oa_lng` in the output are the *cluster centroid*, which will not
  match any single opportunity exactly once points have been clustered into a venue.
