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
"""Tests for the Dashboard query module."""
import json
from unittest.mock import ANY, Mock, patch

import pytest

from secops.chronicle import dashboard_query
from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import InputInterval
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client() -> ChronicleClient:
    """Create a mock Chronicle client for testing.

    Returns:
        A mock ChronicleClient instance.
    """
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        client = ChronicleClient(
            customer_id="test-customer", project_id="test-project"
        )
        client.base_url = "https://testapi.com"
        client.instance_id = "test-project/locations/test-location"
        return client


@pytest.fixture
def response_mock() -> Mock:
    """Create a mock API response object.

    Returns:
        A mock response object.
    """
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"name": "test-dashboard"}
    return mock


class TestExecuteQuery:
    """Test the execute_query function."""

    @pytest.fixture
    def interval(self) -> InputInterval:
        """Create a sample interval for testing.

        Returns:
            An InputInterval instance.
        """
        return InputInterval(
            relative_time={"timeUnit": "DAY", "startTimeVal": "1"}
        )

    def test_execute_query_success(
        self,
        chronicle_client: ChronicleClient,
        response_mock: Mock,
        interval: InputInterval,
    ) -> None:
        """Test execute_query function with successful response."""
        response_mock.json.return_value = {
            "results": [{"value": "test-result"}]
        }
        chronicle_client.session.request.return_value = response_mock
        query = 'udm.metadata.event_type = "PROCESS_LAUNCH"'

        result = dashboard_query.execute_query(
            chronicle_client, query=query, interval=interval
        )

        url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "dashboardQueries:execute"
        )
        payload = {
            "query": {
                "query": 'udm.metadata.event_type = "PROCESS_LAUNCH"',
                "input": interval.to_dict(),
            }
        }
        chronicle_client.session.request.assert_called_once_with(
            method="POST",
            url=url,
            params=None,
            json=payload,
            headers=ANY,
            timeout=None,
        )

        assert "results" in result
        assert result["results"][0]["value"] == "test-result"

    def test_execute_query_with_filters(
        self,
        chronicle_client: ChronicleClient,
        response_mock: Mock,
        interval: InputInterval,
    ) -> None:
        """Test execute_query with filters parameter."""
        response_mock.json.return_value = {"results": []}
        chronicle_client.session.request.return_value = response_mock
        query = 'udm.metadata.event_type = "PROCESS_LAUNCH"'
        filters = [{"field": "hostname", "value": "test-host"}]

        result = dashboard_query.execute_query(
            chronicle_client, query=query, interval=interval, filters=filters
        )

        url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "dashboardQueries:execute"
        )
        payload = {
            "query": {"query": query, "input": interval.to_dict()},
            "filters": filters,
        }
        chronicle_client.session.request.assert_called_once_with(
            method="POST",
            url=url,
            params=None,
            json=payload,
            headers=ANY,
            timeout=None,
        )

        assert "results" in result

    def test_execute_query_with_clear_cache(
        self,
        chronicle_client: ChronicleClient,
        response_mock: Mock,
        interval: InputInterval,
    ) -> None:
        """Test execute_query with clear_cache parameter."""
        response_mock.json.return_value = {"results": []}
        chronicle_client.session.request.return_value = response_mock
        query = 'udm.metadata.event_type = "PROCESS_LAUNCH"'

        result = dashboard_query.execute_query(
            chronicle_client, query=query, interval=interval, clear_cache=True
        )

        url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "dashboardQueries:execute"
        )
        payload = {
            "query": {"query": query, "input": interval.to_dict()},
            "clearCache": True,
        }
        chronicle_client.session.request.assert_called_once_with(
            method="POST",
            url=url,
            params=None,
            json=payload,
            headers=ANY,
            timeout=None,
        )

        assert "results" in result

    def test_execute_query_with_string_json(
        self, chronicle_client: ChronicleClient, response_mock: Mock
    ) -> None:
        """Test execute_query with string JSON interval."""
        response_mock.json.return_value = {"results": []}
        chronicle_client.session.request.return_value = response_mock
        query = 'udm.metadata.event_type = "PROCESS_LAUNCH"'
        interval_str = (
            '{"relativeTime": {"timeUnit": "DAY", "startTimeVal": "1"}}'
        )

        result = dashboard_query.execute_query(
            chronicle_client, query=query, interval=interval_str
        )

        chronicle_client.session.request.assert_called_once_with(
            method="POST",
            url=(
                f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
                "dashboardQueries:execute"
            ),
            params=None,
            json={"query": {"query": query, "input": json.loads(interval_str)}},
            headers=ANY,
            timeout=None,
        )

        assert "results" in result

    def test_execute_query_error(
        self,
        chronicle_client: ChronicleClient,
        response_mock: Mock,
        interval: InputInterval,
    ) -> None:
        """Test execute_query function with error response."""
        response_mock.status_code = 400
        response_mock.text = "Invalid Query"
        chronicle_client.session.request.return_value = response_mock
        query = "invalid query syntax"

        with pytest.raises(APIError, match="Failed to execute query"):
            dashboard_query.execute_query(
                chronicle_client, query=query, interval=interval
            )


class TestGetExecuteQuery:
    """Test the get_execute_query function."""

    def test_get_execute_query_success(
        self, chronicle_client: ChronicleClient, response_mock: Mock
    ) -> None:
        """Test get_execute_query function with successful response."""
        # Setup mock response
        response_mock.json.return_value = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "displayName": "Test Query",
            "query": 'udm.metadata.event_type = "PROCESS_LAUNCH"',
        }
        chronicle_client.session.request.return_value = response_mock
        query_id = "test-query"

        # Call function
        result = dashboard_query.get_execute_query(chronicle_client, query_id)

        # Verify API call
        url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            f"dashboardQueries/{query_id}"
        )
        chronicle_client.session.request.assert_called_once_with(
            method="GET",
            url=url,
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )

        # Verify result
        assert result["name"].endswith("/test-query")
        assert result["displayName"] == "Test Query"

    def test_get_execute_query_with_full_id(
        self, chronicle_client: ChronicleClient, response_mock: Mock
    ) -> None:
        """Test get_execute_query with full project path query ID."""
        # Setup mock response
        response_mock.json.return_value = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "displayName": "Test Query",
            "query": 'udm.metadata.event_type = "PROCESS_LAUNCH"',
        }
        chronicle_client.session.request.return_value = response_mock

        # Full project path query ID
        query_id = "projects/test-project/locations/test-location/dashboardQueries/test-query"
        expected_id = "test-query"

        # Call function
        result = dashboard_query.get_execute_query(chronicle_client, query_id)

        # Verify API call uses the extracted ID
        url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            f"dashboardQueries/{expected_id}"
        )
        chronicle_client.session.request.assert_called_once_with(
            method="GET",
            url=url,
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )

        # Verify result
        assert result["displayName"] == "Test Query"

    def test_get_execute_query_error(
        self, chronicle_client: ChronicleClient, response_mock: Mock
    ) -> None:
        """Test get_execute_query function with error response."""
        # Setup error response
        response_mock.status_code = 404
        response_mock.text = "Query not found"
        chronicle_client.session.request.return_value = response_mock
        query_id = "nonexistent-query"

        # Verify the function raises an APIError
        with pytest.raises(APIError, match="Failed to get query"):
            dashboard_query.get_execute_query(chronicle_client, query_id)
