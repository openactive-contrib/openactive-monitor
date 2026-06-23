"""Debug helper: crawl a single RPDE feed and dump all of its data to one JSON file.

Set the `feed_url` variable in `main()` to the RPDE feed endpoint you want to
inspect. The script traverses every page of the feed (following the `next`
cursor) and writes the collected items into separate part files, flushing a new
file every 100 pages:

    jobs/ingest-opportunities/debug/<sanitised-feed-url>_part0001.json
    jobs/ingest-opportunities/debug/<sanitised-feed-url>_part0002.json
    ...

Usage:
    cd jobs/ingest-opportunities
    source virt/bin/activate
    python patches/debug_crawl_feed.py
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from time import sleep
from urllib.parse import urljoin

import requests

# Allow importing the job modules (request_client, rpde) when run from anywhere.
JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

from request_client import build_session, get  # noqa: E402
from rpde import RPDE_REQUEST_TIMEOUT, RPDE_WAIT_BETWEEN_PAGES, is_terminal_page  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

DEBUG_OUTPUT_DIR = JOB_ROOT / "debug"

# Flush the collected items to a separate file after this many pages.
PAGES_PER_FILE = 100


def sanitise_filename(url: str) -> str:
    """Turn a feed URL into a filesystem-safe filename stem."""
    stem = re.sub(r"^https?://", "", url)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem)
    return stem.strip("_") or "feed"


def _write_part(output_dir: Path, stem: str, part: int, feed_url: str, items: list[dict]) -> Path:
    """Write a batch of collected items to its own part file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{stem}_part{part:04d}.json"
    payload = {
        "feed_url": feed_url,
        "part": part,
        "items_count": len(items),
        "items": items,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("Wrote %d items to %s", len(items), output_file)
    return output_file


def crawl_feed(feed_url: str, output_dir: Path, stem: str) -> dict:
    """Traverse all RPDE pages for `feed_url`, writing a part file every PAGES_PER_FILE pages."""
    logger.info("Start crawling RPDE feed: %s", feed_url)

    buffer: list[dict] = []
    pages_fetched = 0
    pages_in_buffer = 0
    total_items = 0
    part = 1
    part_files: list[str] = []
    status = "COMPLETE"
    session = build_session()
    url: str | None = feed_url

    try:
        while url:
            current_url = url
            logger.info("Fetching page %d: %s", pages_fetched + 1, current_url)
            try:
                response = get(session, current_url, timeout=RPDE_REQUEST_TIMEOUT)
                response.raise_for_status()
            except requests.RequestException as exc:
                logger.error("Failed to fetch %s: %s", current_url, exc)
                status = "ERROR"
                break

            try:
                page_data = response.json()
            except json.JSONDecodeError as exc:
                logger.error("Failed to parse JSON from %s: %s", current_url, exc)
                status = "ERROR"
                break

            page_items = page_data.get("items")
            if not isinstance(page_items, list):
                logger.warning("RPDE page missing/invalid 'items': %s", current_url)
                status = "ERROR"
                break

            buffer.extend(page_items)
            total_items += len(page_items)
            pages_fetched += 1
            pages_in_buffer += 1

            # Flush a separate file every PAGES_PER_FILE pages.
            if pages_in_buffer >= PAGES_PER_FILE:
                part_files.append(str(_write_part(output_dir, stem, part, feed_url, buffer)))
                part += 1
                buffer = []
                pages_in_buffer = 0

            next_url = page_data.get("next")
            if not isinstance(next_url, str) or not next_url:
                break

            next_url = urljoin(current_url, next_url)

            if is_terminal_page(current_url, next_url, page_items):
                break

            if next_url == current_url:
                logger.error("RPDE self-loop with non-empty items at %s", current_url)
                status = "WARNING"
                break

            url = next_url
            sleep(RPDE_WAIT_BETWEEN_PAGES)

        # Flush any remaining items that didn't fill a complete batch.
        if buffer:
            part_files.append(str(_write_part(output_dir, stem, part, feed_url, buffer)))

        logger.info("Crawled %d pages, collected %d items across %d file(s) [%s]",
                    pages_fetched, total_items, len(part_files), status)
        return {
            "feed_url": feed_url,
            "pages_fetched": pages_fetched,
            "items_count": total_items,
            "status": status,
            "part_files": part_files,
        }
    finally:
        session.close()


def main() -> None:
    # Set the RPDE feed URL you want to crawl here.
    feed_url = "https://loughboroughuniversity-openactive.legendonlineservices.co.uk/api/facility-uses/events"

    stem = sanitise_filename(feed_url)
    result = crawl_feed(feed_url, DEBUG_OUTPUT_DIR, stem)

    logger.info("Saved %d items across %d file(s) under %s",
                result["items_count"], len(result["part_files"]), DEBUG_OUTPUT_DIR)


if __name__ == "__main__":
    main()

