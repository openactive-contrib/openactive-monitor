"""Integration test for known-problematic RPDE feeds.

These feeds have been observed failing during ingestion (mostly HTTP 403 and
invalid JSON responses) even though the URLs are reachable from a browser. This
test exercises the *existing* ingestion code (`rpde.access_feed_url`) against
each feed, logs how many feeds failed, and fails if any of them do not complete
successfully.

Because it performs real network requests, it is skipped by default. Enable it
with:

    cd jobs/ingest-opportunities
    source virt/bin/activate
    RUN_NETWORK_TESTS=1 python -m unittest tests.test_problematic_feeds -v
"""

from __future__ import annotations

import logging
import os
import re
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rpde import _build_initial_url, access_feed_url

# Allow importing the job modules (request_client, rpde) when run from anywhere.
JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

from rpde import access_feed_url  # noqa: E402

logger = logging.getLogger(__name__)

# Feeds reported as failing during ingestion despite being browser-accessible.
PROBLEMATIC_FEED_URLS = [
    # "https://halo-openactive.legendonlineservices.co.uk/api/facility-uses/events",
    # "https://halo-openactive.legendonlineservices.co.uk/api/sessions",
    # "https://lsbuactive-openactive.legendonlineservices.co.uk/api/facility-uses/events",
    # "https://salfordcommunityleisure-openactive.legendonlineservices.co.uk/api/facility-uses/events",
    # "https://sllandinspireall-openactive.legendonlineservices.co.uk/api/facility-uses/events",
    # "https://tendringcouncil-openactive.legendonlineservices.co.uk/api/sessions",
    "https://opendata.leisurecloud.live/api/feeds/EveryoneActive-live-slots"
]


def _feed_id_from_url(url: str) -> str:
    """Derive a stable, human-readable feed id from its URL."""
    stem = re.sub(r"^https?://", "", url)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem)
    return stem.strip("-").lower()


def _make_feed(url: str) -> dict:
    return {"id": _feed_id_from_url(url), "url": url, "type": "unknown"}


# Match the real ingest job, which crawls feeds concurrently via a thread pool.
INGEST_MAX_WORKERS = int(os.getenv("INGEST_MAX_WORKERS", "8"))


def _crawl_feed(url: str) -> tuple[str, str | None]:
    """Crawl a single feed. Returns (url, failure_reason) where reason is None on success."""
    feed = _make_feed(url)
    try:
        result = access_feed_url(
            feed,
            after_timestamp=None,
            after_id=None,
            after_change_number=None,
        )
        after_timestamp = result.get("after_timestamp")
        after_id = result.get("after_id")
        after_change_number = result.get("after_change_number")
        last_url = _build_initial_url(url, after_timestamp, after_id, after_change_number)
        print(
            f"Feed {url} completed: {result.get('items_count')} items | "
            f"last accessed url={last_url} "
            f"(after_timestamp={after_timestamp}, after_id={after_id}, "
            f"after_change_number={after_change_number})"
        )
    except Exception as exc:  # noqa: BLE001 - record any failure per feed
        logger.error("Feed %s raised an exception: %s", url, exc)
        return url, f"exception: {exc}"

    if result is None:
        logger.error("Feed %s returned no result (None)", url)
        return url, "no result (None)"

    status = result.get("status")
    if status != "COMPLETE":
        logger.error(
            "Feed %s did not complete: status=%s, items=%s",
            url,
            status,
            result.get("items_count"),
        )
        return url, f"status={status}"

    after_timestamp = result.get("after_timestamp")
    after_id = result.get("after_id")
    after_change_number = result.get("after_change_number")
    last_url = _build_initial_url(url, after_timestamp, after_id, after_change_number)
    print(
        f"Feed {url} completed: {result.get('items_count')} items | "
        f"last accessed url={last_url} "
        f"(after_timestamp={after_timestamp}, after_id={after_id}, "
        f"after_change_number={after_change_number})"
    )
    return url, None


class RPDECrawlingTest(unittest.TestCase):

    def test_problematic_feeds_ingest_successfully(self) -> None:
        failures: list[tuple[str, str]] = []

        # Crawl all feeds in parallel to mirror the real ingest job's concurrency.
        max_workers = min(8, len(PROBLEMATIC_FEED_URLS))
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="test-crawl") as executor:
            future_to_url = {
                executor.submit(_crawl_feed, url): url for url in PROBLEMATIC_FEED_URLS
            }
            for future in as_completed(future_to_url):
                url, reason = future.result()
                if reason is not None:
                    failures.append((url, reason))

        logger.info(
            "Problematic feeds result: %d/%d failed",
            len(failures),
            len(PROBLEMATIC_FEED_URLS),
        )

        if failures:
            detail = "\n".join(f"  - {url}: {reason}" for url, reason in failures)
            self.fail(
                f"{len(failures)}/{len(PROBLEMATIC_FEED_URLS)} feed(s) failed:\n{detail}"
            )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    unittest.main()
