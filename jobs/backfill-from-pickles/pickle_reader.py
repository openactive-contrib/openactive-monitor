"""Read legacy pickle files and yield records ready for the backfill writers.

The legacy pipelines stored:
- ``volume-1/data-feeds/{regular,preview}-feeds--timeFinish-…--numFeeds-…--numDatasets-…*.pickle``:
  one file per catalogue (regular vs preview), each a ``list[dict]`` of feed dicts.
- ``volume-1/data-opportunities/{regular,preview}-ops--<feed_id>--…*.pickle.gzip``:
  one gzipped pickle per feed, each a ``dict`` containing ``items``, ``feed``,
  ``status``, ``next_url`` etc.

This module parses the filenames + payloads into a normalised shape the
backfill writers consume.
"""

from __future__ import annotations

import gzip
import logging
import pickle
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterator

logger = logging.getLogger(__name__)

# regular-feeds--timeFinish-2026-05-07-00-03-05-472730-UTC--timeTaken-160-318566--numFeeds-470--numDatasets-170.pickle
_FEEDS_FILENAME_RE = re.compile(
    r"^(?P<scope>regular|preview)-feeds"
    r"--timeFinish-(?P<ts>\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+-UTC)"
    r"--timeTaken-(?P<taken>[\d-]+)"
    r"--numFeeds-(?P<num_feeds>\d+)"
    r"--numDatasets-(?P<num_datasets>\d+)"
    r"\.pickle$"
)

# regular-ops--<feed_id>--timeFinish-…--timeTaken-…--numItems-…--numUrls-…--status-….pickle.gzip
_OPPS_FILENAME_RE = re.compile(
    r"^(?P<scope>regular|preview)-ops"
    r"--(?P<feed_id>.+?)"
    r"--timeFinish-(?P<ts>\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+-UTC)"
    r"--timeTaken-[\d-]+"
    r"--numItems-(?P<num_items>\d+)"
    r"--numUrls-(?P<num_urls>\d+)"
    r"--status-(?P<status>COMPLETE|ERROR|WARNING|TIMEOUT)"
    r"\.pickle\.gzip$"
)


def _parse_time_finish(ts_str: str) -> datetime:
    """Parse `2026-05-07-00-03-05-472730-UTC` into a UTC-aware datetime."""
    parts = ts_str.removesuffix("-UTC").split("-")
    if len(parts) != 7:
        raise ValueError(f"Unrecognised timeFinish string: {ts_str!r}")
    y, mo, d, h, mi, s, micro = (int(p) for p in parts)
    return datetime(y, mo, d, h, mi, s, micro, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Feeds pickles
# ---------------------------------------------------------------------------

@dataclass
class FeedsPickle:
    path: Path
    is_regular: bool
    time_finish: datetime
    num_feeds: int
    num_datasets: int
    feeds: list[dict]   # list of feed dicts (from pickle.load)


def load_feeds_pickles(data_feeds_dir: Path) -> tuple[FeedsPickle | None, FeedsPickle | None]:
    """Find the latest timestamped regular and preview feeds pickles and load them.

    The legacy job also writes ``regular-feeds.pickle`` / ``preview-feeds.pickle``
    as 0-byte symlinks; we ignore those and pick the most-recent timestamped file
    so we know exactly which catalogue snapshot we're loading.
    """
    regular = _latest_feeds_pickle(data_feeds_dir, scope="regular")
    preview = _latest_feeds_pickle(data_feeds_dir, scope="preview")
    return regular, preview


def _latest_feeds_pickle(data_feeds_dir: Path, scope: str) -> FeedsPickle | None:
    candidates: list[tuple[datetime, Path, dict]] = []
    for path in data_feeds_dir.iterdir():
        if not path.is_file() or path.suffix != ".pickle":
            continue
        m = _FEEDS_FILENAME_RE.match(path.name)
        if not m or m.group("scope") != scope:
            continue
        candidates.append((_parse_time_finish(m.group("ts")), path, m.groupdict()))
    if not candidates:
        logger.warning("No %s feeds pickle found in %s", scope, data_feeds_dir)
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    ts, path, meta = candidates[0]
    with path.open("rb") as f:
        feeds = pickle.load(f)
    if not isinstance(feeds, list):
        raise TypeError(f"Expected list in {path.name}, got {type(feeds).__name__}")
    logger.info("Loaded %s feeds pickle: %s (%d feeds)", scope, path.name, len(feeds))
    return FeedsPickle(
        path=path,
        is_regular=(scope == "regular"),
        time_finish=ts,
        num_feeds=int(meta["num_feeds"]),
        num_datasets=int(meta["num_datasets"]),
        feeds=feeds,
    )


# ---------------------------------------------------------------------------
# Opportunities pickles
# ---------------------------------------------------------------------------

@dataclass
class OpportunityPickle:
    path: Path
    is_regular: bool
    feed_id: str            # parsed from filename; should match payload['feed']['id']
    time_finish: datetime
    num_items: int
    num_urls: int
    status: str
    _payload: dict | None = field(default=None, repr=False)

    def load(self) -> dict:
        """Lazily decode the gzipped pickle. Cached after first call.

        Reads the whole compressed file then decompresses in one shot — this is
        typically 2–3× faster than streaming through ``gzip.open`` for large files
        because it lets the C zlib code work in one big buffer instead of being
        driven from Python in 8 KiB chunks.
        """
        if self._payload is None:
            with open(self.path, "rb") as raw:
                compressed = raw.read()
            self._payload = pickle.loads(gzip.decompress(compressed))
        return self._payload

    def release(self) -> None:
        """Drop cached payload to free memory once the dataset is written."""
        self._payload = None


def iter_opportunity_pickles(data_opportunities_dir: Path) -> Iterator[OpportunityPickle]:
    for path in sorted(data_opportunities_dir.iterdir()):
        if not path.is_file() or not path.name.endswith(".pickle.gzip"):
            continue
        m = _OPPS_FILENAME_RE.match(path.name)
        if not m:
            logger.warning("Skipping unrecognised opportunities filename: %s", path.name)
            continue
        yield OpportunityPickle(
            path=path,
            is_regular=(m.group("scope") == "regular"),
            feed_id=m.group("feed_id"),
            time_finish=_parse_time_finish(m.group("ts")),
            num_items=int(m.group("num_items")),
            num_urls=int(m.group("num_urls")),
            status=m.group("status"),
        )


def list_opportunity_pickles(data_opportunities_dir: Path) -> list[OpportunityPickle]:
    """Eager variant — handy for grouping by dataset before dispatching workers."""
    return list(iter_opportunity_pickles(data_opportunities_dir))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def date_from_time_finish(ts: datetime) -> date:
    return ts.date()
