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
"""Tests for Chronicle integration logical operators functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.logical_operators import (
    list_integration_logical_operators,
    get_integration_logical_operator,
    delete_integration_logical_operator,
    create_integration_logical_operator,
    update_integration_logical_operator,
    execute_integration_logical_operator_test,
    get_integration_logical_operator_template,
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


# -- list_integration_logical_operators tests --


def test_list_integration_logical_operators_success(chronicle_client):
    """Test list_integration_logical_operators delegates to paginated request."""
    expected = {
        "logicalOperators": [{"name": "lo1"}, {"name": "lo2"}],
        "nextPageToken": "token",
    }

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.logical_operators.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_logical_operators(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/My Integration/logicalOperators",
            items_key="logicalOperators",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_logical_operators_default_args(chronicle_client):
    """Test list_integration_logical_operators with default args."""
    expected = {"logicalOperators": []}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_logical_operators(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/logicalOperators",
            items_key="logicalOperators",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=False,
        )


def test_list_integration_logical_operators_with_filter_order_expand(
    chronicle_client,
):
    """Test list passes filter/orderBy/excludeStaging/expand in extra_params."""
    expected = {"logicalOperators": [{"name": "lo1"}]}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_logical_operators(
            chronicle_client,
            integration_name="test-integration",
            filter_string='displayName = "My Operator"',
            order_by="displayName",
            exclude_staging=True,
            expand="parameters",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/logicalOperators",
            items_key="logicalOperators",
            page_size=None,
            page_token=None,
            extra_params={
                "filter": 'displayName = "My Operator"',
                "orderBy": "displayName",
                "excludeStaging": True,
                "expand": "parameters",
            },
            as_list=False,
        )


# -- get_integration_logical_operator tests --


def test_get_integration_logical_operator_success(chronicle_client):
    """Test get_integration_logical_operator delegates to chronicle_request."""
    expected = {"name": "lo1", "displayName": "My Operator"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.format_resource_id",
        return_value="test-integration",
    ):
        result = get_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/logicalOperators/lo1",
            api_version=APIVersion.V1ALPHA,
            params=None,
        )


def test_get_integration_logical_operator_with_expand(chronicle_client):
    """Test get_integration_logical_operator with expand parameter."""
    expected = {"name": "lo1"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            expand="parameters",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/logicalOperators/lo1",
            api_version=APIVersion.V1ALPHA,
            params={"expand": "parameters"},
        )


# -- delete_integration_logical_operator tests --


def test_delete_integration_logical_operator_success(chronicle_client):
    """Test delete_integration_logical_operator delegates to chronicle_request."""
    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=None,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.format_resource_id",
        return_value="test-integration",
    ):
        delete_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration/logicalOperators/lo1",
            api_version=APIVersion.V1ALPHA,
        )


# -- create_integration_logical_operator tests --


def test_create_integration_logical_operator_minimal(chronicle_client):
    """Test create_integration_logical_operator with minimal required fields."""
    expected = {"name": "lo1", "displayName": "New Operator"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.format_resource_id",
        return_value="test-integration",
    ):
        result = create_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            display_name="New Operator",
            script="def evaluate(a, b): return a == b",
            script_timeout="60s",
            enabled=True,
        )

        assert result == expected

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "POST"
        assert (
            call_kwargs["endpoint_path"]
            == "integrations/test-integration/logicalOperators"
        )
        assert call_kwargs["api_version"] == APIVersion.V1ALPHA
        assert call_kwargs["json"]["displayName"] == "New Operator"
        assert call_kwargs["json"]["script"] == "def evaluate(a, b): return a == b"
        assert call_kwargs["json"]["scriptTimeout"] == "60s"
        assert call_kwargs["json"]["enabled"] is True


def test_create_integration_logical_operator_with_all_fields(chronicle_client):
    """Test create_integration_logical_operator with all optional fields."""
    expected = {"name": "lo1"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            display_name="Full Operator",
            script="def evaluate(a, b): return a > b",
            script_timeout="120s",
            enabled=False,
            description="Test logical operator description",
            parameters=[{"name": "param1", "type": "STRING"}],
        )

        assert result == expected

        call_kwargs = mock_request.call_args[1]
        body = call_kwargs["json"]
        assert body["displayName"] == "Full Operator"
        assert body["description"] == "Test logical operator description"
        assert body["parameters"] == [{"name": "param1", "type": "STRING"}]


# -- update_integration_logical_operator tests --


def test_update_integration_logical_operator_display_name(chronicle_client):
    """Test update_integration_logical_operator updates display name."""
    expected = {"name": "lo1", "displayName": "Updated Name"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.build_patch_body",
        return_value=({"displayName": "Updated Name"}, {"updateMask": "displayName"}),
    ) as mock_build:
        result = update_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            display_name="Updated Name",
        )

        assert result == expected

        mock_build.assert_called_once()
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["method"] == "PATCH"
        assert (
            call_kwargs["endpoint_path"]
            == "integrations/test-integration/logicalOperators/lo1"
        )


def test_update_integration_logical_operator_with_update_mask(chronicle_client):
    """Test update_integration_logical_operator with explicit update mask."""
    expected = {"name": "lo1"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.build_patch_body",
        return_value=(
            {"displayName": "New Name", "enabled": True},
            {"updateMask": "displayName,enabled"},
        ),
    ):
        result = update_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            display_name="New Name",
            enabled=True,
            update_mask="displayName,enabled",
        )

        assert result == expected


def test_update_integration_logical_operator_all_fields(chronicle_client):
    """Test update_integration_logical_operator with all fields."""
    expected = {"name": "lo1"}

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.build_patch_body",
        return_value=(
            {
                "displayName": "Updated",
                "script": "new script",
                "scriptTimeout": "90s",
                "enabled": False,
                "description": "Updated description",
                "parameters": [{"name": "p1"}],
            },
            {"updateMask": "displayName,script,scriptTimeout,enabled,description"},
        ),
    ):
        result = update_integration_logical_operator(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            display_name="Updated",
            script="new script",
            script_timeout="90s",
            enabled=False,
            description="Updated description",
            parameters=[{"name": "p1"}],
        )

        assert result == expected


# -- execute_integration_logical_operator_test tests --


def test_execute_integration_logical_operator_test_success(chronicle_client):
    """Test execute_integration_logical_operator_test delegates to chronicle_request."""
    logical_operator = {
        "displayName": "Test Operator",
        "script": "def evaluate(a, b): return a == b",
    }
    expected = {
        "outputMessage": "Success",
        "debugOutputMessage": "Debug info",
        "resultValue": True,
    }

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.format_resource_id",
        return_value="test-integration",
    ):
        result = execute_integration_logical_operator_test(
            chronicle_client,
            integration_name="test-integration",
            logical_operator=logical_operator,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/logicalOperators:executeTest",
            api_version=APIVersion.V1ALPHA,
            json={"logicalOperator": logical_operator},
        )


# -- get_integration_logical_operator_template tests --


def test_get_integration_logical_operator_template_success(chronicle_client):
    """Test get_integration_logical_operator_template delegates to chronicle_request."""
    expected = {
        "script": "def evaluate(a, b):\n    # Template code\n    return True",
        "displayName": "Template Operator",
    }

    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operators.format_resource_id",
        return_value="test-integration",
    ):
        result = get_integration_logical_operator_template(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path=(
                "integrations/test-integration/logicalOperators:fetchTemplate"
            ),
            api_version=APIVersion.V1ALPHA,
        )


# -- Error handling tests --


def test_list_integration_logical_operators_api_error(chronicle_client):
    """Test list_integration_logical_operators handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_paginated_request",
        side_effect=APIError("API Error"),
    ):
        with pytest.raises(APIError, match="API Error"):
            list_integration_logical_operators(
                chronicle_client,
                integration_name="test-integration",
            )


def test_get_integration_logical_operator_api_error(chronicle_client):
    """Test get_integration_logical_operator handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        side_effect=APIError("Not found"),
    ):
        with pytest.raises(APIError, match="Not found"):
            get_integration_logical_operator(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="nonexistent",
            )


def test_create_integration_logical_operator_api_error(chronicle_client):
    """Test create_integration_logical_operator handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        side_effect=APIError("Creation failed"),
    ):
        with pytest.raises(APIError, match="Creation failed"):
            create_integration_logical_operator(
                chronicle_client,
                integration_name="test-integration",
                display_name="New Operator",
                script="def evaluate(a, b): return a == b",
                script_timeout="60s",
                enabled=True,
            )


def test_update_integration_logical_operator_api_error(chronicle_client):
    """Test update_integration_logical_operator handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        side_effect=APIError("Update failed"),
    ), patch(
        "secops.chronicle.integration.logical_operators.build_patch_body",
        return_value=({"displayName": "Updated"}, {"updateMask": "displayName"}),
    ):
        with pytest.raises(APIError, match="Update failed"):
            update_integration_logical_operator(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="lo1",
                display_name="Updated",
            )


def test_delete_integration_logical_operator_api_error(chronicle_client):
    """Test delete_integration_logical_operator handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operators.chronicle_request",
        side_effect=APIError("Delete failed"),
    ):
        with pytest.raises(APIError, match="Delete failed"):
            delete_integration_logical_operator(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="lo1",
            )

