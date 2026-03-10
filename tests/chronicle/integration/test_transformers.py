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
"""Tests for Chronicle integration transformers functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.transformers import (
    list_integration_transformers,
    get_integration_transformer,
    delete_integration_transformer,
    create_integration_transformer,
    update_integration_transformer,
    execute_integration_transformer_test,
    get_integration_transformer_template,
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
            default_api_version=APIVersion.V1ALPHA,
        )


# -- list_integration_transformers tests --


def test_list_integration_transformers_success(chronicle_client):
    """Test list_integration_transformers delegates to chronicle_paginated_request."""
    expected = {
        "transformers": [{"name": "t1"}, {"name": "t2"}],
        "nextPageToken": "token",
    }

    with patch(
        "secops.chronicle.integration.transformers.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.transformers.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_transformers(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/My Integration/transformers",
            items_key="transformers",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_transformers_default_args(chronicle_client):
    """Test list_integration_transformers with default args."""
    expected = {"transformers": []}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_transformers(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/transformers",
            items_key="transformers",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=False,
        )


def test_list_integration_transformers_with_filter_order_expand(chronicle_client):
    """Test list passes filter/orderBy/excludeStaging/expand in extra_params."""
    expected = {"transformers": [{"name": "t1"}]}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_transformers(
            chronicle_client,
            integration_name="test-integration",
            filter_string='displayName = "My Transformer"',
            order_by="displayName",
            exclude_staging=True,
            expand="parameters",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/transformers",
            items_key="transformers",
            page_size=None,
            page_token=None,
            extra_params={
                "filter": 'displayName = "My Transformer"',
                "orderBy": "displayName",
                "excludeStaging": True,
                "expand": "parameters",
            },
            as_list=False,
        )


# -- get_integration_transformer tests --


def test_get_integration_transformer_success(chronicle_client):
    """Test get_integration_transformer delegates to chronicle_request."""
    expected = {"name": "transformer1", "displayName": "My Transformer"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.format_resource_id",
        return_value="test-integration",
    ):
        result = get_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            transformer_id="transformer1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/transformers/transformer1",
            api_version=APIVersion.V1ALPHA,
            params=None,
        )


def test_get_integration_transformer_with_expand(chronicle_client):
    """Test get_integration_transformer with expand parameter."""
    expected = {"name": "transformer1"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            transformer_id="transformer1",
            expand="parameters",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/transformers/transformer1",
            api_version=APIVersion.V1ALPHA,
            params={"expand": "parameters"},
        )


# -- delete_integration_transformer tests --


def test_delete_integration_transformer_success(chronicle_client):
    """Test delete_integration_transformer delegates to chronicle_request."""
    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=None,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.format_resource_id",
        return_value="test-integration",
    ):
        delete_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            transformer_id="transformer1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration/transformers/transformer1",
            api_version=APIVersion.V1ALPHA,
        )


# -- create_integration_transformer tests --


def test_create_integration_transformer_minimal(chronicle_client):
    """Test create_integration_transformer with minimal required fields."""
    expected = {"name": "transformer1", "displayName": "New Transformer"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.format_resource_id",
        return_value="test-integration",
    ):
        result = create_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            display_name="New Transformer",
            script="def transform(data): return data",
            script_timeout="60s",
            enabled=True,
        )

        assert result == expected

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "POST"
        assert (
            call_kwargs["endpoint_path"]
            == "integrations/test-integration/transformers"
        )
        assert call_kwargs["api_version"] == APIVersion.V1ALPHA
        assert call_kwargs["json"]["displayName"] == "New Transformer"
        assert call_kwargs["json"]["script"] == "def transform(data): return data"
        assert call_kwargs["json"]["scriptTimeout"] == "60s"
        assert call_kwargs["json"]["enabled"] is True


def test_create_integration_transformer_with_all_fields(chronicle_client):
    """Test create_integration_transformer with all optional fields."""
    expected = {"name": "transformer1"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            display_name="Full Transformer",
            script="def transform(data): return data",
            script_timeout="120s",
            enabled=False,
            description="Test transformer description",
            parameters=[{"name": "param1", "type": "STRING"}],
            usage_example="Example usage",
            expected_output="Output format",
            expected_input="Input format",
        )

        assert result == expected

        call_kwargs = mock_request.call_args[1]
        body = call_kwargs["json"]
        assert body["displayName"] == "Full Transformer"
        assert body["description"] == "Test transformer description"
        assert body["parameters"] == [{"name": "param1", "type": "STRING"}]
        assert body["usageExample"] == "Example usage"
        assert body["expectedOutput"] == "Output format"
        assert body["expectedInput"] == "Input format"


# -- update_integration_transformer tests --


def test_update_integration_transformer_display_name(chronicle_client):
    """Test update_integration_transformer updates display name."""
    expected = {"name": "transformer1", "displayName": "Updated Name"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.build_patch_body",
        return_value=({"displayName": "Updated Name"}, {"updateMask": "displayName"}),
    ) as mock_build:
        result = update_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            transformer_id="transformer1",
            display_name="Updated Name",
        )

        assert result == expected

        mock_build.assert_called_once()
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "PATCH"
        assert (
            call_kwargs["endpoint_path"]
            == "integrations/test-integration/transformers/transformer1"
        )


def test_update_integration_transformer_with_update_mask(chronicle_client):
    """Test update_integration_transformer with explicit update mask."""
    expected = {"name": "transformer1"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.build_patch_body",
        return_value=(
            {"displayName": "New Name", "enabled": True},
            {"updateMask": "displayName,enabled"},
        ),
    ):
        result = update_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            transformer_id="transformer1",
            display_name="New Name",
            enabled=True,
            update_mask="displayName,enabled",
        )

        assert result == expected


def test_update_integration_transformer_all_fields(chronicle_client):
    """Test update_integration_transformer with all fields."""
    expected = {"name": "transformer1"}

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.build_patch_body",
        return_value=(
            {
                "displayName": "Updated",
                "script": "new script",
                "scriptTimeout": "90s",
                "enabled": False,
                "description": "Updated description",
                "parameters": [{"name": "p1"}],
                "usageExample": "New example",
                "expectedOutput": "New output",
                "expectedInput": "New input",
            },
            {"updateMask": "displayName,script,scriptTimeout,enabled,description"},
        ),
    ):
        result = update_integration_transformer(
            chronicle_client,
            integration_name="test-integration",
            transformer_id="transformer1",
            display_name="Updated",
            script="new script",
            script_timeout="90s",
            enabled=False,
            description="Updated description",
            parameters=[{"name": "p1"}],
            usage_example="New example",
            expected_output="New output",
            expected_input="New input",
        )

        assert result == expected


# -- execute_integration_transformer_test tests --


def test_execute_integration_transformer_test_success(chronicle_client):
    """Test execute_integration_transformer_test delegates to chronicle_request."""
    transformer = {
        "displayName": "Test Transformer",
        "script": "def transform(data): return data",
    }
    expected = {
        "outputMessage": "Success",
        "debugOutputMessage": "Debug info",
        "resultValue": {"status": "ok"},
    }

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.format_resource_id",
        return_value="test-integration",
    ):
        result = execute_integration_transformer_test(
            chronicle_client,
            integration_name="test-integration",
            transformer=transformer,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/transformers:executeTest",
            api_version=APIVersion.V1ALPHA,
            json={"transformer": transformer},
        )


# -- get_integration_transformer_template tests --


def test_get_integration_transformer_template_success(chronicle_client):
    """Test get_integration_transformer_template delegates to chronicle_request."""
    expected = {
        "script": "def transform(data):\n    # Template code\n    return data",
        "displayName": "Template Transformer",
    }

    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.transformers.format_resource_id",
        return_value="test-integration",
    ):
        result = get_integration_transformer_template(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/transformers:fetchTemplate",
            api_version=APIVersion.V1ALPHA,
        )


# -- Error handling tests --


def test_list_integration_transformers_api_error(chronicle_client):
    """Test list_integration_transformers handles API errors."""
    with patch(
        "secops.chronicle.integration.transformers.chronicle_paginated_request",
        side_effect=APIError("API Error"),
    ):
        with pytest.raises(APIError, match="API Error"):
            list_integration_transformers(
                chronicle_client,
                integration_name="test-integration",
            )


def test_get_integration_transformer_api_error(chronicle_client):
    """Test get_integration_transformer handles API errors."""
    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        side_effect=APIError("Not found"),
    ):
        with pytest.raises(APIError, match="Not found"):
            get_integration_transformer(
                chronicle_client,
                integration_name="test-integration",
                transformer_id="nonexistent",
            )


def test_create_integration_transformer_api_error(chronicle_client):
    """Test create_integration_transformer handles API errors."""
    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        side_effect=APIError("Creation failed"),
    ):
        with pytest.raises(APIError, match="Creation failed"):
            create_integration_transformer(
                chronicle_client,
                integration_name="test-integration",
                display_name="New Transformer",
                script="def transform(data): return data",
                script_timeout="60s",
                enabled=True,
            )


def test_update_integration_transformer_api_error(chronicle_client):
    """Test update_integration_transformer handles API errors."""
    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        side_effect=APIError("Update failed"),
    ), patch(
        "secops.chronicle.integration.transformers.build_patch_body",
        return_value=({"displayName": "Updated"}, {"updateMask": "displayName"}),
    ):
        with pytest.raises(APIError, match="Update failed"):
            update_integration_transformer(
                chronicle_client,
                integration_name="test-integration",
                transformer_id="transformer1",
                display_name="Updated",
            )


def test_delete_integration_transformer_api_error(chronicle_client):
    """Test delete_integration_transformer handles API errors."""
    with patch(
        "secops.chronicle.integration.transformers.chronicle_request",
        side_effect=APIError("Delete failed"),
    ):
        with pytest.raises(APIError, match="Delete failed"):
            delete_integration_transformer(
                chronicle_client,
                integration_name="test-integration",
                transformer_id="transformer1",
            )

