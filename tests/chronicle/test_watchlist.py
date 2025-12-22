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
"""Tests for Chronicle watchlist functions."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.watchlist import (
    list_watchlists,
    get_watchlist,
    delete_watchlist,
    create_watchlist,
    update_watchlist,
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
            default_api_version=APIVersion.V1,
        )


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {}
    return mock


@pytest.fixture
def mock_error_response() -> Mock:
    """Create a mock error API response object."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock


# -- list_watchlists tests --


def test_list_watchlists_success(chronicle_client):
    """Test list_watchlists delegates to chronicle_paginated_request."""
    expected: Dict[str, Any] = {
        "watchlists": [
            {"name": "watchlist1"},
            {"name": "watchlist2"},
        ]
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_watchlists(
            chronicle_client,
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url(APIVersion.V1),
            path="watchlists",
            items_key="watchlists",
            page_size=10,
            page_token="next-token",
        )


def test_list_watchlists_default_args(chronicle_client):
    """Test list_watchlists with default pagination args."""
    expected: Dict[str, Any] = {"watchlists": []}

    with patch(
        "secops.chronicle.watchlist.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_watchlists(chronicle_client)

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url(APIVersion.V1),
            path="watchlists",
            items_key="watchlists",
            page_size=None,
            page_token=None,
        )


def test_list_watchlists_error(chronicle_client):
    """Test list_watchlists propagates APIError from helper."""
    with patch(
        "secops.chronicle.watchlist.chronicle_paginated_request",
        side_effect=APIError("Failed to list watchlists"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_watchlists(chronicle_client)

        assert "Failed to list watchlists" in str(exc_info.value)


# -- get_watchlist tests --


def test_get_watchlist_success(chronicle_client):
    """Test get_watchlist returns expected result."""
    expected = {
        "name": "test-watchlist-id",
        "displayName": "test-watchlist",
        "multiplyingFactor": 1,
        "description": "test-description",
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_watchlist(chronicle_client, "test-watchlist-id")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="watchlists/test-watchlist-id",
            api_version=APIVersion.V1,
        )


def test_get_watchlist_error(chronicle_client):
    """Test get_watchlist raises APIError on error."""
    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        side_effect=APIError("Failed to get watchlist test-watchlist-id"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_watchlist(chronicle_client, "test-watchlist-id")

        assert "Failed to get watchlist" in str(exc_info.value)


# -- delete_watchlist tests --


def test_delete_watchlist_success(chronicle_client):
    """Test delete_watchlist calls helper and returns response JSON."""
    expected: Dict[str, Any] = {}

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = delete_watchlist(chronicle_client, "watchlist-123")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="watchlists/watchlist-123",
            api_version=APIVersion.V1,
            params={},
        )


def test_delete_watchlist_force_true(chronicle_client):
    """Test delete_watchlist with force=True."""
    expected: Dict[str, Any] = {}

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = delete_watchlist(
            chronicle_client,
            "watchlist-123",
            force=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="watchlists/watchlist-123",
            api_version=APIVersion.V1,
            params={"force": True},
        )


# -- create_watchlist tests --


def test_create_watchlist_success(chronicle_client):
    """Test create_watchlist calls helper and returns response JSON."""
    expected = {
        "name": "watchlist-123",
        "displayName": "My Watchlist",
        "multiplyingFactor": 1.5,
        "description": "Test description",
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_watchlist(
            chronicle_client,
            name="watchlist-123",
            display_name="My Watchlist",
            multiplying_factor=1.5,
            description="Test description",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="watchlists",
            api_version=APIVersion.V1,
            json={
                "name": "watchlist-123",
                "displayName": "My Watchlist",
                "multiplyingFactor": 1.5,
                "description": "Test description",
                "entityPopulationMechanism": {"manual": {}},
            },
        )


def test_create_watchlist_without_description(chronicle_client):
    """Test create_watchlist when description is None."""
    expected = {
        "name": "watchlist-123",
        "displayName": "My Watchlist",
        "multiplyingFactor": 2.0,
        "description": None,
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_watchlist(
            chronicle_client,
            name="watchlist-123",
            display_name="My Watchlist",
            multiplying_factor=2.0,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="watchlists",
            api_version=APIVersion.V1,
            json={
                "name": "watchlist-123",
                "displayName": "My Watchlist",
                "multiplyingFactor": 2.0,
                "description": None,
                "entityPopulationMechanism": {"manual": {}},
            },
        )


# -- update_watchlist tests --


def test_update_watchlist_success_all_fields(chronicle_client):
    """Test update_watchlist with all fields provided."""
    expected = {
        "name": "watchlist-123",
        "displayName": "Updated Watchlist",
        "description": "Updated description",
        "multiplyingFactor": 2.5,
        "entityPopulationMechanism": {"manual": {}},
        "watchlistUserPreferences": {"pinned": True},
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_watchlist(
            chronicle_client,
            watchlist_id="watchlist-123",
            display_name="Updated Watchlist",
            description="Updated description",
            multiplying_factor=2.5,
            entity_population_mechanism={"manual": {}},
            watchlist_user_preferences={"pinned": True},
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="watchlists/watchlist-123",
            api_version=APIVersion.V1,
            params={
                "updateMask": (
                    "display_name,description,multiplying_factor,"
                    "entity_population_mechanism,watchlist_user_preferences"
                )
            },
            json={
                "displayName": "Updated Watchlist",
                "description": "Updated description",
                "multiplyingFactor": 2.5,
                "entityPopulationMechanism": {"manual": {}},
                "watchlistUserPreferences": {"pinned": True},
            },
        )


def test_update_watchlist_single_field(chronicle_client):
    """Test update_watchlist with only display_name."""
    expected = {
        "name": "watchlist-123",
        "displayName": "New Name",
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_watchlist(
            chronicle_client,
            watchlist_id="watchlist-123",
            display_name="New Name",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="watchlists/watchlist-123",
            api_version=APIVersion.V1,
            params={"updateMask": "display_name"},
            json={"displayName": "New Name"},
        )


def test_update_watchlist_explicit_update_mask(chronicle_client):
    """Test update_watchlist with explicit update_mask overrides auto-mask."""
    expected = {
        "name": "watchlist-123",
        "displayName": "Updated Name",
        "description": "Updated desc",
    }

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_watchlist(
            chronicle_client,
            watchlist_id="watchlist-123",
            display_name="Updated Name",
            description="Updated desc",
            update_mask="display_name",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="watchlists/watchlist-123",
            api_version=APIVersion.V1,
            params={"updateMask": "display_name"},
            json={
                "displayName": "Updated Name",
                "description": "Updated desc",
            },
        )


def test_update_watchlist_no_fields(chronicle_client):
    """Test update_watchlist with no optional fields (edge case)."""
    expected = {"name": "watchlist-123"}

    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_watchlist(
            chronicle_client,
            watchlist_id="watchlist-123",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="watchlists/watchlist-123",
            api_version=APIVersion.V1,
            params=None,
            json={},
        )


def test_update_watchlist_error(chronicle_client):
    """Test update_watchlist raises APIError on failure."""
    with patch(
        "secops.chronicle.watchlist.chronicle_request",
        side_effect=APIError("Failed to update watchlist watchlist-123"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_watchlist(
                chronicle_client,
                watchlist_id="watchlist-123",
                display_name="New Name",
            )

        assert "Failed to update watchlist" in str(exc_info.value)
