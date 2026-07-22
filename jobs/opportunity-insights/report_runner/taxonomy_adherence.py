"""Generate a taxonomy adherence report for OpenActive activities and facilities.

Fetches the OpenActive activity list and facility types taxonomies, then analyzes
how many opportunities in the database match each taxonomy (case-insensitive).
Generates a markdown report with overall statistics and top 20 non-matching terms.

Run with:
    python jobs/opportunity-insights/report_runner/taxonomy_adherence.py
"""

from __future__ import annotations

import json
import logging
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

logger = logging.getLogger(__name__)

BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BQ_DATASET_ID")
OPPORTUNITIES_TABLE = os.getenv("BQ_OPPORTUNITIES_TABLE")

ACTIVITY_LIST_URL = "https://openactive.io/activity-list/activity-list.jsonld"
FACILITY_LIST_URL = "https://openactive.io/facility-types/facility-types.jsonld"

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_FILENAME = "taxonomy_adherence.md"


def fetch_taxonomy(url: str) -> set[str]:
    """Fetch and extract taxonomy terms from a JSON-LD file (case-insensitive)."""
    try:
        logger.info("Fetching taxonomy from %s", url)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        terms = set()

        # Try "concept" array (OpenActive format)
        if "concept" in data and isinstance(data["concept"], list):
            for item in data["concept"]:
                if "prefLabel" in item:
                    label = item["prefLabel"]
                    if isinstance(label, str):
                        terms.add(label.lower())

        # Fallback to @graph format
        elif "@graph" in data and isinstance(data["@graph"], list):
            for item in data["@graph"]:
                if "prefLabel" in item:
                    label = item["prefLabel"]
                    if isinstance(label, str):
                        terms.add(label.lower())
                    elif isinstance(label, dict):
                        for lang, value in label.items():
                            if isinstance(value, str):
                                terms.add(value.lower())
                elif "name" in item:
                    name = item["name"]
                    if isinstance(name, str):
                        terms.add(name.lower())

        logger.info("Fetched %d terms from taxonomy", len(terms))
        return terms
    except Exception as e:
        logger.error("Failed to fetch taxonomy from %s: %s", url, e)
        return set()


def query_opportunities_taxonomy_data() -> tuple[list[dict], list[dict]]:
    """Query opportunities table for activity and facility data."""
    if (
        not BIGQUERY_PROJECT
        or not BIGQUERY_DATASET
        or not OPPORTUNITIES_TABLE
    ):
        raise RuntimeError(
            "BigQuery environment not configured. Expected GCP_PROJECT_ID, "
            "BQ_DATASET_ID, and BQ_OPPORTUNITIES_TABLE."
        )

    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{OPPORTUNITIES_TABLE}"

    query = f"""
        SELECT
            activity,
            facility
        FROM `{table_id}`
        WHERE activity IS NOT NULL OR facility IS NOT NULL
        LIMIT 1000000
    """

    logger.info("Querying opportunities for activity and facility data")
    client = bigquery.Client(project=BIGQUERY_PROJECT)
    rows = client.query(query).result()

    activity_rows = []
    facility_rows = []

    for row in rows:
        if row["activity"] is not None:
            activity_rows.append(row)
        if row["facility"] is not None:
            facility_rows.append(row)

    logger.info("Retrieved %d rows with activity data", len(activity_rows))
    logger.info("Retrieved %d rows with facility data", len(facility_rows))
    return activity_rows, facility_rows


def extract_taxonomy_values(
    rows: list[dict],
    field_name: str,
) -> list[str]:
    """Extract taxonomy values (e.g., activity labels) from rows."""
    all_values = []

    for row in rows:
        value = row.get(field_name)
        if value is None:
            continue

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    all_values.extend([str(v).lower() for v in parsed if v])
                elif parsed:
                    all_values.append(str(parsed).lower())
            except (json.JSONDecodeError, TypeError):
                if value:
                    all_values.append(value.lower())
        elif isinstance(value, list):
            all_values.extend([str(v).lower() for v in value if v])
        elif value:
            all_values.append(str(value).lower())

    return all_values


def calculate_adherence(
    all_values: list[str],
    taxonomy_terms: set[str],
) -> tuple[int, int, float, dict[str, int]]:
    """Calculate adherence statistics and top non-matching terms."""
    total_count = len(all_values)
    matching_count = sum(1 for v in all_values if v in taxonomy_terms)
    non_matching_percentage = (
        ((total_count - matching_count) / total_count * 100)
        if total_count > 0
        else 0.0
    )

    non_matching_terms = Counter(v for v in all_values if v not in taxonomy_terms)
    top_non_matching = dict(non_matching_terms.most_common(20))

    return matching_count, total_count, non_matching_percentage, top_non_matching


def generate_report(
    activity_taxonomy: set[str],
    facility_taxonomy: set[str],
    activity_rows: list[dict],
    facility_rows: list[dict],
) -> str:
    """Generate the markdown report."""
    lines = [
        "# OpenActive Taxonomy Adherence Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "This report analyzes how well the opportunities in our database adhere to the",
        "OpenActive activity and facility type taxonomies.",
        "",
        "## Taxonomies",
        "",
        f"- **Activity List**: {ACTIVITY_LIST_URL}",
        f"- **Facility Types**: {FACILITY_LIST_URL}",
        "",
    ]

    # Activity analysis
    lines.append("## Activity Analysis")
    lines.append("")
    activity_values = extract_taxonomy_values(activity_rows, "activity")
    activity_matching, activity_total, activity_non_pct, activity_top_non = calculate_adherence(
        activity_values, activity_taxonomy
    )

    lines.append(f"**Taxonomy Size**: {len(activity_taxonomy)} terms")
    lines.append("")
    lines.append("### Adherence Statistics")
    lines.append("")
    lines.append(f"- **Total Activity Values**: {activity_total:,}")
    lines.append(f"- **Matching Terms**: {activity_matching:,} ({(activity_matching/activity_total*100):.2f}%)")
    lines.append(f"- **Non-Matching Terms**: {activity_total - activity_matching:,} ({activity_non_pct:.2f}%)")
    lines.append("")

    if activity_top_non:
        lines.append("### Top 20 Non-Matching Activity Terms")
        lines.append("")
        lines.append("| Term | Count |")
        lines.append("|------|-------|")
        for term, count in activity_top_non.items():
            lines.append(f"| `{term}` | {count:,} |")
        lines.append("")
    else:
        lines.append("*All activity terms match the taxonomy!*")
        lines.append("")

    # Facility analysis
    lines.append("## Facility Analysis")
    lines.append("")
    facility_values = extract_taxonomy_values(facility_rows, "facility")
    facility_matching, facility_total, facility_non_pct, facility_top_non = calculate_adherence(
        facility_values, facility_taxonomy
    )

    lines.append(f"**Taxonomy Size**: {len(facility_taxonomy)} terms")
    lines.append("")
    lines.append("### Adherence Statistics")
    lines.append("")
    lines.append(f"- **Total Facility Values**: {facility_total:,}")
    lines.append(f"- **Matching Terms**: {facility_matching:,} ({(facility_matching/facility_total*100):.2f}%)")
    lines.append(f"- **Non-Matching Terms**: {facility_total - facility_matching:,} ({facility_non_pct:.2f}%)")
    lines.append("")

    if facility_top_non:
        lines.append("### Top 20 Non-Matching Facility Terms")
        lines.append("")
        lines.append("| Term | Count |")
        lines.append("|------|-------|")
        for term, count in facility_top_non.items():
            lines.append(f"| `{term}` | {count:,} |")
        lines.append("")
    else:
        lines.append("*All facility terms match the taxonomy!*")
        lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    combined_matching = activity_matching + facility_matching
    combined_total = activity_total + facility_total
    combined_adherence = (combined_matching / combined_total * 100) if combined_total > 0 else 0.0

    lines.append(f"**Overall Taxonomy Adherence**: {combined_adherence:.2f}%")
    lines.append("")
    lines.append("| Taxonomy | Adherence | Non-Matching |")
    lines.append("|----------|-----------|--------------|")
    lines.append(f"| Activity | {(activity_matching/activity_total*100):.2f}% | {activity_non_pct:.2f}% |")
    lines.append(f"| Facility | {(facility_matching/facility_total*100):.2f}% | {facility_non_pct:.2f}% |")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Run the taxonomy adherence report."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("Starting taxonomy adherence report generation")

    # Fetch taxonomies
    activity_taxonomy = fetch_taxonomy(ACTIVITY_LIST_URL)
    facility_taxonomy = fetch_taxonomy(FACILITY_LIST_URL)

    if not activity_taxonomy or not facility_taxonomy:
        logger.error("Failed to fetch one or more taxonomies")
        return

    # Query opportunities
    activity_rows, facility_rows = query_opportunities_taxonomy_data()

    if not activity_rows and not facility_rows:
        logger.error("No opportunities found with activity or facility data")
        return

    # Generate report
    report_content = generate_report(
        activity_taxonomy,
        facility_taxonomy,
        activity_rows,
        facility_rows,
    )

    # Save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / REPORT_FILENAME

    with open(report_path, "w") as f:
        f.write(report_content)

    logger.info("Report saved to %s", report_path)
    print(f"\n✓ Report generated: {report_path}")


if __name__ == "__main__":
    main()
