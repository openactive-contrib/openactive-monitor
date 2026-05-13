---
name: rpde-feed-traversal
description: Use this skill when working on RPDE feed fetching, pagination, cursor handling, terminal page detection, or any changes to rpde.py and feed ingestion logic.
---

# Skill: RPDE Feed Traversal

## When to use
Use this skill when working on RPDE feed fetching, pagination, cursor handling, or any changes to `rpde.py` or feed ingestion logic.

## Key files
- `jobs/ingest-opportunities/rpde.py` — RPDE page traversal and cursor extraction
- `jobs/ingest-opportunities/main.py` — Feed orchestration, cursor state management

## RPDE Protocol Rules

### Cursor types (mutually exclusive)
1. **afterTimestamp + afterId** — most common, used together
2. **afterChangeNumber** — integer-based cursor, used alone

### Terminal page detection
A page is terminal when `next == current URL` AND `items` is empty. This means the feed is fully caught up.

### Self-loop protection
If `next == current URL` but items is **not** empty, this is a malformed feed. Log a warning and break.

### Incremental fetching
Cursors are persisted in the `opportunity_ingestion` table. On the next run, traversal resumes from the last cursor, not from the beginning.

### Feed execution order
Feeds within a dataset must be processed in this order to ensure superEvent data is available before subEvents need it:
```
HeadlineEvent → Event → OnDemandEvent → FacilityUse → IndividualFacilityUse → Slot → SessionSeries → ScheduledSession → CourseInstance
```

### Batching strategy
Feeds are split into two batches to reduce peak memory:
1. `FacilityUse`, `IndividualFacilityUse`, `Slot`
2. Everything else

## Common pitfalls
- Some feeds return relative `next` URLs — always resolve with `urljoin(current_url, next_url)`
- Some feeds have non-standard type names (e.g. "ScheduledSessions") — `get_feed_type()` normalizes these
- RPDE items with `state: "deleted"` have no `data` payload — only `id` and `modified`

