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
from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from secops.chronicle.log_search import search_raw_logs
from secops.chronicle.models import APIVersion


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
            allow_partial_results=True,
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
        assert json_body["allowPartialResults"] is True


def test_search_raw_logs_defaults(client):
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
        assert "allowPartialResults" not in json_body
