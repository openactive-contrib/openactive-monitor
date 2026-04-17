import logging
import warnings
from time import sleep

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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

MAX_RETRIES = 6
BACKOFF_FACTOR = 0.3  # 0.3s, 0.6s, 1.2s, 2.4s, 4.8s, 9.6s ...
RETRY_STATUS_FORCELIST = {403, 429, 500, 502, 503, 504}


def build_session() -> requests.Session:
    """Return a Session with retry-capable adapters attached."""
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=tuple(RETRY_STATUS_FORCELIST),
        allowed_methods=["GET"],
        raise_on_status=False,
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
    request_headers = headers or DEFAULT_HEADERS
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

