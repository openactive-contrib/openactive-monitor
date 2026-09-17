"""Load and clean the Sport England Active Places export.

The export ships two CSVs that join on ``Site ID``:

* ``facilities.csv`` — one row per facility, carrying the operational status and
  the public/private access flag.
* ``sites.csv``      — one row per site, carrying the geography we report on.

The "universe" of sites this report measures coverage against is defined as the
sites reachable through at least one facility that is both operational and not
private, and that are not themselves flagged as closed.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# `Operational Status` is an integer code with no accompanying label file in the
# export. 3 = Operational, 4 = Temporarily Closed. Everything else (5 closed,
# 7 not currently in use, 2 under construction, 1 planned, 8 unusable) is out.
OPERATIONAL_STATUSES = {"3", "4"}

# `Accessibility Type Group (Text)` is one of `Public Access`, `Private` or
# `Not Known`. Excluding `Private` rather than requiring `Public Access` keeps the
# small `Not Known` bucket in scope.
EXCLUDED_ACCESSIBILITY_GROUP = "Private"

FACILITY_COLUMNS = [
    "Site ID",
    "Facility ID",
    "Operational Status",
    "Accessibility Type Group (Text)",
    "Facility Type",
    "Facility Subtype",
    "Management Type Group (Text)",
]

# Geography columns whose words are place names rather than venue names.
PLACE_COLUMNS = ["Town", "Local Authority Name", "County Name", "Region Name"]

SITE_COLUMNS = [
    "Site ID",
    "Site Name",
    "Postcode",
    "Local Authority Code",
    "Local Authority Name",
    "Region Code",
    "Region Name",
    "lat",
    "long",
    "Ownership Type Group",
    "Management Type Group",
    "Closed Date",
]

_DATA_VERSION_RE = re.compile(r"Active Places Data Version:\s*(.+)")


def load_place_tokens(data_dir: Path) -> frozenset[str]:
    """Words that name a place rather than a venue, taken from the export itself.

    Used to stop the name-matching channel pairing a site with a venue whose only
    common word is the town they share. Built from the data rather than an external
    gazetteer so it stays in step with whatever geography the export covers.
    """
    from .names import all_tokens

    frame = pd.read_csv(
        data_dir / "sites.csv",
        usecols=PLACE_COLUMNS,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False,
    )
    tokens: set[str] = set()
    for column in PLACE_COLUMNS:
        for value in frame[column].dropna().unique():
            tokens.update(all_tokens(value))
    logger.info("Built a place-name vocabulary of %d words from the export geography", len(tokens))
    return frozenset(tokens)


def read_data_version(data_dir: Path) -> str:
    """Read the export's data version from ``information.txt``.

    Returns ``"unknown"`` if the file is missing or does not carry the line, so a
    stale or hand-assembled data directory does not break the run.
    """
    info_path = data_dir / "information.txt"
    try:
        text = info_path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Could not read %s: %s", info_path, exc)
        return "unknown"

    match = _DATA_VERSION_RE.search(text)
    if not match:
        logger.warning("No 'Active Places Data Version' line in %s", info_path)
        return "unknown"
    return match.group(1).strip()


def _strip_object_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip surrounding whitespace from every text column.

    Several lookup values in the export carry a trailing space (for example
    ``'Local Authority '`` in ``Ownership Type (Text)``), which would otherwise
    split what should be a single group.
    """
    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].str.strip()
    return df


def _load_facilities(data_dir: Path) -> pd.DataFrame:
    """Facilities that are operational and not private, aggregated per site."""
    path = data_dir / "facilities.csv"
    facilities = pd.read_csv(
        path,
        usecols=FACILITY_COLUMNS,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False,
    )
    facilities = _strip_object_columns(facilities)
    total = len(facilities)

    kept = facilities[
        facilities["Operational Status"].isin(OPERATIONAL_STATUSES)
        & (facilities["Accessibility Type Group (Text)"] != EXCLUDED_ACCESSIBILITY_GROUP)
    ]
    logger.info(
        "facilities.csv: %d rows, %d kept (operational status in %s, access group != %r)",
        total,
        len(kept),
        sorted(OPERATIONAL_STATUSES),
        EXCLUDED_ACCESSIBILITY_GROUP,
    )

    per_site = kept.groupby("Site ID", sort=False).agg(
        ap_facility_count=("Facility ID", "nunique"),
        ap_facility_types=(
            "Facility Type",
            lambda values: "|".join(sorted(set(values))),
        ),
        ap_facility_subtypes=(
            "Facility Subtype",
            lambda values: "|".join(sorted(set(values))),
        ),
    )
    logger.info("facilities.csv: %d distinct sites after filtering", len(per_site))
    return per_site.reset_index()


def load_active_places_sites(data_dir: Path) -> pd.DataFrame:
    """Return the Active Places site universe this report measures coverage against.

    One row per site, with the geography columns, the ownership/management groups
    and a count of the qualifying facilities that put the site in scope.
    """
    per_site = _load_facilities(data_dir)

    sites = pd.read_csv(
        data_dir / "sites.csv",
        usecols=SITE_COLUMNS,
        dtype={c: str for c in SITE_COLUMNS if c not in ("lat", "long")},
        encoding="utf-8-sig",
        keep_default_na=False,
    )
    sites["lat"] = pd.to_numeric(sites["lat"], errors="coerce")
    sites["long"] = pd.to_numeric(sites["long"], errors="coerce")
    sites = _strip_object_columns(sites)
    logger.info("sites.csv: %d rows", len(sites))

    merged = sites.merge(per_site, on="Site ID", how="inner")
    logger.info("%d sites reachable through a qualifying facility", len(merged))

    # Site-level closure guard. This drops nothing against the 2026-09-17 export
    # (the facility-level status filter already excludes every closed site), but
    # the two fields are maintained independently upstream so a future export
    # could disagree. Log it so a non-zero value is visible rather than silent.
    closed_mask = merged["Closed Date"] != ""
    if closed_mask.any():
        logger.warning(
            "%d sites dropped for a non-empty site-level Closed Date despite having "
            "an operational facility — facility and site status have diverged",
            int(closed_mask.sum()),
        )
    else:
        logger.info("0 sites dropped by the site-level Closed Date filter")
    merged = merged[~closed_mask]

    missing_coords = merged["lat"].isna() | merged["long"].isna()
    if missing_coords.any():
        logger.warning("%d sites dropped for missing coordinates", int(missing_coords.sum()))
        merged = merged[~missing_coords]

    merged = merged.drop(columns=["Closed Date"]).reset_index(drop=True)
    logger.info(
        "Active Places universe: %d sites across %d local authorities",
        len(merged),
        merged["Local Authority Code"].nunique(),
    )
    return merged
