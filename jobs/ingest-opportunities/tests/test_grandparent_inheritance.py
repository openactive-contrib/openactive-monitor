"""Unit tests for multi-level (grandparent+) superEvent inheritance.

``inherited_data`` is never persisted and is still empty for rows in the
current batch when parent payloads are built, so inheritance must walk the
ancestor chain explicitly.  Two chain shapes exist in production data:

  A. ScheduledSession → inline SessionSeries → inline EventSeries
  B. ScheduledSession → "@id" → SessionSeries row → inline EventSeries

These tests perform no network or BigQuery access.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import pandas as pd

JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

from processing import (  # noqa: E402
    DF_COLUMNS,
    collect_super_event_refs,
    denormalize_dataset,
    extract_rows,
)

EVENT_SERIES = {
    "@type": "EventSeries",
    "activity": [{"@id": "https://openactive.io/activity-list#swim", "prefLabel": "Swimming"}],
    "genderRestriction": "https://openactive.io/NoRestriction",
    "organizer": {"@type": "Organization", "name": "Everyone Active"},
    "level": ["Beginner"],
    "ageRange": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 100},
}


def _frame(*items: dict) -> pd.DataFrame:
    rpde = {"items": [{"state": "updated", "id": i["@id"], "modified": 1, "data": i} for i in items]}
    updated, _ = extract_rows("https://dataset", "feed", rpde)
    return pd.DataFrame(updated, columns=DF_COLUMNS)


def _empty() -> pd.DataFrame:
    return pd.DataFrame(columns=DF_COLUMNS)


def _row(df: pd.DataFrame, data_id: str) -> pd.Series:
    return df.loc[df["data_id"] == data_id].iloc[0]


class GrandparentInheritanceTests(unittest.TestCase):
    def assert_inherited_from_event_series(self, row: pd.Series) -> None:
        self.assertEqual(row["activity"], ["Swimming"])
        self.assertEqual(row["activity_json"], EVENT_SERIES["activity"])
        self.assertEqual(row["genderRestriction"], "https://openactive.io/NoRestriction")
        self.assertEqual(row["organization_name"], "Everyone Active")
        self.assertEqual(row["level"], ["Beginner"])
        self.assertEqual(row["ageRange"], EVENT_SERIES["ageRange"])

    def test_shape_a_inline_parent_with_inline_grandparent(self) -> None:
        session = {
            "@id": "C1",
            "@type": "ScheduledSession",
            "startDate": "2026-12-01T10:00:00Z",
            "superEvent": {"@type": "SessionSeries", "superEvent": copy.deepcopy(EVENT_SERIES)},
        }
        df = _frame(session)
        denormalize_dataset(df, _empty())
        self.assert_inherited_from_event_series(_row(df, "C1"))

    def test_shape_b_parent_row_in_same_batch(self) -> None:
        series = {"@id": "S1", "@type": "SessionSeries", "superEvent": copy.deepcopy(EVENT_SERIES)}
        session = {"@id": "C1", "@type": "ScheduledSession", "superEvent": "S1"}
        df = _frame(series, session)
        denormalize_dataset(df, _empty())
        self.assert_inherited_from_event_series(_row(df, "C1"))
        self.assert_inherited_from_event_series(_row(df, "S1"))

    def test_shape_b_parent_row_from_bigquery(self) -> None:
        series = {"@id": "S1", "@type": "SessionSeries", "superEvent": copy.deepcopy(EVENT_SERIES)}
        session = {"@id": "C1", "@type": "ScheduledSession", "superEvent": "S1"}
        df_bq = _frame(series)  # inherited_data is {} — exactly as stored in BigQuery
        df = _frame(session)
        denormalize_dataset(df, df_bq)
        self.assert_inherited_from_event_series(_row(df, "C1"))

    def test_three_levels_of_string_references(self) -> None:
        great = {"@id": "G", "@type": "EventSeries", **{k: v for k, v in EVENT_SERIES.items() if k != "@type"}}
        grand = {"@id": "P", "@type": "EventSeries", "superEvent": "G"}
        parent = {"@id": "S1", "@type": "SessionSeries", "superEvent": "P"}
        session = {"@id": "C1", "@type": "ScheduledSession", "superEvent": "S1"}
        df = _frame(session)
        denormalize_dataset(df, _frame(great, grand, parent))
        self.assert_inherited_from_event_series(_row(df, "C1"))

    def test_closer_levels_win(self) -> None:
        series = {
            "@id": "S1",
            "@type": "SessionSeries",
            "level": ["Advanced"],  # parent overrides grandparent
            "superEvent": copy.deepcopy(EVENT_SERIES),
        }
        session = {
            "@id": "C1",
            "@type": "ScheduledSession",
            "superEvent": "S1",
            "genderRestriction": "https://openactive.io/FemaleOnly",  # child's own value
        }
        df = _frame(series, session)
        denormalize_dataset(df, _empty())
        row = _row(df, "C1")
        self.assertEqual(row["level"], ["Advanced"])
        self.assertEqual(row["genderRestriction"], "https://openactive.io/FemaleOnly")
        self.assertEqual(row["activity"], ["Swimming"])

    def test_empty_parent_value_does_not_mask_grandparent(self) -> None:
        series = {"@id": "S1", "@type": "SessionSeries", "activity": [], "superEvent": copy.deepcopy(EVENT_SERIES)}
        session = {"@id": "C1", "@type": "ScheduledSession", "superEvent": "S1"}
        df = _frame(series, session)
        denormalize_dataset(df, _empty())
        self.assertEqual(_row(df, "C1")["activity"], ["Swimming"])

    def test_cycle_terminates(self) -> None:
        a = {"@id": "A", "@type": "SessionSeries", "superEvent": "B", "level": ["A-level"]}
        b = {"@id": "B", "@type": "SessionSeries", "superEvent": "A", "genderRestriction": "https://openactive.io/MaleOnly"}
        df = _frame(a, b)
        denormalize_dataset(df, _empty())
        self.assertEqual(_row(df, "A")["genderRestriction"], "https://openactive.io/MaleOnly")
        self.assertEqual(_row(df, "B")["level"], ["A-level"])

    def test_self_reference_is_skipped(self) -> None:
        df = _frame({"@id": "A", "@type": "SessionSeries", "superEvent": "A"})
        denormalize_dataset(df, _empty())
        self.assertEqual(_row(df, "A")["activity"], [])

    def test_inline_super_event_in_json_data_is_not_mutated(self) -> None:
        session = {
            "@id": "C1",
            "@type": "ScheduledSession",
            "superEvent": {"@type": "SessionSeries", "superEvent": copy.deepcopy(EVENT_SERIES)},
        }
        df = _frame(session)
        before = copy.deepcopy(_row(df, "C1")["json_data"]["superEvent"])
        denormalize_dataset(df, _empty())
        self.assertEqual(_row(df, "C1")["json_data"]["superEvent"], before)

    def test_sub_event_push_includes_grandparent(self) -> None:
        series = {
            "@id": "S1",
            "@type": "SessionSeries",
            "superEvent": "E1",
            "subEvent": ["C1"],
        }
        event_series = {"@id": "E1", **copy.deepcopy(EVENT_SERIES)}
        # Child has no superEvent link of its own; only the parent lists it.
        session = {"@id": "C1", "@type": "ScheduledSession"}
        df = _frame(series, session)
        denormalize_dataset(df, _frame(event_series))
        self.assert_inherited_from_event_series(_row(df, "C1"))

    def test_nested_ifu_virtual_payload_still_resolves(self) -> None:
        facility_use = {
            "@id": "FU1",
            "@type": "FacilityUse",
            "provider": {"@type": "Organization", "name": "Provider Ltd"},
            "facilityType": [{"prefLabel": "Squash Court"}],
            "individualFacilityUse": [{"@id": "IFU1", "@type": "IndividualFacilityUse", "name": "Court 1"}],
        }
        slot = {"@id": "SL1", "@type": "Slot", "facilityUse": "IFU1", "startDate": "2026-12-01T10:00:00Z"}
        df = _frame(slot)
        denormalize_dataset(df, _frame(facility_use))
        row = _row(df, "SL1")
        self.assertEqual(row["facility"], ["Squash Court"])
        self.assertEqual(row["organization_name"], "Provider Ltd")


class CollectSuperEventRefsTests(unittest.TestCase):
    def test_collects_top_level_and_nested_string_refs(self) -> None:
        df = pd.DataFrame(
            {
                "has_superEvent": [
                    '"S1"',
                    {"@type": "SessionSeries", "superEvent": "E9"},
                    {"@type": "SessionSeries", "superEvent": {"@type": "EventSeries"}},
                    None,
                ]
            }
        )
        self.assertEqual(collect_super_event_refs(df), {"S1", "E9"})


if __name__ == "__main__":
    unittest.main()
