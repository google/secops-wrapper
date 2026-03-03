# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests for Chronicle raw log search functionality."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pytest

from secops.chronicle.log_search import search_raw_logs
from secops.chronicle.models import APIVersion
from secops.exceptions import APIError


@pytest.fixture
def client():
    return Mock()


def test_search_raw_logs_calls_chronicle_request_correctly(client):
    start_time = datetime(2023, 1, 1, 12, 0, 0)
    end_time = datetime(2023, 1, 2, 12, 0, 0)
    query = 'user = "foo"'

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        search_raw_logs(
            client,
            query=query,
            start_time=start_time,
            end_time=end_time,
            log_types=["OKTA", "AWS"],
            case_sensitive=True,
        )

        mock_request.assert_called_once()
        kwargs = mock_request.call_args.kwargs
        json_body = kwargs["json"]

        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == ":searchRawLogs"
        assert kwargs["api_version"] == APIVersion.V1ALPHA

        assert json_body["baselineQuery"] == query
        assert (
            json_body["baselineTimeRange"]["startTime"]
            == "2023-01-01T12:00:00.000000Z"
        )
        assert (
            json_body["baselineTimeRange"]["endTime"]
            == "2023-01-02T12:00:00.000000Z"
        )
        assert json_body["caseSensitive"] is True
        assert json_body["logTypes"] == [
            {"displayName": "OKTA"},
            {"displayName": "AWS"},
        ]


def test_search_raw_logs_defaults(client):
    """Test that default values are used when optional params not set."""
    start_time = datetime(2023, 1, 1, 12, 0, 0)
    end_time = datetime(2023, 1, 2, 12, 0, 0)
    query = 'user = "foo"'

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        search_raw_logs(
            client,
            query=query,
            start_time=start_time,
            end_time=end_time,
        )

        mock_request.assert_called_once()
        kwargs = mock_request.call_args.kwargs
        json_body = kwargs["json"]

        assert json_body["caseSensitive"] is False
        assert "logTypes" not in json_body
        assert "snapshotQuery" not in json_body
        assert "maxAggregationsPerField" not in json_body
        assert "pageSize" not in json_body


def test_search_raw_logs_with_empty_log_types(client):
    """Test that empty log_types list is not included in request."""
    start_time = datetime(2023, 1, 1, 12, 0, 0)
    end_time = datetime(2023, 1, 2, 12, 0, 0)
    query = "test"

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        search_raw_logs(
            client,
            query=query,
            start_time=start_time,
            end_time=end_time,
            log_types=[],
        )

        kwargs = mock_request.call_args.kwargs
        json_body = kwargs["json"]

        assert "logTypes" not in json_body


def test_search_raw_logs_with_all_optional_params(client):
    """Test search with all optional parameters set."""
    start_time = datetime(2023, 1, 1, 12, 0, 0)
    end_time = datetime(2023, 1, 2, 12, 0, 0)
    query = 'raw = "test"'

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        mock_request.return_value = {"results": []}

        result = search_raw_logs(
            client,
            query=query,
            start_time=start_time,
            end_time=end_time,
            snapshot_query='status = "success"',
            case_sensitive=True,
            log_types=["WINDOWS", "LINUX"],
            max_aggregations_per_field=200,
            page_size=25,
        )

        kwargs = mock_request.call_args.kwargs
        json_body = kwargs["json"]

        assert json_body["baselineQuery"] == query
        assert json_body["snapshotQuery"] == 'status = "success"'
        assert json_body["caseSensitive"] is True
        assert json_body["logTypes"] == [
            {"displayName": "WINDOWS"},
            {"displayName": "LINUX"},
        ]
        assert json_body["maxAggregationsPerField"] == 200
        assert json_body["pageSize"] == 25
        assert result == {"results": []}


def test_search_raw_logs_with_timezone_aware_datetime(client):
    """Test that timezone-aware datetime objects are formatted."""
    start_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
    query = "test"

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        search_raw_logs(
            client,
            query=query,
            start_time=start_time,
            end_time=end_time,
        )

        kwargs = mock_request.call_args.kwargs
        json_body = kwargs["json"]

        assert (
            json_body["baselineTimeRange"]["startTime"]
            == "2023-01-01T12:00:00.000000Z"
        )
        assert (
            json_body["baselineTimeRange"]["endTime"]
            == "2023-01-02T12:00:00.000000Z"
        )


def test_search_raw_logs_with_microseconds(client):
    """Test that microseconds are preserved in timestamps."""
    start_time = datetime(2023, 1, 1, 12, 0, 0, 123456)
    end_time = datetime(2023, 1, 2, 12, 0, 0, 654321)
    query = "test"

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        search_raw_logs(
            client,
            query=query,
            start_time=start_time,
            end_time=end_time,
        )

        kwargs = mock_request.call_args.kwargs
        json_body = kwargs["json"]

        assert (
            json_body["baselineTimeRange"]["startTime"]
            == "2023-01-01T12:00:00.123456Z"
        )
        assert (
            json_body["baselineTimeRange"]["endTime"]
            == "2023-01-02T12:00:00.654321Z"
        )


def test_search_raw_logs_propagates_api_error(client):
    """Test that API errors are propagated correctly."""
    start_time = datetime(2023, 1, 1, 12, 0, 0)
    end_time = datetime(2023, 1, 2, 12, 0, 0)
    query = "test"

    with patch("secops.chronicle.log_search.chronicle_request") as mock_request:
        mock_request.side_effect = APIError("Request failed")

        with pytest.raises(APIError, match="Request failed"):
            search_raw_logs(
                client,
                query=query,
                start_time=start_time,
                end_time=end_time,
            )
