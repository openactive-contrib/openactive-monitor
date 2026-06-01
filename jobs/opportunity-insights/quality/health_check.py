"""Parallel HTTP probes for feeds whose latest ingestion status was ERROR."""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Literal

import requests

logger = logging.getLogger(__name__)


ProbeKind = Literal["ok", "http_error", "parse_error", "empty"]


@dataclass(frozen=True)
class ProbeResult:
    kind: ProbeKind
    message: str


def probe_feeds(
    feed_url_by_id: dict[str, str],
    max_workers: int,
    timeout_s: float = 10.0,
) -> dict[str, ProbeResult]:
    """GET each feed URL in parallel and classify the result.

    Returns a dict keyed by ``feed_id`` with one ``ProbeResult`` each.

    Classification:
      * ``http_error``  — connection failure, timeout, or HTTP status >= 400.
      * ``parse_error`` — 2xx response but body is not JSON, or JSON is missing
        the RPDE ``items`` key.
      * ``empty``       — 2xx response with valid RPDE page but ``items`` is empty.
      * ``ok``          — 2xx response with parseable JSON containing non-empty ``items``.
    """
    if not feed_url_by_id:
        return {}

    results: dict[str, ProbeResult] = {}
    with ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        future_to_feed = {
            executor.submit(_probe_single, url, timeout_s): feed_id
            for feed_id, url in feed_url_by_id.items()
        }
        for future in as_completed(future_to_feed):
            feed_id = future_to_feed[future]
            try:
                results[feed_id] = future.result()
            except Exception as exc:  # never let one bad probe abort the batch
                logger.exception("Unexpected error probing feed %s", feed_id)
                results[feed_id] = ProbeResult("http_error", f"Probe crashed: {exc.__class__.__name__}")

    logger.info(
        "Probed %d feeds: ok=%d http_error=%d parse_error=%d empty=%d",
        len(results),
        sum(1 for r in results.values() if r.kind == "ok"),
        sum(1 for r in results.values() if r.kind == "http_error"),
        sum(1 for r in results.values() if r.kind == "parse_error"),
        sum(1 for r in results.values() if r.kind == "empty"),
    )
    return results


def _probe_single(url: str, timeout_s: float) -> ProbeResult:
    if not url:
        return ProbeResult("http_error", "Feed URL is empty")
    try:
        resp = requests.get(url, timeout=timeout_s)
    except requests.RequestException as exc:
        return ProbeResult("http_error", f"Network error: {exc.__class__.__name__}")

    if resp.status_code >= 400:
        return ProbeResult("http_error", f"HTTP {resp.status_code} from feed URL")

    try:
        payload = json.loads(resp.text)
    except json.JSONDecodeError:
        return ProbeResult("parse_error", "Invalid JSON in feed response")

    if not isinstance(payload, dict) or "items" not in payload:
        return ProbeResult("parse_error", "Feed response missing 'items' key")

    items = payload.get("items") or []
    if not items:
        return ProbeResult("empty", "Empty feed")

    return ProbeResult("ok", "Feed responded with items")
