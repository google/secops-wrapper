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
"""Tests for Chronicle rule functions."""

import pytest
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.rule import (
    create_rule,
    get_rule,
    list_rules,
    update_rule,
    delete_rule,
    enable_rule,
    search_rules,
    run_rule_test,
)
from secops.exceptions import APIError, SecOpsError
from datetime import datetime, timezone
import json


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer", project_id="test-project",
            default_api_version=APIVersion.V1
        )


@pytest.fixture
def mock_response():
    """Create a mock API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/rules/ru_12345"
    }
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock


@pytest.fixture
def mock_streaming_response():
    """Create a mock streaming API response."""
    mock = Mock()
    mock.status_code = 200

    # Create an iterable with simulated chunks of streamed response
    chunks = [
        '{"type": "progress", "percentDone": 10}\n',
        '{"type": "progress", "percentDone": 50}\n',
        '{"type": "detection", "detection": {"rule_id": "rule1", "data": "test"}}\n',
        '{"type": "progress", "percentDone": 100}\n',
    ]

    # Set up the iter_content method to return our chunks
    mock.iter_content.return_value = chunks

    return mock


def test_create_rule(chronicle_client, mock_response):
    """Test create_rule function."""
    # Arrange
    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        # Act
        result = create_rule(chronicle_client, "rule test {}")

        # Assert
        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules",
            json={"text": "rule test {}"},
        )
        assert result == mock_response.json.return_value


def test_create_rule_error(chronicle_client, mock_error_response):
    """Test create_rule function with error response."""
    # Arrange
    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            create_rule(chronicle_client, "rule test {}")

        assert "Failed to create rule" in str(exc_info.value)


def test_get_rule(chronicle_client, mock_response):
    """Test get_rule function."""
    # Arrange
    rule_id = "ru_12345"
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        # Act
        result = get_rule(chronicle_client, rule_id)

        # Assert
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}"
        )
        assert result == mock_response.json.return_value


def test_get_rule_error(chronicle_client, mock_error_response):
    """Test get_rule function with error response."""
    # Arrange
    rule_id = "ru_12345"
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            get_rule(chronicle_client, rule_id)

        assert "Failed to get rule" in str(exc_info.value)


def test_list_rules(chronicle_client, mock_response):
    """Test list_rules function with single page."""
    # Arrange
    mock_response.json.return_value = {
        "rules": [{"name": "rule1"}, {"name": "rule2"}]
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        # Act
        result = list_rules(chronicle_client)

        # Assert
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules",
            params={"pageSize": 1000, "view": "FULL"},
        )
        assert result == mock_response.json.return_value
        assert len(result["rules"]) == 2


def test_list_rules_empty(chronicle_client, mock_response):
    """Test list_rules function with no rules"""
    # Arrange
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        # Act
        result = list_rules(chronicle_client)

        # Assert
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules",
            params={"pageSize": 1000, "view": "FULL"},
        )
        assert result == {"rules": []}
        assert len(result["rules"]) == 0


def test_list_rules_pagination(chronicle_client):
    """Test list_rules function with pagination."""

    # Arrange
    def get_mock_response(url, **kwargs):
        params = kwargs.get("params", {})
        if "pageToken" not in params:
            # First page response
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "rules": [{"name": "rule1"}, {"name": "rule2"}],
                "nextPageToken": "page2token",
            }
            return response
        elif params["pageToken"] == "page2token":
            # Second page response
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "rules": [{"name": "rule3"}, {"name": "rule4"}],
            }
            return response
        else:
            raise ValueError(f"Unexpected pageToken: {params.get('pageToken')}")

    # Setup session.get to use our dynamic mock response function
    with patch.object(chronicle_client.session, "get") as mock_get:
        mock_get.side_effect = get_mock_response

        # Act
        result = list_rules(chronicle_client)

        # Assert
        assert mock_get.call_count == 2

        # Verify the combined results
        assert len(result["rules"]) == 4
        assert [rule["name"] for rule in result["rules"]] == [
            "rule1",
            "rule2",
            "rule3",
            "rule4",
        ]


def test_list_rules_error(chronicle_client, mock_error_response):
    """Test list_rules function with error response."""
    # Arrange
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            list_rules(chronicle_client)

        assert "Failed to list rules" in str(exc_info.value)


def test_update_rule(chronicle_client, mock_response):
    """Test update_rule function."""
    # Arrange
    rule_id = "ru_12345"
    rule_text = "rule updated_test {}"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        # Act
        result = update_rule(chronicle_client, rule_id, rule_text)

        # Assert
        mock_patch.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}",
            params={"update_mask": "text"},
            json={"text": rule_text},
        )
        assert result == mock_response.json.return_value


def test_update_rule_error(chronicle_client, mock_error_response):
    """Test update_rule function with error response."""
    # Arrange
    rule_id = "ru_12345"
    rule_text = "rule updated_test {}"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            update_rule(chronicle_client, rule_id, rule_text)

        assert "Failed to update rule" in str(exc_info.value)


def test_delete_rule(chronicle_client, mock_response):
    """Test delete_rule function."""
    # Arrange
    rule_id = "ru_12345"
    mock_response.json.return_value = {}  # Empty response on successful delete

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_response
    ) as mock_delete:
        # Act
        result = delete_rule(chronicle_client, rule_id)

        # Assert
        mock_delete.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}",
            params={},
        )
        assert result == {}


def test_delete_rule_error(chronicle_client, mock_error_response):
    """Test delete_rule function with error response."""
    # Arrange
    rule_id = "ru_12345"

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            delete_rule(chronicle_client, rule_id)

        assert "Failed to delete rule" in str(exc_info.value)


def test_delete_rule_force(chronicle_client, mock_response):
    """Test delete_rule function with force=True."""
    # Arrange
    rule_id = "ru_12345"
    mock_response.json.return_value = {}  # Empty response on successful delete

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_response
    ) as mock_delete:
        # Act
        result = delete_rule(chronicle_client, rule_id, force=True)

        # Assert
        mock_delete.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}",
            params={"force": "true"},
        )
        assert result == {}


def test_enable_rule(chronicle_client, mock_response):
    """Test enable_rule function."""
    # Arrange
    rule_id = "ru_12345"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        # Act
        result = enable_rule(chronicle_client, rule_id, True)

        # Assert
        mock_patch.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}/deployment",
            params={"update_mask": "enabled"},
            json={"enabled": True},
        )
        assert result == mock_response.json.return_value


def test_disable_rule(chronicle_client, mock_response):
    """Test disable_rule function (enable_rule with enabled=False)."""
    # Arrange
    rule_id = "ru_12345"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        # Act
        result = enable_rule(chronicle_client, rule_id, False)

        # Assert
        mock_patch.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}/deployment",
            params={"update_mask": "enabled"},
            json={"enabled": False},
        )
        assert result == mock_response.json.return_value


def test_enable_rule_error(chronicle_client, mock_error_response):
    """Test enable_rule function with error response."""
    # Arrange
    rule_id = "ru_12345"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            enable_rule(chronicle_client, rule_id, True)

        assert "Failed to update rule deployment" in str(exc_info.value)


def test_search_rules(chronicle_client, mock_response):
    """Test search_rules function."""
    # Arrange
    mock_response.json.return_value = {
        "rules": [{"name": "rule1"}, {"name": "rule2"}]
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        # Act
        result = search_rules(chronicle_client, ".*")

        # Assert
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules",
            params={"pageSize": 1000, "view": "FULL"},
        )
        assert result == mock_response.json.return_value
        assert len(result["rules"]) == 2


def test_search_rules_error(chronicle_client, mock_error_response):
    """Test list_rules function with error response."""
    # Arrange
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(SecOpsError) as exc_info:
            search_rules(chronicle_client, "(")

        assert "Invalid regular expression" in str(exc_info.value)


def test_run_rule_test(chronicle_client, mock_streaming_response):
    """Test run_rule_test function."""
    # Arrange
    start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_time = datetime(2023, 1, 2, tzinfo=timezone.utc)
    rule_text = "rule test {}"

    # Mock the response to return a JSON array
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(
        [
            {"progressPercent": 10},
            {"progressPercent": 50},
            {"detection": {"rule_id": "rule1", "data": "test"}},
            {"progressPercent": 100},
        ]
    )

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        # Act
        results = list(
            run_rule_test(chronicle_client, rule_text, start_time, end_time)
        )

        # Assert
        expected_url = f"{chronicle_client.base_url}/projects/{chronicle_client.project_id}/locations/{chronicle_client.region}/instances/{chronicle_client.customer_id}/legacy:legacyRunTestRule"
        mock_post.assert_called_once_with(
            expected_url,
            json={
                "ruleText": rule_text,
                "timeRange": {
                    "startTime": "2023-01-01T00:00:00Z",
                    "endTime": "2023-01-02T00:00:00Z",
                },
                "maxResults": 100,
                "scope": "",
            },
            timeout=300,
        )

        # Verify we processed all streamed objects
        assert len(results) == 4
        assert results[0] == {"type": "progress", "percentDone": 10}
        assert results[1] == {"type": "progress", "percentDone": 50}
        assert results[2] == {
            "type": "detection",
            "detection": {"rule_id": "rule1", "data": "test"},
        }
        assert results[3] == {"type": "progress", "percentDone": 100}


def test_run_rule_test_error(chronicle_client, mock_error_response):
    """Test run_rule_test function with error response."""
    # Arrange
    start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_time = datetime(2023, 1, 2, tzinfo=timezone.utc)
    rule_text = "rule test {}"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            list(
                run_rule_test(chronicle_client, rule_text, start_time, end_time)
            )

        assert "Failed to test rule" in str(exc_info.value)


def test_run_rule_test_invalid_max_results(chronicle_client):
    """Test run_rule_test function with invalid max_results."""
    # Arrange
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    rule_text = "rule test {}"

    # Act & Assert - Test with too large value
    with pytest.raises(ValueError) as exc_info:
        list(
            run_rule_test(
                chronicle_client,
                rule_text,
                start_time,
                end_time,
                max_results=20000,
            )
        )

    assert "max_results must be between" in str(exc_info.value)

    # Act & Assert - Test with negative value
    with pytest.raises(ValueError) as exc_info:
        list(
            run_rule_test(
                chronicle_client,
                rule_text,
                start_time,
                end_time,
                max_results=-5,
            )
        )

    assert "max_results must be between" in str(exc_info.value)


def test_run_rule_test_handles_exceptions(chronicle_client):
    """Test that run_rule_test handles exceptions properly."""
    # Arrange
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    rule_text = "rule test {}"

    with patch.object(
        chronicle_client.session,
        "post",
        side_effect=Exception("Connection error"),
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            list(
                run_rule_test(chronicle_client, rule_text, start_time, end_time)
            )

        assert "Error testing rule" in str(exc_info.value)


def test_get_rule_deployment(chronicle_client, mock_response):
    """Test get_rule_deployment function."""
    rule_id = "ru_12345"
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        from secops.chronicle.rule import get_rule_deployment

        result = get_rule_deployment(chronicle_client, rule_id)

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/{rule_id}/deployment"
        )
        assert result == mock_response.json.return_value


def test_get_rule_deployment_error(chronicle_client, mock_error_response):
    """Test get_rule_deployment function with error response."""
    rule_id = "ru_12345"
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        from secops.chronicle.rule import get_rule_deployment

        with pytest.raises(APIError) as exc_info:
            get_rule_deployment(chronicle_client, rule_id)

        assert "Failed to get rule deployment" in str(exc_info.value)


def test_list_rule_deployments_single_page(chronicle_client, mock_response):
    """Test list_rule_deployments with a single page."""
    mock_response.json.return_value = {
        "ruleDeployments": [{"name": "dep1"}, {"name": "dep2"}]
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        from secops.chronicle.rule import list_rule_deployments

        result = list_rule_deployments(chronicle_client)

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/-/deployments",
            params={},
        )
        assert result == {
            "ruleDeployments": [{"name": "dep1"}, {"name": "dep2"}]
        }


def test_list_rule_deployments_pagination(chronicle_client):
    """Test list_rule_deployments function with pagination."""

    def get_mock_response(url, **kwargs):
        params = kwargs.get("params", {})
        if "pageToken" not in params:
            # First page response
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "ruleDeployments": [{"name": "dep1"}],
                "nextPageToken": "page2token",
            }
            return response
        elif params["pageToken"] == "page2token":
            # Second page response
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "ruleDeployments": [{"name": "dep2"}],
            }
            return response
        else:
            raise ValueError(f"Unexpected pageToken: {params.get('pageToken')}")

    with patch.object(chronicle_client.session, "get") as mock_get:
        mock_get.side_effect = get_mock_response

        from secops.chronicle.rule import list_rule_deployments

        result = list_rule_deployments(chronicle_client)

        assert mock_get.call_count == 2
        assert [d["name"] for d in result["ruleDeployments"]] == [
            "dep1",
            "dep2",
        ]


def test_list_rule_deployments_error(chronicle_client, mock_error_response):
    """Test list_rule_deployments function with error response."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        from secops.chronicle.rule import list_rule_deployments

        with pytest.raises(APIError) as exc_info:
            list_rule_deployments(chronicle_client)

        assert "Failed to list rule deployments" in str(exc_info.value)


def test_list_rule_deployments_empty(chronicle_client, mock_response):
    """Test list_rule_deployments function with no rule deployments."""
    # Arrange
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        from secops.chronicle.rule import list_rule_deployments

        # Act
        result = list_rule_deployments(chronicle_client)

        # Assert
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/-/deployments",
            params={},
        )
        assert result == {"ruleDeployments": []}
        assert len(result["ruleDeployments"]) == 0


def test_list_rule_deployments_with_filter(chronicle_client, mock_response):
    """Test list_rule_deployments function with filter parameter."""
    # Arrange
    mock_response.json.return_value = {
        "ruleDeployments": [{"name": "filtered_deployment", "enabled": True}]
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        from secops.chronicle.rule import list_rule_deployments

        # Act
        filter_query = "enabled=true"
        result = list_rule_deployments(
            chronicle_client, filter_query=filter_query
        )

        # Assert
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/rules/-/deployments",
            params={"filter": filter_query},
        )
        assert result == {
            "ruleDeployments": [
                {"name": "filtered_deployment", "enabled": True}
            ]
        }
        assert len(result["ruleDeployments"]) == 1
