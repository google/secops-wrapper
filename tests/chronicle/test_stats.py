"""Tests for Chronicle stats functionality."""

import unittest
from unittest import mock
from datetime import datetime, timedelta, timezone

from secops.chronicle.stats import get_stats, process_stats_results
from secops.chronicle.models import APIVersion
from secops.exceptions import APIError


class TestChronicleStats(unittest.TestCase):
    """Tests for Chronicle stats functionality."""

    def setUp(self) -> None:
        self.mock_client = mock.MagicMock()
        self.start_time = datetime.now(tz=timezone.utc) - timedelta(days=7)
        self.end_time = datetime.now(tz=timezone.utc)

    @mock.patch("secops.chronicle.stats.chronicle_request")
    def test_get_stats_regular_values(self, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "col1",
                        "values": [
                            {"value": {"stringVal": "value1"}},
                            {"value": {"stringVal": "value2"}},
                        ],
                    },
                    {
                        "column": "col2",
                        "values": [
                            {"value": {"int64Val": "10"}},
                            {"value": {"int64Val": "20"}},
                        ],
                    },
                ]
            }
        }

        result = get_stats(self.mock_client, "test query", self.start_time, self.end_time)

        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["columns"], ["col1", "col2"])
        self.assertEqual(result["rows"][0], {"col1": "value1", "col2": 10})
        self.assertEqual(result["rows"][1], {"col1": "value2", "col2": 20})

        # Verify get_stats called chronicle_request with expected args/params
        mock_chronicle_request.assert_called_once()
        _, kwargs = mock_chronicle_request.call_args

        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["endpoint_path"], ":udmSearch")
        self.assertEqual(kwargs["api_version"], APIVersion.V1ALPHA)

        params = kwargs["params"]
        self.assertEqual(params["query"], "test query")
        self.assertEqual(params["limit"], 60)
        self.assertEqual(
            params["timeRange.start_time"],
            self.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(
            params["timeRange.end_time"],
            self.end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )

    @mock.patch("secops.chronicle.stats.chronicle_request")
    def test_get_stats_array_distinct(self, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "array_col",
                        "values": [
                            {"list": {"values": [{"stringVal": "X1"}, {"stringVal": "X2"}]}},
                            {"list": {"values": [{"stringVal": "Y1"}, {"stringVal": "Y2"}]}},
                        ],
                    }
                ]
            }
        }

        result = get_stats(
            self.mock_client,
            "test query with array_distinct",
            self.start_time,
            self.end_time,
        )

        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["columns"], ["array_col"])
        self.assertEqual(result["rows"][0]["array_col"], ["X1", "X2"])
        self.assertEqual(result["rows"][1]["array_col"], ["Y1", "Y2"])

    @mock.patch("secops.chronicle.stats.chronicle_request")
    def test_get_stats_timestamp_values(self, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "timestamp_col",
                        "values": [
                            {"value": {"timestampVal": "2024-01-15T10:30:00Z"}},
                            {"value": {"timestampVal": "2024-01-15T11:45:30.123Z"}},
                        ],
                    },
                    {
                        "column": "event_count",
                        "values": [
                            {"value": {"int64Val": "100"}},
                            {"value": {"int64Val": "200"}},
                        ],
                    },
                ]
            }
        }

        result = get_stats(self.mock_client, "test query", self.start_time, self.end_time)

        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["columns"], ["timestamp_col", "event_count"])
        self.assertIsInstance(result["rows"][0]["timestamp_col"], datetime)
        self.assertIsInstance(result["rows"][1]["timestamp_col"], datetime)
        self.assertEqual(result["rows"][0]["event_count"], 100)
        self.assertEqual(result["rows"][1]["event_count"], 200)

    @mock.patch("secops.chronicle.stats.chronicle_request")
    def test_get_stats_timestamp_in_list(self, mock_chronicle_request: mock.MagicMock) -> None:
        mock_chronicle_request.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "timestamp_array",
                        "values": [
                            {
                                "list": {
                                    "values": [
                                        {"timestampVal": "2024-01-15T10:00:00Z"},
                                        {"timestampVal": "2024-01-15T11:00:00Z"},
                                    ]
                                }
                            }
                        ],
                    }
                ]
            }
        }

        result = get_stats(self.mock_client, "test query", self.start_time, self.end_time)

        self.assertEqual(result["total_rows"], 1)
        self.assertEqual(result["columns"], ["timestamp_array"])
        self.assertIsInstance(result["rows"][0]["timestamp_array"], list)
        self.assertEqual(len(result["rows"][0]["timestamp_array"]), 2)
        self.assertIsInstance(result["rows"][0]["timestamp_array"][0], datetime)
        self.assertIsInstance(result["rows"][0]["timestamp_array"][1], datetime)

    @mock.patch("secops.chronicle.stats.chronicle_request")
    def test_get_stats_malformed_response_missing_stats_key(
        self, mock_chronicle_request: mock.MagicMock
    ) -> None:
        """Test that get_stats raises APIError when response missing stats."""
        mock_chronicle_request.return_value = {
            "someOtherKey": "value",
            "events": [],
        }

        with self.assertRaises(APIError) as context:
            get_stats(
                self.mock_client, "test query", self.start_time, self.end_time
            )

        self.assertIn("No stats found in response", str(context.exception))

    @mock.patch("secops.chronicle.stats.chronicle_request")
    def test_get_stats_api_error_propagation(
        self, mock_chronicle_request: mock.MagicMock
    ) -> None:
        """Test that APIError from chronicle_request propagates correctly."""
        mock_chronicle_request.side_effect = APIError(
            "API request failed: method=GET, url=test-url, "
            "status=500, response={'error': 'Internal server error'}"
        )

        with self.assertRaises(APIError) as context:
            get_stats(
                self.mock_client, "test query", self.start_time, self.end_time
            )

        self.assertIn("API request failed", str(context.exception))
        self.assertIn("status=500", str(context.exception))

    def test_process_stats_results_empty(self) -> None:
        result = process_stats_results({})
        self.assertEqual(result["total_rows"], 0)
        self.assertEqual(result["columns"], [])
        self.assertEqual(result["rows"], [])


if __name__ == "__main__":
    unittest.main()
