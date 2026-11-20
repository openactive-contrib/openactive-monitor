"""Unit tests for postcode fallback on unusable ``geo`` and the boundary-completion pass.

Real-world cases (Legend feeds) publish swapped latitude/longitude or a flipped
longitude sign; the point then falls outside every UK district even though the
location's postcode is valid.  Separately, rows have been observed with
coordinates but empty district columns; ``ensure_boundaries`` must fill them.

These tests use the local boundary geojson files and the offline ``uklookup``
postcode data; no network or BigQuery access.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

from processing import (  # noqa: E402
    DF_COLUMNS,
    _build_location_validated,
    ensure_boundaries,
    extract_rows,
)


def _place(lat: float, lng: float, postcode: str | None = None) -> dict:
    place: dict = {
        "@type": "Place",
        "name": "Test Leisure Centre",
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
    }
    if postcode:
        place["address"] = {"@type": "PostalAddress", "postalCode": postcode}
    return place


class BuildLocationValidatedTests(unittest.TestCase):
    def test_swapped_lat_lng_falls_back_to_postcode(self) -> None:
        # Saffron Walden (CB11 3EG) published as lat=0.253199, lng=52.01489.
        location = _build_location_validated(_place(0.253199, 52.01489, "CB11 3EG"))
        self.assertEqual(location["geo_source"], "postcode_fallback")
        self.assertAlmostEqual(location["latitude"], 52.0155, places=2)
        self.assertAlmostEqual(location["longitude"], 0.2516, places=2)
        self.assertEqual(location["postal_code"], "CB11 3EG")

    def test_flipped_longitude_sign_falls_back_to_postcode(self) -> None:
        # Neath Port Talbot (SA12 6QW) published with lng=+3.81375.
        location = _build_location_validated(_place(51.592764, 3.81375, "SA12 6QW"))
        self.assertEqual(location["geo_source"], "postcode_fallback")
        self.assertAlmostEqual(location["longitude"], -3.8137, places=2)

    def test_valid_geo_is_untouched(self) -> None:
        raw = _place(50.9818466, -1.383649, "SO53 3DA")
        location = _build_location_validated(raw)
        self.assertNotIn("geo_source", location)
        self.assertEqual(location["latitude"], 50.981847)
        self.assertEqual(location["longitude"], -1.383649)

    def test_unresolvable_geo_without_postcode_is_untouched(self) -> None:
        location = _build_location_validated(_place(41.69301, 44.79542))
        self.assertNotIn("geo_source", location)
        self.assertEqual(location["latitude"], 41.69301)

    def test_list_location_uses_first_entry(self) -> None:
        location = _build_location_validated([_place(0.253199, 52.01489, "CB11 3EG")])
        self.assertEqual(location["geo_source"], "postcode_fallback")

    def test_extract_rows_resolves_district_via_fallback(self) -> None:
        result = {
            "items": [{
                "state": "updated",
                "id": "1",
                "modified": 1,
                "data": {
                    "@type": "ScheduledSession",
                    "@id": "https://example.com/session/1",
                    "startDate": "2027-01-01T10:00:00Z",
                    "location": _place(51.7499, 2.2251, "GL5 4AF"),
                },
            }]
        }
        updated, _ = extract_rows("https://example.com/", "feed", result)
        self.assertEqual(updated[0]["district_name"], "Stroud")
        self.assertEqual(updated[0]["location"]["geo_source"], "postcode_fallback")


class EnsureBoundariesTests(unittest.TestCase):
    def _row(self, **overrides) -> dict:
        row = {col: None for col in DF_COLUMNS}
        row.update({"json_data": {}, "inherited_data": {}, "location": {}})
        row.update(overrides)
        return row

    def test_fills_district_for_row_with_coordinates(self) -> None:
        df = pd.DataFrame([
            self._row(id="a", location={"latitude": 50.981847, "longitude": -1.383649}),
        ], columns=DF_COLUMNS)
        ensure_boundaries(df)
        self.assertEqual(df.at[0, "district_name"], "Eastleigh")
        self.assertEqual(df.at[0, "region_name"], "South East")
        self.assertIsNotNone(df.at[0, "district_code"])
        self.assertEqual(df.at[0, "nhstrust_code"], "RN5")

    def test_keeps_existing_values_and_skips_rows_without_coordinates(self) -> None:
        df = pd.DataFrame([
            self._row(
                id="a",
                location={"latitude": 50.981847, "longitude": -1.383649},
                district_name="Existing",
                nhstrust_name="Kept",
            ),
            self._row(id="b", location={"place_name": "Colwyn Leisure Centre"}),
        ], columns=DF_COLUMNS)
        ensure_boundaries(df)
        self.assertEqual(df.at[0, "district_name"], "Existing")
        self.assertEqual(df.at[0, "nhstrust_name"], "Kept")
        # pandas 3 stores a missing string as NaN, pandas 2 as None.
        self.assertTrue(pd.isna(df.at[1, "district_name"]))


if __name__ == "__main__":
    unittest.main()
