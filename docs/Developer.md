# Developer Guide

Checkout the project and run the following command to setup the project structure:

```bash
make all
```

## Services

### Open Active Monitor

To start the frontend application, run the following command:

```bash
streamlit run main.py
```

## Jobs

### Authenticate locally

To be able to connect BigQuery from your local machine, you need to authenticate with Google Cloud.

Run this command in your terminal. It will open a browser to log you in and save a local credential file that Python will find automatically:

```
gcloud auth application-default login
```

### Ingest Feeds

This job discovers OpenActive feed metadata from the OpenActive data catalog collections and writes the resulting feed definitions into BigQuery. It visits both the preview and regular catalog collections, extracts dataset pages, scrapes each dataset page for JSON-LD `distribution` entries, and updates the feeds table plus a feed-ingestion summary table.

Before running it locally, make sure your local `.env` contains the BigQuery settings used by the code:

- `GCP_PROJECT_ID`
- `BQ_DATASET_ID`
- `BQ_FEEDS_TABLE`
- `BQ_FEED_INGESTION_TABLE`

This job also relies on the Google Cloud local authentication step documented above.

#### CLI interface

Run it from `jobs/ingest_feeds`:

```bash
./virt/bin/python main.py
```

#### High-level execution flow

1. Create a retry-capable HTTP session for outbound requests.
2. Visit the two OpenActive catalog collection URLs in this order:
   - `preview`
   - `regular`
3. For each collection:
   - fetch the collection JSON-LD
   - read its `hasPart` entries to get catalogue URLs
   - fetch each catalogue and collect its `dataset` URLs
   - keep a mapping from each dataset URL back to its parent catalogue URL
4. Visit each dataset URL and parse the HTML page:
   - extract OpenActive spec version links (`rpde_version` and `model_version`) from page links when present
   - find JSON-LD `<script>` blocks
   - read each dataset's `distribution` entries and turn them into feed rows
5. For each discovered feed, derive the final BigQuery row fields including:
   - stable feed `id` generated from the feed URL
   - `type`, `url`, `dataset_name`, `dataset_url`
   - provider metadata such as `provider`, `publisher_name`, `logo_url`, `license_url`
   - detected `rpde_version` and `model_version`
   - `last_access` set to the current date
6. Combine all feeds from preview and regular collections into one DataFrame, then de-duplicate by `id`, keeping the last occurrence. This means the later-collected source wins when the same feed appears more than once.
7. Update the BigQuery feeds table:
   - read the existing feeds table if it already exists
   - concatenate existing rows with the newly collected rows
   - de-duplicate again by `id`, keeping the new row for matching ids
   - write the full merged result back with `if_exists="replace"`
8. Append one ingestion summary record to the feed-ingestion table containing:
   - ingestion timestamp
   - counts of catalogues, datasets and feeds
   - JSON-encoded lists of visited catalogue URLs, dataset URLs and feed ids

This structure keeps the feeds table refreshed from the OpenActive catalog while preserving stable feed ids and recording a summary of each collection run.

### Ingest Opportunities

This job ingests RPDE opportunity feeds into BigQuery. It reads the feed definitions already stored in the feeds table for a given day (default today), groups them by `dataset_url`, processes one dataset at a time, and writes both opportunity rows and per-feed ingestion cursors/status back to BigQuery.

Before running it locally, make sure your local `.env` contains the BigQuery settings used by the code:

- `GCP_PROJECT_ID`
- `BQ_DATASET_ID`
- `BQ_FEEDS_TABLE`
- `BQ_OPPORTUNITY_INGESTION_TABLE`
- `BQ_OPPORTUNITIES_TABLE`

#### CLI interface

Run it from `jobs/ingest-opportunities`:

```bash
./virt/bin/python main.py
./virt/bin/python main.py --target-date 2026-04-10 --verbose
./virt/bin/python main.py \
  --dataset "https://example-dataset.example/openactive" \
  --dataset "https://another-dataset.example/openactive" \
  --verbose
```

Available options:

- `--dataset TEXT`: optional dataset filter matched against `dataset_url`. Repeat the flag to process multiple datasets.
- `--verbose`: enables debug logging for the main job plus the RPDE, BigQuery, geolocation and request layers.
- `--help`: prints the Click help output.

#### High-level execution flow

1. System queries BigQuery the latest feed_ingestion date, retrieved feeds for that date and group the returned feeds by `dataset_url`.
2. Process datasets one at a time. At the start of each dataset, retry any deferred deletes from earlier work to reduce conflicts with the BigQuery streaming buffer.
3. Sort each dataset's feeds by `FEED_EXECUTION_ORDER`, then split them into two batches for memory efficiency:
   - first batch: `FacilityUse`, `IndividualFacilityUse`, `Slot`
   - second batch: all remaining feed types
4. For each batch, fetch the last successful RPDE cursor (`afterTimestamp` / `afterId`) for each feed from the opportunity-ingestion table, then traverse the RPDE pages incrementally from that cursor.
5. Flatten RPDE items into two collections:
   - updated items become opportunity rows with extracted fields such as `data_id`, `kind`, `activity`, `location`, `startDate`, `endDate`, `ageRange`, `level`, `has_superEvent`, and `has_subEvent`
   - items with `state=deleted` become delete instructions keyed by dataset, feed and item id
6. Persist each batch immediately after collection rather than holding the whole dataset in memory:
   - delete rows marked as deleted from the opportunities table
   - if BigQuery refuses a delete because the row is still in the streaming buffer, keep it in a deferred-delete queue and retry later with exponential backoff
   - build a DataFrame from the updated items
   - fetch only the existing BigQuery rows needed for denormalization (for referenced `superEvent` / `subEvent` data ids)
   - denormalize the new rows by inheriting missing fields from parent/sibling records and by normalizing derived fields such as dates, activity and location
7. Upsert the denormalized rows through a staging table instead of writing directly into the main opportunities table:
   - deduplicate on the merge key (`dataset_url`, `feed_id`, `id`, `modified`)
   - load the batch into a short-lived staging table
   - run a BigQuery `MERGE` so existing rows are updated and new rows are inserted
   - drop the staging table afterwards
8. After each dataset finishes, write ingestion summary records for every feed:
   - successful batches store the next cursor, update/delete counts and final RPDE status
   - failed feeds keep their previous cursor and are written with status `ERROR`, so the next run retries from the last known good position
9. After all datasets are processed, keep draining any remaining deferred deletes until they succeed or the job reaches its timeout.

This structure keeps the job incremental, reduces peak memory usage by persisting per batch, and avoids replacing the whole opportunities table on every run.
