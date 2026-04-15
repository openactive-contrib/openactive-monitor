import json
import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import requests
from request_client import build_session, get

logger = logging.getLogger(__name__)

RPDE_REQUEST_TIMEOUT = 30  # seconds
RPDE_WAIT_BETWEEN_PAGES = 0  # seconds

# for debugging and development
OPPORTUNITIES_OUTPUT_DIR = os.getenv("OPPORTUNITIES_OUTPUT_DIR", "./opportunities")


def _build_initial_url(
    feed_url: str,
    after_timestamp: str | None,
    after_id: str | None,
    after_change_number: int | None,
) -> str:
    """Build initial RPDE URL with optional cursor parameters."""
    if after_change_number is not None:
        params = urlencode({"afterChangeNumber": after_change_number})
    elif after_timestamp and after_id:
        params = urlencode({"afterTimestamp": after_timestamp, "afterId": after_id})
    else:
        return feed_url

    separator = "&" if "?" in feed_url else "?"
    return f"{feed_url}{separator}{params}"


def _extract_cursor_from_url(url: str) -> tuple[str | None, str | None, int | None]:
    """Extract RPDE cursor values from a page URL query string."""
    query = parse_qs(urlparse(url).query)
    after_timestamp = query.get("afterTimestamp", [None])[0]
    after_id = query.get("afterId", [None])[0]
    raw_after_change_number = query.get("afterChangeNumber", [None])[0]

    try:
        after_change_number = int(raw_after_change_number) if raw_after_change_number not in (None, "") else None
    except (TypeError, ValueError):
        logger.warning("Invalid afterChangeNumber in RPDE URL %s", url)
        after_change_number = None

    return after_timestamp, after_id, after_change_number


def access_feed_url(
    feed: dict,
    after_timestamp: str | None,
    after_id: str | None,
    after_change_number: int | None,
    persist_data: bool = False,
) -> dict | None:
    """
        Traverse all RPDE pages for a feed and returns the collected data information.
        Args:
            feed: Dictionary containing feed information, must include 'id' and 'url' keys.
            after_timestamp: Optional RPDE cursor parameter for incremental fetching.
            after_id: Optional RPDE cursor parameter for incremental fetching.
            after_change_number: Optional RPDE cursor parameter for incremental fetching for feeds using afterChangeNumber.
            persist_data: Whether to persist the fetched items to a file for debugging purposes. Defaults to False.
        Returns:
            Dictionary with feed_id, feed_url, items_count, items list, and status. Returns None if an unexpected error occurs.
    """
    feed_id = feed["id"]
    feed_url = feed["url"]

    logger.debug("Fetching RPDE feed: %s (%s)", feed_id, feed.get("type", "unknown"))

    url = _build_initial_url(feed_url, after_timestamp, after_id, after_change_number)

    items: list[dict] = []
    pages_fetched = 0
    status = "COMPLETE"
    session = build_session()
    last_after_timestamp: str | None = None
    last_after_id: str | None = None
    last_after_change_number: int | None = None

    try:
        while url:
            current_url = url
            page_after_timestamp, page_after_id, page_after_change_number = _extract_cursor_from_url(current_url)
            if page_after_change_number is not None:
                last_after_change_number = page_after_change_number
                last_after_timestamp = None
                last_after_id = None
            elif page_after_timestamp and page_after_id:
                last_after_timestamp = page_after_timestamp
                last_after_id = page_after_id
                last_after_change_number = None
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

            # Resolve relative next URLs (e.g. "/api/feed?afterTimestamp=123") against the current page URL.
            next_url = urljoin(current_url, next_url)

            if is_terminal_page(current_url, next_url, page_items):
                url = None
                continue

            # Guard against infinite self-loop on malformed RPDE pages.
            if next_url == current_url:
                logger.error("RPDE self-loop with non-empty items at %s", current_url)
                status = "WARNING"
                break
            if len(page_items) == 0:
                logger.error("RPDE malformed self-loop without items %s", current_url)
                status = "WARNING"
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
            "after_change_number": last_after_change_number,
        }

        if persist_data:
            output_file = dump_to_file(feed_id, result)
            logger.debug("Saved %d items from %d pages to %s", len(items), pages_fetched, output_file)

        logger.info("Completed feed %s: %d items ingested with [%s]",feed["id"], result["items_count"], result["status"],)
        return result
    except Exception as exc:
        logger.error("Unexpected error fetching feed %s: %s", feed_id, exc, exc_info=True)
        raise RuntimeError(f"RPDE returned no result for feed {feed_id}")
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
