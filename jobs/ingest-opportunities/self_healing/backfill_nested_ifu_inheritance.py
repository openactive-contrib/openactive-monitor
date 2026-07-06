"""
Self-healing backfill: repair Slots that should inherit from a *nested*
IndividualFacilityUse.

Background
----------
A ``Slot``'s ``facilityUse`` reference is stored in ``has_superEvent``.  For some
publishers (observed on ``better-admin.org.uk``) that reference points at an
``IndividualFacilityUse`` ``@id`` such as::

    .../facility-uses/activity_recurrence_group:2968/individual-facility-uses/3372...

There is no opportunities row whose ``data_id`` equals that IFU ``@id`` — the IFU
exists only *nested* inside its parent FacilityUse's
``json_data.individualFacilityUse`` list.  The production denormalization used to
resolve parents only by ``data_id``, so these Slots inherited nothing and were
left with an empty ``location`` (and empty activity / facility / organisation /
boundary columns).  ~500k Slots are affected.

The production fix (``processing._build_super_event_payload_by_data_id`` expanding
nested IFUs, plus ``bigquery_ops.get_dataset_facility_uses``) heals new/updated
rows going forward.  This backfill repairs the rows already in BigQuery.

Target rows
-----------
- ``kind = 'Slot'``
- ``location`` is the empty JSON object (inheritance never ran)
- ``has_superEvent`` is a string that looks like a nested IFU reference

The script fills only-when-empty and writes back via a *targeted* MERGE that
touches only the inheritable columns (never ``json_data`` or the whole record),
so it is idempotent and safe to re-run as part of self-healing.

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python self_healing/backfill_nested_ifu_inheritance.py [--dry-run] \
        [--max-workers 8] [--dataset <url>] [--limit 0]
"""

from __future__ import annotations

import gc
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

import click
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Make the ingest-opportunities package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigquery_ops import (  # noqa: E402
    OPPORTUNITIES_COLUMNS,
    get_dataset_facility_uses,
    get_dataset_opportunities,
    parse_opportunities_json_columns,
)
from processing import (  # noqa: E402
    _build_super_event_payload_by_data_id,
    handle_super_events,
)
from self_healing._common import discover_affected_datasets, run_dml_with_retry  # noqa: E402
from self_healing.backfill_super_event_inheritance import (  # noqa: E402
    INHERITABLE_FIELDS,
    _empty_mask,
    _is_empty_value,
    _strip_ref,
    _values_equal,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backfill_nested_ifu_inheritance")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

_AFFECTED_PREDICATE = (
    "kind = 'Slot' "
    "AND TO_JSON_STRING(location) = '{}' "
    "AND has_superEvent IS NOT NULL "
)

# Inheritable columns partitioned by their BigQuery type, used to build the
# targeted staging table + fill-only-when-empty MERGE.  Union must equal
# ``INHERITABLE_FIELDS`` (the fields ``apply_inherited_data`` may fill).
_JSON_COLUMNS: tuple[str, ...] = (
    "activity",
    "facility",
    "location",
    "ageRange",
    "level",
    "accessibilitySupport",
)
_TIMESTAMP_COLUMNS: tuple[str, ...] = ("startDate", "endDate")
_STRING_COLUMNS: tuple[str, ...] = (
    "genderRestriction",
    "organization_name",
    "district_name",
    "region_name",
    "district_code",
    "region_code",
    "country_code",
    "country_name",
    "nhstrust_name",
    "nhstrust_code",
)

assert set(_JSON_COLUMNS) | set(_TIMESTAMP_COLUMNS) | set(_STRING_COLUMNS) == set(
    INHERITABLE_FIELDS
), "inheritable-column partition must cover exactly INHERITABLE_FIELDS"


def _coerce_json(value: Any) -> Any:
    """Return a JSON-loadable Python object (dict/list) or None for empty cells."""
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _coerce_timestamp(value: Any) -> str | None:
    """Return a BigQuery TIMESTAMP-friendly string, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat(sep=" ")
    return None


def _coerce_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return str(value)


def _staging_schema() -> list[bigquery.SchemaField]:
    fields = [
        bigquery.SchemaField("dataset_url", "STRING"),
        bigquery.SchemaField("feed_id", "STRING"),
        bigquery.SchemaField("id", "STRING"),
    ]
    fields += [bigquery.SchemaField(c, "JSON") for c in _JSON_COLUMNS]
    fields += [bigquery.SchemaField(c, "TIMESTAMP") for c in _TIMESTAMP_COLUMNS]
    fields += [bigquery.SchemaField(c, "STRING") for c in _STRING_COLUMNS]
    return fields


def _empty_check_sql(col: str) -> str:
    """SQL predicate that is TRUE when the target column is 'missing'."""
    if col in _JSON_COLUMNS:
        return f"(T.{col} IS NULL OR TO_JSON_STRING(T.{col}) IN ('{{}}', '[]', 'null'))"
    if col in _TIMESTAMP_COLUMNS:
        return f"T.{col} IS NULL"
    return f"(T.{col} IS NULL OR T.{col} = '')"


def _build_targeted_merge(staging_table_id: str) -> str:
    """MERGE that fills only-when-empty and touches only the inheritable columns."""
    update_set = ",\n                ".join(
        f"T.{col} = IF({_empty_check_sql(col)}, S.{col}, T.{col})"
        for col in INHERITABLE_FIELDS
    )
    return f"""
        MERGE `{TABLE_ID}` AS T
        USING `{staging_table_id}` AS S
        ON  T.dataset_url = S.dataset_url
        AND T.feed_id = S.feed_id
        AND T.id = S.id
        WHEN MATCHED THEN
            UPDATE SET
                {update_set}
    """


def _build_staging_rows(updates_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Coerce the changed-rows DataFrame into JSON-load-ready staging dicts."""
    rows: list[dict[str, Any]] = []
    for record in updates_df.to_dict(orient="records"):
        row: dict[str, Any] = {
            "dataset_url": record.get("dataset_url"),
            "feed_id": record.get("feed_id"),
            "id": record.get("id"),
        }
        for col in _JSON_COLUMNS:
            row[col] = _coerce_json(record.get(col))
        for col in _TIMESTAMP_COLUMNS:
            row[col] = _coerce_timestamp(record.get(col))
        for col in _STRING_COLUMNS:
            row[col] = _coerce_str(record.get(col))
        rows.append(row)
    return rows


def _write_inherited_updates(
    client: bigquery.Client,
    dataset_url: str,
    updates_df: pd.DataFrame,
) -> int:
    """Upsert ONLY the inheritable columns for the given rows via a slim MERGE.

    Loads a staging table (merge keys + inheritable columns) and MERGEs with
    per-column fill-only-when-empty guards, so already-populated columns and the
    heavy ``json_data`` payload are never rewritten.  Returns rows affected.
    """
    if updates_df.empty:
        return 0

    staging_table_id = (
        f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"
        f"_nested_ifu_staging_{uuid4().hex[:12]}"
    )
    staging_rows = _build_staging_rows(updates_df)

    try:
        load_job = client.load_table_from_json(
            staging_rows,
            staging_table_id,
            job_config=bigquery.LoadJobConfig(
                schema=_staging_schema(),
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            ),
        )
        load_job.result()

        affected = run_dml_with_retry(
            client,
            _build_targeted_merge(staging_table_id),
            label=f"nested-ifu MERGE {dataset_url}",
        )
        logger.info("Updated %d rows for %s", affected, dataset_url)
        return affected
    finally:
        client.delete_table(staging_table_id, not_found_ok=True)


def _load_affected_rows(dataset_url: str) -> pd.DataFrame:
    """Load every affected Slot for a single dataset, with all opportunities columns."""
    client = bigquery.Client(project=GCP_PROJECT_ID)
    selected = ", ".join(OPPORTUNITIES_COLUMNS)
    query = f"""
        SELECT {selected}
        FROM `{TABLE_ID}`
        WHERE dataset_url = @dataset_url
          AND {_AFFECTED_PREDICATE}
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url),
        ]
    )
    return client.query(query, job_config=job_config).to_dataframe()


def _fix_dataset(
    dataset_url: str,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int, int]:
    """Repair affected Slots for one dataset_url.

    Returns (examined, merged, location_filled):
      - examined: affected Slots loaded
      - merged: rows that actually received inherited data (written back)
      - location_filled: subset of merged where location went from {} to non-{}
    """
    start = perf_counter()
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)
    affected_df = _load_affected_rows(dataset_url)
    examined = len(affected_df)
    logger.info("[%d/%d] loaded %d affected rows for %s", index, total, examined, dataset_url)
    if examined == 0:
        return 0, 0, 0

    affected_df = affected_df.reset_index(drop=True)
    parse_opportunities_json_columns(affected_df)

    # Resolve parents from two sources:
    #   1. FacilityUse rows whose nested individualFacilityUse[] holds the ref
    #      (the primary nested-IFU scenario), and
    #   2. any real rows matching the ref by data_id (covers datasets that also
    #      publish IFUs as first-class rows).
    parent_ids = {p for p in (_strip_ref(r) for r in affected_df["has_superEvent"]) if p}
    parent_frames: list[pd.DataFrame] = []
    if parent_ids:
        real_parents = get_dataset_opportunities(dataset_url, required_data_ids=sorted(parent_ids))
        if not real_parents.empty:
            parent_frames.append(real_parents)
    facility_uses = get_dataset_facility_uses(dataset_url)
    if not facility_uses.empty:
        parent_frames.append(facility_uses)

    if not parent_frames:
        logger.info(
            "[%d/%d] DONE %s — examined=%d, no parents found (in %.2fs)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        del affected_df
        gc.collect()
        return examined, 0, 0

    parent_df = (
        parent_frames[0]
        if len(parent_frames) == 1
        else pd.concat(parent_frames, ignore_index=True)
    )
    payload_by_data_id = _build_super_event_payload_by_data_id(affected_df, parent_df)

    # Snapshot each inheritable field BEFORE the merge so we can detect which
    # rows actually received new data and defensively restore any populated
    # value that handle_super_events might touch (it fills only-when-empty).
    before_empty: dict[str, pd.Series] = {
        field: _empty_mask(affected_df[field]) for field in INHERITABLE_FIELDS
    }
    before_values: dict[str, pd.Series] = {
        field: affected_df[field].copy() for field in INHERITABLE_FIELDS
    }

    handle_super_events(affected_df, payload_by_data_id)

    merged_mask = pd.Series(False, index=affected_df.index)
    location_filled_mask = pd.Series(False, index=affected_df.index)
    for field in INHERITABLE_FIELDS:
        after_empty = _empty_mask(affected_df[field])
        field_filled = before_empty[field] & ~after_empty
        merged_mask = merged_mask | field_filled
        if field == "location":
            location_filled_mask = field_filled

        previously_populated = ~before_empty[field]
        if previously_populated.any():
            mismatch = previously_populated & affected_df[field].combine(
                before_values[field],
                lambda a, b: not _values_equal(a, b),
            )
            mismatch_count = int(mismatch.sum())
            if mismatch_count:
                logger.warning(
                    "[%d/%d] %s — %d rows had non-empty %s altered by handle_super_events; restoring",
                    index, total, dataset_url, mismatch_count, field,
                )
                affected_df.loc[mismatch, field] = before_values[field][mismatch]

    merged = int(merged_mask.sum())
    if merged == 0:
        logger.info(
            "[%d/%d] DONE %s — examined=%d, no parents had usable inheritable data (in %.2fs)",
            index, total, dataset_url, examined, perf_counter() - start,
        )
        del affected_df, parent_df, payload_by_data_id, before_empty, before_values
        gc.collect()
        return examined, 0, 0

    location_filled = int(location_filled_mask.sum())
    keep_columns = ["dataset_url", "feed_id", "id", *INHERITABLE_FIELDS]
    updates_df = affected_df.loc[merged_mask, keep_columns].copy()
    del affected_df, parent_df, payload_by_data_id, before_empty, before_values
    gc.collect()

    if not dry_run:
        logger.info("[%d/%d] writing %d rows for %s", index, total, len(updates_df), dataset_url)
        client = bigquery.Client(project=GCP_PROJECT_ID)
        _write_inherited_updates(client, dataset_url, updates_df)

    logger.info(
        "[%d/%d] DONE %s — examined=%d merged=%d location_filled=%d in %.2fs (dry_run=%s)",
        index, total, dataset_url, examined, merged, location_filled,
        perf_counter() - start, dry_run,
    )
    del updates_df
    gc.collect()
    return examined, merged, location_filled


def run(
    dry_run: bool = False,
    max_workers: int | None = None,
    datasets: list[str] | None = None,
    limit: int = 0,
) -> None:
    """Programmatic entry point.  Called by the self-heal step of the ingest job."""
    if max_workers is None:
        max_workers = int(os.getenv("INGEST_MAX_WORKERS", "8"))

    overall_start = perf_counter()
    client = bigquery.Client(project=GCP_PROJECT_ID)

    if datasets:
        dataset_urls = list(datasets)
        logger.info("Restricting to %d explicit dataset_url(s)", len(dataset_urls))
    else:
        affected = discover_affected_datasets(client, TABLE_ID, _AFFECTED_PREDICATE)
        total = sum(c for _, c in affected)
        logger.info("Discovery: %d datasets, %d total affected rows", len(affected), total)
        if limit and limit > 0:
            affected = affected[:limit]
            logger.info("Limiting to top %d datasets by affected-row count", limit)
        dataset_urls = [url for url, _ in affected]

    if not dataset_urls:
        logger.info("Nothing to fix.")
        return

    total_examined = 0
    total_merged = 0
    total_location_filled = 0
    total_datasets = len(dataset_urls)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="nested-ifu") as executor:
        futures = {
            executor.submit(_fix_dataset, ds, dry_run, idx, total_datasets): ds
            for idx, ds in enumerate(dataset_urls, start=1)
        }
        completed = 0
        for future in as_completed(futures):
            ds = futures[future]
            try:
                examined, merged, location_filled = future.result()
                total_examined += examined
                total_merged += merged
                total_location_filled += location_filled
            except Exception:
                logger.exception("Failed for dataset %s", ds)
            completed += 1
            logger.info(
                "Progress %d/%d datasets complete — running totals examined=%d merged=%d location_filled=%d",
                completed, total_datasets, total_examined, total_merged, total_location_filled,
            )

    logger.info(
        "DONE in %.2fs — datasets=%d examined=%d merged=%d location_filled=%d (dry_run=%s)",
        perf_counter() - overall_start,
        len(dataset_urls),
        total_examined,
        total_merged,
        total_location_filled,
        dry_run,
    )


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Compute the fixes but do not write them back to BigQuery.",
)
@click.option(
    "--max-workers",
    type=int,
    default=int(os.getenv("INGEST_MAX_WORKERS", "8")),
    show_default=True,
    help="Thread-pool size for parallel dataset processing.",
)
@click.option(
    "--dataset",
    "datasets",
    multiple=True,
    help="Restrict to specific dataset_url(s); repeat for multiple. Skips discovery.",
)
@click.option(
    "--limit",
    type=int,
    default=0,
    show_default=True,
    help="Process at most this many datasets (largest-first). 0 = no limit.",
)
def main(dry_run: bool, max_workers: int, datasets: tuple[str, ...], limit: int) -> None:
    """Backfill Slots that should inherit from a nested IndividualFacilityUse."""
    run(dry_run=dry_run, max_workers=max_workers, datasets=list(datasets) if datasets else None, limit=limit)


if __name__ == "__main__":
    main()
