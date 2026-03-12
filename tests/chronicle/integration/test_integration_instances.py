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
"""Tests for Chronicle marketplace integration instances functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import (
    APIVersion,
    IntegrationInstanceParameter,
)
from secops.chronicle.integration.integration_instances import (
    list_integration_instances,
    get_integration_instance,
    delete_integration_instance,
    create_integration_instance,
    update_integration_instance,
    execute_integration_instance_test,
    get_integration_instance_affected_items,
    get_default_integration_instance,
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


# -- list_integration_instances tests --


def test_list_integration_instances_success(chronicle_client):
    """Test list_integration_instances delegates to chronicle_paginated_request."""
    expected = {
        "integrationInstances": [{"name": "ii1"}, {"name": "ii2"}],
        "nextPageToken": "t",
    }

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.integration_instances.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_instances(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert "integrationInstances" in kwargs["path"]
        assert kwargs["items_key"] == "integrationInstances"
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "next-token"


def test_list_integration_instances_default_args(chronicle_client):
    """Test list_integration_instances with default args."""
    expected = {"integrationInstances": []}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_paginated_request",
        return_value=expected,
    ):
        result = list_integration_instances(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected


def test_list_integration_instances_with_filters(chronicle_client):
    """Test list_integration_instances with filter and order_by."""
    expected = {"integrationInstances": [{"name": "ii1"}]}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_instances(
            chronicle_client,
            integration_name="test-integration",
            filter_string="environment = 'prod'",
            order_by="displayName",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": "environment = 'prod'",
            "orderBy": "displayName",
        }


def test_list_integration_instances_as_list(chronicle_client):
    """Test list_integration_instances returns list when as_list=True."""
    expected = [{"name": "ii1"}, {"name": "ii2"}]

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_instances(
            chronicle_client,
            integration_name="test-integration",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_integration_instances_error(chronicle_client):
    """Test list_integration_instances raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_paginated_request",
        side_effect=APIError("Failed to list integration instances"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_instances(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to list integration instances" in str(exc_info.value)


# -- get_integration_instance tests --


def test_get_integration_instance_success(chronicle_client):
    """Test get_integration_instance issues GET request."""
    expected = {
        "name": "integrationInstances/ii1",
        "displayName": "My Instance",
        "environment": "production",
    }

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "integrationInstances/ii1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_integration_instance_error(chronicle_client):
    """Test get_integration_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to get integration instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_instance(
                chronicle_client,
                integration_name="test-integration",
                integration_instance_id="ii1",
            )
        assert "Failed to get integration instance" in str(exc_info.value)


# -- delete_integration_instance tests --


def test_delete_integration_instance_success(chronicle_client):
    """Test delete_integration_instance issues DELETE request."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert "integrationInstances/ii1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_delete_integration_instance_error(chronicle_client):
    """Test delete_integration_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to delete integration instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_instance(
                chronicle_client,
                integration_name="test-integration",
                integration_instance_id="ii1",
            )
        assert "Failed to delete integration instance" in str(exc_info.value)


# -- create_integration_instance tests --


def test_create_integration_instance_required_fields_only(chronicle_client):
    """Test create_integration_instance sends only required fields."""
    expected = {"name": "integrationInstances/new", "displayName": "My Instance"}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            environment="production",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/integrationInstances",
            api_version=APIVersion.V1BETA,
            json={
                "environment": "production",
            },
        )


def test_create_integration_instance_with_optional_fields(chronicle_client):
    """Test create_integration_instance includes optional fields when provided."""
    expected = {"name": "integrationInstances/new"}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            environment="production",
            display_name="My Instance",
            description="Test instance",
            parameters=[{"id": 1, "value": "test"}],
            agent="agent-123",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["environment"] == "production"
        assert kwargs["json"]["displayName"] == "My Instance"
        assert kwargs["json"]["description"] == "Test instance"
        assert kwargs["json"]["parameters"] == [{"id": 1, "value": "test"}]
        assert kwargs["json"]["agent"] == "agent-123"


def test_create_integration_instance_with_dataclass_params(chronicle_client):
    """Test create_integration_instance converts dataclass parameters."""
    expected = {"name": "integrationInstances/new"}

    param = IntegrationInstanceParameter(value="test-value")

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            environment="production",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["value"] == "test-value"


def test_create_integration_instance_error(chronicle_client):
    """Test create_integration_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to create integration instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_instance(
                chronicle_client,
                integration_name="test-integration",
                environment="production",
            )
        assert "Failed to create integration instance" in str(exc_info.value)


# -- update_integration_instance tests --


def test_update_integration_instance_with_single_field(chronicle_client):
    """Test update_integration_instance with single field updates updateMask."""
    expected = {"name": "integrationInstances/ii1", "displayName": "Updated"}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
            display_name="Updated",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PATCH"
        assert "integrationInstances/ii1" in kwargs["endpoint_path"]
        assert kwargs["json"]["displayName"] == "Updated"
        assert kwargs["params"]["updateMask"] == "displayName"


def test_update_integration_instance_with_multiple_fields(chronicle_client):
    """Test update_integration_instance with multiple fields."""
    expected = {"name": "integrationInstances/ii1"}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
            display_name="Updated",
            description="New description",
            environment="staging",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["displayName"] == "Updated"
        assert kwargs["json"]["description"] == "New description"
        assert kwargs["json"]["environment"] == "staging"
        assert "displayName" in kwargs["params"]["updateMask"]
        assert "description" in kwargs["params"]["updateMask"]
        assert "environment" in kwargs["params"]["updateMask"]


def test_update_integration_instance_with_custom_update_mask(chronicle_client):
    """Test update_integration_instance with explicitly provided update_mask."""
    expected = {"name": "integrationInstances/ii1"}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
            display_name="Updated",
            update_mask="displayName,environment",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["params"]["updateMask"] == "displayName,environment"


def test_update_integration_instance_with_dataclass_params(chronicle_client):
    """Test update_integration_instance converts dataclass parameters."""
    expected = {"name": "integrationInstances/ii1"}

    param = IntegrationInstanceParameter(value="test-value")

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_instance(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["value"] == "test-value"


def test_update_integration_instance_error(chronicle_client):
    """Test update_integration_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to update integration instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration_instance(
                chronicle_client,
                integration_name="test-integration",
                integration_instance_id="ii1",
                display_name="Updated",
            )
        assert "Failed to update integration instance" in str(exc_info.value)


# -- execute_integration_instance_test tests --


def test_execute_integration_instance_test_success(chronicle_client):
    """Test execute_integration_instance_test issues POST request."""
    expected = {
        "successful": True,
        "message": "Test successful",
    }

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = execute_integration_instance_test(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert "integrationInstances/ii1:executeTest" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_execute_integration_instance_test_failure(chronicle_client):
    """Test execute_integration_instance_test when test fails."""
    expected = {
        "successful": False,
        "message": "Connection failed",
    }

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ):
        result = execute_integration_instance_test(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
        )

        assert result == expected
        assert result["successful"] is False


def test_execute_integration_instance_test_error(chronicle_client):
    """Test execute_integration_instance_test raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to execute test"),
    ):
        with pytest.raises(APIError) as exc_info:
            execute_integration_instance_test(
                chronicle_client,
                integration_name="test-integration",
                integration_instance_id="ii1",
            )
        assert "Failed to execute test" in str(exc_info.value)


# -- get_integration_instance_affected_items tests --


def test_get_integration_instance_affected_items_success(chronicle_client):
    """Test get_integration_instance_affected_items issues GET request."""
    expected = {
        "affectedPlaybooks": [
            {"name": "playbook1", "displayName": "Playbook 1"},
            {"name": "playbook2", "displayName": "Playbook 2"},
        ]
    }

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_instance_affected_items(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "integrationInstances/ii1:fetchAffectedItems" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_integration_instance_affected_items_empty(chronicle_client):
    """Test get_integration_instance_affected_items with no affected items."""
    expected = {"affectedPlaybooks": []}

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ):
        result = get_integration_instance_affected_items(
            chronicle_client,
            integration_name="test-integration",
            integration_instance_id="ii1",
        )

        assert result == expected
        assert len(result["affectedPlaybooks"]) == 0


def test_get_integration_instance_affected_items_error(chronicle_client):
    """Test get_integration_instance_affected_items raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to fetch affected items"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_instance_affected_items(
                chronicle_client,
                integration_name="test-integration",
                integration_instance_id="ii1",
            )
        assert "Failed to fetch affected items" in str(exc_info.value)


# -- get_default_integration_instance tests --


def test_get_default_integration_instance_success(chronicle_client):
    """Test get_default_integration_instance issues GET request."""
    expected = {
        "name": "integrationInstances/default",
        "displayName": "Default Instance",
        "environment": "default",
    }

    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_default_integration_instance(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "integrationInstances:fetchDefaultInstance" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_default_integration_instance_error(chronicle_client):
    """Test get_default_integration_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integration_instances.chronicle_request",
        side_effect=APIError("Failed to get default instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_default_integration_instance(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to get default instance" in str(exc_info.value)

