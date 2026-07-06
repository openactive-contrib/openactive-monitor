"""CLI entrypoint for the OpenActive data-model field-usage analysis.

Run manually (≈ once a month) from the ``opportunity-insights`` directory:

    python -m field_usage.run --samples-per-kind 200 --output-dir ./out/field_usage

Streams a random sample of ``json_data`` payloads from the BigQuery
``opportunities`` table, walks each payload to tally field usage per entity
type (handling in-place vs referenced entities), optionally cross-checks the
known top-level model fields with an exact full-table scan, and writes two
markdown reports:

* ``field_usage_model_report.md`` — unused / rarely-used model fields per
  entity, deletion candidates, provider extensions, discovered nested types.
* ``field_usage_per_dataset_dump.md`` — fields used by each dataset.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

import click

import bigquery_ops
from field_usage import model_catalog, queries
from field_usage.aggregator import UsageAggregator, UsageResults
from field_usage.model_spec import get_alternatives
from field_usage.report import render_model_usage_report, render_per_dataset_dump

logger = logging.getLogger(__name__)

MODEL_REPORT_FILENAME = "field_usage_model_report.md"
PER_DATASET_FILENAME = "field_usage_per_dataset_dump.md"


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s  %(levelname)-8s  %(message)s")
    logging.getLogger().setLevel(level)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def _coerce_payload(value: object) -> dict | None:
    """Normalise a BigQuery JSON column value to a dict (or None)."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (ValueError, TypeError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _stream_samples(
    opportunities_tbl: str,
    reference_date: date,
    window_days: int | None,
    samples_per_kind: int,
    agg: UsageAggregator,
) -> int:
    sql = queries.sampled_json_data(
        opportunities_tbl, reference_date, window_days, samples_per_kind
    )
    logger.info("Running sampling query (samples_per_kind=%s)…", samples_per_kind)
    job = bigquery_ops._client().query(sql)
    rows = 0
    for row in job.result():
        payload = _coerce_payload(row["json_data"])
        if payload is None:
            continue
        agg.add_payload(row["dataset_url"], row["feed_id"], row["kind"], payload)
        rows += 1
        if rows % 50_000 == 0:
            logger.info("  processed %s sampled rows…", f"{rows:,}")
    logger.info("Sampling complete: %s payloads aggregated.", f"{rows:,}")
    return rows


def _build_exact_specs(model_version: str) -> list[tuple[str, str, list[str]]]:
    """Return (category, field, [field + alternatives]) for every model field."""
    specs: list[tuple[str, str, list[str]]] = []
    for category in model_catalog.SPEC_CATEGORIES:
        for field in model_catalog.model_fields_for_category(category, model_version):
            specs.append((category, field, [field, *get_alternatives(category, field)]))
    return specs


def _apply_exact_scan(
    results: UsageResults,
    opportunities_tbl: str,
    reference_date: date,
    window_days: int | None,
    model_version: str,
) -> None:
    """Run the exact full-table scan and merge Exact % into model field rows."""
    specs = _build_exact_specs(model_version)
    sql = queries.exact_field_presence(
        opportunities_tbl, [paths for _, _, paths in specs], window_days, reference_date
    )
    logger.info("Running exact full-scan query over %s model fields…", len(specs))
    job = bigquery_ops._client().query(sql)

    cat_total: dict[str, int] = {}
    cat_field: dict[tuple[str, str], int] = {}
    for row in job.result():
        kind = row["kind"]
        if not model_catalog.is_model_type(kind):
            continue
        cat = model_catalog.spec_category_for_kind(kind)
        cat_total[cat] = cat_total.get(cat, 0) + int(row["total"])
        for i, (spec_cat, field, _paths) in enumerate(specs):
            if spec_cat != cat:
                continue
            cat_field[(cat, field)] = cat_field.get((cat, field), 0) + int(row[f"f{i}"])

    for cat_report in results.categories:
        total = cat_total.get(cat_report.category, 0)
        if not total:
            continue
        for fr in cat_report.model_fields:
            cnt = cat_field.get((cat_report.category, fr.field), 0)
            fr.exact_pct = cnt / total * 100.0
    logger.info("Exact full-scan merged.")


def _load_publisher_names(results: UsageResults) -> None:
    """Best-effort join of feeds.publisher_name onto each dataset report."""
    try:
        feeds_tbl = bigquery_ops.table_id(bigquery_ops.FEEDS_TABLE)
        sql = f"""
            SELECT dataset_url, ANY_VALUE(publisher_name) AS publisher_name
            FROM `{feeds_tbl}`
            WHERE dataset_url IS NOT NULL
            GROUP BY dataset_url
        """
        mapping = {
            row["dataset_url"]: row["publisher_name"]
            for row in bigquery_ops._client().query(sql).result()
        }
        for ds in results.datasets:
            ds.publisher_name = mapping.get(ds.dataset_url)
    except Exception as exc:  # non-fatal enrichment
        logger.warning("Could not load publisher names: %s", exc)


def run(
    samples_per_kind: int,
    window_days: int | None,
    reference_date: date,
    rare_threshold: float,
    low_threshold: float,
    output_dir: Path,
    exact_scan: bool,
    dump_percentages: bool,
    model_version: str,
) -> None:
    opportunities_tbl = bigquery_ops.table_id(bigquery_ops.OPPORTUNITIES_TABLE)

    agg = UsageAggregator(model_version=model_version)
    _stream_samples(opportunities_tbl, reference_date, window_days, samples_per_kind, agg)

    results = agg.compute_results(rare_threshold, low_threshold)

    # Exact full-scan disabled: its top-level-only, row-weighted Exact % was
    # confusing alongside the per-group Sampled % (e.g. Sampled 0.7% vs Exact
    # 0.0% for a field that lives mostly on nested objects / a few small feeds).
    # The calculation is kept below — re-enable by uncommenting.
    # if exact_scan:
    #     _apply_exact_scan(results, opportunities_tbl, reference_date, window_days, model_version)

    _load_publisher_names(results)

    window_desc = "all-time" if window_days is None else (
        f"last {window_days} days (to {reference_date.isoformat()})"
    )
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "table": opportunities_tbl,
        "window": window_desc,
        "samples_per_kind": samples_per_kind,
        "rare_threshold": rare_threshold,
        "low_threshold": low_threshold,
        "exact_scan": exact_scan,
        "model_version": model_version,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / MODEL_REPORT_FILENAME
    dump_path = output_dir / PER_DATASET_FILENAME
    model_path.write_text(render_model_usage_report(results, meta), encoding="utf-8")
    dump_path.write_text(
        render_per_dataset_dump(results, dump_percentages=dump_percentages), encoding="utf-8"
    )
    logger.info("Wrote %s", model_path)
    logger.info("Wrote %s", dump_path)


@click.command()
@click.option("--verbose", is_flag=True, default=False, help="Enable DEBUG logging.")
@click.option(
    "--samples-per-kind",
    type=int,
    default=queries.DEFAULT_SAMPLES_PER_KIND,
    show_default=True,
    help="Random json_data samples per (dataset_url, feed_id, kind).",
)
@click.option(
    "--window-days",
    type=int,
    default=None,
    help="Restrict to opportunities updated within N days of --reference-date. "
    "Omit for all-time.",
)
@click.option(
    "--reference-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="Anchor date for --window-days (default: today).",
)
@click.option("--rare-threshold", type=float, default=1.0, show_default=True,
              help="Presence %% below which a field is classed RARE.")
@click.option("--low-threshold", type=float, default=10.0, show_default=True,
              help="Presence %% below which a field is classed LOW.")
@click.option("--output-dir", type=click.Path(file_okay=False, path_type=Path),
              default=Path("./out/field_usage"), show_default=True,
              help="Directory for the generated markdown reports.")
@click.option("--exact-scan/--no-exact-scan", default=True, show_default=True,
              help="[Currently disabled] Exact full-table %% for top-level model fields. "
              "The calculation is commented out in run.py; this flag is a no-op until re-enabled.")
@click.option("--dump-percentages", is_flag=True, default=False,
              help="Include per-field percentages in the per-dataset dump.")
@click.option("--model-version", type=click.Choice(model_catalog.AVAILABLE_VERSIONS),
              default=model_catalog.DEFAULT_MODEL_VERSION, show_default=True,
              help="OpenActive model spec version whose field catalog drives the analysis. "
              "Categories lacking the chosen version fall back to the newest available below it "
              "(e.g. RouteGuide → V1.0).")
def cli(
    verbose: bool,
    samples_per_kind: int,
    window_days: int | None,
    reference_date: datetime | None,
    rare_threshold: float,
    low_threshold: float,
    output_dir: Path,
    exact_scan: bool,
    dump_percentages: bool,
    model_version: str,
) -> None:
    _configure_logging(verbose)
    ref = reference_date.date() if reference_date else date.today()
    run(
        samples_per_kind=samples_per_kind,
        window_days=window_days,
        reference_date=ref,
        rare_threshold=rare_threshold,
        low_threshold=low_threshold,
        output_dir=output_dir,
        exact_scan=exact_scan,
        dump_percentages=dump_percentages,
        model_version=model_version,
    )


if __name__ == "__main__":
    cli()
