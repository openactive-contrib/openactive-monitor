"""Detect OpenActive points whose coordinates are really a postcode centroid.

A publisher that holds only a postcode for a venue will often geocode it to the
postcode centroid and publish that as `geo`. Such a point is not a venue
coordinate: it is the mean position of a postcode unit, typically tens to
hundreds of metres from the building. Those points cannot be expected to fall
within a tight radius of an Active Places site, so knowing how many there are is
essential to interpreting the coverage figure.

They are detectable because a centroid lands *exactly* on a Code-Point Open
record. Code-Point stores integer eastings/northings, so a 3x3 integer probe
around each point implements a sub-metre test exactly, with no spatial index.

Code-Point Open ships inside the ``uklookup`` package that the ingest job already
depends on. If it is unavailable the diagnostic is skipped rather than failing
the run — it informs the report, it does not drive the matching.
"""

from __future__ import annotations

import csv
import glob
import gzip
import logging
import math
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Code-Point coordinates are integer metres, so a true centroid lands within
# rounding distance. 1m keeps the false-positive rate on real building
# coordinates low (measured at ~1.5% against the Active Places sites).
SNAP_TOLERANCE_METRES = 1.0


def default_codepoint_dir() -> Path | None:
    """Locate the Code-Point Open CSVs bundled with ``uklookup``, if installed."""
    try:
        import uklookup
    except ImportError:
        return None
    candidate = Path(uklookup.__file__).parent / "codepointopen" / "Data" / "CSV"
    return candidate if candidate.is_dir() else None


def load_centroid_index(codepoint_dir: Path) -> dict[tuple[int, int], str]:
    """Map integer (easting, northing) to postcode for every Code-Point record."""
    index: dict[tuple[int, int], str] = {}
    for path in sorted(glob.glob(str(codepoint_dir / "*.csv.gz"))):
        with gzip.open(path, "rt") as handle:
            for row in csv.reader(handle):
                try:
                    index[(int(row[2]), int(row[3]))] = row[0]
                except (ValueError, IndexError):
                    continue
    logger.info("Loaded %d Code-Point Open centroids from %s", len(index), codepoint_dir)
    return index


def snap_to_centroids(x: np.ndarray,
                      y: np.ndarray,
                      index: dict[tuple[int, int], str],
                      tolerance: float = SNAP_TOLERANCE_METRES) -> tuple[np.ndarray, np.ndarray]:
    """Snap BNG points to postcode centroids.

    Returns ``(is_centroid, recovered_postcode)``. A point that lands on a centroid
    both tells us its coordinates were geocoded from a postcode *and* tells us
    which postcode that was — so the same pass that flags the weakness also
    supplies the key that works around it.
    """
    flags = np.zeros(len(x), dtype=bool)
    recovered = np.empty(len(x), dtype=object)
    recovered[:] = None
    offsets = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for i, (px, py) in enumerate(zip(x, y)):
        base_x, base_y = int(round(px)), int(round(py))
        for dx, dy in offsets:
            key = (base_x + dx, base_y + dy)
            postcode = index.get(key)
            if postcode is not None and math.hypot(px - key[0], py - key[1]) <= tolerance:
                flags[i] = True
                recovered[i] = postcode
                break
    return flags, recovered
