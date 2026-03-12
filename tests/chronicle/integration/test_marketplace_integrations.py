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
"""Tests for Chronicle marketplace integration functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.marketplace_integrations import (
    list_marketplace_integrations,
    get_marketplace_integration,
    get_marketplace_integration_diff,
    install_marketplace_integration,
    uninstall_marketplace_integration,
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


# -- list_marketplace_integrations tests --


def test_list_marketplace_integrations_success(chronicle_client):
    """Test list_marketplace_integrations delegates to chronicle_paginated_request."""
    expected = {
        "marketplaceIntegrations": [
            {"name": "integration1"},
            {"name": "integration2"},
        ]
    }

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_marketplace_integrations(
            chronicle_client,
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="marketplaceIntegrations",
            items_key="marketplaceIntegrations",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_marketplace_integrations_default_args(chronicle_client):
    """Test list_marketplace_integrations with default args."""
    expected = {"marketplaceIntegrations": []}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_marketplace_integrations(chronicle_client)

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="marketplaceIntegrations",
            items_key="marketplaceIntegrations",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=False,
        )


def test_list_marketplace_integrations_with_filter(chronicle_client):
    """Test list_marketplace_integrations passes filter_string in extra_params."""
    expected = {"marketplaceIntegrations": [{"name": "integration1"}]}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_marketplace_integrations(
            chronicle_client,
            filter_string='displayName = "My Integration"',
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="marketplaceIntegrations",
            items_key="marketplaceIntegrations",
            page_size=None,
            page_token=None,
            extra_params={"filter": 'displayName = "My Integration"'},
            as_list=False,
        )


def test_list_marketplace_integrations_with_order_by(chronicle_client):
    """Test list_marketplace_integrations passes order_by in extra_params."""
    expected = {"marketplaceIntegrations": []}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_marketplace_integrations(
            chronicle_client,
            order_by="displayName",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="marketplaceIntegrations",
            items_key="marketplaceIntegrations",
            page_size=None,
            page_token=None,
            extra_params={"orderBy": "displayName"},
            as_list=False,
        )


def test_list_marketplace_integrations_with_filter_and_order_by(chronicle_client):
    """Test list_marketplace_integrations with both filter_string and order_by."""
    expected = {"marketplaceIntegrations": []}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_marketplace_integrations(
            chronicle_client,
            filter_string='displayName = "My Integration"',
            order_by="displayName",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="marketplaceIntegrations",
            items_key="marketplaceIntegrations",
            page_size=None,
            page_token=None,
            extra_params={
                "filter": 'displayName = "My Integration"',
                "orderBy": "displayName",
            },
            as_list=False,
        )


def test_list_marketplace_integrations_as_list(chronicle_client):
    """Test list_marketplace_integrations with as_list=True."""
    expected = [{"name": "integration1"}, {"name": "integration2"}]

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_marketplace_integrations(chronicle_client, as_list=True)

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="marketplaceIntegrations",
            items_key="marketplaceIntegrations",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=True,
        )


def test_list_marketplace_integrations_error(chronicle_client):
    """Test list_marketplace_integrations propagates APIError from helper."""
    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_paginated_request",
        side_effect=APIError("Failed to list marketplace integrations"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_marketplace_integrations(chronicle_client)

        assert "Failed to list marketplace integrations" in str(exc_info.value)


# -- get_marketplace_integration tests --


def test_get_marketplace_integration_success(chronicle_client):
    """Test get_marketplace_integration returns expected result."""
    expected = {
        "name": "test-integration",
        "displayName": "Test Integration",
        "version": "1.0.0",
    }

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_marketplace_integration(chronicle_client, "test-integration")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="marketplaceIntegrations/test-integration",
            api_version=APIVersion.V1BETA,
        )


def test_get_marketplace_integration_error(chronicle_client):
    """Test get_marketplace_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        side_effect=APIError("Failed to get marketplace integration test-integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_marketplace_integration(chronicle_client, "test-integration")

        assert "Failed to get marketplace integration" in str(exc_info.value)


# -- get_marketplace_integration_diff tests --


def test_get_marketplace_integration_diff_success(chronicle_client):
    """Test get_marketplace_integration_diff returns expected result."""
    expected = {
        "name": "test-integration",
        "diff": {"added": [], "removed": [], "modified": []},
    }

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_marketplace_integration_diff(chronicle_client, "test-integration")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path=(
                "marketplaceIntegrations/test-integration"
                ":fetchCommercialDiff"
            ),
            api_version=APIVersion.V1BETA,
        )


def test_get_marketplace_integration_diff_error(chronicle_client):
    """Test get_marketplace_integration_diff raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        side_effect=APIError("Failed to get marketplace integration diff"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_marketplace_integration_diff(chronicle_client, "test-integration")

        assert "Failed to get marketplace integration diff" in str(exc_info.value)


# -- install_marketplace_integration tests --


def test_install_marketplace_integration_no_optional_fields(chronicle_client):
    """Test install_marketplace_integration with no optional fields sends empty body."""
    expected = {
        "name": "test-integration",
        "displayName": "Test Integration",
        "installedVersion": "1.0.0",
    }

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = install_marketplace_integration(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="marketplaceIntegrations/test-integration:install",
            json={},
            api_version=APIVersion.V1BETA,
        )


def test_install_marketplace_integration_all_fields(chronicle_client):
    """Test install_marketplace_integration with all optional fields."""
    expected = {
        "name": "test-integration",
        "displayName": "Test Integration",
        "installedVersion": "2.0.0",
    }

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = install_marketplace_integration(
            chronicle_client,
            integration_name="test-integration",
            override_mapping=True,
            staging=False,
            version="2.0.0",
            restore_from_snapshot=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="marketplaceIntegrations/test-integration:install",
            json={
                "overrideMapping": True,
                "staging": False,
                "version": "2.0.0",
                "restoreFromSnapshot": True,
            },
            api_version=APIVersion.V1BETA,
        )


def test_install_marketplace_integration_override_mapping_only(chronicle_client):
    """Test install_marketplace_integration with only override_mapping set."""
    expected = {"name": "test-integration"}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = install_marketplace_integration(
            chronicle_client,
            integration_name="test-integration",
            override_mapping=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="marketplaceIntegrations/test-integration:install",
            json={"overrideMapping": True},
            api_version=APIVersion.V1BETA,
        )


def test_install_marketplace_integration_version_only(chronicle_client):
    """Test install_marketplace_integration with only version set."""
    expected = {"name": "test-integration"}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = install_marketplace_integration(
            chronicle_client,
            integration_name="test-integration",
            version="1.2.3",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="marketplaceIntegrations/test-integration:install",
            json={"version": "1.2.3"},
            api_version=APIVersion.V1BETA,
        )


def test_install_marketplace_integration_none_fields_excluded(chronicle_client):
    """Test that None optional fields are not included in the request body."""
    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value={"name": "test-integration"},
    ) as mock_request:
        install_marketplace_integration(
            chronicle_client,
            integration_name="test-integration",
            override_mapping=None,
            staging=None,
            version=None,
            restore_from_snapshot=None,
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="marketplaceIntegrations/test-integration:install",
            json={},
            api_version=APIVersion.V1BETA,
        )


def test_install_marketplace_integration_error(chronicle_client):
    """Test install_marketplace_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        side_effect=APIError("Failed to install marketplace integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            install_marketplace_integration(
                chronicle_client,
                integration_name="test-integration",
            )

        assert "Failed to install marketplace integration" in str(exc_info.value)


# -- uninstall_marketplace_integration tests --


def test_uninstall_marketplace_integration_success(chronicle_client):
    """Test uninstall_marketplace_integration returns expected result."""
    expected = {}

    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = uninstall_marketplace_integration(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="marketplaceIntegrations/test-integration:uninstall",
            api_version=APIVersion.V1BETA,
        )


def test_uninstall_marketplace_integration_error(chronicle_client):
    """Test uninstall_marketplace_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.marketplace_integrations.chronicle_request",
        side_effect=APIError("Failed to uninstall marketplace integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            uninstall_marketplace_integration(
                chronicle_client,
                integration_name="test-integration",
            )

        assert "Failed to uninstall marketplace integration" in str(exc_info.value)