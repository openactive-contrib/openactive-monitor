"""One-off backfill: legacy pickles -> BigQuery.

Usage::

    cd jobs/backfill-from-pickles
    python -m venv virt && source virt/bin/activate
    pip install -r requirements.txt
    python main.py --verbose

Run **once** after manually truncating the four target tables. After this
finishes, run ``jobs/ingest-opportunities`` as usual to apply RPDE deltas on
top of the backfilled state.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# This project depends on jobs/ingest-opportunities/ for `processing.py`,
# `bigquery_ops.py`, `rpde.py`, and `geolocation.py`. Add it to sys.path before
# importing anything else from there.
_INGEST_DIR = (Path(__file__).resolve().parent.parent / "ingest-opportunities").as_posix()
if _INGEST_DIR not in sys.path:
    sys.path.insert(0, _INGEST_DIR)

import click
from dotenv import load_dotenv

from feeds_writer import write_feed_ingestion, write_feeds
from opportunities_writer import write_opportunities
from pickle_reader import list_opportunity_pickles, load_feeds_pickles

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_DATA_FEEDS_DIR = Path(__file__).resolve().parent.parent.parent / "volume-1" / "data-feeds"
DEFAULT_DATA_OPPORTUNITIES_DIR = Path(__file__).resolve().parent.parent.parent / "volume-1" / "data-opportunities"


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s [%(processName)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


@click.command()
@click.option("--feeds-only", is_flag=True, default=False,
              help="Only backfill `feeds` and `feed_ingestion`. Skip opportunities.")
@click.option("--opportunities-only", is_flag=True, default=False,
              help="Only backfill `opportunities` and `opportunity_ingestion`. Skip feeds.")
@click.option("--datasets", "dataset_filter", multiple=True,
              help="Optional dataset_url to include. Repeat for multiple.")
@click.option("--data-feeds-dir", default=str(DEFAULT_DATA_FEEDS_DIR), show_default=True,
              type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              help="Path to volume-1/data-feeds/.")
@click.option("--data-opportunities-dir", default=str(DEFAULT_DATA_OPPORTUNITIES_DIR), show_default=True,
              type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              help="Path to volume-1/data-opportunities/.")
@click.option("--max-workers", type=int, default=None,
              help="Override INGEST_MAX_WORKERS env (default: 8 from ingest-opportunities).")
@click.option("--dry-run", is_flag=True, default=False,
              help="Read + group pickles but skip every BigQuery write.")
@click.option("--verbose", is_flag=True, default=False, help="Enable DEBUG logging.")
def cli(
    feeds_only: bool,
    opportunities_only: bool,
    dataset_filter: tuple[str, ...],
    data_feeds_dir: Path,
    data_opportunities_dir: Path,
    max_workers: int | None,
    dry_run: bool,
    verbose: bool,
) -> None:
    if feeds_only and opportunities_only:
        raise click.UsageError("--feeds-only and --opportunities-only are mutually exclusive")

    _configure_logging(verbose)
    logger.info("Backfill start (feeds_only=%s, opportunities_only=%s, dry_run=%s)",
                feeds_only, opportunities_only, dry_run)
    logger.info("data-feeds dir          : %s", data_feeds_dir)
    logger.info("data-opportunities dir  : %s", data_opportunities_dir)

    if max_workers is None:
        max_workers = int(os.getenv("INGEST_MAX_WORKERS", "8"))
    logger.info("max workers             : %d", max_workers)

    # ---- Phase 1: feeds + feed_ingestion ----
    # Always load the feeds pickles (even in --opportunities-only mode) because
    # phase 2 needs the feed_id → dataset_url map to group opportunity pickles
    # without having to decode each one upfront.
    regular, preview = load_feeds_pickles(data_feeds_dir)
    if not opportunities_only:
        if regular is None and preview is None:
            logger.error("No feeds pickles found — aborting feeds phase")
        elif dry_run:
            r_count = len(regular.feeds) if regular else 0
            p_count = len(preview.feeds) if preview else 0
            logger.info("[dry-run] would write %d feeds rows (regular=%d, preview=%d) + 1 feed_ingestion row",
                        r_count + p_count, r_count, p_count)
        else:
            write_feeds(regular, preview)
            write_feed_ingestion(regular, preview)

    # ---- Phase 2: opportunities + opportunity_ingestion ----
    if not feeds_only:
        # Build feed_id → {dataset_url, type} from the feeds pickles. The type
        # is needed so we can split each dataset's pickles into the two
        # processing batches (FacilityUse/IndividualFacilityUse/Slot first,
        # then everything else) without having to decode any opportunities
        # pickle ahead of time.
        feed_info: dict[str, dict[str, str]] = {}
        for src in (regular, preview):
            if src is None:
                continue
            for feed in src.feeds:
                if not isinstance(feed, dict):
                    continue
                fid = feed.get("id")
                durl = feed.get("dataset_url")
                if fid and durl:
                    feed_info[fid] = {"dataset_url": durl, "type": feed.get("type") or ""}
        logger.info("Built feed_id → {dataset_url, type} map (%d entries)", len(feed_info))

        pickles = list_opportunity_pickles(data_opportunities_dir)
        logger.info("Discovered %d opportunity pickles", len(pickles))
        if dry_run:
            from collections import Counter
            scope_counts = Counter(("regular" if p.is_regular else "preview") for p in pickles)
            status_counts = Counter(p.status for p in pickles)
            logger.info("[dry-run] scopes=%s, statuses=%s", dict(scope_counts), dict(status_counts))
        else:
            summary = write_opportunities(
                pickles=pickles,
                max_workers=max_workers,
                feed_info=feed_info,
                dataset_filter=set(dataset_filter) if dataset_filter else None,
            )
            logger.info("Opportunities backfill summary: %s", summary)

    logger.info("Backfill complete")


if __name__ == "__main__":
    cli()
