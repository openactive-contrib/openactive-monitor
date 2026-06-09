"""One-time backfill script: populate district_code, region_code, country_code,
country_name on existing opportunities rows using the district_name column and
the 000-district-region-country.json lookup file.

Usage:
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python migrations/backfill_district_enrichment.py [--dry-run] [--batch-size 50000]

Requires:
    - GCP_PROJECT_ID and BQ_DATASET_ID environment variables (or .env)
    - The 000-district-region-country.json file in volume-1/data-analysis/
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "openactive-monitor")
BQ_DATASET_ID = os.getenv("BQ_DATASET_ID", "openactive_analytics")
BQ_OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE", "opportunities")

DISTRICT_LOOKUP_FILENAME = "000-district-region-country.json"
DEFAULT_LOOKUP_DIR = Path(__file__).resolve().parents[3] / "volume-1" / "data-analysis"


def _load_lookup(lookup_dir: Path) -> dict[str, dict[str, str | None]]:
    path = lookup_dir / DISTRICT_LOOKUP_FILENAME
    if not path.exists():
        raise FileNotFoundError(f"Lookup file not found: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@click.command()
@click.option("--dry-run", is_flag=True, default=False, help="Print the UPDATE query but don't execute.")
@click.option(
    "--lookup-dir",
    type=click.Path(path_type=Path, exists=True),
    default=DEFAULT_LOOKUP_DIR,
    help="Directory containing the district lookup JSON.",
)
def main(dry_run: bool, lookup_dir: Path) -> None:
    """Backfill district_code, region_code, country_code, country_name from district_name."""
    lookup = _load_lookup(lookup_dir)
    logger.info("Loaded %d district entries from %s", len(lookup), lookup_dir / DISTRICT_LOOKUP_FILENAME)

    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_OPPORTUNITIES_TABLE}"

    # Build a temporary lookup table in BigQuery using a CTE of values
    # For ~400 districts this is well within query limits.
    value_rows: list[str] = []
    for district_name, info in lookup.items():
        district_code = info.get("district_code") or ""
        region_code = info.get("region_code") or ""
        region_name = info.get("region_name") or ""
        country_code = info.get("country_code") or ""
        country_name = info.get("country_name") or ""

        # Escape single quotes in strings
        dn = district_name.replace("'", "\\'")
        dc = district_code.replace("'", "\\'")
        rc = region_code.replace("'", "\\'")
        rn = region_name.replace("'", "\\'")
        cc = country_code.replace("'", "\\'")
        cn = country_name.replace("'", "\\'")

        value_rows.append(f"('{dn}', '{dc}', '{rc}', '{rn}', '{cc}', '{cn}')")

    if not value_rows:
        logger.warning("No lookup entries found; nothing to backfill.")
        return

    # Split into chunks if needed (BigQuery has a query size limit)
    # ~400 districts * ~100 chars per row = ~40KB, well within limits
    values_sql = ",\n    ".join(value_rows)

    update_query = f"""
UPDATE `{table_id}` AS o
SET
  o.district_code = lkp.district_code,
  o.region_code = lkp.region_code,
  o.country_code = lkp.country_code,
  o.country_name = lkp.country_name
FROM (
  SELECT * FROM UNNEST([
    STRUCT<district_name STRING, district_code STRING, region_code STRING, region_name STRING, country_code STRING, country_name STRING>
    {values_sql}
  ])
) AS lkp
WHERE o.district_name = lkp.district_name
  AND o.district_name IS NOT NULL
  AND (o.district_code IS NULL OR o.district_code = '');
"""

    if dry_run:
        logger.info("DRY RUN — would execute:\n%s", update_query[:2000] + "..." if len(update_query) > 2000 else update_query)
        return

    client = bigquery.Client(project=GCP_PROJECT_ID)
    logger.info("Executing backfill UPDATE on %s...", table_id)
    job = client.query(update_query)
    result = job.result()
    logger.info(
        "Backfill complete: %d rows modified",
        job.num_dml_affected_rows or 0,
    )


if __name__ == "__main__":
    main()

