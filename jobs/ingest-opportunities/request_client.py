import logging
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

