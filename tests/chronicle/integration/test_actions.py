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
"""Tests for Chronicle marketplace integration actions functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.actions import (
    list_integration_actions,
    get_integration_action,
    delete_integration_action,
    create_integration_action,
    update_integration_action,
    execute_integration_action_test,
    get_integration_actions_by_environment,
    get_integration_action_template,
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


# -- list_integration_actions tests --


def test_list_integration_actions_success(chronicle_client):
    """Test list_integration_actions delegates to chronicle_paginated_request."""
    expected = {"actions": [{"name": "a1"}, {"name": "a2"}], "nextPageToken": "t"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        # Avoid assuming how format_resource_id encodes/cases values
        "secops.chronicle.integration.actions.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_actions(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/My Integration/actions",
            items_key="actions",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_actions_default_args(chronicle_client):
    """Test list_integration_actions with default args."""
    expected = {"actions": []}

    with patch(
        "secops.chronicle.integration.actions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_actions(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/test-integration/actions",
            items_key="actions",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=False,
        )


def test_list_integration_actions_with_filter_order_expand(chronicle_client):
    """Test list_integration_actions passes filter/orderBy/expand in extra_params."""
    expected = {"actions": [{"name": "a1"}]}

    with patch(
        "secops.chronicle.integration.actions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_actions(
            chronicle_client,
            integration_name="test-integration",
            filter_string='displayName = "My Action"',
            order_by="displayName",
            expand="parameters,dynamicResults",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/test-integration/actions",
            items_key="actions",
            page_size=None,
            page_token=None,
            extra_params={
                "filter": 'displayName = "My Action"',
                "orderBy": "displayName",
                "expand": "parameters,dynamicResults",
            },
            as_list=False,
        )


def test_list_integration_actions_as_list(chronicle_client):
    """Test list_integration_actions with as_list=True."""
    expected = [{"name": "a1"}, {"name": "a2"}]

    with patch(
        "secops.chronicle.integration.actions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_actions(
            chronicle_client,
            integration_name="test-integration",
            as_list=True,
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/test-integration/actions",
            items_key="actions",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=True,
        )


def test_list_integration_actions_error(chronicle_client):
    """Test list_integration_actions propagates APIError from helper."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_paginated_request",
        side_effect=APIError("Failed to list integration actions"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_actions(
                chronicle_client,
                integration_name="test-integration",
            )

        assert "Failed to list integration actions" in str(exc_info.value)


# -- get_integration_action tests --


def test_get_integration_action_success(chronicle_client):
    """Test get_integration_action returns expected result."""
    expected = {"name": "actions/a1", "displayName": "Action 1"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_action(
            chronicle_client,
            integration_name="test-integration",
            action_id="a1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/actions/a1",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_action_error(chronicle_client):
    """Test get_integration_action raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to get integration action"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_action(
                chronicle_client,
                integration_name="test-integration",
                action_id="a1",
            )
        assert "Failed to get integration action" in str(exc_info.value)


# -- delete_integration_action tests --


def test_delete_integration_action_success(chronicle_client):
    """Test delete_integration_action issues DELETE request."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_action(
            chronicle_client,
            integration_name="test-integration",
            action_id="a1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration/actions/a1",
            api_version=APIVersion.V1BETA,
        )


def test_delete_integration_action_error(chronicle_client):
    """Test delete_integration_action raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to delete integration action"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_action(
                chronicle_client,
                integration_name="test-integration",
                action_id="a1",
            )
        assert "Failed to delete integration action" in str(exc_info.value)


# -- create_integration_action tests --


def test_create_integration_action_required_fields_only(chronicle_client):
    """Test create_integration_action sends only required fields when optionals omitted."""
    expected = {"name": "actions/new", "displayName": "My Action"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_action(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Action",
            script="print('hi')",
            timeout_seconds=120,
            enabled=True,
            script_result_name="result",
            is_async=False,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/actions",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Action",
                "script": "print('hi')",
                "timeoutSeconds": 120,
                "enabled": True,
                "scriptResultName": "result",
                "async": False,
            },
        )


def test_create_integration_action_all_fields(chronicle_client):
    """Test create_integration_action with all optional fields."""
    expected = {"name": "actions/new"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_action(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Action",
            script="print('hi')",
            timeout_seconds=120,
            enabled=True,
            script_result_name="result",
            is_async=True,
            description="desc",
            default_result_value="default",
            async_polling_interval_seconds=5,
            async_total_timeout_seconds=60,
            dynamic_results=[{"name": "dr1"}],
            parameters=[{"name": "p1"}],
            ai_generated=False,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/actions",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Action",
                "script": "print('hi')",
                "timeoutSeconds": 120,
                "enabled": True,
                "scriptResultName": "result",
                "async": True,
                "description": "desc",
                "defaultResultValue": "default",
                "asyncPollingIntervalSeconds": 5,
                "asyncTotalTimeoutSeconds": 60,
                "dynamicResults": [{"name": "dr1"}],
                "parameters": [{"name": "p1"}],
                "aiGenerated": False,
            },
        )


def test_create_integration_action_none_fields_excluded(chronicle_client):
    """Test that None optional fields are not included in request body."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value={"name": "actions/new"},
    ) as mock_request:
        create_integration_action(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Action",
            script="print('hi')",
            timeout_seconds=120,
            enabled=True,
            script_result_name="result",
            is_async=False,
            description=None,
            default_result_value=None,
            async_polling_interval_seconds=None,
            async_total_timeout_seconds=None,
            dynamic_results=None,
            parameters=None,
            ai_generated=None,
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/actions",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Action",
                "script": "print('hi')",
                "timeoutSeconds": 120,
                "enabled": True,
                "scriptResultName": "result",
                "async": False,
            },
        )


def test_create_integration_action_error(chronicle_client):
    """Test create_integration_action raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to create integration action"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_action(
                chronicle_client,
                integration_name="test-integration",
                display_name="My Action",
                script="print('hi')",
                timeout_seconds=120,
                enabled=True,
                script_result_name="result",
                is_async=False,
            )
        assert "Failed to create integration action" in str(exc_info.value)


# -- update_integration_action tests --


def test_update_integration_action_with_explicit_update_mask(chronicle_client):
    """Test update_integration_action passes through explicit update_mask."""
    expected = {"name": "actions/a1", "displayName": "New Name"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_action(
            chronicle_client,
            integration_name="test-integration",
            action_id="a1",
            display_name="New Name",
            update_mask="displayName",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="integrations/test-integration/actions/a1",
            api_version=APIVersion.V1BETA,
            json={"displayName": "New Name"},
            params={"updateMask": "displayName"},
        )


def test_update_integration_action_auto_update_mask(chronicle_client):
    """Test update_integration_action auto-generates updateMask based on fields.

    build_patch_body ordering isn't guaranteed; assert order-insensitively.
    """
    expected = {"name": "actions/a1"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_action(
            chronicle_client,
            integration_name="test-integration",
            action_id="a1",
            enabled=False,
            timeout_seconds=300,
        )

        assert result == expected

        # Assert the call happened once and inspect args to avoid ordering issues.
        assert mock_request.call_count == 1
        _, kwargs = mock_request.call_args

        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == "integrations/test-integration/actions/a1"
        assert kwargs["api_version"] == APIVersion.V1BETA

        assert kwargs["json"] == {"enabled": False, "timeoutSeconds": 300}

        update_mask = kwargs["params"]["updateMask"]
        assert set(update_mask.split(",")) == {"enabled", "timeoutSeconds"}


def test_update_integration_action_error(chronicle_client):
    """Test update_integration_action raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to update integration action"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration_action(
                chronicle_client,
                integration_name="test-integration",
                action_id="a1",
                display_name="New Name",
            )
        assert "Failed to update integration action" in str(exc_info.value)


# -- test_integration_action tests --


def test_execute_test_integration_action_success(chronicle_client):
    """Test test_integration_action issues executeTest POST with correct body."""
    expected = {"output": "ok", "debugOutput": ""}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        action = {"displayName": "My Action", "script": "print('hi')"}
        result = execute_integration_action_test(
            chronicle_client,
            integration_name="test-integration",
            test_case_id=123,
            action=action,
            scope="INTEGRATION_INSTANCE",
            integration_instance_id="inst-1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/actions:executeTest",
            api_version=APIVersion.V1BETA,
            json={
                "testCaseId": 123,
                "action": action,
                "scope": "INTEGRATION_INSTANCE",
                "integrationInstanceId": "inst-1",
            },
        )


def test_execute_test_integration_action_error(chronicle_client):
    """Test test_integration_action raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to test integration action"),
    ):
        with pytest.raises(APIError) as exc_info:
            execute_integration_action_test(
                chronicle_client,
                integration_name="test-integration",
                test_case_id=123,
                action={"displayName": "My Action"},
                scope="INTEGRATION_INSTANCE",
                integration_instance_id="inst-1",
            )
        assert "Failed to test integration action" in str(exc_info.value)


# -- get_integration_actions_by_environment tests --


def test_get_integration_actions_by_environment_success(chronicle_client):
    """Test get_integration_actions_by_environment issues GET with correct params."""
    expected = {"actions": [{"name": "a1"}]}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_actions_by_environment(
            chronicle_client,
            integration_name="test-integration",
            environments=["prod", "dev"],
            include_widgets=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/actions:fetchActionsByEnvironment",
            api_version=APIVersion.V1BETA,
            params={"environments": ["prod", "dev"], "includeWidgets": True},
        )


def test_get_integration_actions_by_environment_error(chronicle_client):
    """Test get_integration_actions_by_environment raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to fetch actions by environment"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_actions_by_environment(
                chronicle_client,
                integration_name="test-integration",
                environments=["prod"],
                include_widgets=False,
            )
        assert "Failed to fetch actions by environment" in str(exc_info.value)


# -- get_integration_action_template tests --


def test_get_integration_action_template_default_async_false(chronicle_client):
    """Test get_integration_action_template uses async=False by default."""
    expected = {"script": "# template"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_action_template(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/actions:fetchTemplate",
            api_version=APIVersion.V1BETA,
            params={"async": False},
        )


def test_get_integration_action_template_async_true(chronicle_client):
    """Test get_integration_action_template with is_async=True."""
    expected = {"script": "# async template"}

    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_action_template(
            chronicle_client,
            integration_name="test-integration",
            is_async=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/actions:fetchTemplate",
            api_version=APIVersion.V1BETA,
            params={"async": True},
        )


def test_get_integration_action_template_error(chronicle_client):
    """Test get_integration_action_template raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.actions.chronicle_request",
        side_effect=APIError("Failed to fetch action template"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_action_template(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to fetch action template" in str(exc_info.value)