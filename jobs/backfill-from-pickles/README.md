# backfill-from-pickles

One-off backfill: load the legacy `volume-1/data-feeds/` and
`volume-1/data-opportunities/` pickles into BigQuery so the new pipeline
starts from the same accumulated state the legacy job has been building since
late 2025.

This is **not** a Cloud Run Job. Run it locally, once, then resume normal
operation of `jobs/ingest-opportunities`.

## Why

Both pipelines use cursor-based RPDE deltas — neither does a full re-fetch.
The legacy pickle has ~17 M items because it has been accumulating since
~2025-12; provider feeds (especially `bookteq.com`) only re-emit a recent
~1-week window when called with no cursor, so the new pipeline can never
recover the older items via RPDE alone. This script gives the new pipeline
that historical state in one shot.

## Prereqs

1. Truncate the four target tables:
   ```sql
   TRUNCATE TABLE `openactive-monitor.openactive_analytics.feeds`;
   TRUNCATE TABLE `openactive-monitor.openactive_analytics.feed_ingestion`;
   TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunities`;
   TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunity_ingestion`;
   ```
2. Authenticate: `gcloud auth application-default login`.
3. Make sure `volume-1/data-feeds/` and `volume-1/data-opportunities/` exist
   and contain the latest pickles.

## Run

```bash
cd jobs/backfill-from-pickles
python -m venv virt
source virt/bin/activate
pip install -r requirements.txt

cp .env.example .env

python main.py --verbose
```

Flags:

- `--feeds-only` / `--opportunities-only` — run only one phase. Note:
  `--opportunities-only` still **reads** the feeds pickles (it doesn't write
  them) so it can build a `feed_id → dataset_url` map without re-decoding
  every opportunities gzip just to discover its dataset.
- `--datasets <url>` (repeatable) — filter to specific dataset URLs (debugging).
- `--max-workers N` — override `INGEST_MAX_WORKERS` (default 8). This now
  controls a **process** pool (not threads), so set it close to your CPU core
  count for the opportunities phase.
- `--dry-run` — read + group pickles but skip every BigQuery write.

## What it writes

| Table                  | Source                                                     | Mode                                                                                  |
| ---------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `feeds`                | `volume-1/data-feeds/{regular,preview}-feeds--…*.pickle`   | append                                                                                |
| `feed_ingestion`       | one synthetic row covering this backfill run               | append (1 row)                                                                        |
| `opportunities`        | every `volume-1/data-opportunities/*.pickle.gzip`          | direct `WRITE_APPEND` load job per dataset (no MERGE — backfill assumes TRUNCATEd table) |
| `opportunity_ingestion`| one row per source pickle, cursor extracted from `next_url`| append                                                                                |

Items go through the same `processing.extract_rows` +
`processing.denormalize_dataset` pipeline as the live `ingest-opportunities`
job, so superEvent / subEvent inheritance is applied correctly.

## After it finishes

Just run `jobs/ingest-opportunities` as normal. Each feed resumes from the
cursor we wrote into `opportunity_ingestion`, fetching only the RPDE delta
since the legacy snapshot.

## Dependency on `ingest-opportunities`

`main.py` adds `../ingest-opportunities/` to `sys.path` so it can import
`processing`, `bigquery_ops`, `rpde`, `geolocation`. There is no PYTHONPATH
configuration to set up — just keep the two folders side by side under
`jobs/`.
