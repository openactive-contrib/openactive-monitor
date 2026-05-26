"""Homepage metrics export.

Computes a small set of headline figures for frontend applications and writes
them as ``homepage_metrics.json`` to a directory backed by the ``volume-1``
Cloud Storage bucket (mounted at ``/volume-1/public`` in the Cloud Run Job).

Two values are hard-coded placeholders for now; the other three come from
single-row BigQuery queries against ``insight_run_summary``, ``feeds`` and
``opportunities``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import bigquery_ops

logger = logging.getLogger(__name__)

OUTPUT_FILENAME = "homepage_metrics.json"

_HARDCODED_PERCENTAGE_OF_LOCAL_AUTHORITIES = 74
_HARDCODED_NUMBER_OF_ACTIVITY_PROVIDERS = 4885


def _num_opportunities_sql(insight_run_summary_tbl: str) -> str:
    return f"""
        SELECT total_num_future_opportunity_items AS n
        FROM `{insight_run_summary_tbl}`
        ORDER BY run_date DESC
        LIMIT 1
    """


def _num_publishers_sql(feeds_tbl: str) -> str:
    return f"""
        SELECT COUNT(DISTINCT dataset_url) AS n
        FROM `{feeds_tbl}`
    """


def _num_activities_sql(opportunities_tbl: str) -> str:
    return f"""
        SELECT COUNT(DISTINCT JSON_VALUE(a)) AS n
        FROM `{opportunities_tbl}` AS o,
             UNNEST(JSON_EXTRACT_ARRAY(o.activity)) AS a
        WHERE JSON_VALUE(a) IS NOT NULL
    """


def _scalar_int(sql: str) -> int:
    df = bigquery_ops.run_query(sql)
    if df.empty or df.iloc[0, 0] is None:
        return 0
    return int(df.iloc[0, 0])


def build_homepage_metrics(
    opportunities_tbl: str,
    feeds_tbl: str,
    insight_run_summary_tbl: str,
) -> dict[str, int]:
    return {
        "number_of_opportunities": _scalar_int(_num_opportunities_sql(insight_run_summary_tbl)),
        "number_of_publishers": _scalar_int(_num_publishers_sql(feeds_tbl)),
        "number_of_activities": _scalar_int(_num_activities_sql(opportunities_tbl)),
        "percentage_of_local_authorities": _HARDCODED_PERCENTAGE_OF_LOCAL_AUTHORITIES,
        "number_of_activity_providers": _HARDCODED_NUMBER_OF_ACTIVITY_PROVIDERS,
    }


def write_homepage_metrics(metrics: dict[str, int], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUTPUT_FILENAME
    with output_path.open("w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Wrote homepage metrics to %s: %s", output_path, metrics)
    return output_path
