# field_usage — OpenActive data-model field-usage analysis

A standalone, **manually-run** analysis. It is **not** part of
the automated pipeline and writes no BigQuery tables — just two markdown files.

It answers: *which fields of the [OpenActive Modelling Opportunity Data](https://openactive.io/modelling-opportunity-data/)
model are unused or rarely used across all datasets/feeds (so they could be
deprecated), and which fields does each dataset actually use?*

## What it does

The OpenActive **model spec** that the analysis measures against — the entity
categories and each entity's fields with their `required` / `recommended` /
`optional` status — lives in **`field_usage/model_spec.py`**. It encodes the
[OpenActive Modelling Opportunity Data](https://openactive.io/modelling-opportunity-data/)
spec, primarily **V2.0**, and covers the top-level opportunity types (Event
family, FacilityUse, IndividualFacilityUse, Slot) **plus** the referenced /
nested model types — Organization, Person, Place, SportsActivityLocation,
GeoCoordinates, PostalAddress, Offer, PriceSpecification, Schedule, Concept
(physical activity), Brand (programme), ImageObject, ContactPoint,
OpeningHoursSpecification, QuantitativeValue and PropertyValue — so their field
usage is scored against the model rather than only "discovered".

The analysis uses a single chosen edition, selected with `--model-version`
(default **V2.0**); for a category that doesn't define the chosen version it
falls back to the newest available version at or below it. Feed `kind`s and
observed `@type`s are mapped to these categories via
`model_spec.FEED_TYPE_TO_SPEC_CATEGORY` (which also folds aliases such as
`PhysicalActivity → Concept` and `Programme → Brand`). The Event family
(SessionSeries, ScheduledSession, HeadlineEvent, CourseInstance, …) is folded
into a single `Event` category. The separate RouteGuide spec is **not** covered.

1. **Samples** `json_data` payloads from the `opportunities` table so it never
   pulls the whole ~15M-row table into memory.
   - **Sample size:** up to `--samples-per-kind` rows (default **400**) are
     taken *per `(dataset_url, feed_id, kind)` group*, not per table. The cap is
     applied independently to each group, so a small feed contributes all its
     rows while a huge feed is capped at 400 — every dataset/feed/type is
     represented regardless of how the row counts are skewed. Total rows pulled
     ≈ `400 × (number of distinct dataset/feed/kind groups)`.
   - **How randomness is achieved:** within each group, rows are ranked by
     `ROW_NUMBER() OVER (PARTITION BY dataset_url, feed_id, kind ORDER BY
     FARM_FINGERPRINT(CONCAT(CAST(RAND() AS STRING), id)))` and the top
     `--samples-per-kind` are kept. `RAND()` injects per-row randomness;
     concatenating it with the row `id` and hashing through `FARM_FINGERPRINT`
     turns it into a well-distributed 64-bit ordering key, so the kept rows are
     an unbiased random subset of each group rather than, say, the most recent
     or lowest-id ones. (Because `RAND()` is re-seeded each run, successive runs
     draw different samples — expect small run-to-run wobble on low-presence
     fields.)
2. **Walks** each payload recursively. Field keys are attributed to the `@type`
   of the object they belong to. In-place nested objects (e.g. an inline
   `organizer`, `location`, `offers[]`) that carry their own `@type` are
   recursed into; URI **string** references contribute nothing — the referenced
   object is counted where it is itself published, in its own row.
3. **Aggregates** presence counts per entity type, globally and per dataset
   (bounded memory — counters only, payloads discarded as they stream).
4. **Exact cross-check** — _currently disabled._ An exact `COUNTIF` over the
   full table for the known top-level model fields once produced an `Exact %`
   column, but its top-level-only, row-weighted percentages were confusing next
   to the per-group `Sampled %`, so the calculation is commented out in `run.py`
   and the column is hidden. The code is retained and can be re-enabled there.

## Run

From the `opportunity-insights/` directory (so `import bigquery_ops` resolves),
with the same `.env` / GCP credentials the other jobs use:

```bash
source virt/bin/activate            # the existing opportunity-insights venv
python -m field_usage.run --output-dir ./out/field_usage
```

Quick dry run:

```bash
python -m field_usage.run --samples-per-kind 5 --window-days 5 --verbose
```

## Options

| Option | Default | Meaning |
|--------|---------|---------|
| `--samples-per-kind` | 400 | Random samples per (dataset, feed, kind). |
| `--window-days` | (all-time) | Restrict to rows updated within N days of `--reference-date`. |
| `--reference-date` | today | Anchor for `--window-days` (`YYYY-MM-DD`). |
| `--rare-threshold` | 1.0 | Presence % below which a field is RARE. |
| `--low-threshold` | 10.0 | Presence % below which a field is LOW. |
| `--output-dir` | `./out/field_usage` | Where the reports are written. |
| `--exact-scan/--no-exact-scan` | on | _Disabled — no-op._ Exact full-table % (calculation commented out in `run.py`). |
| `--dump-percentages` | off | Include per-field % in the per-dataset dump. |
| `--model-version` | `V2.0` | OpenActive model spec version driving the field catalog (`V1.0`/`V1.1`/`V2.0`/`V2.1`). |
| `--verbose` | off | DEBUG logging. |

## Output

- `field_usage_model_report.md` — one section per spec category (Event,
  FacilityUse, IndividualFacilityUse, Slot, Organization, Person, Place, Offer,
  Concept, …): model-field usage table (sorted so deletion candidates float to
  the top), a **Deletion candidates** call-out (UNUSED / RARE), provider
  extension fields, and a trailing **discovered-only** section for any `@type`
  still not in the catalog.
- `field_usage_per_dataset_dump.md` — one section per dataset listing, per
  entity `@type`, the fields `present` and the model fields `absent`.

## Notes / caveats

- **Sampling** can under-report fields used in a tiny fraction of items, and
  because the sample is capped per dataset/feed/kind, `Sampled %` is weighted by
  group rather than by row — small feeds count as much as large ones.
- Nested dicts **without** an `@type` are not attributed to any type (a small,
  documented blind spot) to avoid polluting per-type percentages.
- Field **status** in the model report (required / recommended / optional) is
  taken from the single `--model-version` spec (default V2.0), sourced from
  `field_usage.model_spec.VERSION_SPECS` — not collapsed across versions.

## Module layout

| File | Responsibility |
|------|----------------|
| `model_spec.py` | Self-contained OpenActive model field catalog (`VERSION_SPECS`, category mapping, alternatives). Trimmed copy of the data from `quality.version_compliance`. |
| `model_catalog.py` | Adapter over `model_spec` (version resolution, category mapping, alternatives). |
| `walker.py` | Pure recursive `json_data` walker. |
| `aggregator.py` | Streaming counters + result computation. |
| `queries.py` | Sampling and exact-scan SQL builders. |
| `report.py` | Markdown renderers. |
| `run.py` | `click` CLI + orchestration. |
