"""Render the Active Places coverage report as markdown."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from .analysis import MIN_SITES_FOR_RANKING, CoverageResults

# Columns rendered right-aligned in markdown tables.
_NUMERIC_SUFFIXES = ("_count", "_total", "_matched", "_missing", "_pct", "_metres", "_venues",
                     "_covered", "_authorities", "_in_la", "_unmatched")


def _is_numeric_column(name: str, series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) or name.endswith(_NUMERIC_SUFFIXES)


def _format_cell(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "_null_"
    if isinstance(value, (bool, np.bool_)):
        # bool subclasses int, so this must come first or flags render as 0/1.
        return "**←**" if value else ""
    if isinstance(value, float):
        return f"{value:,.1f}"
    if isinstance(value, (int, pd.Int64Dtype().type)):
        return f"{value:,}"
    text = str(value).strip()
    if text == "":
        return "_blank_"
    return text.replace("|", "\\|")


def _table(frame: pd.DataFrame, headers: dict[str, str] | None = None) -> str:
    """Render a DataFrame as a GitHub-flavoured markdown table."""
    if frame.empty:
        return "_No rows._\n"
    headers = headers or {c: c for c in frame.columns}
    frame = frame[list(headers)]
    aligns = ["---:" if _is_numeric_column(c, frame[c]) else "---" for c in frame.columns]
    lines = [
        "| " + " | ".join(headers.values()) + " |",
        "|" + "|".join(aligns) + "|",
    ]
    for row in frame.itertuples(index=False):
        lines.append("| " + " | ".join(_format_cell(v) for v in row) + " |")
    return "\n".join(lines) + "\n"


def _pct(numerator: int, denominator: int) -> str:
    return f"{100 * numerator / denominator:.1f}%" if denominator else "n/a"


def render(results: CoverageResults,
           points_frame: pd.DataFrame,
           scope_counts: dict[str, int],
           data_version: str,
           opportunities_table: str,
           buffer_metres: float,
           cluster_metres: float,
           diameters: pd.Series) -> str:
    """Build the full markdown report."""
    stats = results.stats
    sections: list[str] = []

    sections.append(f"""# Active Places Coverage in the OpenActive Data

- Date: {date.today().isoformat()}
- Active Places data version: {data_version}
- Source table: `{opportunities_table}`
- Scope: England only; all opportunity kinds except `Slot`
- Active Places universe: facilities with `Operational Status` in (3 Operational, 4 Temporarily Closed) \
and `Accessibility Type Group (Text)` != `Private`, joined to their sites, excluding sites with a `Closed Date`
- Match rule: an Active Places site counts as covered when an OpenActive venue lies within \
**{buffer_metres:g}m** (measured in EPSG:27700 metres), shares its postcode within \
{stats['postcode_max_metres']:g}m, or — as a last resort — carries a clearly matching name within \
{stats['name_max_metres']:g}m
- OpenActive venue: distinct `(dataset_url, location)` points single-link clustered at {cluster_metres:g}m
""")

    # --- headline --------------------------------------------------------------
    sections.append(f"""## Headline

**{_pct(stats['sites_matched'], stats['sites_total'])} of Active Places sites appear in the OpenActive data** \
— {stats['sites_matched']:,} of {stats['sites_total']:,} sites match an OpenActive venue on one of the three channels.

Spatial proximity alone accounts for {stats['spatial_only_sites']:,} of those
({stats['spatial_only_pct']}%). The postcode channel adds {stats['postcode_added_sites']:,} sites
that no venue comes within {buffer_metres:g}m of but whose postcode a venue shares, and the
last-resort name channel adds {stats['name_added_sites']:,} more. The name channel also attaches
{stats['name_rescued_venues']:,} otherwise-unmatched venues to sites the other channels had already
found, which does not move the site figure but does reduce the apparent OpenActive-side gap. The extra channels exist because
{stats['centroid_points_pct']}% of OpenActive points are postcode centroids rather than surveyed
coordinates, so distance alone systematically misses real matches; see **Match channels** below.

Read the other way round, the OpenActive data is mostly *not* Active Places estate: of the \
{stats['venues_total']:,} English OpenActive venues, **{stats['venues_unmatched']:,} \
({stats['venues_unmatched_pct']}%) match no Active Places site on any channel**.

| Metric | Value |
|---|---:|
| Active Places sites in scope | {stats['sites_total']:,} |
| … matched to an OpenActive venue | {stats['sites_matched']:,} |
| … unmatched | {stats['sites_missing']:,} |
| **Active Places coverage** | **{stats['coverage_pct']}%** |
| English OpenActive venues | {stats['venues_total']:,} |
| … matched to an Active Places site | {stats['venues_matched']:,} |
| … unmatched | {stats['venues_unmatched']:,} |
| **OpenActive venues absent from Active Places** | **{stats['venues_unmatched_pct']}%** |
| Site–venue pairs (both channels) | {stats['pairs']:,} |
| Sites matched by proximity alone | {stats['spatial_only_sites']:,} |
| Sites added by the postcode channel | {stats['postcode_added_sites']:,} |
| Sites added by the name channel | {stats['name_added_sites']:,} |
| Venues additionally rescued by the name channel | {stats['name_rescued_venues']:,} |
| Local authorities covered by the universe | {stats['local_authorities']:,} |
""")

    # --- distance sensitivity --------------------------------------------------
    sensitivity = results.distance_sensitivity
    at_buffer = sensitivity.loc[sensitivity["threshold_metres"] == buffer_metres, "coverage_pct"]
    wider = sensitivity[sensitivity["threshold_metres"] > buffer_metres]
    at_buffer_text = f"{at_buffer.iloc[0]:g}" if len(at_buffer) else "n/a"
    wider_metres = wider["threshold_metres"].iloc[0] if len(wider) else buffer_metres
    wider_text = f"{wider['coverage_pct'].iloc[0]:g}" if len(wider) else "n/a"

    if stats["centroid_diagnostic"]:
        centroid_sentence = (
            f"{stats['centroid_points']:,} of the in-scope OpenActive points "
            f"({stats['centroid_points_pct']}%) sit *exactly* on a postcode centroid, which means the "
            f"publisher geocoded them from a postcode rather than surveying the venue."
        )
    else:
        centroid_sentence = (
            "The coordinate-provenance diagnostic was skipped because Code-Point Open was "
            "unavailable, so the share of postcode-geocoded points is unmeasured here."
        )
    sections.append(f"""## How sensitive is this to the {buffer_metres:g}m threshold?

This table isolates the **spatial** channel — it counts sites by distance to their nearest OpenActive
venue, ignoring postcode agreement — so it shows what the threshold alone buys. Very sensitive. Coverage roughly doubles between 100m and 250m and doubles again by 1km, which means a large
number of OpenActive venues sit *near* an Active Places site without sitting *on* it.

{_table(sensitivity, {
        'threshold_metres': 'Threshold (m)',
        'sites_matched': 'Sites matched',
        'coverage_pct': 'Coverage %',
        'is_configured_buffer': 'In use',
    })}
That gradient is the single most important caveat in this report. Two things cause it, and they pull
in the same direction.

**Coordinate provenance.** {centroid_sentence} A postcode centroid is the mean position of a postcode
unit, routinely 100m or more from the building it nominally locates, so such a point cannot be
expected to land within {buffer_metres:g}m of the right Active Places site. Note this is *publisher*
geocoding, not ours — our own ingestion falls back to a postcode centroid for only
{stats['postcode_derived_venues']:,} venues ({stats['postcode_derived_pct']}%), which is why the
`location.postal_code` field alone badly understates the problem. See **Coordinate provenance** below
for the per-publisher split.

**Granularity.** Active Places records one point per *site*, effectively its centroid, while
OpenActive records the point a *session* happens at. A leisure complex, school campus, golf course or
park easily spans more than {buffer_metres:g}m, so a genuine match can sit outside the threshold
simply because the two datasets describe the same place at different resolution. The 100–250m band
bears this out: it contains entries such as a leisure centre 100m from a venue published by the
company that operates it.

Widening the threshold is not a free fix — at 500m or 1km, in an urban area, a match stops meaning
"the same place". {buffer_metres:g}m is the defensible conservative choice, and
{stats['coverage_pct']}% should be read as a **lower bound** on true coverage.
""")

    # --- geography -------------------------------------------------------------
    region = results.coverage_by_region.rename(columns={"Region Name": "region"})
    sections.append(f"""## Coverage by region

{_table(region, {
        'region': 'Region',
        'sites_total': 'Sites',
        'sites_matched': 'Matched',
        'sites_missing': 'Missing',
        'coverage_pct': 'Coverage %',
    })}""")

    by_missing = results.coverage_by_la.sort_values("sites_missing", ascending=False).head(20)
    rankable = results.coverage_by_la[results.coverage_by_la["sites_total"] >= MIN_SITES_FOR_RANKING]
    by_worst = rankable.sort_values(["coverage_pct", "sites_total"], ascending=[True, False]).head(20)
    la_headers = {
        "local_authority_code": "LA code",
        "local_authority_name": "Local authority",
        "sites_total": "Sites",
        "sites_matched": "Matched",
        "sites_missing": "Missing",
        "coverage_pct": "Coverage %",
        "oa_venues_in_la": "OA venues",
    }
    sections.append(f"""## Where are the most sites missing?

The direct answer to "where does OpenActive have the most missing sites". The first table ranks by
absolute shortfall — where the most sites are absent — and the second by coverage rate, restricted to
local authorities with at least {MIN_SITES_FOR_RANKING} sites so that small areas do not dominate.

### Top 20 local authorities by number of missing sites

{_table(by_missing, la_headers)}
### Bottom 20 local authorities by coverage rate (≥ {MIN_SITES_FOR_RANKING} sites)

{_table(by_worst, la_headers)}
Full per-authority figures for all {len(results.coverage_by_la):,} local authorities are in
`coverage_by_local_authority.csv`.
""")

    # --- what kind of estate is missing ----------------------------------------
    ownership = results.coverage_by_ownership.rename(columns={"Ownership Type Group": "group"})
    management = results.coverage_by_management.rename(columns={"Management Type Group": "group"})
    breakdown_headers = {
        "group": "Group",
        "sites_total": "Sites",
        "sites_matched": "Matched",
        "sites_missing": "Missing",
        "coverage_pct": "Coverage %",
    }
    sections.append(f"""## What kind of estate is covered?

This is what makes the headline actionable. Coverage is not uniform across the estate: the sites
OpenActive reaches are concentrated in the parts of the sector that publish booking data at all.

### By ownership type group

{_table(ownership, breakdown_headers)}
### By management type group

{_table(management, breakdown_headers)}""")

    facility = results.coverage_by_facility_type.rename(columns={"facility_type": "code"})
    sections.append(f"""### By Active Places facility type

A site is counted once per distinct facility type it offers, so these rows sum to more than the site
total. The export ships no code-to-label lookup in `data/active_places/`, so codes are shown raw;
resolving them needs the Active Places data dictionary.

{_table(facility.head(20), {
        'code': 'Facility type code',
        'sites_total': 'Sites',
        'sites_matched': 'Matched',
        'sites_missing': 'Missing',
        'coverage_pct': 'Coverage %',
    })}""")

    # --- publishers ------------------------------------------------------------
    sections.append(f"""## Which publishers account for the coverage?

{_table(results.publisher_coverage.head(25), {
        'publisher': 'Publisher',
        'ap_sites_covered': 'AP sites covered',
        'oa_venues': 'OA venues',
        'local_authorities': 'LAs',
    })}
{stats['sites_multi_publisher']:,} matched sites are covered by more than one publisher \
({_pct(stats['sites_multi_publisher'], stats['sites_matched'])} of matched sites), which is where
duplicate listings of the same venue are most likely.
""")

    # --- match channels --------------------------------------------------------
    sections.append(f"""## Match channels

Three channels decide whether a site is covered, and every pair records which one fired.

- **`spatial`** — an OpenActive venue with surveyed coordinates within {buffer_metres:g}m.
- **`spatial_and_postcode`** — within {buffer_metres:g}m *and* sharing the postcode. The strongest
  evidence available here.
- **`postcode`** — the postcodes match and the venue is within {stats['postcode_max_metres']:g}m, but
  further than {buffer_metres:g}m. This is what recovers venues published at a postcode centroid.
- **`spatial_centroid_only`** — within {buffer_metres:g}m, but the venue's coordinates *are* a
  postcode centroid and the postcodes do not agree. Proximity here is partly an artefact of where the
  centroid happens to fall, so it is ranked below the others when choosing a site's primary pair. It
  still counts as a match.
- **`name`** — the last resort, run only after the other channels have finished. A site and a venue
  within {stats['name_max_metres']:g}m whose names agree at {stats['name_threshold']} or better on the
  measure described below. Only pairs that rescue a previously unmatched site or venue are considered,
  so this channel can add coverage but never override stronger evidence.

{_table(results.match_methods, {
        'match_method': 'Method',
        'pairs': 'Pairs',
        'sites': 'Sites',
        'venues': 'Venues',
        'median_distance_metres': 'Median distance (m)',
    })}
The {stats['postcode_max_metres']:g}m cap on the postcode channel keeps out pairs that share a
postcode string but sit implausibly far apart, which indicates bad data on one side rather than a
match. A postcode is available for {stats['sites_with_postcode_key']:,} of the
{len(points_frame):,} in-scope points, combining what the feed declared with what could be recovered
by snapping a centroid point back to its postcode.

### How names are compared

Venue names describe the same place in two registers — `Whitwick & Coalville Lc` against
`WHITWICK AND COALVILLE LEISURE CENTRE`. Bridging them needs case folding, `&`/`and` unification,
expansion of sector abbreviations (`Lc`, `RFC`, `CC`), and removal of the address publishers append to
the name (`Queens Park Tennis Club, Queens Park, East Drive, Brighton, BN2 0BQ`). Scoring is
token-based, not edit-distance: word order differs between the registers, and an edit distance over a
name with an address glued to it is meaningless. The score averages Jaccard with containment, so an
appended address does not sink a true match while a name that merely shares a word still scores low.

The threshold of {stats['name_threshold']} was calibrated against the data by hand. Below roughly 0.8
the channel starts pairing venues that share only a town — `Suffolk Rd, Andover` against
`ANDOVER LEISURE CENTRE`. A second guard handles the same failure from the other direction: publishers
often put a bare location in the name field, and since generic words like "leisure centre" are
stripped, `Wetherby` would otherwise score a perfect 1.0 against `WETHERBY LEISURE CENTRE`. When every
shared word is a place name — drawn from the export's own `Town`, `Local Authority`, `County` and
`Region` columns rather than an external gazetteer — the pair survives only if the whole names agree
and the site name adds no distinctive word of its own. That keeps `Whitwick & Coalville Lc`, whose
tokens are themselves town names, while rejecting `Clacton-on-Sea, UK` against
`PUREGYM (CLACTON-ON-SEA)`.

Matches found this way run at a median {stats['name_median_similarity']} similarity and
{stats['name_median_distance']:g}m apart — well beyond the spatial buffer, which is the point.

{_table(results.name_examples.head(15), {
        'site_name': 'Active Places site',
        'oa_location_names': 'OpenActive venue',
        'local_authority_name': 'Local authority',
        'distance_metres': 'Distance (m)',
        'name_similarity': 'Similarity',
    })}
One caveat specific to the postcode channel: Active Places sites are not uniquely postcoded — several sites
can share one postcode — so the postcode channel is inherently many-to-many. The `is_primary_for_site`
flag in the mapping CSV resolves that by ranking on channel strength first, then distance.
""")

    # --- coordinate provenance -------------------------------------------------
    if stats["centroid_diagnostic"]:
        sections.append(f"""## Coordinate provenance

A point that sits *exactly* on a postcode centroid was geocoded from a postcode, not surveyed. Those
points are structurally hard to match: the centroid of a postcode unit is commonly 100m or more from
the building. Detected by snapping each point to Code-Point Open within 1m — a test that flags only
1.5% of Active Places sites, which carry real building coordinates, so it is specific.

{stats['centroid_points']:,} of {len(points_frame):,} in-scope points ({stats['centroid_points_pct']}%) are
postcode centroids, and they are heavily concentrated: **{stats['top_centroid_publisher']}** alone
accounts for {stats['top_centroid_publisher_points']:,} of them. Excluding that publisher, the rate
across the rest of the data is **{stats['centroid_pct_excluding_top']}%**.

That concentration matters for how you read the headline. The publishers whose estate actually
overlaps Active Places — leisure operators and facility bookings — largely publish real coordinates,
so the coverage figure is a fair measurement for them. The publishers with high centroid rates are
mostly publishing outdoor and route-based activity that Active Places does not catalogue anyway.

{_table(results.coordinate_provenance.head(20), {
            'publisher': 'Publisher',
            'points': 'Points',
            'centroid_points': 'Postcode centroids',
            'centroid_pct': 'Centroid %',
        })}""")

    # --- the OpenActive side ---------------------------------------------------
    sections.append(f"""## The OpenActive side: venues with no Active Places site

{stats['venues_unmatched']:,} English OpenActive venues ({stats['venues_unmatched_pct']}%) match no
Active Places site on any channel. Some of these are genuinely outside the Active Places
remit — parks, village halls, outdoor meeting points, online-adjacent locations — and some are the
same coordinate-precision problem seen above, viewed from the other direction.

### The largest unmatched venues

Named where the feed supplies a name, ordered by how many opportunities they carry — the most
worthwhile candidates for manual checking. `unmatched_oa_venues.csv` carries the raw `location` JSON
for each, so a row can be traced straight back to its opportunities with
`WHERE TO_JSON_STRING(location) = '<value>'`.

Putting the venue name next to the nearest Active Places site name is the clearest evidence that the
headline remains a floor even after three channels. The name channel has already claimed the pairs
whose names agree outright; what is left below includes places that are plainly related but not
name-identical — a leisure centre listed under the name of the park it stands in, or under an
operator brand the Active Places record does not carry. Neither distance, postcode nor name could
confirm those, so they are counted as missing.

{_table(results.top_unmatched_venues.head(20), {
        'oa_location_names': 'Venue name',
        'oa_publisher_names': 'Publisher',
        'district_name': 'District',
        'oa_opportunity_count': 'Opportunities',
        'nearest_ap_site_name': 'Nearest AP site',
        'nearest_ap_site_metres': 'Distance (m)',
    })}
### By local authority district

{_table(results.unmatched_venues_by_district.head(20), {
        'district_name': 'District',
        'unmatched_venues': 'Unmatched venues',
        'opportunity_count': 'Opportunities',
    })}
### By publisher

{_table(results.unmatched_venues_by_publisher.head(20), {
        'publisher': 'Publisher',
        'unmatched_venues': 'Unmatched venues',
        'opportunity_count': 'Opportunities',
    })}""")

    # --- scope and QA ----------------------------------------------------------
    over_250 = int((diameters > 250).sum())
    sections.append(f"""## Scope and data quality

Active Places is an England-only register, so the headline figures compare like with like by
restricting the OpenActive side to England. Nothing is silently discarded — the excluded points are:

| OpenActive points | Count |
|---|---:|
| Distinct `(dataset_url, location)` points fetched | {scope_counts['total_points']:,} |
| Excluded: coordinates outside the GB envelope | {scope_counts['out_of_envelope']:,} |
| Excluded: resolved to a country other than England | {scope_counts['other_country']:,} |
| Excluded: no country resolved | {scope_counts['unknown_country']:,} |
| **In scope (England)** | **{scope_counts['england']:,}** |

Those {scope_counts['england']:,} raw points collapse to {stats['venues_total']:,} venues after
single-link clustering at {cluster_metres:g}m — a {_pct(scope_counts['england'] - stats['venues_total'], scope_counts['england'])}
reduction, which is the scale of near-duplicate publishing in the data. Single-link clustering can
chain across dense areas, so cluster spread is checked: the widest cluster spans
{diameters.max():.0f}m and {over_250:,} clusters exceed 250m.
""")

    # --- caveats ---------------------------------------------------------------
    sections.append(f"""## Caveats

- **The {buffer_metres:g}m threshold drives the spatial channel.** Spatial-only coverage is
  {at_buffer_text}% at the {buffer_metres:g}m in use, rising to {wider_text}% at {wider_metres:g}m. Treat {stats['coverage_pct']}% as a lower bound on true coverage, not a
  precise measurement, and see the sensitivity section above for why the two datasets disagree at
  this scale.
- **The name channel is the weakest evidence here.** It is applied last, only to records the other
  channels could not reach, and every pair it produces is labelled `name` with its similarity score in
  the mapping CSV so it can be filtered out. Manual review of a sample found it sound, but a residue
  of same-area-different-facility pairs remains — a school next to the lido it shares a name with.
- **The postcode channel is a string match, not a location.** It asserts that a venue and a site
  share a postcode unit, which is strong evidence but not proof — postcode units can contain several
  distinct facilities. The {stats['postcode_max_metres']:g}m cap and the primary-pair ranking limit
  the damage, but pairs carrying `match_method = postcode` are weaker than the spatial ones and the
  mapping CSV labels them so they can be filtered out.
- **Route- and meeting-point publishers depress the OpenActive side.** The largest single source of
  unmatched venues publishes rides and outdoor events whose coordinates are start points — laybys,
  car parks, trailheads — rather than facilities, and {stats['top_centroid_publisher_points']:,} of
  its points are postcode centroids. These have no Active Places counterpart by construction. Read
  the unmatched-venue tables as a description of what OpenActive covers beyond the built estate, not
  as a list of gaps in Active Places.
- **Active Places is not a complete register of activity venues.** Parks, community halls, streets and
  outdoor spaces host OpenActive opportunities but are out of the Active Places remit, so a high
  "absent from Active Places" figure is expected and is not by itself a data-quality problem.
- **`Slot` items are excluded** because they carry no location of their own and inherit it from a
  parent `FacilityUse`, which is already counted.
- **Local authority boundary vintages may differ.** Active Places `Local Authority Code` and the
  `district_code` resolved on opportunities (LAD24) come from different sources; the OA-venues-per-LA
  column is a join on code and will under-count where the vintages disagree.
- **A site is counted as covered if any publisher lists a venue near it.** This measures presence in
  the data, not the quality, completeness or currency of what is published there.
""")

    return "\n".join(sections)
