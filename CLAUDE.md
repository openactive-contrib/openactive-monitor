# CLAUDE.md — Project Instructions for Claude Code

## Project Overview

**openactive-monitor** is a data pipeline and monitoring platform for [OpenActive](https://www.openactive.io/) — a UK initiative that publishes open data about physical activity opportunities. The project collects, ingests, analyses, and visualises feeds and opportunities published by leisure providers across the UK using the [RPDE (Realtime Paged Data Exchange)](https://openactive.io/realtime-paged-data-exchange/) specification.

The project runs on **Google Cloud Platform** and consists of several **Cloud Run Jobs** and a **Cloud Run Service**.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                        │
│                                                                  │
│  LEGACY PIPELINE (pickle-file based):                           │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │  get-feeds   │→ │ get-opportunities │→ │analyse-opportunities│ │
│  │ (Cloud Job)  │  │   (Cloud Job)     │  │   (Cloud Job)     │  │
│  └──────────────┘  └──────────────────┘  └───────────────────┘  │
│         ↓                   ↓                      ↓             │
│     pickle files       pickle files          pickle files        │
│                                                                  │
│  NEW PIPELINE (BigQuery based, under development):              │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │ ingest_feeds │→ │ingest-opportunities│→ │opportunity-insigths│ │
│  │ (Cloud Job)  │  │   (Cloud Job)     │  │   (Cloud Job)     │  │
│  └──────────────┘  └──────────────────┘  └───────────────────┘  │
│         ↓                   ↓                     ↓             │
│       BigQuery           BigQuery              BigQuery          │
│                                                                  │
│  ┌────────────────────────┐                                     │
│  │  openactive-monitor    │  (Streamlit dashboard)              │
│  │   (Cloud Run Service)  │                                     │
│  └────────────────────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

| Path | Type | Status | Description |
|------|------|--------|-------------|
| `jobs/get-feeds/` | Cloud Run Job | **Production** (legacy) | Collects OpenActive feed metadata from catalog collections, stores as pickle files. Uses Pub/Sub to trigger `get-opportunities`. |
| `jobs/get-opportunities/` | Cloud Run Job | **Production** (legacy) | Fetches opportunity data from RPDE feeds, stores as pickle files. |
| `jobs/analyse-opportunities/` | Cloud Run Job | **Production** (legacy) | Analyses collected opportunities, produces aggregate statistics. |
| `jobs/ingest_feeds/` | Cloud Run Job | **In development** | Replacement for `get-feeds`. Collects feed metadata from OpenActive catalogs and merges into BigQuery `feeds` table. Writes ingestion summary to `feed_ingestion` table. |
| `jobs/ingest-opportunities/` | Cloud Run Job | **In development** | Replacement for `get-opportunities`. Ingests RPDE opportunity data into BigQuery with incremental cursor tracking, superEvent/subEvent denormalization, and UK postcode geolocation. |
| `services/openactive-monitor/` | Cloud Run Service | **Production** | Streamlit dashboard that visualises feed and opportunity data. Currently reads from legacy pickle files. |
| `volume-1/` | Shared code | **Production** | Common utilities and settings shared by legacy jobs/services. |
| `workflows/run-job.yaml` | Cloud Workflow | **Production** | GCP Workflow that triggers Cloud Run jobs via Pub/Sub. |

## Technology Stack

- **Language:** Python 3.13+
- **Cloud:** Google Cloud Platform (Cloud Run Jobs, Cloud Run Services, BigQuery, Pub/Sub, Workflows)
- **Data store (new):** Google BigQuery
- **Data store (legacy):** Pickle files on shared volume
- **Dashboard:** Streamlit
- **Key libraries:**
  - `google-cloud-bigquery`, `pandas-gbq` — BigQuery operations
  - `pandas`, `pyarrow` — Data manipulation
  - `requests`, `beautifulsoup4` — HTTP and HTML scraping
  - `click` — CLI for ingest-opportunities
  - `uklookup` — UK postcode geocoding
  - `python-dotenv` — Environment variable management

## BigQuery Schema

### GCP Project: `openactive-monitor`
### Dataset: `openactive_analytics`

### Table: `feeds`
Stores metadata about all discovered OpenActive RPDE feeds.

| Column | Type | Description |
|--------|------|-------------|
| `id` | STRING | Stable ID derived from feed URL (e.g. `example-com-api-feeds-sessions`) |
| `url` | STRING | Full URL of the RPDE feed endpoint |
| `type` | STRING | Feed type: `SessionSeries`, `ScheduledSession`, `FacilityUse`, `IndividualFacilityUse`, `Slot`, `Event`, `HeadlineEvent`, `OnDemandEvent`, `CourseInstance`, or empty |
| `dataset_name` | STRING | Human-readable dataset name from JSON-LD |
| `dataset_url` | STRING | URL of the dataset site page |
| `provider` | STRING | Domain of the catalogue URL (e.g. `opendata.leisurecloud.live`) |
| `license_url` | STRING | License URL from JSON-LD |
| `logo_url` | STRING | Publisher logo URL |
| `publisher_name` | STRING | Publisher name from JSON-LD |
| `rpde_version` | STRING | RPDE spec version URL |
| `model_version` | STRING | Modelling Opportunity Data spec version URL |
| `is_regular` | BOOL | `TRUE` if the feed was found in the regular catalog, `FALSE` if preview-only. |
| `last_access` | DATE | Date when this feed was last seen/collected |

### Table: `feed_ingestion`
Append-only log of feed collection runs.

| Column | Type | Description |
|--------|------|-------------|
| `ingestion_date` | TIMESTAMP | UTC timestamp of the ingestion run |
| `number_of_catalogues` | INTEGER | Number of catalogue URLs visited |
| `catalogues` | JSON | JSON array of catalogue URLs |
| `number_of_datasets` | INTEGER | Number of dataset URLs visited |
| `datasets` | JSON | JSON array of dataset URLs |
| `number_of_feeds` | INTEGER | Total feeds collected |
| `feed_ids` | JSON | JSON array of all feed IDs |

### Table: `opportunities`
Stores denormalized opportunity data from RPDE feeds.

**Scale note:** This is the only large table in the project (about 8 million rows, about 10 GB). Other tables are typically small.

| Column | Type | Description |
|--------|------|-------------|
| `dataset_url` | STRING | Dataset URL (part of composite key) |
| `feed_id` | STRING | Feed ID (part of composite key) |
| `id` | STRING | RPDE item ID (part of composite key) |
| `data_id` | STRING | `@id` from the opportunity data |
| `kind` | STRING | `@type` from the opportunity data (e.g. `SessionSeries`, `Slot`) |
| `modified` | STRING | RPDE `modified` timestamp |
| `json_data` | JSON | Full opportunity data payload |
| `inherited_data` | JSON | Properties inherited from superEvent/parent |
| `activity` | JSON | Extracted activity labels |
| `location` | JSON | Extracted geolocation (`latitude`, `longitude`, `postal_code`, etc.) |
| `district_name` | STRING | UK Local Authority District name resolved from `location.latitude/longitude` (`LAD24NM`) |
| `region_name` | STRING | UK Region name resolved from `location.latitude/longitude` (`eer18nm`) |
| `publisher_name` | STRING | Publisher name copied from `feeds.publisher_name` using `opportunities.dataset_url = feeds.dataset_url` |
| `district_code` | STRING | UK Local Authority District code resolved from `district_name` (`LAD24CD`) via `000-district-region-country.json` |
| `region_code` | STRING | UK Region code resolved from `district_name` via `000-district-region-country.json` |
| `country_code` | STRING | UK country code resolved from `district_name` via `000-district-region-country.json` |
| `country_name` | STRING | UK country name resolved from `district_name` via `000-district-region-country.json` |
| `startDate` | TIMESTAMP | Start date |
| `endDate` | TIMESTAMP | End date |
| `ageRange` | JSON | Age range information |
| `level` | STRING | Difficulty/skill level |
| `has_superEvent` | STRING | Reference to parent event `@id` or inline dict |
| `has_subEvent` | STRING | Reference to child event(s) |
| `accessibilitySupport` | JSON | Normalised list of accessibility-support `prefLabel` strings extracted from `json_data.accessibilitySupport` (e.g. `["Hearing impairment", "Visual impairment"]`). Inherited from superEvent when missing. `NULL` when no labels resolved. |
| `genderRestriction` | STRING | Gender restriction URI (e.g. `https://openactive.io/FemaleOnly`, `https://openactive.io/NoRestriction`). Inherited from superEvent when missing. |
| `last_updated` | DATE | UTC date (day/month/year) when this row was last upserted by the `ingest-opportunities` job |

**Composite primary key (MERGE key):** `(dataset_url, feed_id, id)`

### Table: `opportunity_ingestion`
Append-only log of per-feed opportunity ingestion runs with cursor tracking.

| Column | Type | Description |
|--------|------|-------------|
| `dataset_id` | STRING | Dataset URL |
| `feed_id` | STRING | Feed ID |
| `kind` | STRING | Feed type |
| `ingestion_date` | TIMESTAMP | UTC timestamp of this ingestion |
| `updated` | INTEGER | Number of updated items |
| `deleted` | INTEGER | Number of deleted items |
| `afterTimestamp` | STRING | RPDE cursor: afterTimestamp |
| `afterId` | STRING | RPDE cursor: afterId |
| `afterChangeNumber` | INTEGER | RPDE cursor: afterChangeNumber |
| `status` | STRING | `COMPLETE`, `ERROR`, or `WARNING` |

## Environment Variables

All BigQuery jobs require these environment variables (loaded via `.env` or Cloud Run config):

| Variable | Description |
|----------|-------------|
| `GCP_PROJECT_ID` | Google Cloud project ID — `openactive-monitor` |
| `BQ_DATASET_ID` | BigQuery dataset ID — `openactive_analytics` |
| `BQ_FEEDS_TABLE` | BigQuery feeds table name — `feeds` |
| `BQ_FEED_INGESTION_TABLE` | BigQuery feed_ingestion table name — `feed_ingestion` |
| `BQ_OPPORTUNITY_INGESTION_TABLE` | BigQuery opportunity_ingestion table name — `opportunity_ingestion` |
| `BQ_OPPORTUNITIES_TABLE` | BigQuery opportunities table name — `opportunities` |
| `INGEST_MAX_WORKERS` | Thread pool size for parallel dataset processing (default: `4`) |
| `OPPORTUNITY_CSV_OUTPUT_DIR` | Debug CSV output directory (default: `./opportunities/csv`) |

## Development Setup

```bash
# Install all virtual environments
make setup

# Or for a specific job:
cd jobs/ingest-opportunities
python3 -m venv virt
source virt/bin/activate
pip install -r requirements.txt
```

Each job has its own `virt/` virtual environment and `requirements.txt`. Do NOT commit `virt/` directories.

## Key Domain Concepts

- **RPDE (Realtime Paged Data Exchange):** Pagination protocol for OpenActive feeds. Pages are traversed using cursor params (`afterTimestamp`+`afterId` or `afterChangeNumber`). A terminal page has `next == current URL` and empty items.
- **SuperEvent / SubEvent inheritance:** Opportunities can reference parent events. Properties are inherited from superEvent to subEvent where the child lacks them (e.g., location, activity, dates).
- **Feed types execution order:** `HeadlineEvent → Event → OnDemandEvent → FacilityUse → IndividualFacilityUse → Slot → SessionSeries → ScheduledSession → CourseInstance`
- **Streaming buffer:** BigQuery has a ~30min streaming buffer that prevents immediate DELETE of recently inserted rows. The code handles this with exponential backoff retry.

## Coding Conventions

- Python 3.13+ type hints (use `list[str]` not `List[str]`, use `X | None` not `Optional[X]`)
- Use `logging` module, not `print()` for operational output
- Use `python-dotenv` and `os.getenv()` for configuration
- Use parameterized BigQuery queries (never f-string interpolate user values into SQL)
- Use `click` for CLI interfaces in new jobs
- Pandas DataFrames for data manipulation
- Each job is self-contained with its own `requirements.txt` and `virt/`

## Performance and Memory Guidance

- Runtime target environment is typically 16 GB Cloud Run/VM memory; design processing to stay comfortably below this.
- Treat `opportunities` as the primary scale bottleneck; optimize queries and ingestion logic for this table first.
- Prefer incremental and chunked processing (paged RPDE fetches, batched BigQuery writes/reads) over loading full datasets into memory.
- Avoid holding the same dataset in multiple in-memory representations at once (for example dict + DataFrame + inverted dict) unless strictly necessary.
- Select only required columns from BigQuery and push filters/aggregations to SQL to minimize transfer and Python-side memory use.
- Clean up large temporary objects promptly and stream outputs where possible.

## Testing

- No formal unit tests currently, but code is structured for testability (e.g. separation of concerns, pure functions where possible).

## Skills

Claude should reference the `.claude/skills/` directory for task-specific guidance.
