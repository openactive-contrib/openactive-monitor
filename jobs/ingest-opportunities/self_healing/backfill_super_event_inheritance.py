"""
Self-healing backfill: re-apply superEvent inheritance (parent, grandparent, …)
to rows that are missing values an ancestor can provide.

Why rows end up with gaps
-------------------------
- Multi-level chains were not resolved before ``processing._resolve_ancestry``
  existed: a ScheduledSession → SessionSeries → EventSeries chain only received
  the SessionSeries' own fields, never the EventSeries' (activity, gender,
  organizer, level, ageRange …).
- A parent may be updated by the nightly ingestion while its children are not
  re-published, so the children never see the parent's new data.
- Columns added later (``activity_json``, ``facility_json``,
  ``isAccessibleForFree``, ``organization_name``) were only populated for rows
  ingested after they existed.

Which rows are examined
-----------------------
Only rows where an inheritable column is empty AND the parent (or the parent's
inline ``superEvent``) actually carries the matching raw property — so routine
self-heal runs don't keep reloading rows nothing can fill.  Two link shapes:

- inline: ``has_superEvent`` is an object (checked at depth 1 and 2), and
- reference: ``has_superEvent`` is an ``@id`` string, resolved to a parent row
  in the same dataset (checked against the parent's ``json_data`` and its
  inline ``superEvent``).

Deeper string → string chains are not pre-filtered here (none exist in the data
today); ``processing.denormalize_dataset`` resolves them at ingestion time.

How rows are fixed
------------------
Per dataset, affected rows are streamed in chunks with only the columns
inheritance needs (child ``json_data`` is reduced to its top-level keys — the
only thing ``_merge_inherited_data`` reads from it).  Ancestor rows are fetched
by ``data_id`` (multi-hop), ``processing.handle_super_events`` runs with the
full ancestor chain, and only rows that gained data are written back via a slim
fill-only-when-empty MERGE (``json_data`` is never rewritten).  Safe to re-run.

Usage
-----
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python self_healing/backfill_super_event_inheritance.py [--dry-run] \
        [--max-workers 8] [--dataset <url>] [--kind ScheduledSession] \
        [--limit 0] [--chunk-size 50000]
"""

from __future__ import annotations

import gc
import logging
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter
from typing import Any, Iterator

import click
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Make the ingest-opportunities package importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bigquery_ops import (  # noqa: E402
    OPPORTUNITIES_COLUMNS,
    get_dataset_ancestor_opportunities,
    get_dataset_facility_uses,
    get_dataset_opportunities,
    parse_opportunities_json_columns,
)
from processing import (  # noqa: E402
    _build_super_event_payload_by_data_id,
    collect_super_event_refs,
    handle_super_events,
)
from self_healing._common import (  # noqa: E402
    INHERITABLE_BOOL_COLUMNS,
    INHERITABLE_FIELDS,
    INHERITABLE_STRING_COLUMNS,
    inherited_changes_mask,
    snapshot_inheritable,
    write_inherited_updates,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backfill_super_event_inheritance")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

DEFAULT_CHUNK_SIZE = 50_000


# ---------------------------------------------------------------------------
# Affected-row predicate
# ---------------------------------------------------------------------------

_JSON_EMPTY_LITERALS = "('[]', '{}', 'null', '\"\"')"


def _json_empty(expr: str) -> str:
    return f"({expr} IS NULL OR TO_JSON_STRING({expr}) IN {_JSON_EMPTY_LITERALS})"


def _json_present(expr: str) -> str:
    return f"({expr} IS NOT NULL AND TO_JSON_STRING({expr}) NOT IN {_JSON_EMPTY_LITERALS})"


def _str_empty(expr: str) -> str:
    return f"({expr} IS NULL OR TRIM({expr}) = '')"


def _fillable_conditions(child: str, level: str) -> list[str]:
    """Conditions that are TRUE when ``child`` lacks a value ``level`` (a parent
    JSON payload expression) can provide.  Mirrors ``apply_inherited_data``."""
    activity_present = f"({_json_present(f'{level}.activity')} OR {_json_present(f'{level}.activities')})"
    org_name = (
        f"COALESCE(JSON_VALUE({level}.organizer.name), JSON_VALUE({level}.organizer[0].name), "
        f"JSON_VALUE({level}.provider.name), '') != ''"
    )
    return [
        f"{_json_empty(f'{child}.activity')} AND {activity_present}",
        f"{_json_empty(f'{child}.activity_json')} AND {activity_present}",
        f"{_json_empty(f'{child}.facility')} AND {_json_present(f'{level}.facilityType')}",
        f"{_json_empty(f'{child}.facility_json')} AND {_json_present(f'{level}.facilityType')}",
        f"{_json_empty(f'{child}.location')} AND {_json_present(f'{level}.location')}",
        f"{_json_empty(f'{child}.ageRange')} AND {_json_present(f'{level}.ageRange')}",
        f"{_json_empty(f'{child}.level')} AND {_json_present(f'{level}.level')}",
        f"{_json_empty(f'{child}.accessibilitySupport')} AND {_json_present(f'{level}.accessibilitySupport')}",
        f"{_str_empty(f'{child}.genderRestriction')} AND COALESCE(JSON_VALUE({level}.genderRestriction), '') != ''",
        f"{child}.isAccessibleForFree IS NULL AND JSON_TYPE({level}.isAccessibleForFree) = 'boolean'",
        f"{_str_empty(f'{child}.organization_name')} AND {org_name}",
    ]


def _any_fillable(child: str, levels: list[str]) -> str:
    conditions = [c for level in levels for c in _fillable_conditions(child, level)]
    return "(" + "\n            OR ".join(f"({c})" for c in conditions) + ")"


def _affected_predicate(dataset_scoped: bool) -> str:
    """SQL predicate over ``opportunities AS o``.

    ``dataset_scoped`` adds ``@dataset_url`` filters so BigQuery can prune on the
    table's ``dataset_url`` clustering for both the row and its parent lookup.
    """
    parent_dataset_filter = "p.dataset_url = @dataset_url" if dataset_scoped else "p.dataset_url = o.dataset_url"
    inline = (
        "JSON_TYPE(o.has_superEvent) = 'object' AND "
        + _any_fillable("o", ["o.has_superEvent", "o.has_superEvent.superEvent"])
    )
    reference = f"""JSON_TYPE(o.has_superEvent) = 'string' AND EXISTS (
            SELECT 1 FROM `{TABLE_ID}` AS p
            WHERE {parent_dataset_filter}
              AND p.data_id = JSON_VALUE(o.has_superEvent)
              AND {_any_fillable("o", ["p.json_data", "p.json_data.superEvent"])}
        )"""
    predicate = f"(({inline})\n        OR ({reference}))"
    predicate += "\n        AND (ARRAY_LENGTH(@kinds) = 0 OR o.kind IN UNNEST(@kinds))"
    if dataset_scoped:
        predicate = f"o.dataset_url = @dataset_url\n        AND {predicate}"
    return predicate


def _kinds_param(kinds: list[str]) -> bigquery.ArrayQueryParameter:
    return bigquery.ArrayQueryParameter("kinds", "STRING", list(kinds))


# ---------------------------------------------------------------------------
# Discovery + streaming load
# ---------------------------------------------------------------------------

def _get_affected_datasets(client: bigquery.Client, kinds: list[str]) -> list[tuple[str, int]]:
    """Return (dataset_url, row_count) tuples ordered by row_count desc."""
    query = f"""
        SELECT o.dataset_url, COUNT(*) AS row_count
        FROM `{TABLE_ID}` AS o
        WHERE {_affected_predicate(dataset_scoped=False)}
        GROUP BY o.dataset_url
        ORDER BY row_count DESC
    """
    job_config = bigquery.QueryJobConfig(query_parameters=[_kinds_param(kinds)])
    rows = client.query(query, job_config=job_config).result()
    out = [(r["dataset_url"], int(r["row_count"])) for r in rows if r["dataset_url"]]
    logger.info("Discovery: %d datasets, %d total affected rows", len(out), sum(c for _, c in out))
    return out


_LOAD_COLUMNS: tuple[str, ...] = ("dataset_url", "feed_id", "id", "data_id", "kind", "has_superEvent", *INHERITABLE_FIELDS)


def _prepare_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Shape a streamed chunk into what ``handle_super_events`` expects."""
    chunk = chunk.reset_index(drop=True)
    parse_opportunities_json_columns(chunk)
    # ``_merge_inherited_data`` only checks top-level key presence on the child,
    # so a key-only stand-in avoids loading every child's full json_data.
    chunk["json_data"] = [
        {key: True for key in keys} if keys is not None else {}
        for keys in chunk.pop("json_keys").tolist()
    ]
    chunk["inherited_data"] = [{} for _ in range(len(chunk))]
    # Nullable BigQuery types arrive as pandas NA; inheritance expects None.
    for col in (*INHERITABLE_STRING_COLUMNS, *INHERITABLE_BOOL_COLUMNS):
        chunk[col] = chunk[col].astype(object).where(chunk[col].notna(), None)
    return chunk


def _iter_affected_chunks(
    client: bigquery.Client,
    dataset_url: str,
    kinds: list[str],
    chunk_size: int,
) -> Iterator[pd.DataFrame]:
    """Stream a dataset's affected rows in chunks from a single query."""
    selected = ", ".join(f"o.{c}" for c in _LOAD_COLUMNS)
    query = f"""
        SELECT {selected}, JSON_KEYS(o.json_data, 1) AS json_keys
        FROM `{TABLE_ID}` AS o
        WHERE {_affected_predicate(dataset_scoped=True)}
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("dataset_url", "STRING", dataset_url),
            _kinds_param(kinds),
        ]
    )
    result = client.query(query, job_config=job_config).result(page_size=chunk_size)
    buffer: list[pd.DataFrame] = []
    buffered = 0
    for page_df in result.to_dataframe_iterable():
        buffer.append(page_df)
        buffered += len(page_df)
        if buffered >= chunk_size:
            yield _prepare_chunk(pd.concat(buffer, ignore_index=True))
            buffer, buffered = [], 0
    if buffer:
        yield _prepare_chunk(pd.concat(buffer, ignore_index=True))


# ---------------------------------------------------------------------------
# Parent resolution
# ---------------------------------------------------------------------------

class _AncestorLookup:
    """Per-dataset, incrementally grown ``data_id → payload`` lookup.

    Parents (and their ancestors) are fetched by ``data_id`` the first time a
    chunk references them; FacilityUse rows are loaded once if a Slot ref can't
    be resolved otherwise (nested IndividualFacilityUse pattern).
    """

    def __init__(self, dataset_url: str) -> None:
        self.dataset_url = dataset_url
        self.known_ids: set[str] = set()
        self.frames: list[pd.DataFrame] = []
        self.payload_by_data_id: dict[str, dict[str, Any]] = {}
        self.cache: dict[str, dict[str, Any]] = {}
        self._facility_uses_loaded = False

    def _add(self, frame: pd.DataFrame) -> None:
        """Append parent rows and rebuild the lookup (and reset the ancestry
        cache, since earlier chains may have lacked now-available ancestors)."""
        if frame.empty:
            return
        self.known_ids.update(d for d in frame["data_id"].tolist() if isinstance(d, str) and d)
        self.frames.append(frame)
        parents = pd.concat(self.frames, ignore_index=True) if len(self.frames) > 1 else frame
        self.frames = [parents]
        self.payload_by_data_id = _build_super_event_payload_by_data_id(
            pd.DataFrame(columns=OPPORTUNITIES_COLUMNS), parents
        )
        self.cache = {}

    def ensure(self, chunk: pd.DataFrame) -> None:
        missing = sorted(collect_super_event_refs(chunk) - self.known_ids)
        if missing:
            self.known_ids.update(missing)
            parents = get_dataset_opportunities(self.dataset_url, required_data_ids=missing)
            if not parents.empty:
                ancestors = get_dataset_ancestor_opportunities(self.dataset_url, [parents], self.known_ids)
                self._add(pd.concat([parents, ancestors], ignore_index=True) if not ancestors.empty else parents)

        if self._facility_uses_loaded or "Slot" not in set(chunk["kind"].tolist()):
            return
        unresolved_slot_refs = collect_super_event_refs(chunk[chunk["kind"] == "Slot"]) - set(self.payload_by_data_id)
        if unresolved_slot_refs:
            self._facility_uses_loaded = True
            self._add(get_dataset_facility_uses(self.dataset_url))


# ---------------------------------------------------------------------------
# Per-dataset fix
# ---------------------------------------------------------------------------

def _fix_dataset(
    dataset_url: str,
    kinds: list[str],
    chunk_size: int,
    dry_run: bool,
    index: int,
    total: int,
) -> tuple[int, int, Counter]:
    """Repair affected rows for one dataset_url.

    Returns (examined, merged, filled_by_field):
      - examined: affected rows loaded
      - merged: rows that gained at least one value (written back)
      - filled_by_field: per-column count of cells filled
    """
    start = perf_counter()
    prefix = f"[{index}/{total}] {dataset_url} —"
    logger.info("[%d/%d] START dataset=%s", index, total, dataset_url)

    client = bigquery.Client(project=GCP_PROJECT_ID)
    lookup = _AncestorLookup(dataset_url)
    examined = 0
    merged = 0
    filled_by_field: Counter = Counter()
    pending_updates: list[pd.DataFrame] = []
    pending_rows = 0

    def flush() -> None:
        nonlocal pending_updates, pending_rows
        if not pending_updates:
            return
        updates_df = pd.concat(pending_updates, ignore_index=True)
        pending_updates, pending_rows = [], 0
        if not dry_run:
            logger.info("%s writing %d rows", prefix, len(updates_df))
            write_inherited_updates(client, TABLE_ID, dataset_url, updates_df, label="super_event_inheritance")
        del updates_df
        gc.collect()

    for chunk in _iter_affected_chunks(client, dataset_url, kinds, chunk_size):
        examined += len(chunk)
        lookup.ensure(chunk)

        before = snapshot_inheritable(chunk)
        handle_super_events(chunk, lookup.payload_by_data_id, lookup.cache)
        changed, counts = inherited_changes_mask(chunk, before, prefix)
        filled_by_field.update({k: v for k, v in counts.items() if v})

        chunk_merged = int(changed.sum())
        merged += chunk_merged
        if chunk_merged:
            pending_updates.append(chunk.loc[changed, ["dataset_url", "feed_id", "id", *INHERITABLE_FIELDS]].copy())
            pending_rows += chunk_merged
        logger.info("%s chunk examined=%d merged=%d (running examined=%d merged=%d)",
                    prefix, len(chunk), chunk_merged, examined, merged)
        del chunk, before, changed
        gc.collect()
        if pending_rows >= chunk_size:
            flush()

    flush()
    logger.info(
        "[%d/%d] DONE %s — examined=%d merged=%d filled=%s in %.2fs (dry_run=%s)",
        index, total, dataset_url, examined, merged, dict(filled_by_field),
        perf_counter() - start, dry_run,
    )
    return examined, merged, filled_by_field


def run(
    dry_run: bool = False,
    max_workers: int | None = None,
    datasets: list[str] | None = None,
    limit: int = 0,
    kinds: list[str] | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    """Programmatic entry point for backfilling missing inherited columns.

    Called by the self-heal step at the end of ``ingest_opportunities``.
    """
    if max_workers is None:
        max_workers = int(os.getenv("INGEST_MAX_WORKERS", "8"))
    kinds = list(kinds or [])

    overall_start = perf_counter()
    client = bigquery.Client(project=GCP_PROJECT_ID)

    if datasets:
        dataset_urls = list(datasets)
        logger.info("Restricting to %d explicit dataset_url(s)", len(dataset_urls))
    else:
        affected = _get_affected_datasets(client, kinds)
        if limit and limit > 0:
            affected = affected[:limit]
            logger.info("Limiting to top %d datasets by affected-row count", limit)
        dataset_urls = [url for url, _ in affected]

    if not dataset_urls:
        logger.info("Nothing to fix.")
        return

    total_examined = 0
    total_merged = 0
    total_filled: Counter = Counter()
    total_datasets = len(dataset_urls)

    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="backfill") as executor:
        futures = {
            executor.submit(_fix_dataset, ds, kinds, chunk_size, dry_run, idx, total_datasets): ds
            for idx, ds in enumerate(dataset_urls, start=1)
        }
        completed = 0
        for future in as_completed(futures):
            ds = futures[future]
            try:
                examined, merged, filled = future.result()
                total_examined += examined
                total_merged += merged
                total_filled.update(filled)
            except Exception:
                logger.exception("Failed for dataset %s", ds)
            completed += 1
            logger.info(
                "Progress %d/%d datasets complete — running totals examined=%d merged=%d",
                completed, total_datasets, total_examined, total_merged,
            )

    logger.info(
        "DONE in %.2fs — datasets=%d examined=%d merged=%d filled=%s (dry_run=%s)",
        perf_counter() - overall_start,
        len(dataset_urls),
        total_examined,
        total_merged,
        dict(total_filled),
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
    help="Restrict to specific dataset_url(s); repeat for multiple. Skips the discovery query.",
)
@click.option(
    "--kind",
    "kinds",
    multiple=True,
    help="Restrict to opportunity kind(s), e.g. ScheduledSession; repeat for multiple.",
)
@click.option(
    "--limit",
    type=int,
    default=0,
    show_default=True,
    help="Process at most this many datasets (largest-first). 0 = no limit.",
)
@click.option(
    "--chunk-size",
    type=int,
    default=DEFAULT_CHUNK_SIZE,
    show_default=True,
    help="Rows per streamed chunk and per write batch (bounds memory per worker).",
)
def main(
    dry_run: bool,
    max_workers: int,
    datasets: tuple[str, ...],
    kinds: tuple[str, ...],
    limit: int,
    chunk_size: int,
) -> None:
    """Backfill inherited columns from parents and grandparents."""
    run(
        dry_run=dry_run,
        max_workers=max_workers,
        datasets=list(datasets) if datasets else None,
        limit=limit,
        kinds=list(kinds),
        chunk_size=chunk_size,
    )


if __name__ == "__main__":
    main()
