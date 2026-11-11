"""Unit tests for the ``error_code`` / ``warning_message`` failure detail.

Focus: every non-COMPLETE ``opportunity_ingestion`` row must carry a groupable
``error_code`` token and a bounded ``warning_message`` explaining why, and every
COMPLETE row must carry neither. The detail is produced at each RPDE failure
site in ``rpde.access_feed_url`` and threaded through ``feed_states`` into
``main._build_ingestion_records``, which also has to cover the two cases RPDE
never sees: a batch that raised, and a batch that never ran.

These tests perform no network or BigQuery access.
"""

from __future__ import annotations

import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

# Allow importing the job modules when run from anywhere.
JOB_ROOT = Path(__file__).resolve().parent.parent
if str(JOB_ROOT) not in sys.path:
    sys.path.insert(0, str(JOB_ROOT))

import main  # noqa: E402
import rpde  # noqa: E402

FEED = {"id": "feed-1", "url": "https://example.com/api/sessions", "type": "SessionSeries"}


def _http_error(status_code: int) -> requests.exceptions.HTTPError:
    """An HTTPError shaped like the one raise_for_status() produces."""
    response = requests.Response()
    response.status_code = status_code
    return requests.exceptions.HTTPError(f"{status_code} Server Error", response=response)


class RpdeFailureReportingTest(unittest.TestCase):
    """One case per failure site in ``access_feed_url``."""

    def _access(self, side_effect) -> dict:
        with (
            patch.object(rpde, "build_session", return_value=MagicMock()),
            patch.object(rpde, "get_json_with_retry", side_effect=side_effect) as fetch,
        ):
            result = rpde.access_feed_url(FEED, None, None, None)
        self.assertIsNotNone(result)
        self.assertGreater(fetch.call_count, 0)
        return result

    def test_complete_feed_records_no_failure_detail(self) -> None:
        """A terminal page leaves both new fields NULL."""
        terminal = {"items": [], "next": FEED["url"]}
        result = self._access([terminal])

        self.assertEqual(result["status"], "COMPLETE")
        self.assertIsNone(result["error_code"])
        self.assertIsNone(result["warning_message"])

    def test_http_error_records_status_code_as_token(self) -> None:
        """An HTTP failure records the numeric status as the error_code."""
        result = self._access(_http_error(403))

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "403")
        self.assertTrue(result["warning_message"].startswith("HTTP 403 fetching "))
        self.assertIn(FEED["url"], result["warning_message"])

    def test_timeout_records_timeout_token(self) -> None:
        """Timeouts have no response, so they get a symbolic token."""
        result = self._access(requests.exceptions.ConnectTimeout("timed out"))

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "TIMEOUT")
        self.assertTrue(result["warning_message"].startswith("ConnectTimeout fetching "))

    def test_ssl_error_is_not_classified_as_connection_error(self) -> None:
        """SSLError subclasses ConnectionError; the more specific token must win."""
        result = self._access(requests.exceptions.SSLError("certificate verify failed"))

        self.assertEqual(result["error_code"], "SSL_ERROR")

    def test_connection_error_records_connection_token(self) -> None:
        """A plain connection failure falls through to CONNECTION_ERROR."""
        result = self._access(requests.exceptions.ConnectionError("name resolution failed"))

        self.assertEqual(result["error_code"], "CONNECTION_ERROR")

    def test_other_request_exception_records_generic_token(self) -> None:
        """Any other requests failure is still classified rather than left NULL."""
        result = self._access(requests.exceptions.TooManyRedirects("too many redirects"))

        self.assertEqual(result["error_code"], "REQUEST_FAILED")

    def test_invalid_json_records_parse_detail(self) -> None:
        """A body that never parses records INVALID_JSON with the parser message."""
        result = self._access(json.JSONDecodeError("Expecting value", "", 0))

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "INVALID_JSON")
        self.assertIn("Expecting value", result["warning_message"])
        self.assertIn(FEED["url"], result["warning_message"])

    def test_page_without_items_key_records_missing_items(self) -> None:
        """A page with no 'items' key is a malformed RPDE response."""
        result = self._access([{"next": "https://example.com/api/sessions?afterId=2"}])

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "MISSING_ITEMS")

    def test_page_with_non_list_items_records_invalid_items(self) -> None:
        """The detail names the type actually received."""
        result = self._access([{"items": {}, "next": "https://example.com/api/sessions?afterId=2"}])

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "INVALID_ITEMS")
        self.assertIn("is dict, expected list", result["warning_message"])

    def test_self_loop_with_items_records_warning(self) -> None:
        """A next URL pointing at itself while serving items never terminates."""
        page = {"items": [{"id": "a"}], "next": FEED["url"]}
        result = self._access([page])

        self.assertEqual(result["status"], "WARNING")
        self.assertEqual(result["error_code"], "SELF_LOOP")
        self.assertIn("1 item(s)", result["warning_message"])

    def test_empty_non_terminal_page_records_warning(self) -> None:
        """An empty page that still advances the cursor is malformed."""
        page = {"items": [], "next": "https://example.com/api/sessions?afterId=2"}
        result = self._access([page])

        self.assertEqual(result["status"], "WARNING")
        self.assertEqual(result["error_code"], "EMPTY_PAGE")

    def test_partial_progress_keeps_items_cursor_and_failure_detail(self) -> None:
        """A mid-feed failure keeps collected items and the resume cursor."""
        first_page = {
            "items": [{"id": "a"}],
            "next": "https://example.com/api/sessions?afterTimestamp=10&afterId=a",
        }
        result = self._access([first_page, _http_error(403)])

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["items_count"], 1)
        self.assertEqual(result["after_timestamp"], "10")
        self.assertEqual(result["after_id"], "a")
        self.assertEqual(result["error_code"], "403")

    def test_unexpected_exception_is_retagged_and_chained(self) -> None:
        """A non-requests failure keeps its cause instead of being swallowed."""
        with (
            patch.object(rpde, "build_session", return_value=MagicMock()),
            patch.object(rpde, "get_json_with_retry", side_effect=KeyError("boom")),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                rpde.access_feed_url(FEED, None, None, None)

        self.assertTrue(str(ctx.exception).startswith("UNEXPECTED_ERROR:"))
        self.assertIsInstance(ctx.exception.__cause__, KeyError)


class MessageBoundingTest(unittest.TestCase):
    """warning_message must stay short and single-line whatever the input."""

    def test_long_message_is_truncated(self) -> None:
        """A provider HTML body cannot blow up the column."""
        message = rpde.truncate_message("x" * 5000)

        self.assertLessEqual(len(message), rpde.MAX_WARNING_MESSAGE_LENGTH)
        self.assertTrue(message.endswith("..."))

    def test_whitespace_is_collapsed(self) -> None:
        """Newlines and tabs from an HTML challenge page collapse to spaces."""
        self.assertEqual(rpde.truncate_message("a\n\tb  \r\n c"), "a b c")

    def test_short_message_is_unchanged(self) -> None:
        """Ordinary messages pass through untouched."""
        self.assertEqual(rpde.truncate_message("HTTP 403 fetching https://x.co"),
                         "HTTP 403 fetching https://x.co")


class IngestionRecordTest(unittest.TestCase):
    """_build_ingestion_records must never emit an unexplained failure row."""

    def setUp(self) -> None:
        self.dataset_url = "https://example.com/dataset"
        self.feeds = [FEED]
        self.lock = threading.Lock()
        counts_patcher = patch.object(main, "get_dataset_feed_opportunity_counts", return_value={})
        counts_patcher.start()
        self.addCleanup(counts_patcher.stop)

    def _state(self, **overrides) -> dict:
        state = main._initialize_feed_states(self.dataset_url, self.feeds)
        state[FEED["id"]].update(overrides)
        return state

    def _build(self, feed_states, persisted, failed, batch_failure_message=None) -> dict:
        records = main._build_ingestion_records(
            self.dataset_url,
            self.feeds,
            feed_states,
            persisted,
            failed,
            {},
            self.lock,
            batch_failure_message=batch_failure_message,
        )
        self.assertEqual(len(records), 1)
        return records[0]

    def test_persisted_complete_feed_has_no_failure_detail(self) -> None:
        """The NULL-on-COMPLETE invariant."""
        states = self._state(status="COMPLETE")
        record = self._build(states, {FEED["id"]}, set())

        self.assertEqual(record["status"], "COMPLETE")
        self.assertIsNone(record["error_code"])
        self.assertIsNone(record["warning_message"])

    def test_persisted_warning_feed_carries_detail_through(self) -> None:
        """A WARNING feed still persists, so its detail comes from feed_states."""
        states = self._state(
            status="WARNING", error_code="SELF_LOOP", warning_message="next URL equals current URL"
        )
        record = self._build(states, {FEED["id"]}, set())

        self.assertEqual(record["status"], "WARNING")
        self.assertEqual(record["error_code"], "SELF_LOOP")
        self.assertEqual(record["warning_message"], "next URL equals current URL")

    def test_failed_batch_records_batch_failure_message(self) -> None:
        """A downstream exception is reported instead of a bare ERROR."""
        states = self._state(previous_afterTimestamp="10", previous_afterId="a")
        record = self._build(
            states, set(), {FEED["id"]}, batch_failure_message="RuntimeError: merge failed"
        )

        self.assertEqual(record["status"], "ERROR")
        self.assertEqual(record["error_code"], "BATCH_FAILED")
        self.assertEqual(record["warning_message"], "RuntimeError: merge failed")
        self.assertEqual(record["afterTimestamp"], "10")
        self.assertEqual(record["afterId"], "a")

    def test_feed_specific_detail_wins_over_batch_message(self) -> None:
        """An RPDE failure names the URL and status, so it is more actionable."""
        states = self._state(
            status="ERROR", error_code="403", warning_message="HTTP 403 fetching https://x.co"
        )
        record = self._build(
            states, set(), {FEED["id"]}, batch_failure_message="RuntimeError: merge failed"
        )

        self.assertEqual(record["error_code"], "403")
        self.assertEqual(record["warning_message"], "HTTP 403 fetching https://x.co")

    def test_unreached_batch_records_not_processed(self) -> None:
        """Feeds in a batch that never ran are neither persisted nor failed."""
        record = self._build(self._state(), set(), set())

        self.assertEqual(record["status"], "ERROR")
        self.assertEqual(record["error_code"], "NOT_PROCESSED")
        self.assertEqual(record["warning_message"], main.NOT_PROCESSED_MESSAGE)

    def test_no_failure_row_is_left_unexplained(self) -> None:
        """Sweep the branches: status and detail agree in every combination."""
        cases = [
            (self._state(status="COMPLETE"), {FEED["id"]}, set(), None),
            (self._state(status="ERROR", error_code="500", warning_message="HTTP 500"),
             {FEED["id"]}, set(), None),
            (self._state(), set(), {FEED["id"]}, "RuntimeError: boom"),
            (self._state(), set(), set(), None),
        ]
        for states, persisted, failed, batch_message in cases:
            with self.subTest(persisted=bool(persisted), failed=bool(failed)):
                record = self._build(states, persisted, failed, batch_message)
                if record["status"] == "COMPLETE":
                    self.assertIsNone(record["error_code"])
                    self.assertIsNone(record["warning_message"])
                else:
                    self.assertIsNotNone(record["error_code"])
                    self.assertIsNotNone(record["warning_message"])
                    self.assertNotEqual(record["warning_message"], "")


if __name__ == "__main__":
    unittest.main()
