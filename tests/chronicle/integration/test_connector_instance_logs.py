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
"""Tests for Chronicle integration connector instance logs functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.connector_instance_logs import (
    list_connector_instance_logs,
    get_connector_instance_log,
)
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer",
            project_id="test-project",
            default_api_version=APIVersion.V1BETA,
        )


# -- list_connector_instance_logs tests --


def test_list_connector_instance_logs_success(chronicle_client):
    """Test list_connector_instance_logs delegates to paginated request."""
    expected = {
        "logs": [{"name": "log1"}, {"name": "log2"}],
        "nextPageToken": "t",
    }

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.connector_instance_logs.format_resource_id",
        return_value="My Integration",
    ):
        result = list_connector_instance_logs(
            chronicle_client,
            integration_name="My Integration",
            connector_id="c1",
            connector_instance_id="ci1",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert "connectors/c1/connectorInstances/ci1/logs" in kwargs["path"]
        assert kwargs["items_key"] == "logs"
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "next-token"


def test_list_connector_instance_logs_default_args(chronicle_client):
    """Test list_connector_instance_logs with default args."""
    expected = {"logs": []}

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_paginated_request",
        return_value=expected,
    ):
        result = list_connector_instance_logs(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
        )

        assert result == expected


def test_list_connector_instance_logs_with_filters(chronicle_client):
    """Test list_connector_instance_logs with filter and order_by."""
    expected = {"logs": [{"name": "log1"}]}

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_instance_logs(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            filter_string='severity = "ERROR"',
            order_by="timestamp desc",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": 'severity = "ERROR"',
            "orderBy": "timestamp desc",
        }


def test_list_connector_instance_logs_as_list(chronicle_client):
    """Test list_connector_instance_logs returns list when as_list=True."""
    expected = [{"name": "log1"}, {"name": "log2"}]

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_instance_logs(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_connector_instance_logs_error(chronicle_client):
    """Test list_connector_instance_logs raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_paginated_request",
        side_effect=APIError("Failed to list connector instance logs"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_connector_instance_logs(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
            )
        assert "Failed to list connector instance logs" in str(exc_info.value)


# -- get_connector_instance_log tests --


def test_get_connector_instance_log_success(chronicle_client):
    """Test get_connector_instance_log issues GET request."""
    expected = {
        "name": "logs/log1",
        "message": "Test log message",
        "severity": "INFO",
        "timestamp": "2026-03-09T10:00:00Z",
    }

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_instance_log(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            log_id="log1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "connectors/c1/connectorInstances/ci1/logs/log1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_connector_instance_log_error(chronicle_client):
    """Test get_connector_instance_log raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_request",
        side_effect=APIError("Failed to get connector instance log"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_connector_instance_log(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
                log_id="log1",
            )
        assert "Failed to get connector instance log" in str(exc_info.value)


# -- API version tests --


def test_list_connector_instance_logs_custom_api_version(chronicle_client):
    """Test list_connector_instance_logs with custom API version."""
    expected = {"logs": []}

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_instance_logs(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_get_connector_instance_log_custom_api_version(chronicle_client):
    """Test get_connector_instance_log with custom API version."""
    expected = {"name": "logs/log1"}

    with patch(
        "secops.chronicle.integration.connector_instance_logs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_instance_log(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            log_id="log1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA

