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
4. Inherited properties are applied to: `activity`, `location`, `startDate`, `endDate`, `ageRange`, `level`

### Parent → SubEvent enrichment
The inverse: a parent row's `has_subEvent` contains a list of `@id` references. The parent's properties are pushed down to matching subEvent rows.

## Guards
- **Self-reference detection:** Skips if `superEvent @id == row's own data_id`
- **Cycle detection:** `_merge_inherited_data` tracks `(id(json_data), id(super_event_data))` pairs
- **Max depth:** `MAX_INHERITED_MERGE_DEPTH = 6` prevents runaway recursion
- **Priority:** Direct `json_data` always wins over `inherited_data`

## Targeted BigQuery fetch
To avoid loading the entire dataset from BigQuery for denormalization, the code extracts referenced `data_id` values from `has_superEvent` and `has_subEvent` columns and fetches only those rows (`get_dataset_opportunities(dataset_url, required_data_ids=...)`).

