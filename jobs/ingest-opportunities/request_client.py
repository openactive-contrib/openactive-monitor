import json
import logging
import random
import warnings
from time import sleep
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    # RPDE feeds serve JSON. Advertising a JSON Accept avoids WAF/CDN rules that
    # block or serve HTML challenge pages to clients claiming to want text/html.
    "Accept": "application/json, text/plain;q=0.9, */*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

MAX_RETRIES = 5
# Higher base backoff so throttled/WAF-guarded hosts get real cool-down time:
# ~1s, 2s, 4s, 8s, 16s, 32s (capped by BACKOFF_MAX), plus jitter.
BACKOFF_FACTOR = 1.0
BACKOFF_MAX = 20.0  # seconds; cap per-attempt sleep so a run can't stall for minutes
BACKOFF_JITTER = 1.0  # seconds of random jitter added per attempt to de-sync workers
RETRY_STATUS_FORCELIST = {403, 429, 500, 502, 503, 504}


def _origin_headers(url: str) -> dict[str, str]:
    """Browser-like Referer/Origin headers derived from the target URL.

    Some hosts behind a WAF reject API requests that arrive without a plausible
    same-origin Referer/Origin, returning 403. Setting them to the feed's own
    origin mimics a same-site fetch.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {}
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return {"Referer": f"{origin}/", "Origin": origin}


def build_session() -> requests.Session:
    """Return a Session with retry-capable adapters attached."""
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        backoff_max=BACKOFF_MAX,
        backoff_jitter=BACKOFF_JITTER,
        status_forcelist=tuple(RETRY_STATUS_FORCELIST),
        allowed_methods=["GET"],
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get(
    session: requests.Session,
    url: str,
    timeout: int,
    headers: dict[str, str] | None = None,
) -> requests.Response:
    """GET with browser-like headers. Retries handled by session adapter."""
    request_headers = {**DEFAULT_HEADERS, **_origin_headers(url)}
    if headers:
        request_headers.update(headers)
    try:
        return session.get(url, headers=request_headers, timeout=timeout, verify=True)
    except requests.exceptions.SSLError:
        # Fallback: retry without cert verification for problematic hosts
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)
            return session.get(url, headers=request_headers, timeout=timeout, verify=False)


def _backoff_delay(attempt: int) -> float:
    """Backoff delay for a given (1-based) retry attempt, mirroring the adapter.

    Matches the session Retry config: exponential growth from BACKOFF_FACTOR,
    capped at BACKOFF_MAX, plus random jitter to de-synchronise parallel workers.
    """
    delay = BACKOFF_FACTOR * (2 ** (attempt - 1))
    delay = min(delay, BACKOFF_MAX)
    return delay + random.uniform(0, BACKOFF_JITTER)


def get_json_with_retry(
    session: requests.Session,
    url: str,
    timeout: int,
    max_attempts: int = MAX_RETRIES,
) -> dict:
    """GET a URL and parse its JSON body, retrying transient failures.

    HTTP status failures (e.g. 403/429/5xx) are retried by the session adapter.
    This adds application-level retries for responses that arrive with a success
    status but a body that is not valid JSON - typically WAF/CDN challenge HTML
    pages served with 200 - re-fetching with backoff between attempts.

    Returns the parsed JSON. Raises the last exception (JSON decode error or an
    ``HTTPError`` from ``raise_for_status``) if every attempt fails.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        response = get(session, url, timeout=timeout)
        response.raise_for_status()
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            last_exc = exc
            snippet = response.text[:200].replace("\n", " ") if response.text else ""
            logger.warning(
                "Invalid JSON (attempt %d/%d) from %s (content-type=%s): %s | body: %s",
                attempt,
                max_attempts,
                url,
                response.headers.get("Content-Type", "unknown"),
                exc,
                snippet,
            )
            if attempt < max_attempts:
                sleep(_backoff_delay(attempt))

    assert last_exc is not None
    raise last_exc


def get_json(session: requests.Session, url: str, timeout: int) -> dict | None:
    """GET JSON from URL. Returns None on HTTP or JSON parse failure."""
    try:
        response = get(session, url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        logger.warning("HTTP %s fetching: %s", exc.response.status_code, url)
        return None
    except ValueError:
        logger.warning("Failed to parse JSON from: %s", url)
        return None
    except Exception:
        logger.warning("Failed to fetch: %s", url, exc_info=True)
        return None


def get_text(session: requests.Session, url: str, timeout: int) -> str | None:
    """GET text from URL. Returns None on HTTP failure."""
    try:
        response = get(session, url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as exc:
        logger.warning("HTTP %s fetching: %s", exc.response.status_code, url)
        return None
    except Exception:
        logger.warning("Failed to fetch: %s", url, exc_info=True)
        return None

