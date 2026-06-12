---
name: bigquery-schemas
description: Use this skill as a reference for the exact BigQuery table schemas in the openactive_analytics dataset. Consult this before writing any SQL, creating DataFrames from query results, or adding/modifying BigQuery ingestion code.
---

# Skill: BigQuery Table Schemas

## Dataset
**Project:** `openactive-monitor`  
**Dataset:** `openactive_analytics`

---

## Table: `feeds`
Feed metadata collected from OpenActive catalogues.  
**Merge key:** `id`

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `id` | STRING | NULLABLE | Stable ID derived from feed URL |
| `url` | STRING | NULLABLE | Full URL of the RPDE feed endpoint |
| `type` | STRING | NULLABLE | Feed type (e.g. `SessionSeries`, `Slot`, `FacilityUse`, …) |
| `dataset_name` | STRING | NULLABLE | Human-readable dataset name from JSON-LD |
| `dataset_url` | STRING | NULLABLE | URL of the dataset site page |
| `license_url` | STRING | NULLABLE | License URL from JSON-LD |
| `logo_url` | STRING | NULLABLE | Publisher logo URL |
| `publisher_name` | STRING | NULLABLE | Publisher name from JSON-LD |
| `last_access` | DATE | NULLABLE | Date when this feed was last seen |
| `provider` | STRING | NULLABLE | Domain of the catalogue URL |
| `rpde_version` | STRING | NULLABLE | RPDE spec version URL |
| `model_version` | STRING | NULLABLE | Modelling Opportunity Data spec version URL |
| `is_regular` | BOOLEAN | NULLABLE | `TRUE` if in regular catalog; `FALSE` if preview-only |

---

## Table: `feed_ingestion`
Append-only log of feed collection runs.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `ingestion_date` | TIMESTAMP | NULLABLE | UTC timestamp of the ingestion run |
| `number_of_feeds` | INTEGER | NULLABLE | Total feeds collected |
| `feed_ids` | JSON | NULLABLE | JSON array of all feed IDs |
| `number_of_catalogues` | INTEGER | NULLABLE | Number of catalogue URLs visited |
| `catalogues` | JSON | NULLABLE | JSON array of catalogue URLs |
| `number_of_datasets` | INTEGER | NULLABLE | Number of dataset URLs visited |
| `datasets` | JSON | NULLABLE | JSON array of dataset URLs |

---

## Table: `opportunities`
Denormalized opportunity data from RPDE feeds.  
**Scale:** ~8 million rows, ~10 GB — treat as the primary memory/performance bottleneck.  
**Composite merge key:** `(dataset_url, feed_id, id)`

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `dataset_url` | STRING | NULLABLE | Dataset URL |
| `feed_id` | STRING | NULLABLE | Feed identifier (normalised feed URL) |
| `id` | STRING | NULLABLE | ID from the RPDE feed |
| `data_id` | STRING | NULLABLE | `@id` from the opportunity data (may differ from RPDE item ID) |
| `kind` | STRING | NULLABLE | `@type` of the opportunity (e.g. `Event`, `FacilityUse`, `Slot`) |
| `modified` | INTEGER | NULLABLE | Modified timestamp from the RPDE feed |
| `json_data` | JSON | NULLABLE | Full opportunity payload as ingested, no transformations |
| `inherited_data` | JSON | NULLABLE | Properties inherited from superEvent/parent |
| `activity` | JSON | NULLABLE | Activity labels associated with the opportunity |
| `facility` | JSON | NULLABLE | Facility label associated with the opportunity |
| `location` | JSON | NULLABLE | Geographical location (`latitude`, `longitude`, `postal_code`, …) |
| `district_name` | STRING | NULLABLE | UK Local Authority District name resolved from location (`LAD24NM`) |
| `region_name` | STRING | NULLABLE | UK region name resolved from location (`eer18nm`) |
| `publisher_name` | STRING | NULLABLE | Publisher name copied from `feeds.publisher_name` via `dataset_url` |
| `district_code` | STRING | NULLABLE | UK Local Authority District code resolved from `district_name` (`LAD24CD`) |
| `region_code` | STRING | NULLABLE | UK region code resolved from `district_name` |
| `country_code` | STRING | NULLABLE | UK country code resolved from `district_name` |
| `country_name` | STRING | NULLABLE | UK country name resolved from `district_name` |
| `startDate` | TIMESTAMP | NULLABLE | Opportunity start date and time |
| `endDate` | TIMESTAMP | NULLABLE | Opportunity end date and time |
| `ageRange` | JSON | NULLABLE | Age range for the opportunity |
| `level` | JSON | NULLABLE | Difficulty level of the opportunity |
| `has_superEvent` | JSON | NULLABLE | SuperEvent URL or inline superEvent data |
| `has_subEvent` | JSON | NULLABLE | SubEvent URLs or inline subEvent data |
| `accessibilitySupport` | JSON | NULLABLE | Normalised list of accessibility-support `prefLabel` strings extracted from `json_data.accessibilitySupport`. Inherited from superEvent when missing. `NULL` when no labels resolved. |
| `genderRestriction` | STRING | NULLABLE | Gender restriction URI (e.g. `https://openactive.io/FemaleOnly`, `https://openactive.io/NoRestriction`). Inherited from superEvent when missing. |
| `last_updated` | DATE | UTC date (day/month/year) when this row was last upserted |

---

## Table: `opportunity_ingestion`
Append-only log of per-feed opportunity ingestion runs with cursor tracking.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `dataset_id` | STRING | NULLABLE | Dataset URL |
| `feed_id` | STRING | NULLABLE | Feed ID |
| `kind` | STRING | NULLABLE | Feed type |
| `ingestion_date` | TIMESTAMP | NULLABLE | UTC timestamp of this ingestion run |
| `afterTimestamp` | STRING | NULLABLE | RPDE cursor: afterTimestamp |
| `afterId` | STRING | NULLABLE | RPDE cursor: afterId |
| `afterChangeNumber` | INTEGER | NULLABLE | RPDE cursor: afterChangeNumber |
| `updated` | INTEGER | NULLABLE | Number of updated items in this run |
| `deleted` | INTEGER | NULLABLE | Number of deleted items in this run |
| `status` | STRING | NULLABLE | `COMPLETE`, `ERROR`, or `WARNING` |

---

## Table: `insight_run_summary`
Append-only log of insight/analysis run outputs — high-level aggregate statistics per run.  
**Primary key:** `run_date` (REQUIRED TIMESTAMP)

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `run_date` | TIMESTAMP | REQUIRED | UTC timestamp of the analysis run |
| `num_publishers` | INTEGER | NULLABLE | Total publishers |
| `num_publishers_regular` | INTEGER | NULLABLE | Publishers in regular catalog |
| `num_publishers_preview` | INTEGER | NULLABLE | Publishers in preview catalog |
| `num_datasets` | INTEGER | NULLABLE | Total datasets |
| `num_datasets_regular` | INTEGER | NULLABLE | Datasets in regular catalog |
| `num_datasets_preview` | INTEGER | NULLABLE | Datasets in preview catalog |
| `num_feeds` | INTEGER | NULLABLE | Total feeds |
| `num_feeds_regular` | INTEGER | NULLABLE | Feeds in regular catalog |
| `num_feeds_preview` | INTEGER | NULLABLE | Feeds in preview catalog |
| `num_feeds_with_analysed_data` | INTEGER | NULLABLE | Feeds with any analysed data |
| `num_feeds_with_analysed_data_regular` | INTEGER | NULLABLE | — regular |
| `num_feeds_with_analysed_data_preview` | INTEGER | NULLABLE | — preview |
| `num_feeds_with_future_opportunity_items` | INTEGER | NULLABLE | Feeds containing future opportunities |
| `num_feeds_with_future_opportunity_items_regular` | INTEGER | NULLABLE | — regular |
| `num_feeds_with_future_opportunity_items_preview` | INTEGER | NULLABLE | — preview |
| `total_num_items` | INTEGER | NULLABLE | Total opportunity items |
| `total_num_items_regular` | INTEGER | NULLABLE | — regular |
| `total_num_items_preview` | INTEGER | NULLABLE | — preview |
| `total_num_future_opportunity_items` | INTEGER | NULLABLE | Future opportunity items |
| `total_num_future_opportunity_items_regular` | INTEGER | NULLABLE | — regular |
| `total_num_future_opportunity_items_preview` | INTEGER | NULLABLE | — preview |
| `total_num_future_week_opportunity_items` | INTEGER | NULLABLE | Future items within the next 7 days |
| `total_num_future_week_opportunity_items_regular` | INTEGER | NULLABLE | — regular |
| `total_num_future_week_opportunity_items_preview` | INTEGER | NULLABLE | — preview |
| `total_num_item_kinds` | INTEGER | NULLABLE | Distinct item kinds |
| `total_num_item_types` | INTEGER | NULLABLE | Distinct item types |
| `total_num_organizer_names` | INTEGER | NULLABLE | Distinct organizer names |
| `total_num_activities` | INTEGER | NULLABLE | Distinct activity labels |
| `total_num_facilities` | INTEGER | NULLABLE | Distinct facility labels |
| `total_num_accessibilities` | INTEGER | NULLABLE | Distinct accessibility labels |
| `total_num_regions` | INTEGER | NULLABLE | Distinct regions |
| `total_num_districts` | INTEGER | NULLABLE | Distinct districts |
| `total_num_trusts` | INTEGER | NULLABLE | Distinct NHS trusts |
| `total_num_items_with_kinds` | INTEGER | NULLABLE | Items that have a kind value |
| `total_num_items_with_types` | INTEGER | NULLABLE | Items that have a type value |
| `total_num_items_with_organizer_names` | INTEGER | NULLABLE | Items with organizer name |
| `total_num_items_with_activities` | INTEGER | NULLABLE | Items with activity labels |
| `total_num_items_with_facilities` | INTEGER | NULLABLE | Items with facility labels |
| `total_num_items_with_accessibilities` | INTEGER | NULLABLE | Items with accessibility info |
| `total_num_items_with_regions` | INTEGER | NULLABLE | Items with region resolved |
| `total_num_items_with_districts` | INTEGER | NULLABLE | Items with district resolved |
| `total_num_items_with_trusts` | INTEGER | NULLABLE | Items with NHS trust resolved |
| `total_num_items_with_sad` | INTEGER | NULLABLE | Items matched to a Sport and Discipline (SAD) entry |
| `total_num_items_without_sad` | INTEGER | NULLABLE | Items not matched to SAD |
| `total_num_activities_with_sad` | INTEGER | NULLABLE | Activity labels matched to SAD |
| `total_num_activities_without_sad` | INTEGER | NULLABLE | Activity labels not matched to SAD |
| `num_sad` | INTEGER | NULLABLE | Total SAD entries |
| `num_sad_matched` | INTEGER | NULLABLE | SAD entries with at least one match |
| `num_sad_unmatched` | INTEGER | NULLABLE | SAD entries with no match |
| `percentage_sad_matched` | FLOAT | NULLABLE | % of SAD entries matched |
| `percentage_sad_unmatched` | FLOAT | NULLABLE | % of SAD entries unmatched |
