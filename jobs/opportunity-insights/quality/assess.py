"""Per-feed data-quality assessment orchestrator.

Builds rows for the ``feed_quality`` BigQuery table by combining:

* Latest ``opportunity_ingestion.status`` (already loaded in ``main.run()``).
* HTTP probes against feed URLs that last ingested with ``status = 'ERROR'``.
* Random-sample-based check for required-field presence in ``json_data``.
* Top-level completeness percentages over the last ``QUALITY_WINDOW_DAYS`` days.
* ``num_future_opportunity_items`` from the feed_insights rows built earlier.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Any

import pandas as pd

import bigquery_ops
from quality import queries as quality_queries
from quality.health_check import ProbeResult, probe_feeds
from quality.version_compliance import (
    FEED_TYPE_TO_SPEC_CATEGORY,
    VERSION_ORDER,
    VERSION_SPECS,
    compute_feed_score,
    get_alternatives,
)

logger = logging.getLogger(__name__)

_EMPTY_VALUES = (None, "", [], {})


def assess_feed_quality(
    run_date: datetime,
    df_feeds: pd.DataFrame,
    df_status: pd.DataFrame,
    feed_rows: list[dict[str, Any]],
    opportunities_tbl: str,
    reference_date: date,
    max_workers: int,
) -> list[dict[str, Any]]:
    """Build one ``feed_quality`` row per feed in ``df_feeds``.

    See module docstring for the inputs each row is derived from.
    """
    logger.info(
        "Assessing data quality for %d feeds (reference_date=%s)",
        len(df_feeds), reference_date.isoformat(),
    )

    future_count_by_feed = {
        row["feed_id"]: int(row.get("num_future_opportunity_items") or 0)
        for row in feed_rows
        if row.get("feed_id")
    }

    status_by_feed = {
        row["feed_id"]: row["status"]
        for _, row in df_status.iterrows()
        if row.get("feed_id")
    }

    completeness_by_key = _fetch_completeness(opportunities_tbl, reference_date)
    samples_by_key, samples_by_kind_key = _fetch_samples(opportunities_tbl, reference_date)

    # Probe any feed whose latest ingestion was ERROR / WARNING, or where the
    # in-memory feed_insights row reports zero future opportunities. The probe
    # tells us whether the feed URL is reachable and whether ``items`` is empty.
    feeds_to_probe = {}
    for _, row in df_feeds.iterrows():
        feed_id = row.get("feed_id")
        if not feed_id:
            continue
        ingestion_status = status_by_feed.get(feed_id)
        future_count = future_count_by_feed.get(feed_id, 0)
        if ingestion_status in ("ERROR", "WARNING") or future_count == 0:
            feeds_to_probe[feed_id] = row.get("feed_url")
    probe_results = probe_feeds(feeds_to_probe, max_workers=max_workers)

    rows: list[dict[str, Any]] = []
    for _, feed in df_feeds.iterrows():
        feed_id = feed.get("feed_id")
        if not feed_id:
            continue
        dataset_url = feed.get("dataset_url")
        key = (dataset_url, feed_id)

        completeness = completeness_by_key.get(key, {})
        ingestion_status = status_by_feed.get(feed_id)
        future_count = future_count_by_feed.get(feed_id, 0)

        # Version detection and scoring from sampled json_data payloads
        feed_type = feed.get("feed_type") or ""
        feed_samples = samples_by_key.get(key, [])
        version_result = compute_feed_score(feed_samples, feed_type_str=feed_type)

        # Detect missing required fields per kind, based on the detected version's spec
        kind_samples = {
            kind: payloads
            for (du, fid, kind), payloads in samples_by_kind_key.items()
            if du == dataset_url and fid == feed_id
        }
        missing_by_kind = _missing_required_by_kind(
            kind_samples,
            detected_version=version_result["version"],
        )

        status, warnings, errors = _classify(
            ingestion_status=ingestion_status,
            probe=probe_results.get(feed_id),
            missing_by_kind=missing_by_kind,
            num_future=future_count,
        )

        grade = _grade(
            status=status,
            num_future=future_count,
            completeness=completeness,
            missing_by_kind=missing_by_kind,
        )


        rows.append({
            "dataset_url":             dataset_url,
            "dataset_name":            feed.get("dataset_name"),
            "feed_id":                 feed_id,
            "feed_type":               feed_type,
            "feed_url":                feed.get("feed_url"),
            "is_regular":              _coerce_bool(feed.get("is_regular")),
            "status":                  status,
            "warnings":                warnings,
            "errors":                  errors,
            "missing_required_fields": missing_by_kind,
            "location_completeness":   _round(completeness.get("location_completeness")),
            "start_date_completeness": _round(completeness.get("start_date_completeness")),
            "end_date_completeness":   _round(completeness.get("end_date_completeness")),
            "activities_completeness": _round(completeness.get("activities_completeness")),
            "facilities_completeness": _round(completeness.get("facilities_completeness")),
            "num_future_opportunity_items": future_count,
            "grade":                   grade,
            "feed_version":            version_result["version"],
            "score":                   version_result["score"],
            "last_assessed":           run_date,
        })

    logger.info("Built %d feed_quality rows", len(rows))
    return rows


# ---------------------------------------------------------------------------
# Data fetchers
# ---------------------------------------------------------------------------

def _fetch_completeness(
    opportunities_tbl: str,
    reference_date: date,
) -> dict[tuple[str | None, str], dict[str, float]]:
    df = bigquery_ops.run_query(
        quality_queries.per_feed_completeness(opportunities_tbl, reference_date)
    )
    out: dict[tuple[str | None, str], dict[str, float]] = {}
    for _, row in df.iterrows():
        key = (row.get("dataset_url"), row.get("feed_id"))
        if not key[1]:
            continue
        out[key] = {
            "location_completeness":   float(row.get("location_completeness") or 0.0),
            "start_date_completeness": float(row.get("start_date_completeness") or 0.0),
            "end_date_completeness":   float(row.get("end_date_completeness") or 0.0),
            "activities_completeness": float(row.get("activities_completeness") or 0.0),
            "facilities_completeness": float(row.get("facilities_completeness") or 0.0),
        }
    return out


def _fetch_samples(
    opportunities_tbl: str,
    reference_date: date,
) -> tuple[
    dict[tuple[str | None, str], list[dict[str, Any]]],
    dict[tuple[str | None, str, str], list[dict[str, Any]]],
]:
    """Fetch sampled json_data payloads per feed and per (feed, kind).

    Returns:
      - samples_by_key: {(dataset_url, feed_id): [payload_dict, ...]}
      - samples_by_kind_key: {(dataset_url, feed_id, kind): [payload_dict, ...]}
    """
    df = bigquery_ops.run_query(
        quality_queries.sampled_opportunities_by_feed_and_kind(
            opportunities_tbl, reference_date
        )
    )

    samples_by_kind_key: dict[tuple[str | None, str, str], list[dict[str, Any]]] = {}
    samples_by_key: dict[tuple[str | None, str], list[dict[str, Any]]] = {}
    for _, row in df.iterrows():
        feed_id = row.get("feed_id")
        kind = row.get("kind")
        if not feed_id or not kind:
            continue
        payload = _coerce_json_payload(row.get("json_data"))
        if payload is None:
            continue
        samples_by_kind_key.setdefault((row.get("dataset_url"), feed_id, kind), []).append(payload)
        samples_by_key.setdefault((row.get("dataset_url"), feed_id), []).append(payload)

    return samples_by_key, samples_by_kind_key


def _missing_required_by_kind(
    kind_samples: dict[str, list[dict[str, Any]]],
    detected_version: str,
) -> dict[str, list[str]]:
    """For each kind in a feed, return required fields that are missing in all sampled payloads.

    Uses ``VERSION_SPECS`` for the kind's spec category at the feed's detected version
    (falling back to the highest version available for that spec category if the
    detected version is not defined for it).
    """
    out: dict[str, list[str]] = {}
    if detected_version in (None, "Unknown"):
        return out

    for kind, payloads in kind_samples.items():
        if not payloads:
            continue
        spec_category = FEED_TYPE_TO_SPEC_CATEGORY.get(kind.strip(), "Event")
        version_specs = VERSION_SPECS.get(spec_category)
        if not version_specs:
            continue

        # Pick the spec for the detected version, or fall back to the highest
        # version available for this category if the detected version is missing
        # (e.g. detected V1.1 but kind is FacilityUse which is V2.0+ only).
        spec = version_specs.get(detected_version)
        if spec is None:
            fallback = max(version_specs.keys(), key=lambda v: VERSION_ORDER.get(v, 0))
            spec = version_specs[fallback]

        required_fields = [p for p, status in spec.items() if status == "required"]
        if not required_fields:
            continue

        missing = []
        for field in required_fields:
            alts = get_alternatives(spec_category, field)
            if not any(
                _is_field_present(payload, field)
                or any(_is_field_present(payload, alt) for alt in alts)
                for payload in payloads
            ):
                missing.append(field)

        if missing:
            out[kind] = missing

    return out


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def _classify(
    ingestion_status: str | None,
    probe: ProbeResult | None,
    missing_by_kind: dict[str, list[str]],
    num_future: int,
) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []

    if ingestion_status == "ERROR":
        if probe is not None and probe.kind in ("http_error", "parse_error", "empty"):
            errors.append(probe.message)
        else:
            errors.append("Data parsing error (invalid JSON or missing 'items')")
        return "ERROR", warnings, errors

    if missing_by_kind:
        fragments = [
            f"{kind}: {', '.join(fields)}"
            for kind, fields in missing_by_kind.items()
        ]
        warnings.append("Missing required fields — " + "; ".join(fragments))

    if ingestion_status == "WARNING":
        if probe is None:
            warnings.append("Ingestion reported WARNING in last run")
        elif probe.kind == "empty":
            _add_unique(warnings, probe.message)
        elif probe.kind in ("http_error", "parse_error"):
            errors.append(probe.message)
        else:
            warnings.append("Ingestion reported WARNING in last run")

    if num_future == 0:
        if probe is not None and probe.kind == "empty":
            _add_unique(warnings, probe.message)
        elif probe is not None and probe.kind in ("http_error", "parse_error"):
            _add_unique(errors, probe.message)
        else:
            _add_unique(warnings, "No future opportunities scheduled")

    if errors:
        return "ERROR", warnings, errors
    if warnings:
        return "WARNING", warnings, errors
    return "OK", warnings, errors


def _add_unique(target: list[str], message: str) -> None:
    if message not in target:
        target.append(message)


def _grade(
    status: str,
    num_future: int,
    completeness: dict[str, float],
    missing_by_kind: dict[str, list[str]],
) -> str | None:
    if num_future == 0 or status in ("WARNING", "ERROR"):
        return None

    loc = completeness.get("location_completeness", 0.0)
    start = completeness.get("start_date_completeness", 0.0)
    acts = completeness.get("activities_completeness", 0.0)
    facs = completeness.get("facilities_completeness", 0.0)

    if (
        num_future > 150
        and loc >= 40 and start >= 40
        and (acts >= 5 or facs >= 5)
        and not missing_by_kind
    ):
        return "Gold"

    if loc >= 25 and start >= 15 and not missing_by_kind:
        return "Silver"

    return "Bronze"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_field_present(payload: dict[str, Any], field: str) -> bool:
    if field not in payload:
        return False
    value = payload[field]
    return value not in _EMPTY_VALUES


def _coerce_json_payload(value: Any) -> dict[str, Any] | None:
    """Normalise a ``json_data`` cell into a Python dict, or ``None`` if unparseable."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _coerce_bool(value: Any) -> bool | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        s = value.strip().lower()
        if s in {"true", "t", "yes", "y", "1"}:
            return True
        if s in {"false", "f", "no", "n", "0"}:
            return False
    return None


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)
