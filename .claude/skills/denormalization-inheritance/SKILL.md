---
name: denormalization-inheritance
description: Use this skill when working on superEvent/subEvent inheritance, property propagation between related opportunities, or the denormalize_dataset logic.
---

# Skill: Denormalization & Inheritance

## When to use
Use this skill when working on superEvent/subEvent inheritance, the `denormalize_dataset` function, or any logic that propagates properties between related opportunities.

## Key files
- `jobs/ingest-opportunities/main.py` — `denormalize_dataset()`, `handle_super_events()`, `handle_sub_events()`, `_merge_inherited_data()`

## How inheritance works

### SuperEvent → child row
1. A row's `has_superEvent` field contains either:
   - An inline dict (the superEvent data itself)
   - A string `@id` reference to another row's `data_id`
2. The code builds a lookup `data_id → merged payload` from both the new DataFrame and existing BigQuery rows
3. For each row with a superEvent, properties from the parent are inherited where the child lacks them
4. Inherited properties are applied to: `activity`, `facility`, `activity_json`, `facility_json` (raw payloads, same fill-only-when-empty rule), `location` (and its derived boundary columns `district_name`/`region_name`/`district_code`/`region_code`/`country_code`/`country_name`), `startDate`, `endDate`, `ageRange`, `level`, `accessibilitySupport`, `genderRestriction`, `organization_name`

**Not inherited:** `organization_json` is intentionally excluded — it stays a faithful reflection of the row's own `json_data.organizer` / `json_data.provider`. Only the resolved `organization_name` propagates from a parent.

### Multi-level (grandparent+) resolution
`inherited_data` is **never persisted** to BigQuery (always `{}` in the table) and is still `{}` for rows in the current batch when parent payloads are built. So a parent payload alone only carries the parent's own `json_data`. `_resolve_ancestry()` walks the chain explicitly:
- follows the parent link (`superEvent`, falling back to `facilityUse`) whether it is an inline dict or a string `@id` looked up in the payload table,
- returns a flattened copy where the **closest level wins** (parent > grandparent > …); an empty value at a closer level never masks a non-empty ancestor value,
- is bounded by `MAX_INHERITED_MERGE_DEPTH`, detects cycles, never mutates the input, and memoises per `data_id` via a per-call cache.

Both `handle_super_events` and `handle_sub_events` resolve through it. Production chain shapes: ScheduledSession → inline SessionSeries → inline EventSeries, and ScheduledSession → `@id` → SessionSeries row → inline EventSeries.

`main._persist_dataset_results` fetches ancestors hop by hop (`bigquery_ops.get_dataset_ancestor_opportunities`, using `processing.collect_super_event_refs`, which includes string refs nested inside inline parents) so `@id`-linked grandparents not in the batch are loaded.

### Parent → SubEvent enrichment
The inverse: a parent row's `has_subEvent` contains a list of `@id` references. The parent's properties are pushed down to matching subEvent rows.

## Guards
- **Self-reference detection:** Skips if `superEvent @id == row's own data_id`
- **Cycle detection:** `_merge_inherited_data` tracks `(id(json_data), id(super_event_data))` pairs
- **Max depth:** `MAX_INHERITED_MERGE_DEPTH = 6` prevents runaway recursion
- **Priority:** Direct `json_data` always wins over `inherited_data`

## Backfill
`self_healing/backfill_super_event_inheritance.py` re-applies multi-level inheritance to stored rows where an inheritable column is empty and the parent (or the parent's inline `superEvent`) carries the matching raw property. It streams rows per dataset in chunks (child `json_data` reduced to `JSON_KEYS`, since `_merge_inherited_data` only checks top-level key presence), and writes via the slim fill-only MERGE in `self_healing/_common.py` (`write_inherited_updates`, shared with `backfill_nested_ifu_inheritance.py`). `INHERITABLE_FIELDS` in `_common.py` must stay in sync with what `apply_inherited_data` fills.

## Targeted BigQuery fetch
To avoid loading the entire dataset from BigQuery for denormalization, the code extracts referenced `data_id` values from `has_superEvent` and `has_subEvent` columns and fetches only those rows (`get_dataset_opportunities(dataset_url, required_data_ids=...)`).

