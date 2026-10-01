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
"""Tests for Chronicle marketplace integration managers functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.soar.integration.managers import (
    list_integration_managers,
    get_integration_manager,
    delete_integration_manager,
    create_integration_manager,
    update_integration_manager,
    get_integration_manager_template,
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


# -- list_integration_managers tests --


def test_list_integration_managers_success(chronicle_client):
    """Test list_integration_managers delegates to chronicle_paginated_request."""
    expected = {
        "managers": [{"name": "m1"}, {"name": "m2"}],
        "nextPageToken": "t",
    }

    with (
        patch(
            "secops.chronicle.soar.integration.managers.chronicle_paginated_request",
            return_value=expected,
        ) as mock_paginated,
        patch(
            "secops.chronicle.soar.integration.managers.format_resource_id",
            return_value="My Integration",
        ),
    ):
        result = list_integration_managers(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/My Integration/managers",
            items_key="managers",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_managers_default_args(chronicle_client):
    """Test list_integration_managers with default args."""
    expected = {"managers": []}

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_managers(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected


def test_list_integration_managers_with_filters(chronicle_client):
    """Test list_integration_managers with filter and order_by."""
    expected = {"managers": [{"name": "m1"}]}

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_managers(
            chronicle_client,
            integration_name="test-integration",
            filter_string='displayName = "My Manager"',
            order_by="displayName",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": 'displayName = "My Manager"',
            "orderBy": "displayName",
        }


def test_list_integration_managers_as_list(chronicle_client):
    """Test list_integration_managers returns list when as_list=True."""
    expected = [{"name": "m1"}, {"name": "m2"}]

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_managers(
            chronicle_client,
            integration_name="test-integration",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_integration_managers_error(chronicle_client):
    """Test list_integration_managers raises APIError on failure."""
    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_paginated_request",
        side_effect=APIError("Failed to list integration managers"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_managers(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to list integration managers" in str(exc_info.value)


# -- get_integration_manager tests --


def test_get_integration_manager_success(chronicle_client):
    """Test get_integration_manager issues GET request."""
    expected = {
        "name": "managers/m1",
        "displayName": "My Manager",
        "script": "def helper(): pass",
    }

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            manager_id="m1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/managers/m1",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_manager_error(chronicle_client):
    """Test get_integration_manager raises APIError on failure."""
    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        side_effect=APIError("Failed to get integration manager"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_manager(
                chronicle_client,
                integration_name="test-integration",
                manager_id="m1",
            )
        assert "Failed to get integration manager" in str(exc_info.value)


# -- delete_integration_manager tests --


def test_delete_integration_manager_success(chronicle_client):
    """Test delete_integration_manager issues DELETE request."""
    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            manager_id="m1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration/managers/m1",
            api_version=APIVersion.V1BETA,
        )


def test_delete_integration_manager_error(chronicle_client):
    """Test delete_integration_manager raises APIError on failure."""
    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        side_effect=APIError("Failed to delete integration manager"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_manager(
                chronicle_client,
                integration_name="test-integration",
                manager_id="m1",
            )
        assert "Failed to delete integration manager" in str(exc_info.value)


# -- create_integration_manager tests --


def test_create_integration_manager_required_fields_only(chronicle_client):
    """Test create_integration_manager sends only required fields when optionals omitted."""
    expected = {"name": "managers/new", "displayName": "My Manager"}

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Manager",
            script="def helper(): pass",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/managers",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Manager",
                "script": "def helper(): pass",
            },
        )


def test_create_integration_manager_with_description(chronicle_client):
    """Test create_integration_manager includes description when provided."""
    expected = {"name": "managers/new", "displayName": "My Manager"}

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Manager",
            script="def helper(): pass",
            description="A helpful manager",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["description"] == "A helpful manager"


def test_create_integration_manager_error(chronicle_client):
    """Test create_integration_manager raises APIError on failure."""
    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        side_effect=APIError("Failed to create integration manager"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_manager(
                chronicle_client,
                integration_name="test-integration",
                display_name="My Manager",
                script="def helper(): pass",
            )
        assert "Failed to create integration manager" in str(exc_info.value)


# -- update_integration_manager tests --


def test_update_integration_manager_single_field(chronicle_client):
    """Test update_integration_manager updates a single field."""
    expected = {"name": "managers/m1", "displayName": "Updated Manager"}

    with (
        patch(
            "secops.chronicle.soar.integration.managers.chronicle_request",
            return_value=expected,
        ) as mock_request,
        patch(
            "secops.chronicle.soar.integration.managers.build_patch_body",
            return_value=(
                {"displayName": "Updated Manager"},
                {"updateMask": "displayName"},
            ),
        ) as mock_build_patch,
    ):
        result = update_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            manager_id="m1",
            display_name="Updated Manager",
        )

        assert result == expected

        mock_build_patch.assert_called_once()
        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="integrations/test-integration/managers/m1",
            api_version=APIVersion.V1BETA,
            json={"displayName": "Updated Manager"},
            params={"updateMask": "displayName"},
        )


def test_update_integration_manager_multiple_fields(chronicle_client):
    """Test update_integration_manager updates multiple fields."""
    expected = {"name": "managers/m1", "displayName": "Updated Manager"}

    with (
        patch(
            "secops.chronicle.soar.integration.managers.chronicle_request",
            return_value=expected,
        ) as mock_request,
        patch(
            "secops.chronicle.soar.integration.managers.build_patch_body",
            return_value=(
                {
                    "displayName": "Updated Manager",
                    "script": "def new_helper(): pass",
                    "description": "New description",
                },
                {"updateMask": "displayName,script,description"},
            ),
        ),
    ):
        result = update_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            manager_id="m1",
            display_name="Updated Manager",
            script="def new_helper(): pass",
            description="New description",
        )

        assert result == expected


def test_update_integration_manager_with_update_mask(chronicle_client):
    """Test update_integration_manager respects explicit update_mask."""
    expected = {"name": "managers/m1", "displayName": "Updated Manager"}

    with (
        patch(
            "secops.chronicle.soar.integration.managers.chronicle_request",
            return_value=expected,
        ) as mock_request,
        patch(
            "secops.chronicle.soar.integration.managers.build_patch_body",
            return_value=(
                {"displayName": "Updated Manager"},
                {"updateMask": "displayName"},
            ),
        ),
    ):
        result = update_integration_manager(
            chronicle_client,
            integration_name="test-integration",
            manager_id="m1",
            display_name="Updated Manager",
            update_mask="displayName",
        )

        assert result == expected


def test_update_integration_manager_error(chronicle_client):
    """Test update_integration_manager raises APIError on failure."""
    with (
        patch(
            "secops.chronicle.soar.integration.managers.chronicle_request",
            side_effect=APIError("Failed to update integration manager"),
        ),
        patch(
            "secops.chronicle.soar.integration.managers.build_patch_body",
            return_value=(
                {"displayName": "Updated"},
                {"updateMask": "displayName"},
            ),
        ),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration_manager(
                chronicle_client,
                integration_name="test-integration",
                manager_id="m1",
                display_name="Updated",
            )
        assert "Failed to update integration manager" in str(exc_info.value)


# -- get_integration_manager_template tests --


def test_get_integration_manager_template_success(chronicle_client):
    """Test get_integration_manager_template issues GET request."""
    expected = {
        "displayName": "Template Manager",
        "script": "# Template script\ndef template(): pass",
    }

    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_manager_template(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/managers:fetchTemplate",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_manager_template_error(chronicle_client):
    """Test get_integration_manager_template raises APIError on failure."""
    with patch(
        "secops.chronicle.soar.integration.managers.chronicle_request",
        side_effect=APIError("Failed to get integration manager template"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_manager_template(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to get integration manager template" in str(
            exc_info.value
        )
