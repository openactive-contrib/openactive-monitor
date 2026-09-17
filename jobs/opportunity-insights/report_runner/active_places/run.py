"""Ad-hoc report: what percentage of Active Places sites are in the OpenActive data?

Standalone — not part of the opportunity-insights main flow. Reads the Sport
England Active Places export from disk and the `opportunities` table from
BigQuery, matches the two spatially, and writes CSV mapping tables plus a
markdown coverage report.

Run with:
    cd jobs/opportunity-insights
    python -m report_runner.active_places.run --verbose
"""

from __future__ import annotations

import logging
from pathlib import Path

import click
import numpy as np
import pandas as pd

import bigquery_ops

from . import analysis, centroids, matching, oa_data, report, venues as venues_module
from .ap_data import load_active_places_sites, load_place_tokens, read_data_version

logger = logging.getLogger(__name__)

JOB_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = JOB_ROOT / "data" / "active_places"
DEFAULT_OUTPUT_DIR = JOB_ROOT / "reports" / "active_places"

REPORT_FILENAME = "active_places_coverage.md"


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _write_csv(frame: pd.DataFrame, output_dir: Path, filename: str) -> None:
    path = output_dir / filename
    frame.to_csv(path, index=False)
    logger.info("Wrote %s (%d rows)", path, len(frame))


def _resolve_coordinate_provenance(points: pd.DataFrame, codepoint_dir: Path | None) -> pd.DataFrame:
    """Mark points whose coordinates are really a postcode centroid, and key them.

    Snapping a point to Code-Point Open does two jobs at once: it flags that the
    coordinates were geocoded from a postcode rather than surveyed, and it recovers
    which postcode that was, filling in the matching key where the feed declared
    none. When Code-Point Open is unavailable the flag is False and the key falls
    back to the declared postcode alone, rather than the run failing.
    """
    codepoint_dir = codepoint_dir or centroids.default_codepoint_dir()
    if codepoint_dir is None:
        logger.warning(
            "Code-Point Open not found (install `uklookup` or pass --codepoint-dir); "
            "skipping the coordinate-provenance diagnostic"
        )
        return points.assign(
            is_centroid_derived=False,
            centroid_diagnostic=False,
            postcode_key=matching.normalise_postcode(points["postal_code"]),
        )

    index = centroids.load_centroid_index(Path(codepoint_dir))
    x, y = matching.to_bng(points["lat"].values, points["lng"].values)
    flags, recovered = centroids.snap_to_centroids(x, y, index)
    logger.info(
        "%d of %d points (%.1f%%) sit on a postcode centroid",
        flags.sum(), len(flags), 100 * flags.mean() if len(flags) else 0.0,
    )
    # A recovered centroid postcode fills the gap where the feed declared none.
    declared = matching.normalise_postcode(points["postal_code"])
    key = declared.fillna(pd.Series(matching.normalise_postcode(pd.Series(recovered)).values,
                                    index=points.index))
    logger.info(
        "Postcode key available for %d of %d points (%.1f%%): %d declared, %d recovered from a centroid",
        key.notna().sum(), len(key), 100 * key.notna().mean() if len(key) else 0.0,
        declared.notna().sum(), int((declared.isna() & key.notna()).sum()),
    )
    return points.assign(is_centroid_derived=flags, centroid_diagnostic=True, postcode_key=key)


def run(data_dir: Path,
        output_dir: Path,
        buffer_metres: float,
        cluster_metres: float,
        points_cache: Path | None = None,
        codepoint_dir: Path | None = None,
        postcode_max_metres: float = 1000.0,
        name_max_metres: float = 500.0,
        name_threshold: float = 0.8) -> None:
    """Build the coverage report end to end."""
    sites = load_active_places_sites(data_dir)
    data_version = read_data_version(data_dir)

    if points_cache and points_cache.exists():
        logger.info("Reading cached OpenActive points from %s", points_cache)
        raw_points = pd.read_parquet(points_cache)
    else:
        raw_points = oa_data.fetch_oa_points()
        if points_cache:
            raw_points.to_parquet(points_cache)
            logger.info("Cached OpenActive points to %s", points_cache)

    england_points, scope_counts = oa_data.split_by_scope(raw_points)
    england_points = _resolve_coordinate_provenance(england_points, codepoint_dir)
    venue_frame, diameters = venues_module.build_venues(england_points, cluster_metres)

    site_xy = matching.to_bng(sites["lat"].values, sites["long"].values)
    venue_xy = (venue_frame["x"].values, venue_frame["y"].values)
    spatial_pairs = matching.match_within(site_xy, venue_xy, buffer_metres)
    postcode_pairs = matching.match_by_postcode(
        sites["Postcode"], venue_frame["oa_postcode_key"], site_xy, venue_xy, postcode_max_metres,
    )
    pairs = matching.combine_channels(
        spatial_pairs, postcode_pairs, venue_frame["is_centroid_derived"].to_numpy()
    )
    # Last resort: only records still unmatched are eligible, so a name match can
    # never displace a pair established on stronger evidence.
    unmatched_sites = np.setdiff1d(np.arange(len(sites)), pairs["site_idx"].to_numpy())
    unmatched_venues = np.setdiff1d(np.arange(len(venue_frame)), pairs["venue_idx"].to_numpy())
    name_pairs = matching.match_by_name(
        sites["Site Name"], venue_frame["oa_location_names"], site_xy, venue_xy,
        unmatched_sites, unmatched_venues, name_max_metres, name_threshold,
        load_place_tokens(data_dir),
    )
    pairs = matching.append_name_pairs(pairs, name_pairs)

    results = analysis.build_results(
        sites, venue_frame, pairs, site_xy, venue_xy, buffer_metres, england_points,
        postcode_max_metres, name_max_metres, name_threshold,
    )
    _validate(results, sites, buffer_metres, postcode_max_metres, name_max_metres, name_threshold)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(results.mapping, output_dir, "site_oa_mapping.csv")
    _write_csv(results.unmatched_sites, output_dir, "unmatched_sites.csv")
    _write_csv(results.unmatched_venues, output_dir, "unmatched_oa_venues.csv")
    _write_csv(results.coverage_by_la, output_dir, "coverage_by_local_authority.csv")

    markdown = report.render(
        results,
        england_points,
        scope_counts,
        data_version,
        bigquery_ops.table_id(bigquery_ops.OPPORTUNITIES_TABLE),
        buffer_metres,
        cluster_metres,
        diameters,
    )
    report_path = output_dir / REPORT_FILENAME
    report_path.write_text(markdown, encoding="utf-8")
    logger.info("Wrote %s", report_path)

    stats = results.stats
    print(
        f"\n✓ {stats['coverage_pct']}% of Active Places sites "
        f"({stats['sites_matched']:,}/{stats['sites_total']:,}) are in the OpenActive data\n"
        f"  {stats['spatial_only_pct']}% within {buffer_metres:g}m, "
        f"plus {stats['postcode_added_sites']:,} sharing a postcode "
        f"and {stats['name_added_sites']:,} on name\n"
        f"  Report: {report_path}"
    )


def _validate(results: analysis.CoverageResults, sites: pd.DataFrame, buffer_metres: float,
              postcode_max_metres: float, name_max_metres: float, name_threshold: float) -> None:
    """Internal consistency checks — cheap, and they catch join mistakes early."""
    stats = results.stats
    assert stats["sites_matched"] <= stats["sites_total"], "matched exceeds the universe"
    assert stats["sites_matched"] + stats["sites_missing"] == stats["sites_total"], "counts do not add up"
    assert results.coverage_by_la["sites_total"].sum() == len(sites), "per-LA totals do not sum"

    mapping = results.mapping
    if not mapping.empty:
        # Each channel has its own ceiling.
        spatial = mapping[mapping["spatial_match"]]
        assert spatial["distance_metres"].max() <= buffer_metres + 0.05, "spatial pair beyond the buffer"

        postcode_only = mapping[~mapping["spatial_match"] & mapping["postcode_match"]]
        if not postcode_only.empty:
            assert postcode_only["distance_metres"].max() <= postcode_max_metres + 0.05, \
                "postcode pair beyond its cap"

        name_only = mapping[mapping["match_method"] == "name"]
        if not name_only.empty:
            assert name_only["distance_metres"].max() <= name_max_metres + 0.05, \
                "name pair beyond its cap"
            assert name_only["name_similarity"].min() >= name_threshold, \
                "name pair below the similarity threshold"
            # "Last resort" means every name pair rescues at least one side that no
            # stronger channel reached; it never re-pairs two already-matched records.
            stronger = mapping[mapping["match_method"] != "name"]
            rescues = (~name_only["site_id"].isin(set(stronger["site_id"]))
                       | ~name_only["venue_id"].isin(set(stronger["venue_id"])))
            assert rescues.all(), "name pair where both sides were already matched"
            assert name_only["site_id"].is_unique and name_only["venue_id"].is_unique, \
                "name channel produced a fan-out"

        assert (mapping["spatial_match"] | mapping["postcode_match"]
                | (mapping["match_method"] == "name")).all(), "pair with no channel"

    sensitivity = results.distance_sensitivity["sites_matched"]
    assert sensitivity.is_monotonic_increasing, "coverage must not fall as the threshold widens"
    logger.info("Validation checks passed")


@click.command()
@click.option("--data-dir", type=click.Path(path_type=Path, file_okay=False, exists=True),
              default=DEFAULT_DATA_DIR, show_default=True,
              help="Directory holding the Active Places facilities.csv and sites.csv.")
@click.option("--output-dir", type=click.Path(path_type=Path, file_okay=False),
              default=DEFAULT_OUTPUT_DIR, show_default=True,
              help="Where the CSV tables and the markdown report are written.")
@click.option("--buffer-metres", type=float, default=200.0, show_default=True,
              help="A site counts as covered when an OpenActive venue is within this distance.")
@click.option("--venue-cluster-metres", type=float, default=50.0, show_default=True,
              help="Radius for collapsing near-duplicate OpenActive points into one venue.")
@click.option("--no-cluster", is_flag=True,
              help="Treat every distinct OpenActive point as its own venue.")
@click.option("--points-cache", type=click.Path(path_type=Path, dir_okay=False), default=None,
              help="Parquet file to cache the BigQuery result in, so reruns skip the query.")
@click.option("--postcode-max-metres", type=float, default=1000.0, show_default=True,
              help="Distance cap on the postcode channel; pairs sharing a postcode but further "
                   "apart than this are treated as bad data rather than a match.")
@click.option("--name-max-metres", type=float, default=500.0, show_default=True,
              help="How far apart a site and venue may be for a name match to be considered.")
@click.option("--name-threshold", type=float, default=0.8, show_default=True,
              help="Name similarity (0-1) required for the last-resort name channel. "
                   "Below about 0.8 the channel starts matching on shared town names.")
@click.option("--codepoint-dir", type=click.Path(path_type=Path, file_okay=False), default=None,
              help="Code-Point Open CSV directory for the coordinate-provenance diagnostic. "
                   "Defaults to the copy bundled with the uklookup package.")
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
def cli(data_dir: Path,
        output_dir: Path,
        buffer_metres: float,
        venue_cluster_metres: float,
        no_cluster: bool,
        points_cache: Path | None,
        postcode_max_metres: float,
        name_max_metres: float,
        name_threshold: float,
        codepoint_dir: Path | None,
        verbose: bool) -> None:
    """Report how much of the Active Places estate appears in the OpenActive data."""
    _configure_logging(verbose)
    run(
        data_dir=data_dir,
        output_dir=output_dir,
        buffer_metres=buffer_metres,
        cluster_metres=0.0 if no_cluster else venue_cluster_metres,
        points_cache=points_cache,
        codepoint_dir=codepoint_dir,
        postcode_max_metres=postcode_max_metres,
        name_max_metres=name_max_metres,
        name_threshold=name_threshold,
    )


if __name__ == "__main__":
    cli()
