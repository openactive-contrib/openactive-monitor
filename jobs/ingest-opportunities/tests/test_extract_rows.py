"""Unit tests for ``processing.extract_rows`` state reconciliation.

Focus: a single RPDE traversal may surface the same ``id`` multiple times with
different ``state`` values (the feed changes mid-pagination). RPDE orders items
by ``modified`` ascending, so an id's last occurrence reflects its current
state. ``extract_rows`` must collapse to that last occurrence and route each id
to exactly one of the (updated, deleted) buckets, otherwise the persist step
(delete then write) would silently re-insert a row RPDE told us to delete.

These tests perform no network or BigQuery access.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Allow importing the job modules when run from anywhere.
JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

from processing import extract_rows  # noqa: E402


def _updated(item_id: str, modified: str) -> dict:
    return {
        "state": "updated",
        "id": item_id,
        "modified": modified,
        "data": {"@id": f"data-{item_id}", "@type": "SessionSeries"},
    }


def _deleted(item_id: str, modified: str) -> dict:
    return {"state": "deleted", "id": item_id, "modified": modified}


def _ids(rows: list[dict]) -> list[str]:
    return [row["id"] for row in rows]


class ExtractRowsStateReconciliationTest(unittest.TestCase):
    def _extract(self, items: list[dict]) -> tuple[list[dict], list[dict]]:
        return extract_rows("dataset-url", "feed-1", {"items": items})

    def test_updated_then_deleted_honours_deletion(self) -> None:
        """updated -> updated -> deleted: id only in deleted, never updated."""
        items = [_updated("A", "1"), _updated("A", "2"), _deleted("A", "3")]

        updated, deleted = self._extract(items)

        self.assertEqual(_ids(updated), [])
        self.assertEqual(_ids(deleted), ["A"])
        self.assertEqual(deleted[0]["modified"], "3")

    def test_deleted_then_updated_keeps_live_row(self) -> None:
        """deleted -> updated: final state is updated, so id only in updated."""
        items = [_deleted("A", "1"), _updated("A", "2")]

        updated, deleted = self._extract(items)

        self.assertEqual(_ids(updated), ["A"])
        self.assertEqual(_ids(deleted), [])
        self.assertEqual(updated[0]["modified"], "2")

    def test_repeated_updates_collapse_to_last(self) -> None:
        """updated -> updated (no delete): a single row for the last update."""
        items = [_updated("A", "1"), _updated("A", "2")]

        updated, deleted = self._extract(items)

        self.assertEqual(len(updated), 1)
        self.assertEqual(_ids(deleted), [])
        self.assertEqual(updated[0]["modified"], "2")

    def test_two_interleaved_ids_resolved_independently(self) -> None:
        """Distinct ids each keep their own final state."""
        items = [
            _updated("A", "1"),
            _updated("B", "2"),
            _deleted("A", "3"),
            _updated("B", "4"),
        ]

        updated, deleted = self._extract(items)

        self.assertEqual(_ids(updated), ["B"])
        self.assertEqual(updated[0]["modified"], "4")
        self.assertEqual(_ids(deleted), ["A"])
        self.assertEqual(deleted[0]["modified"], "3")

    def test_non_dict_items_ignored(self) -> None:
        """Malformed (non-dict) items are skipped without raising."""
        items = [None, "oops", _updated("A", "1")]

        updated, deleted = self._extract(items)

        self.assertEqual(_ids(updated), ["A"])
        self.assertEqual(_ids(deleted), [])


if __name__ == "__main__":
    unittest.main()
