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
"""Tests for Chronicle feed functions."""

import pytest
from unittest.mock import ANY, Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.feeds import (
    create_feed,
    get_feed,
    list_feeds,
    update_feed,
    delete_feed,
    enable_feed,
    disable_feed,
    generate_secret,
    CreateFeedModel,
    UpdateFeedModel,
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
            customer_id="test-customer", project_id="test-project"
        )


@pytest.fixture
def mock_response():
    """Create a mock API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/feeds/feed_12345"
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


def test_create_feed(chronicle_client, mock_response):
    """Test create_feed function."""
    # Arrange
    feed_config = CreateFeedModel(
        display_name="Test Feed",
        details={"feed_source_type": "syslog", "log_type": "network"},
    )

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_post:
        # Act
        result = create_feed(chronicle_client, feed_config)

        # Assert
        mock_post.assert_called_once_with(
            method="POST",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds",
            params=None,
            json=feed_config.to_dict(),
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value


def test_create_feed_with_json_string(chronicle_client, mock_response):
    """Test create_feed function with JSON string details."""
    # Arrange
    feed_config = CreateFeedModel(
        display_name="Test Feed",
        details='{"feed_source_type": "syslog", "log_type": "network"}',
    )

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_post:
        # Act
        result = create_feed(chronicle_client, feed_config)

        # Assert
        expected_json = {
            "display_name": "Test Feed",
            "details": {"feed_source_type": "syslog", "log_type": "network"},
        }
        mock_post.assert_called_once_with(
            method="POST",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds",
            params=None,
            json=expected_json,
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value


def test_create_feed_error(chronicle_client, mock_error_response):
    """Test create_feed function with error response."""
    # Arrange
    feed_config = CreateFeedModel(
        display_name="Test Feed", details={"feed_source_type": "syslog"}
    )

    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            create_feed(chronicle_client, feed_config)

        assert "Failed to create feed" in str(exc_info.value)


def test_get_feed(chronicle_client, mock_response):
    """Test get_feed function."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_get:
        # Act
        result = get_feed(chronicle_client, feed_id)

        # Assert
        mock_get.assert_called_once_with(
            method="GET",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}",
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value


def test_get_feed_error(chronicle_client, mock_error_response):
    """Test get_feed function with error response."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            get_feed(chronicle_client, feed_id)

        assert "Failed to get feed" in str(exc_info.value)


def test_list_feeds(chronicle_client, mock_response):
    """Test list_feeds function."""
    # Arrange
    mock_response.json.return_value = {
        "feeds": [{"name": "feed1"}, {"name": "feed2"}]
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_get:
        # Act
        result = list_feeds(chronicle_client)

        # Assert
        mock_get.assert_called_once_with(
            method="GET",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds",
            params={"pageSize": 100},
            json=None,
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value["feeds"]
        assert len(result) == 2


def test_list_feeds_with_pagination(chronicle_client, mock_response):
    """Test list_feeds function with automatic pagination across multiple pages."""
    # Arrange - When page_token is NOT provided, it automatically fetches
    # all pages and aggregates results
    first_response = Mock()
    first_response.status_code = 200
    first_response.json.return_value = {
        "feeds": [{"name": "feed1"}, {"name": "feed2"}],
        "nextPageToken": "next_token_456",
    }

    second_response = Mock()
    second_response.status_code = 200
    second_response.json.return_value = {
        "feeds": [{"name": "feed3"}],
        "nextPageToken": "next_token_789",
    }

    third_response = Mock()
    third_response.status_code = 200
    third_response.json.return_value = {
        "feeds": [{"name": "feed4"}],
    }

    with patch.object(
        chronicle_client.session,
        "request",
        side_effect=[first_response, second_response, third_response],
    ) as mock_get:
        # Act - Pass page_size=None and page_token=None to enable automatic pagination
        # If page_size has a default value, it triggers single-page mode
        result = list_feeds(chronicle_client, page_size=None, page_token=None)

        # Assert - Multiple calls are made to fetch all pages
        assert mock_get.call_count == 3

        # Verify each call was made with correct params (DEFAULT_PAGE_SIZE=1000)
        calls = mock_get.call_args_list
        assert calls[0].kwargs["params"] == {"pageSize": 1000}
        assert calls[1].kwargs["params"] == {
            "pageSize": 1000,
            "pageToken": "next_token_456",
        }
        assert calls[2].kwargs["params"] == {
            "pageSize": 1000,
            "pageToken": "next_token_789",
        }

        # Result should be aggregated feeds from all pages
        assert len(result) == 4
        assert result[0]["name"] == "feed1"
        assert result[1]["name"] == "feed2"
        assert result[2]["name"] == "feed3"
        assert result[3]["name"] == "feed4"


def test_list_feeds_error(chronicle_client, mock_error_response):
    """Test list_feeds function with error response."""
    # Arrange
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            list_feeds(chronicle_client)

        assert "API request failed" in str(exc_info.value)


def test_update_feed(chronicle_client, mock_response):
    """Test update_feed function."""
    # Arrange
    feed_id = "feed_12345"
    feed_config = UpdateFeedModel(
        display_name="Updated Feed",
        details={"feed_source_type": "syslog", "log_type": "updated"},
    )

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_patch:
        # Act
        result = update_feed(chronicle_client, feed_id, feed_config)

        # Assert
        mock_patch.assert_called_once_with(
            method="PATCH",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}",
            params={"updateMask": "display_name,details"},
            json=feed_config.to_dict(),
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value


def test_update_feed_with_custom_mask(chronicle_client, mock_response):
    """Test update_feed function with custom update mask."""
    # Arrange
    feed_id = "feed_12345"
    feed_config = UpdateFeedModel(display_name="Updated Feed")
    update_mask = ["display_name"]

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_patch:
        # Act
        result = update_feed(
            chronicle_client, feed_id, feed_config, update_mask
        )

        # Assert
        mock_patch.assert_called_once_with(
            method="PATCH",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}",
            params={"updateMask": "display_name"},
            json=feed_config.to_dict(),
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value


def test_update_feed_error(chronicle_client, mock_error_response):
    """Test update_feed function with error response."""
    # Arrange
    feed_id = "feed_12345"
    feed_config = UpdateFeedModel(display_name="Updated Feed")

    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            update_feed(chronicle_client, feed_id, feed_config)

        assert "Failed to update feed" in str(exc_info.value)


def test_delete_feed(chronicle_client, mock_response):
    """Test delete_feed function."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_delete:
        # Act
        result = delete_feed(chronicle_client, feed_id)

        # Assert
        mock_delete.assert_called_once_with(
            method="DELETE",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}",
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )
        assert result is None


def test_delete_feed_error(chronicle_client, mock_error_response):
    """Test delete_feed function with error response."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            delete_feed(chronicle_client, feed_id)

        assert "Failed to delete feed" in str(exc_info.value)


def test_enable_feed(chronicle_client, mock_response):
    """Test enable_feed function."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_post:
        # Act
        result = enable_feed(chronicle_client, feed_id)

        # Assert
        mock_post.assert_called_once_with(
            method="POST",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}:enable",
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )
        assert feed_id in f"{result}"


def test_enable_feed_error(chronicle_client, mock_error_response):
    """Test enable_feed function with error response."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            enable_feed(chronicle_client, feed_id)

        assert "Failed to enable feed" in str(exc_info.value)


def test_disable_feed(chronicle_client, mock_response):
    """Test disable_feed function."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_post:
        # Act
        result = disable_feed(chronicle_client, feed_id)

        # Assert
        mock_post.assert_called_once_with(
            method="POST",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}:disable",
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )
        assert feed_id in f"{result}"


def test_disable_feed_error(chronicle_client, mock_error_response):
    """Test disable_feed function with error response."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            disable_feed(chronicle_client, feed_id)

        assert "Failed to disable feed" in str(exc_info.value)


def test_generate_secret(chronicle_client, mock_response):
    """Test generate_secret function."""
    # Arrange
    feed_id = "feed_12345"
    mock_response.json.return_value = {"secret": "generated_secret_123"}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_post:
        # Act
        result = generate_secret(chronicle_client, feed_id)

        # Assert
        mock_post.assert_called_once_with(
            method="POST",
            url=f"{chronicle_client.base_url()}/{chronicle_client.instance_id}/feeds/{feed_id}:generateSecret",
            params=None,
            json=None,
            headers=ANY,
            timeout=None,
        )
        assert result == mock_response.json.return_value


def test_generate_secret_error(chronicle_client, mock_error_response):
    """Test generate_secret function with error response."""
    # Arrange
    feed_id = "feed_12345"
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            generate_secret(chronicle_client, feed_id)

        assert "Failed to generate secret" in str(exc_info.value)


def test_create_feed_model_invalid_json():
    """Test CreateFeedModel with invalid JSON string."""
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        CreateFeedModel(display_name="Test Feed", details='{"invalid": json}')

    assert "Invalid JSON string for details" in str(exc_info.value)


def test_update_feed_model_invalid_json():
    """Test UpdateFeedModel with invalid JSON string."""
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        UpdateFeedModel(display_name="Test Feed", details='{"invalid": json}')

    assert "Invalid JSON string for details" in str(exc_info.value)
