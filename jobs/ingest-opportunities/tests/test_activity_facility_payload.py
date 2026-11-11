"""Unit tests for the raw ``activity_json`` / ``facility_json`` payload columns.

Covers shape-preserving extraction (``get_activity_payload`` /
``get_facility_payload``), their population by ``extract_rows``, and
fill-only-when-empty inheritance via ``apply_inherited_data``.

These tests perform no network or BigQuery access.
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
    apply_inherited_data,
    extract_rows,
    get_activity_payload,
    get_facility_payload,
)

TAI_CHI = {
    "id": "https://openactive.io/activity-list#c16df6ed-a4a0-4275-a8c3-1c8cff56856f",
    "type": "Concept",
    "prefLabel": "Tai Chi",
    "inScheme": "https://openactive.io/activity-list",
}
SWIMMING_NO_ID = {"type": "Concept", "prefLabel": "Swimming"}
SPORTS_HALL = {
    "@id": "https://openactive.io/facility-types#da364f9b-8bd2-490e-b9d2-0bd14c0c4ec7",
    "@type": "Concept",
    "prefLabel": "Sports Hall",
    "inScheme": "https://openactive.io/facility-types",
}


class ActivityPayloadTest(unittest.TestCase):
    def test_preserves_concept_list(self) -> None:
        self.assertEqual(get_activity_payload({"activity": [TAI_CHI]}), [TAI_CHI])

    def test_preserves_plain_string(self) -> None:
        self.assertEqual(get_activity_payload({"activity": "Table Tennis"}), "Table Tennis")

    def test_preserves_single_dict(self) -> None:
        self.assertEqual(get_activity_payload({"activity": SWIMMING_NO_ID}), SWIMMING_NO_ID)

    def test_falls_back_to_activities(self) -> None:
        self.assertEqual(
            get_activity_payload({"activity": [], "activities": [TAI_CHI]}), [TAI_CHI]
        )

    def test_empty_values_return_none(self) -> None:
        for value in (None, "", "   ", [], {}):
            with self.subTest(value=value):
                self.assertIsNone(get_activity_payload({"activity": value}))
        self.assertIsNone(get_activity_payload({}))


class FacilityPayloadTest(unittest.TestCase):
    def test_preserves_facility_type(self) -> None:
        self.assertEqual(get_facility_payload({"facilityType": [SPORTS_HALL]}), [SPORTS_HALL])

    def test_ignores_category_and_facilities(self) -> None:
        self.assertIsNone(get_facility_payload({"category": ["Fitness"], "facilities": "Gym"}))


class ExtractRowsPayloadTest(unittest.TestCase):
    def test_extract_rows_populates_raw_columns(self) -> None:
        items = [{
            "state": "updated",
            "id": "A",
            "modified": "1",
            "data": {
                "@id": "data-A",
                "@type": "FacilityUse",
                "activity": [TAI_CHI, "Yoga"],
                "facilityType": [SPORTS_HALL],
            },
        }]
        updated, _ = extract_rows("dataset-url", "feed-1", {"items": items})
        self.assertEqual(updated[0]["activity_json"], [TAI_CHI, "Yoga"])
        self.assertEqual(updated[0]["facility_json"], [SPORTS_HALL])
        # The label-only columns are unchanged.
        self.assertEqual(updated[0]["activity"], ["Tai Chi", "Yoga"])
        self.assertEqual(updated[0]["facility"], ["Sports Hall"])


class InheritanceTest(unittest.TestCase):
    def _row_df(self, **overrides) -> pd.DataFrame:
        row = {col: None for col in DF_COLUMNS}
        row.update({"activity": [], "facility": [], "location": {}})
        row.update(overrides)
        return pd.DataFrame([row], columns=DF_COLUMNS)

    def test_inherits_when_empty(self) -> None:
        df = self._row_df()
        apply_inherited_data(df, 0, {"activity": [TAI_CHI], "facilityType": [SPORTS_HALL]})
        self.assertEqual(df.at[0, "activity_json"], [TAI_CHI])
        self.assertEqual(df.at[0, "facility_json"], [SPORTS_HALL])

    def test_does_not_overwrite_existing(self) -> None:
        df = self._row_df(activity_json="Table Tennis", activity=["Table Tennis"])
        apply_inherited_data(df, 0, {"activity": [TAI_CHI]})
        self.assertEqual(df.at[0, "activity_json"], "Table Tennis")


if __name__ == "__main__":
    unittest.main()
