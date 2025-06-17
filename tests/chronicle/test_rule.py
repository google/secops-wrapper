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
from secops.chronicle.rule import (
    create_rule,
    get_rule,
    list_rules,
    update_rule,
    delete_rule,
    enable_rule,
    search_rules,
)
from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    return ChronicleClient(customer_id="test-customer", project_id="test-project")


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
    """Test list_rules function."""
    # Arrange
    mock_response.json.return_value = {"rules": [{"name": "rule1"}, {"name": "rule2"}]}

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
            enable_rule(chronicle_client, rule_id)

        assert "Failed to enable rule" in str(exc_info.value)


def test_search_rules(chronicle_client, mock_response):
    """Test search_rules function."""
    # Arrange
    mock_response.json.return_value = {"rules": [{"name": "rule1"}, {"name": "rule2"}]}

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
