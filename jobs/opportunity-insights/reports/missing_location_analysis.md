# Missing Location Data — Root-Cause Analysis

- Date: 2026-06-23
- Source table: `openactive-monitor.openactive_analytics.opportunities`
- Scope: future-dated opportunities (`startDate >= CURRENT_DATE()`)
- Author: Data pipeline team

## Summary

Of the future-dated opportunities currently held in the `opportunities` table,
roughly 18% carry no resolvable location. The shortfall is not a single defect:
it splits into two broad classes. The first is **broken superEvent inheritance**,
where a `Slot` (or `ScheduledSession`) references a parent `FacilityUse`
(or `SessionSeries`) that is absent from the database, so there is nothing to
inherit location from. The second is **un-mappable coordinates**, where a
location is present on the record but cannot be resolved to a UK administrative
area — either because the feed is genuinely non-UK, the latitude/longitude pair
is transposed, the coordinates are simply wrong, or the boundary file lacks the
resolution to capture a coastal point.

The inheritance failures account for the large majority of the gap and are
concentrated in a small number of `Slot`-heavy datasets.

## Headline figures

| Metric | Count |
|---|---:|
| Future opportunities with location | 8,496,593 |
| Future opportunities without location | 1,911,532 |
| Total future opportunities | 10,408,125 |
| Share without location | ~18.4% |

### Missing-location breakdown by kind

| Rank | Kind | Count |
|---:|---|---:|
| 1 | Slot | 1,736,191 |
| 2 | ScheduledSession | 173,948 |
| 3 | _null_ | 1,079 |
| 4 | SessionSeries | 158 |
| 5 | Event | 122 |
| 6 | CourseInstance | 26 |
| 7 | HeadlineEvent | 8 |

`Slot` records dominate the gap (≈91%), which is consistent with a
superEvent-inheritance problem: a `Slot` has no location of its own and depends
entirely on its parent `FacilityUse`.

## Class 1 — Missing parent events (broken inheritance)

In every case below the child opportunity is well-formed and references a parent
via `facilityUse`, but the referenced parent is not present in our store, so the
denormalisation step has no source to inherit `location` from. The five datasets
below account for the bulk of the affected `Slot` rows.

### 1. Loughborough University — ~438K problematic future slots

- Dataset: `https://loughboroughuniversity-openactive.legendonlineservices.co.uk/OpenActive`
- Example reference: `facilityUse: ".../api/facility-uses/1013-1"`

The publisher's `facility-uses` feed exposes only 7 items, yet the slots
reference 63 distinct `facilityUse` IDs. The feed appears stale — it has not
been refreshed in some time. The volume is amplified by the publisher's
scheduling pattern: 30-minute slots are generated for every facility across the
full forward year (out to 2027-06-16), so a small set of missing parents fans
out into a very large number of orphaned slots.

**Nature:** upstream/publisher data gap. Not recoverable on our side without the
parent records.

### 2. Better (GLL) — ~425K problematic future slots

- Dataset: `https://better-admin.org.uk/api/openactive/better`
- Example reference:
  `facilityUse: ".../facility-uses/activity_recurrence_group:2968/individual-facility-uses/3372bcee073fafe696d6138dbdfe7ea2"`

Here the parent is present, but embedded: the `IndividualFacilityUse` is an
inline object nested inside the `FacilityUse`
(`.../facility-uses/activity_recurrence_group:2968`) rather than being published
as a standalone item. This is a valid but uncommon RPDE shape that our
denormalisation logic does not currently traverse, so the inline parent is never
indexed for lookup.

**Nature:** pipeline limitation. Recoverable by extending parent extraction to
resolve inline `individual-facility-uses` nested within a `FacilityUse`.

### 3. LRSO (Bookteq) — ~73K problematic future slots

- Dataset: `https://lrso.bookteq.com/api/open-active`
- Example reference:
  `facilityUse: ".../16e5291e-.../facility-uses/0083f23e-..."`

20 `IndividualFacilityUse` records that should exist are missing. These were
expected to have been carried over from the legacy pickle files but were never
ingested, leaving a hole in the baseline.

**Nature:** internal data-store gap inherited from the legacy migration. The
clean fix is a full re-crawl from scratch to establish a consistent baseline.

### 4. Leisure Centre (Legend) — ~42K problematic future slots

- Dataset: `https://leisurecentre-openactive.legendonlineservices.co.uk/OpenActive`
- Example reference: `facilityUse: ".../api/facility-uses/1217-143"`

The referenced facility uses genuinely do not exist in the publisher's feed —
139 such missing `facilityUse` items are referenced but never published.

**Nature:** upstream/publisher data gap. Not recoverable on our side.

### 5. Serco (Legend) — ~26K problematic future slots

- Dataset: `https://serco-openactive.legendonlineservices.co.uk/OpenActive`
- Example reference: `facilityUse: ".../api/facility-uses/108-123"`

The feed publishes 136 `FacilityUse` items but the slots reference 153 distinct
parents — 17 are simply absent from the feed.

**Nature:** upstream/publisher data gap. Not recoverable on our side.

### Class 1 disposition

| Dataset | ~Future slots | Root cause | Actionable here? |
|---|---:|---|:--:|
| Loughborough University | 438K | Stale/incomplete parent feed | No |
| Better (GLL) | 425K | Inline `IndividualFacilityUse` not parsed | **Yes** |
| LRSO | 73K | Missing rows from legacy migration | **Yes (re-crawl)** |
| Leisure Centre | 42K | Parents absent from publisher feed | No |
| Serco | 26K | Parents absent from publisher feed | No |

Two of the five — Better and LRSO, together ~498K future slots — are within our
control. The remaining three are genuine publisher-side omissions and should be
reported back to the data providers rather than patched.

## Class 2 — Coordinates present but un-mappable

These records carry a `location` with coordinates, but the point cannot be
resolved to a UK district/region by the geolocation step.

### 2a. Non-UK feeds

| Dataset | Example coordinates | Country | ~Opportunities |
|---|---|---|---:|
| `elgarparkregionalhockeyassociation.bookteq.com/api/open-active` | `-37.797286, 145.116041` | Australia | 22K |
| `eireoggaa.bookteq.com/api/open-active` | `51.87473, -8.667948` | Ireland (RoI) | 70K |
| `uatbook.myeveryoneactive.com/OpenActive/` | `41.69301, 44.79542` | Georgia | 6,432 |

These resolve correctly to their real locations — they are simply outside the UK
boundary set. The `uatbook` host is also a UAT/test environment and should be
excluded from production aggregates regardless.

**Action:** flag and exclude as out-of-scope rather than treat as errors.

### 2b. Latitude/longitude transposed

| Dataset | Example (as published) |
|---|---|
| `leisurefocus-openactive.legendonlineservices.co.uk/OpenActive` | `latitude: -0.71382, longitude: 51.51039` (~18K) |
| `leisurecentre-openactive.legendonlineservices.co.uk/OpenActive` | `latitude: -0.425748, longitude: 51.428657` (~8K) |
| `barrowcouncil-openactive.legendonlineservices.co.uk/OpenActive` | lat/long flipped |

The signature is unmistakable: a latitude near `-0.4` with a longitude near
`51.4` is a swapped UK coordinate. These are recoverable in-pipeline by detecting
the swap (latitude outside UK range while the transposed pair falls inside it)
and correcting before the boundary lookup. The shared Legend host suggests a
provider-side export bug worth reporting upstream as well.

**Action:** add a transposition guard to the geolocation step.

### 2c. Wrong coordinates

| Dataset | Example coordinates | Note | ~Opportunities |
|---|---|---|---:|
| `lrso.bookteq.com/api/open-active` | `52.9665, 1.2121` | Falls in the sea (off the Norfolk coast) | 27K |
| `strouddistrictcouncil-openactive.legendonlineservices.co.uk/OpenActive` | `51.7499, 2.2251` | Falls in the sea | 1.7K |

These are not transpositions — the points are genuinely wrong and land in open
water. Nothing on our side can recover the true location; they need correcting
at source.

**Action:** report to publisher; cannot be fixed in-pipeline.

### 2d. Boundary-file resolution

A residual group of points sits on the UK coastline — for example
`53.927373, -3.015922` near the Fylde coast — and falls just outside the polygons
in the current GeoJSON boundary file. The coordinates are correct; the boundary
geometry is too coarse to capture them.

**Action:** adopt a higher-resolution boundary file (or apply a small coastal
buffer/snap-to-nearest) for points that miss on the first pass. Affects ~1K
opportunities.

## Recommended actions

Ordered by impact and feasibility:

1. **Parse inline `IndividualFacilityUse` objects** nested within `FacilityUse`
   items (Better / GLL). Recovers ~425K future slots.
2. **Full re-crawl from scratch** to rebuild a consistent baseline and close the
   legacy-migration gaps (LRSO and similar). Recovers ~73K slots and removes a
   class of silent inconsistencies.
3. **Add a latitude/longitude transposition guard** to the geolocation step.
   Recovers ~26K+ opportunities across the Legend datasets.
4. **Upgrade the boundary file resolution** (or add coastal snapping) to capture
   valid coastal points. Recovers ~1K opportunities.
5. **Report upstream omissions** to the affected publishers (Loughborough,
   Leisure Centre, Serco missing parents; LRSO/Strouddistrict bad coordinates).
   Not fixable in-pipeline.
6. **Tag and exclude non-UK and UAT feeds** from production aggregates so they no
   longer inflate the "missing location" count.

Items 1–4 are within our control and together address roughly 525K future slots
plus the coordinate-quality issues. The remainder are publisher-side and should
be tracked as data-quality tickets against the providers.

## Appendix — Replication queries

Future `Slot` rows per dataset that could not inherit location from a parent:

```sql
SELECT
  DISTINCT dataset_url, COUNT(*) AS count
FROM `openactive-monitor.openactive_analytics.opportunities`
WHERE district_name IS NULL
  AND kind = "Slot"
  AND TO_JSON_STRING(location) = "{}"
  AND startDate >= TIMESTAMP(CURRENT_DATE())
GROUP BY dataset_url
ORDER BY count DESC
LIMIT 1000;
```

Inspect the affected `Slot` rows for a single dataset:

```sql
SELECT *
FROM `openactive-monitor.openactive_analytics.opportunities`
WHERE dataset_url = "https://lrso.bookteq.com/api/open-active"
  AND district_name IS NULL
  AND kind = "Slot"
  AND TO_JSON_STRING(location) = "{}"
  AND startDate >= TIMESTAMP(CURRENT_DATE())
LIMIT 1000;
```

