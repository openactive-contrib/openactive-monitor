---
name: bigquery-operations
description: Use this skill for any tasks involving BigQuery schema design, SQL optimization, data ingestion patterns, or working on the ingest_feeds and ingest-opportunities jobs.
---

# Skill: BigQuery Operations

## When to use
Use this skill when working on `jobs/ingest_feeds/` or `jobs/ingest-opportunities/` — any task involving BigQuery reads, writes, schema changes, or query optimization.

## Key files
- `jobs/ingest-opportunities/bigquery_ops.py` — All BigQuery CRUD operations for opportunities
- `jobs/ingest_feeds/main.py` — BigQuery merge and ingestion record writing for feeds

## Patterns

### Parameterized queries (ALWAYS)
```python
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("param_name", "STRING", value),
        bigquery.ArrayQueryParameter("ids", "STRING", id_list),
    ]
)
client.query(query, job_config=job_config)
```
Never interpolate user-controlled values into SQL via f-strings.

### Upsert via staging table + MERGE
The opportunities table uses a staging-table pattern:
1. Load rows into a temporary staging table via `load_table_from_json`
2. Run a `MERGE` statement to upsert into the main table
3. Drop the staging table in a `finally` block

This avoids streaming buffer issues that affect `insert_rows_json` + immediate `DELETE`.

### Streaming buffer handling
BigQuery rows inserted via streaming are not immediately deletable (~30 min buffer). The code uses:
- `pending_deletes` dict tracking deferred keys
- Exponential backoff retry (`_retry_delay_seconds`)
- `drain_deferred_deletes_until_timeout` for end-of-run cleanup

### JSON columns
- `insert_rows_json` expects JSON columns as **strings** (`json.dumps(...)`)
- `load_table_from_json` expects JSON columns as **Python objects** (dict/list)
- Use `_coerce_json_value` / `_unwrap_json_fields_for_load` to convert between them

### Schema detection
Always fetch the live schema with `client.get_table(table_id).schema` rather than hardcoding — this ensures the code adapts to schema changes.

## Environment variables required
```
GCP_PROJECT_ID, BQ_DATASET_ID, BQ_FEEDS_TABLE, BQ_FEED_INGESTION_TABLE,
BQ_OPPORTUNITY_INGESTION_TABLE, BQ_OPPORTUNITIES_TABLE
```

