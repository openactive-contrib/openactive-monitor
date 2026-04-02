import json
import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

RPDE_REQUEST_TIMEOUT = 30  # seconds
RPDE_WAIT_BETWEEN_PAGES = 0.1  # seconds

DUMP_TO_FILE = False
OPPORTUNITIES_OUTPUT_DIR = os.getenv("OPPORTUNITIES_OUTPUT_DIR", "./opportunities")


def _build_initial_url(feed_url: str, after_timestamp: str | None, after_id: str | None) -> str:
    """Build initial RPDE URL with optional cursor parameters."""
    if not (after_timestamp and after_id):
        return feed_url

    params = urlencode({"afterTimestamp": after_timestamp, "afterId": after_id})
    separator = "&" if "?" in feed_url else "?"
    return f"{feed_url}{separator}{params}"


def access_feed_url(feed: dict, afterTimestamp: str | None, afterId: str | None) -> dict | None:
    """Traverse all RPDE pages for a feed and save collected data to a JSON file."""
    feed_id = feed["id"]
    feed_url = feed["url"]
    feed_type = feed.get("type", "unknown")

    logger.info("Fetching RPDE feed: %s (%s)", feed_id, feed_type)

    url = _build_initial_url(feed_url, afterTimestamp, afterId)

    Path(OPPORTUNITIES_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(OPPORTUNITIES_OUTPUT_DIR) / f"{feed_id}_{timestamp}.json"

    items: list[dict] = []
    pages_fetched = 0
    status = "COMPLETE"
    session = requests.Session()

    try:
        while url:
            current_url = url
            logger.info("Fetching RPDE url: %s", current_url)
            try:
                response = session.get(current_url, timeout=RPDE_REQUEST_TIMEOUT)
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

            if "items" not in page_data:
                logger.warning("RPDE page missing 'items' key: %s", current_url)
                status = "ERROR"
                break

            page_items = page_data.get("items", [])
            if isinstance(page_items, list):
                items.extend(page_items)
            else:
                logger.warning("RPDE page has non-list 'items': %s", current_url)
                status = "ERROR"
                break
            pages_fetched += 1

            next_url = page_data.get("next")
            if not isinstance(next_url, str) or not next_url:
                url = None
                continue

            # RPDE terminal page: empty items and next equals current page URL.
            if len(page_items) == 0 and next_url == current_url:
                url = None
                continue

            # Guard against infinite self-loop on malformed RPDE pages.
            if next_url == current_url:
                logger.error("RPDE self-loop with non-empty items at %s", current_url)
                status = "ERROR"
                break

            url = next_url
            sleep(RPDE_WAIT_BETWEEN_PAGES)

        payload = {
            "feed_id": feed_id,
            "feed_url": feed_url,
            "items_count": len(items),
            "items": items,
            "status": status,
        }

        if DUMP_TO_FILE:
            dump_to_file(output_file, payload)

        logger.info("Saved %d items from %d pages to %s", len(items), pages_fetched, output_file)

        return {
            "feed_id": feed_id,
            "feed_url": feed_url,
            "items_count": len(items),
            "items": items,
            "status": status,
        }
    except Exception as exc:
        logger.error("Unexpected error fetching feed %s: %s", feed_id, exc, exc_info=True)
        return None
    finally:
        session.close()


def dump_to_file(output_file: Path, payload: dict[str, int | list[dict] | str | Any]):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)

