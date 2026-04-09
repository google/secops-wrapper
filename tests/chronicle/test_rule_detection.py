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
"""Tests for the Rule Detection module."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from secops.chronicle import rule_detection
from secops.chronicle.client import ChronicleClient
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a mock Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer", project_id="test-project"
        )


@pytest.fixture
def response_mock():
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "detections": [
            {
                "id": "de_12345678-1234-1234-1234-1234567890ab",
                "type": "RULE_DETECTION",
                "createdTime": "2025-01-01T12:00:00.000000Z",
                "detectionTime": "2025-01-01T12:00:00.000000Z",
                "timeWindow": {
                    "startTime": "2025-01-01T11:00:00.000000Z",
                    "endTime": "2025-01-01T12:00:00.000000Z",
                },
                "detection": [
                    {
                        "ruleId": "ru_12345678-1234-1234-1234-1234567890ab",
                        "ruleVersion": "ru_12345678-1234-1234-1234-1234567890ab@v_100000_000_000",
                        "ruleName": "Rule 123",
                        "description": "Rule 123 description",
                        "alertState": "ALERTING",
                        "ruleType": "MULTI_EVENT",
                    }
                ],
            },
        ],
        "nextPageToken": "next-1",
    }
    return mock


# --- list_detections Tests ---


def test_list_detections_minimal(chronicle_client, response_mock):
    """Test list_detections with minimal required parameters."""
    chronicle_client.session.request.return_value = response_mock

    result = rule_detection.list_detections(
        chronicle_client, 
        rule_id="ru_12345678-1234-1234-1234-1234567890ab",
        page_size=2
    )

    chronicle_client.session.request.assert_called_once_with(
        method="GET",
        url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/legacy:legacySearchDetections",
        params={
            "pageSize": 2,
            "rule_id": "ru_12345678-1234-1234-1234-1234567890ab",
            "listBasis": "LIST_BASIS_UNSPECIFIED",
        },
        json=None,
        headers=None,
        timeout=None,
    )
    assert result == response_mock.json()


def test_list_detections_all_params(chronicle_client, response_mock):
    """Test list_detections with all optional parameters set."""
    chronicle_client.session.request.return_value = response_mock

    start_time = datetime(2025, 1, 1, 12, 0, 0)
    end_time = datetime(2025, 1, 2, 13, 30, 15)

    result = rule_detection.list_detections(
        client=chronicle_client,
        rule_id="ru_12345678-1234-1234-1234-1234567890ab",
        start_time=start_time,
        end_time=end_time,
        list_basis="DETECTION_TIME",
        alert_state="ALERTING",
        page_size=25,
        page_token="next-1",
    )

    chronicle_client.session.request.assert_called_once_with(
        method="GET",
        url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/legacy:legacySearchDetections",
        params={
            "rule_id": "ru_12345678-1234-1234-1234-1234567890ab",
            "alertState": "ALERTING",
            "listBasis": "DETECTION_TIME",
            "startTime": "2025-01-01T12:00:00.000000Z",
            "endTime": "2025-01-02T13:30:15.000000Z",
            "pageSize": 25,
            "pageToken": "next-1",
        },
        json=None,
        headers=None,
        timeout=None,
    )
    assert result == response_mock.json()


def test_list_detections_invalid_alert_state(chronicle_client, response_mock):
    """Test list_detections raises on invalid alert_state value."""
    chronicle_client.session.request.return_value = response_mock

    with pytest.raises(ValueError, match="alert_state must be one of"):
        rule_detection.list_detections(
            chronicle_client, rule_id="ru_123", alert_state="BAD_STATE"
        )


def test_list_detections_invalid_list_basis(chronicle_client, response_mock):
    """Test list_detections raises on invalid list_basis value."""
    chronicle_client.session.request.return_value = response_mock

    with pytest.raises(ValueError, match="list_basis must be one of"):
        rule_detection.list_detections(
            chronicle_client, rule_id="ru_123", list_basis="BAD_BASIS"
        )


def test_list_detections_api_error(chronicle_client, response_mock):
    """Test list_detections raises APIError on non-200 response."""
    response_mock.status_code = 500
    response_mock.text = "Internal Error"
    chronicle_client.session.request.return_value = response_mock

    with pytest.raises(APIError, match="API request failed"):
        rule_detection.list_detections(chronicle_client, rule_id="ru_123")


# --- list_errors Tests ---


def test_list_errors_minimal(chronicle_client, response_mock):
    """Test list_errors with minimal required parameters."""
    chronicle_client.session.request.return_value = response_mock

    result = rule_detection.list_errors(
        chronicle_client, rule_id="ru_12345678-1234-1234-1234-1234567890ab"
    )

    expected_filter = f'rule = "{chronicle_client.instance_id}/rules/ru_12345678-1234-1234-1234-1234567890ab"'
    chronicle_client.session.request.assert_called_once_with(
        method="GET",
        url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/ruleExecutionErrors",
        params={"filter": expected_filter},
        json=None,
        headers=None,
        timeout=None,
    )
    assert result == response_mock.json()


def test_list_errors_api_error(chronicle_client, response_mock):
    """Test list_errors raises APIError on non-200 response."""
    response_mock.status_code = 404
    response_mock.text = "Not Found"
    chronicle_client.session.request.return_value = response_mock

    with pytest.raises(APIError, match="Failed to list rule errors"):
        rule_detection.list_errors(chronicle_client, rule_id="ru_missing")


def test_list_detections_as_list(chronicle_client, response_mock):
    """Test list_detections returning a list when as_list=True."""
    chronicle_client.session.request.return_value = response_mock

    result = rule_detection.list_detections(
        chronicle_client,
        rule_id="ru_12345678-1234-1234-1234-1234567890ab",
        page_size=1,
        as_list=True,
    )

    chronicle_client.session.request.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "de_12345678-1234-1234-1234-1234567890ab"
