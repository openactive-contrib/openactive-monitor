import json
import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from request_client import build_session, get

logger = logging.getLogger(__name__)

RPDE_REQUEST_TIMEOUT = 30  # seconds
RPDE_WAIT_BETWEEN_PAGES = 0.1  # seconds

# for debugging and development
DUMP_TO_FILE = True
OPPORTUNITIES_OUTPUT_DIR = os.getenv("OPPORTUNITIES_OUTPUT_DIR", "./opportunities")


def _build_initial_url(feed_url: str, after_timestamp: str | None, after_id: str | None) -> str:
    """Build initial RPDE URL with optional cursor parameters."""
    if not (after_timestamp and after_id):
        return feed_url

    params = urlencode({"afterTimestamp": after_timestamp, "afterId": after_id})
    separator = "&" if "?" in feed_url else "?"
    return f"{feed_url}{separator}{params}"


def _extract_cursor_from_url(url: str) -> tuple[str | None, str | None]:
    """Extract RPDE cursor values from a page URL query string."""
    query = parse_qs(urlparse(url).query)
    after_timestamp = query.get("afterTimestamp", [None])[0]
    after_id = query.get("afterId", [None])[0]
    return after_timestamp, after_id


def access_feed_url(feed: dict, after_timestamp: str | None, after_id: str | None) -> dict | None:
    """
        Traverse all RPDE pages for a feed and returns the collected data information.
        Args:
            feed: Dictionary containing feed information, must include 'id' and 'url' keys.
            after_timestamp: Optional RPDE cursor parameter for incremental fetching.
            after_id: Optional RPDE cursor parameter for incremental fetching.
        Returns:
            Dictionary with feed_id, feed_url, items_count, items list, and status. Returns None if an unexpected error occurs.
    """
    feed_id = feed["id"]
    feed_url = feed["url"]

    logger.debug("Fetching RPDE feed: %s (%s)", feed_id, feed.get("type", "unknown"))

    url = _build_initial_url(feed_url, after_timestamp, after_id)

    items: list[dict] = []
    pages_fetched = 0
    status = "COMPLETE"
    session = build_session()
    last_after_timestamp: str | None = None
    last_after_id: str | None = None

    try:
        while url:
            current_url = url
            page_after_timestamp, page_after_id = _extract_cursor_from_url(current_url)
            if page_after_timestamp and page_after_id:
                last_after_timestamp = page_after_timestamp
                last_after_id = page_after_id
            logger.debug("Fetching RPDE url: %s", current_url)
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

            if is_terminal_page(current_url, next_url, page_items):
                url = None
                continue

            # Guard against infinite self-loop on malformed RPDE pages.
            if next_url == current_url:
                logger.error("RPDE self-loop with non-empty items at %s", current_url)
                status = "ERROR"
                break

            url = next_url
            sleep(RPDE_WAIT_BETWEEN_PAGES)

        result = {
            "feed_id": feed_id,
            "feed_url": feed_url,
            "items_count": len(items),
            "items": items,
            "status": status,
            "after_timestamp": last_after_timestamp,
            "after_id": last_after_id,
        }

        if DUMP_TO_FILE:
            output_file = dump_to_file(feed_id, result)
            logger.debug("Saved %d items from %d pages to %s", len(items), pages_fetched, output_file)

        logger.info("Completed feed %s: %d items ingested with [%s]",feed["id"], result["items_count"], result["status"],)
        return result
    except Exception as exc:
        logger.error("Unexpected error fetching feed %s: %s", feed_id, exc, exc_info=True)
        return None
    finally:
        session.close()


def is_terminal_page(current_url: str | Any, next_url: str, page_items: list) -> bool | Any:
    """
        Determine if the current RPDE page is a terminal page indicating the end of the feed.
        A terminal page is defined as one where the 'next' URL is the same as the current URL and there are no items.
    Args:
        current_url: The URL of the current RPDE page being processed.
        next_url: The URL provided in the 'next' field of the RPDE response for the current page.
        page_items: 'items' list from the current RPDE page response.

    Returns:
        True if the current page is a terminal page (indicating end of feed), False otherwise.
    """
    return len(page_items) == 0 and next_url == current_url


def dump_to_file(feed_id: str, payload: dict[str, int | list[dict] | str | Any]):
    Path(OPPORTUNITIES_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(OPPORTUNITIES_OUTPUT_DIR) / f"{feed_id}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return output_file
