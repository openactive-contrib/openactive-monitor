"""Offline tests for ``self_healing.backfill_super_event_inheritance``.

BigQuery I/O is mocked; chunks are shaped exactly like ``to_dataframe()``
output (JSON columns as JSON strings, ``json_keys`` arrays, nullable BOOL as
``pd.NA``) to exercise ``_prepare_chunk`` and the fill-only diff/write path.
"""

from __future__ import annotations

import importlib
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

from bigquery_ops import OPPORTUNITIES_COLUMNS  # noqa: E402
from processing import DF_COLUMNS, extract_rows  # noqa: E402
from self_healing._common import INHERITABLE_FIELDS  # noqa: E402

backfill = importlib.import_module("self_healing.backfill_super_event_inheritance")

DATASET = "https://dataset"
EVENT_SERIES = {
    "@type": "EventSeries",
    "activity": [{"prefLabel": "Swimming"}],
    "genderRestriction": "https://openactive.io/NoRestriction",
    "organizer": {"@type": "Organization", "name": "Everyone Active"},
    "isAccessibleForFree": False,
}


def _bq_chunk(rows: list[dict]) -> pd.DataFrame:
    """Build a raw streamed chunk as BigQuery returns it (pre-_prepare_chunk)."""
    records = []
    for r in rows:
        rec = {c: None for c in backfill._LOAD_COLUMNS}
        rec.update({k: v for k, v in r.items() if k in rec})
        for col in ("has_superEvent", "activity", "activity_json", "facility", "facility_json",
                    "location", "ageRange", "level", "accessibilitySupport"):
            if rec[col] is not None:
                rec[col] = json.dumps(rec[col])
        rec["json_keys"] = list(r.get("json_keys", []))
        records.append(rec)
    df = pd.DataFrame(records)
    df["isAccessibleForFree"] = pd.array([r.get("isAccessibleForFree") for r in rows], dtype="boolean")
    return df


def _bq_parent_rows(*items: dict) -> pd.DataFrame:
    rpde = {"items": [{"state": "updated", "id": i["@id"], "modified": 1, "data": i} for i in items]}
    updated, _ = extract_rows(DATASET, "feed", rpde)
    return pd.DataFrame(updated, columns=DF_COLUMNS).reindex(columns=OPPORTUNITIES_COLUMNS)


class BackfillFixDatasetTests(unittest.TestCase):
    def _run(self, chunk: pd.DataFrame, parents: pd.DataFrame) -> tuple[tuple, list[pd.DataFrame]]:
        written: list[pd.DataFrame] = []
        prepared = backfill._prepare_chunk(chunk)
        with (
            mock.patch.object(backfill, "_iter_affected_chunks", return_value=iter([prepared])),
            mock.patch.object(backfill, "get_dataset_opportunities", return_value=parents),
            mock.patch.object(backfill, "get_dataset_ancestor_opportunities",
                              return_value=pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)),
            mock.patch.object(backfill, "get_dataset_facility_uses",
                              return_value=pd.DataFrame(columns=OPPORTUNITIES_COLUMNS)),
            mock.patch.object(backfill, "write_inherited_updates",
                              side_effect=lambda c, t, d, df, label: written.append(df.copy()) or len(df)),
            mock.patch.object(backfill.bigquery, "Client"),
        ):
            result = backfill._fix_dataset(DATASET, [], 1000, False, 1, 1)
        return result, written

    def test_shape_a_inline_grandparent_and_shape_b_reference(self) -> None:
        chunk = _bq_chunk([
            {   # shape A: inline series → inline event series
                "dataset_url": DATASET, "feed_id": "f", "id": "1", "data_id": "C1", "kind": "ScheduledSession",
                "has_superEvent": {"@type": "SessionSeries", "superEvent": EVENT_SERIES},
                "activity": [], "activity_json": None, "location": {},
                "json_keys": ["@id", "@type", "superEvent", "startDate"],
            },
            {   # shape B: "@id" → series row (fetched) → inline event series
                "dataset_url": DATASET, "feed_id": "f", "id": "2", "data_id": "C2", "kind": "ScheduledSession",
                "has_superEvent": "S1", "activity": [], "location": {"latitude": 1},
                "genderRestriction": "https://openactive.io/FemaleOnly",  # must not be overwritten
                "json_keys": ["@id", "@type", "superEvent", "genderRestriction"],
            },
        ])
        parents = _bq_parent_rows({"@id": "S1", "@type": "SessionSeries", "superEvent": dict(EVENT_SERIES)})

        (examined, merged, filled), written = self._run(chunk, parents)

        self.assertEqual((examined, merged), (2, 2))
        self.assertEqual(len(written), 1)
        out = written[0].set_index("id")
        self.assertEqual(list(written[0].columns), ["dataset_url", "feed_id", "id", *INHERITABLE_FIELDS])
        for row_id in ("1", "2"):
            self.assertEqual(out.at[row_id, "activity"], ["Swimming"])
            self.assertEqual(out.at[row_id, "activity_json"], EVENT_SERIES["activity"])
            self.assertEqual(out.at[row_id, "organization_name"], "Everyone Active")
            self.assertIs(out.at[row_id, "isAccessibleForFree"], False)
        self.assertEqual(out.at["1", "genderRestriction"], "https://openactive.io/NoRestriction")
        self.assertEqual(out.at["2", "genderRestriction"], "https://openactive.io/FemaleOnly")
        self.assertEqual(filled["organization_name"], 2)

    def test_nothing_written_when_no_ancestor_value(self) -> None:
        chunk = _bq_chunk([{
            "dataset_url": DATASET, "feed_id": "f", "id": "1", "data_id": "C1", "kind": "ScheduledSession",
            "has_superEvent": "MISSING", "activity": [], "json_keys": ["@id"],
        }])
        (examined, merged, _), written = self._run(chunk, pd.DataFrame(columns=OPPORTUNITIES_COLUMNS))
        self.assertEqual((examined, merged), (1, 0))
        self.assertEqual(written, [])


if __name__ == "__main__":
    unittest.main()
