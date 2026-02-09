"""Tests for Chronicle UDM search functionality (search_udm)."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

from secops.chronicle.models import APIVersion
from secops.chronicle.search import search_udm


class TestChronicleUdmSearch(unittest.TestCase):
    """Tests for Chronicle search functionality."""

    def setUp(self) -> None:
        self.client = mock.MagicMock()
        self.start_time = datetime.now(tz=timezone.utc) - timedelta(days=1)
        self.end_time = datetime.now(tz=timezone.utc)

    @mock.patch("secops.chronicle.search.chronicle_request")
    def test_search_udm_returns_expected_shape(self, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.return_value = {
            "events": [{"id": 1}, {"id": 2}],
            "moreDataAvailable": True,
        }

        result = search_udm(
            client=self.client,
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=self.start_time,
            end_time=self.end_time,
            max_events=500,
        )

        self.assertEqual(result["events"], [{"id": 1}, {"id": 2}])
        self.assertEqual(result["total_events"], 2)
        self.assertTrue(result["more_data_available"])

        mock_chronicle_request.assert_called_once()
        _, kwargs = mock_chronicle_request.call_args

        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["endpoint_path"], ":udmSearch")
        self.assertEqual(kwargs["api_version"], APIVersion.V1ALPHA)

        params = kwargs["params"]
        self.assertEqual(params["query"], 'metadata.event_type = "NETWORK_CONNECTION"')
        self.assertEqual(params["limit"], 500)
        self.assertEqual(
            params["timeRange.start_time"],
            self.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(
            params["timeRange.end_time"],
            self.end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )

    @mock.patch("secops.chronicle.search.chronicle_request")
    def test_search_udm_defaults_when_keys_missing(self, mock_chronicle_request: mock.MagicMock) -> None:
        # Missing "events" and "moreDataAvailable" should default safely
        mock_chronicle_request.return_value = {}

        result = search_udm(
            client=self.client,
            query="q",
            start_time=self.start_time,
            end_time=self.end_time,
        )

        self.assertEqual(result["events"], [])
        self.assertEqual(result["total_events"], 0)
        self.assertFalse(result["more_data_available"])

    @mock.patch("secops.chronicle.search.chronicle_request")
    @mock.patch("builtins.print")
    def test_search_udm_debug_prints(self, mock_print: mock.MagicMock, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.return_value = {"events": []}

        search_udm(
            client=self.client,
            query="q",
            start_time=self.start_time,
            end_time=self.end_time,
            debug=True,
        )

        # Two prints: query + time range
        self.assertGreaterEqual(mock_print.call_count, 2)

    @mock.patch("secops.chronicle.search.chronicle_request")
    def test_search_udm_propagates_api_error(self, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.side_effect = Exception("boom")

        with self.assertRaises(Exception) as ctx:
            search_udm(
                client=self.client,
                query="q",
                start_time=self.start_time,
                end_time=self.end_time,
            )

        self.assertIn("boom", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
