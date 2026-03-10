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
"""Tests for Chronicle integration connector context properties functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.connector_context_properties import (
    list_connector_context_properties,
    get_connector_context_property,
    delete_connector_context_property,
    create_connector_context_property,
    update_connector_context_property,
    delete_all_connector_context_properties,
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


# -- list_connector_context_properties tests --


def test_list_connector_context_properties_success(chronicle_client):
    """Test list_connector_context_properties delegates to paginated request."""
    expected = {
        "contextProperties": [{"key": "prop1"}, {"key": "prop2"}],
        "nextPageToken": "t",
    }

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.connector_context_properties.format_resource_id",
        return_value="My Integration",
    ):
        result = list_connector_context_properties(
            chronicle_client,
            integration_name="My Integration",
            connector_id="c1",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert "connectors/c1/contextProperties" in kwargs["path"]
        assert kwargs["items_key"] == "contextProperties"
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "next-token"


def test_list_connector_context_properties_default_args(chronicle_client):
    """Test list_connector_context_properties with default args."""
    expected = {"contextProperties": []}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_paginated_request",
        return_value=expected,
    ):
        result = list_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
        )

        assert result == expected


def test_list_connector_context_properties_with_filters(chronicle_client):
    """Test list_connector_context_properties with filter and order_by."""
    expected = {"contextProperties": [{"key": "prop1"}]}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            filter_string='key = "prop1"',
            order_by="key",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": 'key = "prop1"',
            "orderBy": "key",
        }


def test_list_connector_context_properties_as_list(chronicle_client):
    """Test list_connector_context_properties returns list when as_list=True."""
    expected = [{"key": "prop1"}, {"key": "prop2"}]

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_connector_context_properties_error(chronicle_client):
    """Test list_connector_context_properties raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_paginated_request",
        side_effect=APIError("Failed to list context properties"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_connector_context_properties(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
            )
        assert "Failed to list context properties" in str(exc_info.value)


# -- get_connector_context_property tests --


def test_get_connector_context_property_success(chronicle_client):
    """Test get_connector_context_property issues GET request."""
    expected = {
        "name": "contextProperties/prop1",
        "key": "prop1",
        "value": "test-value",
    }

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "connectors/c1/contextProperties/prop1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_connector_context_property_error(chronicle_client):
    """Test get_connector_context_property raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        side_effect=APIError("Failed to get context property"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_connector_context_property(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                context_property_id="prop1",
            )
        assert "Failed to get context property" in str(exc_info.value)


# -- delete_connector_context_property tests --


def test_delete_connector_context_property_success(chronicle_client):
    """Test delete_connector_context_property issues DELETE request."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert "connectors/c1/contextProperties/prop1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_delete_connector_context_property_error(chronicle_client):
    """Test delete_connector_context_property raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        side_effect=APIError("Failed to delete context property"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_connector_context_property(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                context_property_id="prop1",
            )
        assert "Failed to delete context property" in str(exc_info.value)


# -- create_connector_context_property tests --


def test_create_connector_context_property_required_fields_only(chronicle_client):
    """Test create_connector_context_property with required fields only."""
    expected = {"name": "contextProperties/new", "value": "test-value"}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            value="test-value",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/connectors/c1/contextProperties",
            api_version=APIVersion.V1BETA,
            json={"value": "test-value"},
        )


def test_create_connector_context_property_with_key(chronicle_client):
    """Test create_connector_context_property includes key when provided."""
    expected = {"name": "contextProperties/custom-key", "value": "test-value"}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            value="test-value",
            key="custom-key",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["value"] == "test-value"
        assert kwargs["json"]["key"] == "custom-key"


def test_create_connector_context_property_error(chronicle_client):
    """Test create_connector_context_property raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        side_effect=APIError("Failed to create context property"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_connector_context_property(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                value="test-value",
            )
        assert "Failed to create context property" in str(exc_info.value)


# -- update_connector_context_property tests --


def test_update_connector_context_property_success(chronicle_client):
    """Test update_connector_context_property updates value."""
    expected = {
        "name": "contextProperties/prop1",
        "value": "updated-value",
    }

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
            value="updated-value",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PATCH"
        assert "connectors/c1/contextProperties/prop1" in kwargs["endpoint_path"]
        assert kwargs["json"]["value"] == "updated-value"
        assert kwargs["params"]["updateMask"] == "value"


def test_update_connector_context_property_with_custom_mask(chronicle_client):
    """Test update_connector_context_property with custom update_mask."""
    expected = {"name": "contextProperties/prop1"}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
            value="updated-value",
            update_mask="value",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["params"]["updateMask"] == "value"


def test_update_connector_context_property_error(chronicle_client):
    """Test update_connector_context_property raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        side_effect=APIError("Failed to update context property"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_connector_context_property(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                context_property_id="prop1",
                value="updated-value",
            )
        assert "Failed to update context property" in str(exc_info.value)


# -- delete_all_connector_context_properties tests --


def test_delete_all_connector_context_properties_success(chronicle_client):
    """Test delete_all_connector_context_properties issues POST request."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_all_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert "connectors/c1/contextProperties:clearAll" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA
        assert kwargs["json"] == {}


def test_delete_all_connector_context_properties_with_context_id(chronicle_client):
    """Test delete_all_connector_context_properties with context_id."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_all_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_id="my-context",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["contextId"] == "my-context"


def test_delete_all_connector_context_properties_error(chronicle_client):
    """Test delete_all_connector_context_properties raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        side_effect=APIError("Failed to clear context properties"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_all_connector_context_properties(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
            )
        assert "Failed to clear context properties" in str(exc_info.value)


# -- API version tests --


def test_list_connector_context_properties_custom_api_version(chronicle_client):
    """Test list_connector_context_properties with custom API version."""
    expected = {"contextProperties": []}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_get_connector_context_property_custom_api_version(chronicle_client):
    """Test get_connector_context_property with custom API version."""
    expected = {"name": "contextProperties/prop1"}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_delete_connector_context_property_custom_api_version(chronicle_client):
    """Test delete_connector_context_property with custom API version."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
            api_version=APIVersion.V1ALPHA,
        )

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_create_connector_context_property_custom_api_version(chronicle_client):
    """Test create_connector_context_property with custom API version."""
    expected = {"name": "contextProperties/new"}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            value="test-value",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_update_connector_context_property_custom_api_version(chronicle_client):
    """Test update_connector_context_property with custom API version."""
    expected = {"name": "contextProperties/prop1"}

    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_context_property(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            context_property_id="prop1",
            value="updated-value",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_delete_all_connector_context_properties_custom_api_version(chronicle_client):
    """Test delete_all_connector_context_properties with custom API version."""
    with patch(
        "secops.chronicle.integration.connector_context_properties.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_all_connector_context_properties(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            api_version=APIVersion.V1ALPHA,
        )

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA

