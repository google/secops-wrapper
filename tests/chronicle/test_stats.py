"""Tests for Chronicle stats functionality."""

import unittest
from unittest import mock
from datetime import datetime, timedelta
from typing import Dict, Any

from secops.chronicle.stats import get_stats, process_stats_results


class TestChronicleStats(unittest.TestCase):
    """Tests for Chronicle stats functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_client = mock.MagicMock()
        self.mock_client.instance_id = "test-instance"
        self.mock_client.base_url = "https://test-url.com"
        self.mock_session = mock.MagicMock()
        self.mock_client.session = self.mock_session
        self.start_time = datetime.now() - timedelta(days=7)
        self.end_time = datetime.now()

    def test_get_stats_regular_values(self) -> None:
        """Test get_stats with regular single value results."""
        # Mock response data with simple values
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
        self.mock_session.get.return_value = mock_response

        # Execute the function
        result = get_stats(
            self.mock_client, "test query", self.start_time, self.end_time
        )

        # Assertions
        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["columns"], ["col1", "col2"])
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][0], {"col1": "value1", "col2": 10})
        self.assertEqual(result["rows"][1], {"col1": "value2", "col2": 20})

    def test_get_stats_array_distinct(self) -> None:
        """Test get_stats with array_distinct returning list values."""
        # Mock response with array_distinct list structure
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "array_col",
                        "values": [
                            {
                                "list": {
                                    "values": [{"stringVal": "X1"}, {"stringVal": "X2"}]
                                }
                            },
                            {
                                "list": {
                                    "values": [{"stringVal": "Y1"}, {"stringVal": "Y2"}]
                                }
                            },
                        ],
                    }
                ]
            }
        }
        self.mock_session.get.return_value = mock_response

        # Execute the function
        result = get_stats(
            self.mock_client,
            "test query with array_distinct",
            self.start_time,
            self.end_time,
        )

        # This will fail with the current implementation, but after our fix
        # it should handle array_distinct properly
        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["columns"], ["array_col"])
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][0]["array_col"], ["X1", "X2"])
        self.assertEqual(result["rows"][1]["array_col"], ["Y1", "Y2"])

    def test_get_stats_timestamp_values(self) -> None:
        """Test get_stats with timestampVal support."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "timestamp_col",
                        "values": [
                            {"value": {"timestampVal": "2024-01-15T10:30:00Z"}},
                            {
                                "value": {
                                    "timestampVal": "2024-01-15T11:45:30.123Z"
                                }
                            },
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
        self.mock_session.get.return_value = mock_response

        result = get_stats(
            self.mock_client, "test query", self.start_time, self.end_time
        )

        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["columns"], ["timestamp_col", "event_count"])
        self.assertEqual(len(result["rows"]), 2)
        self.assertIsInstance(result["rows"][0]["timestamp_col"], datetime)
        self.assertIsInstance(result["rows"][1]["timestamp_col"], datetime)
        self.assertEqual(result["rows"][0]["event_count"], 100)
        self.assertEqual(result["rows"][1]["event_count"], 200)

    def test_get_stats_timestamp_in_list(self) -> None:
        """Test get_stats with timestampVal in list values."""
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "stats": {
                "results": [
                    {
                        "column": "timestamp_array",
                        "values": [
                            {
                                "list": {
                                    "values": [
                                        {
                                            "timestampVal": (
                                                "2024-01-15T10:00:00Z"
                                            )
                                        },
                                        {
                                            "timestampVal": (
                                                "2024-01-15T11:00:00Z"
                                            )
                                        },
                                    ]
                                }
                            },
                        ],
                    }
                ]
            }
        }
        self.mock_session.get.return_value = mock_response

        result = get_stats(
            self.mock_client, "test query", self.start_time, self.end_time
        )

        self.assertEqual(result["total_rows"], 1)
        self.assertEqual(result["columns"], ["timestamp_array"])
        self.assertEqual(len(result["rows"]), 1)
        self.assertIsInstance(result["rows"][0]["timestamp_array"], list)
        self.assertEqual(len(result["rows"][0]["timestamp_array"]), 2)
        self.assertIsInstance(result["rows"][0]["timestamp_array"][0], datetime)
        self.assertIsInstance(result["rows"][0]["timestamp_array"][1], datetime)

    def test_process_stats_results_empty(self) -> None:
        """Test processing empty stats results."""
        empty_stats: Dict[str, Any] = {}
        result = process_stats_results(empty_stats)

        self.assertEqual(result["total_rows"], 0)
        self.assertEqual(result["columns"], [])
        self.assertEqual(result["rows"], [])


if __name__ == "__main__":
    unittest.main()
