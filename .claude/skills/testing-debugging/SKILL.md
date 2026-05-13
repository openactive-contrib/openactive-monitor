---
name: testing-debugging
description: Use this skill when writing tests, debugging data issues, profiling BigQuery performance, or using CLI debug flags.
---

# Skill: Testing & Debugging

## When to use
Use this skill when writing tests, debugging data issues, or profiling performance.

## Debugging tools

### CSV output (ingest-opportunities)
Set `PERSIST_CSV=True` in `main.py` to write collected DataFrames to CSV files in `OPPORTUNITY_CSV_OUTPUT_DIR`. Useful for inspecting denormalization results without BigQuery.

### JSON dump (rpde.py)
Pass `persist_data=True` to `access_feed_url()` to save raw RPDE responses to `./opportunities/<feed_id>_<timestamp>.json`.

### Benchmark script
```bash
cd jobs/ingest-opportunities
source virt/bin/activate
python benchmark_feeds_query_speed.py --runs 10 --warmup-runs 1
```
Compares BigQuery query latency with reused vs new clients.

### CLI filtering
```bash
python main.py --dataset "https://example.com/OpenActive" --verbose
```
Use `--dataset` to process a single dataset. Use `--verbose` for DEBUG-level logs from all modules.

## Writing tests
- TODO: Test framework not yet configured
- When adding tests, use `pytest` with fixtures
- Mock BigQuery client calls using `unittest.mock`
- Mock HTTP requests using `responses` or `requests-mock`
- Place tests in a `tests/` directory within each job

## Common debugging scenarios
- **"Streaming buffer" errors:** Wait ~30 min or check `pending_deletes` logic in `bigquery_ops.py`
- **Missing inherited data:** Check feed execution order — parent feeds must be processed before children
- **Duplicate MERGE errors:** Check `_dedup_on_merge_keys` — usually caused by self-looping RPDE feeds

