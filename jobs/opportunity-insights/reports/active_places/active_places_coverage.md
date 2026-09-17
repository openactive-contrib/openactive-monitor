# Active Places Coverage in the OpenActive Data

- Date: 2026-09-17
- Active Places data version: 2026-09-17 03:30:29
- Source table: `openactive-monitor.openactive_analytics.opportunities`
- Scope: England only; all opportunity kinds except `Slot`
- Active Places universe: facilities with `Operational Status` in (3 Operational, 4 Temporarily Closed) and `Accessibility Type Group (Text)` != `Private`, joined to their sites, excluding sites with a `Closed Date`
- Match rule: an Active Places site counts as covered when an OpenActive venue lies within **200m** (measured in EPSG:27700 metres), shares its postcode within 1000m, or — as a last resort — carries a clearly matching name within 500m
- OpenActive venue: distinct `(dataset_url, location)` points single-link clustered at 50m

## Headline

**26.4% of Active Places sites appear in the OpenActive data** — 7,351 of 27,857 sites match an OpenActive venue on one of the three channels.

Spatial proximity alone accounts for 6,762 of those
(24.3%). The postcode channel adds 503 sites
that no venue comes within 200m of but whose postcode a venue shares, and the
last-resort name channel adds 161 more. The extra channels exist because
31.3% of OpenActive points are postcode centroids rather than surveyed
coordinates, so distance alone systematically misses real matches; see **Match channels** below.

Read the other way round, the OpenActive data is mostly *not* Active Places estate: of the 16,405 English OpenActive venues, **8,565 (52.2%) match no Active Places site on any channel**.

| Metric | Value |
|---|---:|
| Active Places sites in scope | 27,857 |
| … matched to an OpenActive venue | 7,351 |
| … unmatched | 20,506 |
| **Active Places coverage** | **26.4%** |
| English OpenActive venues | 16,405 |
| … matched to an Active Places site | 7,840 |
| … unmatched | 8,565 |
| **OpenActive venues absent from Active Places** | **52.2%** |
| Site–venue pairs (both channels) | 10,034 |
| Sites matched by proximity alone | 6,762 |
| Sites added by the postcode channel | 503 |
| Sites added by the name channel | 161 |
| Local authorities covered by the universe | 296 |

## How sensitive is this to the 200m threshold?

This table isolates the **spatial** channel — it counts sites by distance to their nearest OpenActive
venue, ignoring postcode agreement — so it shows what the threshold alone buys. Very sensitive. Coverage roughly doubles between 100m and 250m and doubles again by 1km, which means a large
number of OpenActive venues sit *near* an Active Places site without sitting *on* it.

| Threshold (m) | Sites matched | Coverage % |
|---:|---:|---:|
| 25 | 1,676 | 6.0 |
| 50 | 2,601 | 9.3 |
| 100 | 4,086 | 14.7 |
| 250 | 7,943 | 28.5 |
| 500 | 12,936 | 46.4 |
| 1,000 | 19,434 | 69.8 |

That gradient is the single most important caveat in this report. Two things cause it, and they pull
in the same direction.

**Coordinate provenance.** 5,667 of the in-scope OpenActive points (31.3%) sit *exactly* on a postcode centroid, which means the publisher geocoded them from a postcode rather than surveying the venue. A postcode centroid is the mean position of a postcode
unit, routinely 100m or more from the building it nominally locates, so such a point cannot be
expected to land within 200m of the right Active Places site. Note this is *publisher*
geocoding, not ours — our own ingestion falls back to a postcode centroid for only
11,023 venues (67.2%), which is why the
`location.postal_code` field alone badly understates the problem. See **Coordinate provenance** below
for the per-publisher split.

**Granularity.** Active Places records one point per *site*, effectively its centroid, while
OpenActive records the point a *session* happens at. A leisure complex, school campus, golf course or
park easily spans more than 200m, so a genuine match can sit outside the threshold
simply because the two datasets describe the same place at different resolution. The 100–250m band
bears this out: it contains entries such as a leisure centre 100m from a venue published by the
company that operates it.

Widening the threshold is not a free fix — at 500m or 1km, in an urban area, a match stops meaning
"the same place". 200m is the defensible conservative choice, and
26.4% should be read as a **lower bound** on true coverage.

## Coverage by region

| Region | Sites | Matched | Missing | Coverage % |
|---|---:|---:|---:|---:|
| South East | 5,186 | 1,263 | 3,923 | 24.4 |
| North West | 3,550 | 859 | 2,691 | 24.2 |
| South West | 3,503 | 897 | 2,606 | 25.6 |
| East of England | 3,347 | 935 | 2,412 | 27.9 |
| Yorkshire and The Humber | 3,033 | 682 | 2,351 | 22.5 |
| London | 2,826 | 1,110 | 1,716 | 39.3 |
| West Midlands | 2,609 | 633 | 1,976 | 24.3 |
| East Midlands | 2,494 | 659 | 1,835 | 26.4 |
| North East | 1,309 | 313 | 996 | 23.9 |

## Where are the most sites missing?

The direct answer to "where does OpenActive have the most missing sites". The first table ranks by
absolute shortfall — where the most sites are absent — and the second by coverage rate, restricted to
local authorities with at least 20 sites so that small areas do not dominate.

### Top 20 local authorities by number of missing sites

| LA code | Local authority | Sites | Matched | Missing | Coverage % | OA venues |
|---|---|---:|---:|---:|---:|---:|
| E06000065 | North Yorkshire | 540 | 117 | 423 | 21.7 | 271 |
| E08000035 | Leeds | 437 | 100 | 337 | 22.9 | 194 |
| E06000060 | Buckinghamshire | 417 | 100 | 317 | 24.0 | 194 |
| E06000066 | Somerset | 443 | 142 | 301 | 32.1 | 344 |
| E06000054 | Wiltshire | 337 | 73 | 264 | 21.7 | 145 |
| E06000047 | County Durham | 309 | 55 | 254 | 17.8 | 116 |
| E06000052 | Cornwall | 394 | 143 | 251 | 36.3 | 523 |
| E08000034 | Kirklees | 259 | 47 | 212 | 18.1 | 96 |
| E08000032 | Bradford | 263 | 66 | 197 | 25.1 | 140 |
| E06000057 | Northumberland | 244 | 51 | 193 | 20.9 | 111 |
| E08000025 | Birmingham | 305 | 118 | 187 | 38.7 | 292 |
| E06000059 | Dorset | 248 | 66 | 182 | 26.6 | 172 |
| E06000051 | Shropshire | 217 | 38 | 179 | 17.5 | 77 |
| E06000049 | Cheshire East | 208 | 36 | 172 | 17.3 | 73 |
| E06000064 | Westmorland and Furness | 224 | 60 | 164 | 26.8 | 170 |
| E06000050 | Cheshire West and Chester | 213 | 50 | 163 | 23.5 | 127 |
| E08000019 | Sheffield | 228 | 66 | 162 | 28.9 | 160 |
| E06000063 | Cumberland | 214 | 54 | 160 | 25.2 | 192 |
| E06000011 | East Riding of Yorkshire | 205 | 48 | 157 | 23.4 | 157 |
| E08000036 | Wakefield | 178 | 24 | 154 | 13.5 | 72 |

### Bottom 20 local authorities by coverage rate (≥ 20 sites)

| LA code | Local authority | Sites | Matched | Missing | Coverage % | OA venues |
|---|---|---:|---:|---:|---:|---:|
| E07000063 | Lewes | 62 | 2 | 60 | 3.2 | 6 |
| E07000200 | Babergh | 73 | 5 | 68 | 6.8 | 14 |
| E07000034 | Chesterfield | 43 | 3 | 40 | 7.0 | 22 |
| E07000079 | Cotswold | 92 | 7 | 85 | 7.6 | 18 |
| E07000108 | Dover | 65 | 6 | 59 | 9.2 | 23 |
| E07000039 | South Derbyshire | 68 | 7 | 61 | 10.3 | 21 |
| E08000031 | Wolverhampton | 77 | 8 | 69 | 10.4 | 13 |
| E07000199 | Tamworth | 27 | 3 | 24 | 11.1 | 5 |
| E07000038 | North East Derbyshire | 61 | 7 | 54 | 11.5 | 10 |
| E07000033 | Bolsover | 52 | 6 | 46 | 11.5 | 11 |
| E07000043 | North Devon | 68 | 8 | 60 | 11.8 | 19 |
| E07000071 | Colchester | 92 | 11 | 81 | 12.0 | 38 |
| E07000067 | Braintree | 92 | 11 | 81 | 12.0 | 29 |
| E07000207 | Elmbridge | 90 | 11 | 79 | 12.2 | 23 |
| E07000075 | Rochford | 41 | 5 | 36 | 12.2 | 9 |
| E07000228 | Mid Sussex | 120 | 15 | 105 | 12.5 | 28 |
| E08000007 | Stockport | 157 | 20 | 137 | 12.7 | 56 |
| E07000215 | Tandridge | 71 | 9 | 62 | 12.7 | 14 |
| E08000015 | Wirral | 155 | 20 | 135 | 12.9 | 64 |
| E07000082 | Stroud | 91 | 12 | 79 | 13.2 | 28 |

Full per-authority figures for all 296 local authorities are in
`coverage_by_local_authority.csv`.

## What kind of estate is covered?

This is what makes the headline actionable. Coverage is not uniform across the estate: the sites
OpenActive reaches are concentrated in the parts of the sector that publish booking data at all.

### By ownership type group

| Group | Sites | Matched | Missing | Coverage % |
|---|---:|---:|---:|---:|
| Local Authority | 9,958 | 2,758 | 7,200 | 27.7 |
| Commercial | 5,455 | 1,229 | 4,226 | 22.5 |
| Education | 4,977 | 1,873 | 3,104 | 37.6 |
| Sports Club | 4,740 | 842 | 3,898 | 17.8 |
| Community Organisation | 1,720 | 403 | 1,317 | 23.4 |
| Others | 1,001 | 246 | 755 | 24.6 |
| Not Known | 6 | 0 | 6 | 0.0 |

### By management type group

| Group | Sites | Matched | Missing | Coverage % |
|---|---:|---:|---:|---:|
| Others | 10,055 | 1,901 | 8,154 | 18.9 |
| Local Authority | 6,163 | 1,413 | 4,750 | 22.9 |
| Commercial | 5,576 | 1,631 | 3,945 | 29.3 |
| Education | 4,487 | 1,627 | 2,860 | 36.3 |
| Trust | 1,568 | 778 | 790 | 49.6 |
| Not Known | 8 | 1 | 7 | 12.5 |

### By Active Places facility type

A site is counted once per distinct facility type it offers, so these rows sum to more than the site
total. The export ships no code-to-label lookup in `data/active_places/`, so codes are shown raw;
resolving them needs the Active Places data dictionary.

| Facility type code | Sites | Matched | Missing | Coverage % |
|---|---:|---:|---:|---:|
| 5 | 15,227 | 3,126 | 12,101 | 20.5 |
| 6 | 6,456 | 2,860 | 3,596 | 44.3 |
| 2 | 6,107 | 2,611 | 3,496 | 42.8 |
| 17 | 5,146 | 1,674 | 3,472 | 32.5 |
| 12 | 4,556 | 2,277 | 2,279 | 50.0 |
| 8 | 3,874 | 1,791 | 2,083 | 46.2 |
| 7 | 2,942 | 1,368 | 1,574 | 46.5 |
| 9 | 1,854 | 438 | 1,416 | 23.6 |
| 13 | 1,160 | 586 | 574 | 50.5 |
| 18 | 670 | 154 | 516 | 23.0 |
| 20 | 398 | 157 | 241 | 39.4 |
| 1 | 329 | 211 | 118 | 64.1 |
| 4 | 298 | 125 | 173 | 41.9 |
| 3 | 288 | 114 | 174 | 39.6 |
| 11 | 43 | 11 | 32 | 25.6 |
| 10 | 38 | 24 | 14 | 63.2 |

## Which publishers account for the coverage?

| Publisher | AP sites covered | OA venues | LAs |
|---|---:|---:|---:|
| British Cycling | 2,631 | 2,493 | 279 |
| England Netball | 2,228 | 1,786 | 289 |
| Playwaze | 1,210 | 1,130 | 211 |
| Played | 752 | 625 | 222 |
| Open Sessions | 567 | 466 | 110 |
| Bookwhen | 381 | 310 | 159 |
| British Triathlon | 353 | 278 | 154 |
| GLL | 303 | 202 | 59 |
| Everyone Active | 292 | 194 | 62 |
| Better | 287 | 203 | 54 |
| Good Gym | 241 | 195 | 63 |
| Exercise Anywhere | 152 | 131 | 59 |
| Schools Plus Ltd | 125 | 107 | 56 |
| Places Leisure | 114 | 76 | 29 |
| SportSuite | 98 | 71 | 21 |
| Lawn Tennis Association | 87 | 69 | 57 |
| TeamUp | 73 | 64 | 39 |
| Serco Leisure | 60 | 45 | 13 |
| Parkwood Leisure Ltd, its subsidiaries and partner organisations | 59 | 43 | 23 |
| Courtside Hubs CIC | 52 | 42 | 14 |
| Our Parks | 40 | 29 | 19 |
| Halo | 31 | 17 | 7 |
| Actihire | 28 | 26 | 21 |
| Everyone Active (data) | 26 | 15 | 11 |
| Upshot | 26 | 24 | 12 |

2,197 matched sites are covered by more than one publisher (29.9% of matched sites), which is where
duplicate listings of the same venue are most likely.

## Match channels

Three channels decide whether a site is covered, and every pair records which one fired.

- **`spatial`** — an OpenActive venue with surveyed coordinates within 200m.
- **`spatial_and_postcode`** — within 200m *and* sharing the postcode. The strongest
  evidence available here.
- **`postcode`** — the postcodes match and the venue is within 1000m, but
  further than 200m. This is what recovers venues published at a postcode centroid.
- **`spatial_centroid_only`** — within 200m, but the venue's coordinates *are* a
  postcode centroid and the postcodes do not agree. Proximity here is partly an artefact of where the
  centroid happens to fall, so it is ranked below the others when choosing a site's primary pair. It
  still counts as a match.
- **`name`** — the last resort, run only after the other channels have finished. A site and a venue
  within 500m whose names agree at 0.8 or better on the
  measure described below. Only pairs that rescue a previously unmatched site or venue are considered,
  so this channel can add coverage but never override stronger evidence.

| Method | Pairs | Sites | Venues | Median distance (m) |
|---|---:|---:|---:|---:|
| spatial | 5,236 | 4,407 | 4,243 | 97.9 |
| spatial_and_postcode | 2,641 | 2,385 | 2,361 | 73.7 |
| spatial_centroid_only | 1,113 | 994 | 955 | 146.6 |
| postcode | 883 | 811 | 785 | 301.7 |
| name | 161 | 161 | 161 | 310.2 |

The 1000m cap on the postcode channel keeps out pairs that share a
postcode string but sit implausibly far apart, which indicates bad data on one side rather than a
match. A postcode is available for 11,924 of the
18,112 in-scope points, combining what the feed declared with what could be recovered
by snapping a centroid point back to its postcode.

### How names are compared

Venue names describe the same place in two registers — `Whitwick & Coalville Lc` against
`WHITWICK AND COALVILLE LEISURE CENTRE`. Bridging them needs case folding, `&`/`and` unification,
expansion of sector abbreviations (`Lc`, `RFC`, `CC`), and removal of the address publishers append to
the name (`Queens Park Tennis Club, Queens Park, East Drive, Brighton, BN2 0BQ`). Scoring is
token-based, not edit-distance: word order differs between the registers, and an edit distance over a
name with an address glued to it is meaningless. The score averages Jaccard with containment, so an
appended address does not sink a true match while a name that merely shares a word still scores low.

The threshold of 0.8 was calibrated against the data by hand. Below roughly 0.8
the channel starts pairing venues that share only a town — `Suffolk Rd, Andover` against
`ANDOVER LEISURE CENTRE`. A second guard handles the same failure from the other direction: publishers
often put a bare location in the name field, and since generic words like "leisure centre" are
stripped, `Wetherby` would otherwise score a perfect 1.0 against `WETHERBY LEISURE CENTRE`. When every
shared word is a place name — drawn from the export's own `Town`, `Local Authority`, `County` and
`Region` columns rather than an external gazetteer — the pair survives only if the whole names agree
and the site name adds no distinctive word of its own. That keeps `Whitwick & Coalville Lc`, whose
tokens are themselves town names, while rejecting `Clacton-on-Sea, UK` against
`PUREGYM (CLACTON-ON-SEA)`.

Matches found this way run at a median 1.0 similarity and
310.2m apart — well beyond the spatial buffer, which is the point.

| Active Places site | OpenActive venue | Local authority | Distance (m) | Similarity |
|---|---|---|---:|---:|
| DOVERCOURT BAY LIFESTYLES | Dovercourt Bay \| Dovercourt Bay Lifestyles | Tendring | 231.0 | 1.0 |
| TARKA LEISURE CENTRE | Tarka | North Devon | 455.1 | 1.0 |
| HOLMLEIGH PARK | Holmleigh Park | Gloucester | 428.3 | 1.0 |
| HARPENDEN LEISURE CENTRE | Harpenden Leisure Centre | St Albans | 251.7 | 1.0 |
| WHITWICK AND COALVILLE LEISURE CENTRE | Whitwick & Coalville Lc | North West Leicestershire | 304.4 | 1.0 |
| FOREST HILL POOLS | Forest Hill Pools | Lewisham | 217.7 | 1.0 |
| NEWHAM LEISURE CENTRE | Newham Leisure Centre \| Newham Leisure Centre, Prince Regent Ln, London E13 8SD, UK | Newham | 267.5 | 1.0 |
| THE REEF LEISURE CENTRE | Sheringham Football Club (Astro Court) \| The Reef | North Norfolk | 346.3 | 1.0 |
| WHITEHILL AND BORDON LEISURE CENTRE | Whitehill And Bordon Lc | East Hampshire | 491.1 | 1.0 |
| UNIVERSITY OF CHESTER (CHESTER CAMPUS) | Fitness Suite \| Gymnasium \| Small Hall \| Swimming Pool, Exton Park Campus \| University of Chester, Parkgate Road, Chester, UK | Cheshire West and Chester | 215.4 | 1.0 |
| VICTORY SWIM AND FITNESS CENTRE | Victory Swim and Fitness Centre | North Norfolk | 275.3 | 1.0 |
| DORMERS WELLS LEISURE CENTRE | Dormers Wells Leisure Centre | Ealing | 401.9 | 1.0 |
| CO-OP ACADEMY BELLE VUE | Belle Vue Sports Village \| Belle Vue Sports Village M12 4TF \| Manchester Belle Vue Sports Village \| National Basketball Performance Centre | Manchester | 413.1 | 0.8 |
| GREAT SANKEY NEIGHBOURHOOD HUB | Great Sankey Neighbourhood Hub | Warrington | 233.4 | 1.0 |
| OUTWOOD ACADEMY ACKLAM | Outwood Academy Acklam | Middlesbrough | 340.7 | 1.0 |

One caveat specific to the postcode channel: Active Places sites are not uniquely postcoded — several sites
can share one postcode — so the postcode channel is inherently many-to-many. The `is_primary_for_site`
flag in the mapping CSV resolves that by ranking on channel strength first, then distance.

## Coordinate provenance

A point that sits *exactly* on a postcode centroid was geocoded from a postcode, not surveyed. Those
points are structurally hard to match: the centroid of a postcode unit is commonly 100m or more from
the building. Detected by snapping each point to Code-Point Open within 1m — a test that flags only
1.5% of Active Places sites, which carry real building coordinates, so it is specific.

5,667 of 18,112 in-scope points (31.3%) are
postcode centroids, and they are heavily concentrated: **British Cycling** alone
accounts for 4,992 of them. Excluding that publisher, the rate
across the rest of the data is **6.4%**.

That concentration matters for how you read the headline. The publishers whose estate actually
overlaps Active Places — leisure operators and facility bookings — largely publish real coordinates,
so the coverage figure is a fair measurement for them. The publishers with high centroid rates are
mostly publishing outdoor and route-based activity that Active Places does not catalogue anyway.

| Publisher | Points | Postcode centroids | Centroid % |
|---|---:|---:|---:|
| British Cycling | 7,523 | 4,992 | 66.4 |
| Playwaze | 2,416 | 72 | 3.0 |
| England Netball | 2,246 | 13 | 0.6 |
| Open Sessions | 941 | 128 | 13.6 |
| Played | 861 | 27 | 3.1 |
| Bookwhen | 730 | 19 | 2.6 |
| Exercise Anywhere | 544 | 45 | 8.3 |
| Good Gym | 475 | 147 | 30.9 |
| British Triathlon | 447 | 4 | 0.9 |
| Better | 220 | 16 | 7.3 |
| GLL | 215 | 4 | 1.9 |
| Everyone Active | 214 | 11 | 5.1 |
| TeamUp | 148 | 1 | 0.7 |
| Schools Plus Ltd | 145 | 1 | 0.7 |
| SportSuite | 129 | 101 | 78.3 |
| Places Leisure | 78 | 0 | 0.0 |
| Lawn Tennis Association | 78 | 6 | 7.7 |
| Our Parks | 54 | 0 | 0.0 |
| Serco Leisure | 54 | 0 | 0.0 |
| Parkwood Leisure Ltd, its subsidiaries and partner organisations | 53 | 8 | 15.1 |

## The OpenActive side: venues with no Active Places site

8,565 English OpenActive venues (52.2%) match no
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

| Venue name | Publisher | District | Opportunities | Nearest AP site | Distance (m) |
|---|---|---|---:|---|---:|
| Squirrels Bar Squash Court A | Playwaze | Manchester | 9,572 | UNIVERSITY OF MANCHESTER (ARMITAGE SPORTS CENTRE) | 357.9 |
| Cherry Dance Studio 1 \| Client Venue TBC \| EveryBody Fit GYM \| Indoor- Main Black Mat Space \| Stroud Green School | British Cycling\|TeamUp | Bexley | 5,940 | PLANET TURF CROSSWAYS ARENA | 255.6 |
| EAST COAST FITNESS \| EAST COAST FITNESS (INDOORS) \| EAST COAST FITNESS (OUTDOORS) | TeamUp | County Durham | 5,055 | BRUCES GYM | 602.4 |
| Oval - studio 1 \| Oval - studio 2 | TeamUp | Lambeth | 4,418 | REAY PRIMARY SCHOOL | 245.4 |
| Fundamentals Introduction \| Level 1-2. Technique \| Level 2-3. Flow. \| Level 3-4. Advance \| Private lesson \| Women only | TeamUp | Cambridge | 3,360 | NCI SPORTS AND SOCIAL CLUB | 686.3 |
| Fullam Ketch Fitness | Playwaze | Sheffield | 3,195 | SNAP FITNESS (STOCKSBRIDGE) | 240.4 |
| David Ross Sports Village | Playwaze | Nottingham | 3,099 | NOTTINGHAM TENNIS CENTRE | 541.6 |
| Koala Klubs (Dereham) | Parkwood Leisure Ltd, its subsidiaries and partner organisations\|Played | Breckland | 3,085 | DEREHAM LEISURE CENTRE | 261.2 |
| _blank_ | Serco Leisure | Basingstoke and Deane | 2,945 | PLANET ICE BASINGSTOKE | 244.8 |
| _blank_ | Parkwood Leisure Ltd, its subsidiaries and partner organisations | Amber Valley | 2,630 | HORSLEY LODGE GOLF CLUB | 1,211.9 |
| _blank_ | Parkwood Leisure Ltd, its subsidiaries and partner organisations | Cheshire West and Chester | 2,316 | THE NESTON CLUB | 877.0 |
| The Queen's Diamond Jubilee Centre, Rugby | England Netball\|GLL | Rugby | 1,664 | RUGBY SCHOOL SPORTS CENTRE | 230.3 |
| Hamble Tennis Club, Park Road, Frinton, FR6 7YY | Playwaze | Tendring | 1,481 | SPARKLE LADIES GYM | 249.4 |
| Swinton and Pendlebury Leisure Centre | England Netball | Salford | 1,475 | MUSCLE & FITNESS GYM | 558.8 |
| _blank_ | Teignbridge Leisure | Teignbridge | 1,472 | SHALDON APPROACH GOLF COURSE | 206.3 |
| re:new Mind + Body at your Gym | Playwaze | East Lindsey | 1,435 | WOODHALL SPA JUBILEE PARK | 505.0 |
| Queen Alexandra College | Playwaze | Birmingham | 1,394 | HARBORNE POOL AND FITNESS CENTRE | 458.2 |
| The Fox Den | TeamUp | Wokingham | 1,381 | THE EMMBROOK SCHOOL | 291.4 |
| Empower Fitness Studio | Playwaze | East Lindsey | 1,314 | ALFORD SQUASH CLUB | 340.2 |
| _blank_ | strouddistrictcouncil | Stroud | 1,296 | ACTIVE LIFESTYLES DURSLEY | 409.6 |

### By local authority district

| District | Unmatched venues | Opportunities |
|---|---:|---:|
| Cornwall | 339 | 2,473 |
| Somerset | 190 | 2,240 |
| North Yorkshire | 158 | 961 |
| Birmingham | 145 | 3,079 |
| West Northamptonshire | 128 | 4,342 |
| Cumberland | 121 | 754 |
| Dorset | 108 | 3,373 |
| Westmorland and Furness | 105 | 499 |
| East Riding of Yorkshire | 104 | 1,361 |
| Buckinghamshire | 92 | 1,183 |
| North Northamptonshire | 87 | 3,192 |
| Leeds | 87 | 1,934 |
| East Lindsey | 87 | 13,947 |
| St Albans | 80 | 2,873 |
| Sheffield | 79 | 4,242 |
| Bradford | 76 | 464 |
| Cheshire West and Chester | 72 | 3,055 |
| Wiltshire | 72 | 701 |
| Dacorum | 68 | 244 |
| New Forest | 64 | 515 |

### By publisher

| Publisher | Unmatched venues | Opportunities |
|---|---:|---:|
| British Cycling | 4,903 | 47,627 |
| Playwaze | 1,206 | 92,881 |
| Open Sessions | 450 | 2,305 |
| England Netball | 426 | 14,540 |
| Bookwhen | 411 | 4,279 |
| Exercise Anywhere | 397 | 1,867 |
| Good Gym | 279 | 995 |
| Played | 218 | 8,844 |
| British Triathlon | 156 | 672 |
| TeamUp | 79 | 38,484 |
| SportSuite | 55 | 107 |
| Schools Plus Ltd | 37 | 684 |
| Our Parks | 25 | 1,045 |
| Upshot | 21 | 1,367 |
| GLL | 13 | 3,541 |
| Better | 11 | 2,191 |
| Courtside Hubs CIC | 10 | 155 |
| Lawn Tennis Association | 9 | 237 |
| Everyone Active | 7 | 3,932 |
| Orchard Learning Alliance | 6 | 28 |

## Scope and data quality

Active Places is an England-only register, so the headline figures compare like with like by
restricting the OpenActive side to England. Nothing is silently discarded — the excluded points are:

| OpenActive points | Count |
|---|---:|
| Distinct `(dataset_url, location)` points fetched | 19,507 |
| Excluded: coordinates outside the GB envelope | 47 |
| Excluded: resolved to a country other than England | 1,215 |
| Excluded: no country resolved | 133 |
| **In scope (England)** | **18,112** |

Those 18,112 raw points collapse to 16,405 venues after
single-link clustering at 50m — a 9.4%
reduction, which is the scale of near-duplicate publishing in the data. Single-link clustering can
chain across dense areas, so cluster spread is checked: the widest cluster spans
105m and 0 clusters exceed 250m.

## Caveats

- **The 200m threshold drives the spatial channel.** Spatial-only coverage is
  14.7% at 100m and 28.5% at 250m. Treat 26.4% as a lower bound on true coverage, not a
  precise measurement, and see the sensitivity section above for why the two datasets disagree at
  this scale.
- **The name channel is the weakest evidence here.** It is applied last, only to records the other
  channels could not reach, and every pair it produces is labelled `name` with its similarity score in
  the mapping CSV so it can be filtered out. Manual review of a sample found it sound, but a residue
  of same-area-different-facility pairs remains — a school next to the lido it shares a name with.
- **The postcode channel is a string match, not a location.** It asserts that a venue and a site
  share a postcode unit, which is strong evidence but not proof — postcode units can contain several
  distinct facilities. The 1000m cap and the primary-pair ranking limit
  the damage, but pairs carrying `match_method = postcode` are weaker than the spatial ones and the
  mapping CSV labels them so they can be filtered out.
- **Route- and meeting-point publishers depress the OpenActive side.** The largest single source of
  unmatched venues publishes rides and outdoor events whose coordinates are start points — laybys,
  car parks, trailheads — rather than facilities, and 4,992 of
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
