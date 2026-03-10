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
"""Tests for Chronicle integration connector instances functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import (
    APIVersion,
    ConnectorInstanceParameter,
)
from secops.chronicle.integration.connector_instances import (
    list_connector_instances,
    get_connector_instance,
    delete_connector_instance,
    create_connector_instance,
    update_connector_instance,
    get_connector_instance_latest_definition,
    set_connector_instance_logs_collection,
    run_connector_instance_on_demand,
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


# -- list_connector_instances tests --


def test_list_connector_instances_success(chronicle_client):
    """Test list_connector_instances delegates to chronicle_paginated_request."""
    expected = {
        "connectorInstances": [{"name": "ci1"}, {"name": "ci2"}],
        "nextPageToken": "t",
    }

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.connector_instances.format_resource_id",
        return_value="My Integration",
    ):
        result = list_connector_instances(
            chronicle_client,
            integration_name="My Integration",
            connector_id="c1",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert "connectors/c1/connectorInstances" in kwargs["path"]
        assert kwargs["items_key"] == "connectorInstances"
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "next-token"


def test_list_connector_instances_default_args(chronicle_client):
    """Test list_connector_instances with default args."""
    expected = {"connectorInstances": []}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_paginated_request",
        return_value=expected,
    ):
        result = list_connector_instances(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
        )

        assert result == expected


def test_list_connector_instances_with_filters(chronicle_client):
    """Test list_connector_instances with filter and order_by."""
    expected = {"connectorInstances": [{"name": "ci1"}]}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_instances(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            filter_string='enabled = true',
            order_by="displayName",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": 'enabled = true',
            "orderBy": "displayName",
        }


def test_list_connector_instances_as_list(chronicle_client):
    """Test list_connector_instances returns list when as_list=True."""
    expected = [{"name": "ci1"}, {"name": "ci2"}]

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_instances(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_connector_instances_error(chronicle_client):
    """Test list_connector_instances raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_paginated_request",
        side_effect=APIError("Failed to list connector instances"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_connector_instances(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
            )
        assert "Failed to list connector instances" in str(exc_info.value)


# -- get_connector_instance tests --


def test_get_connector_instance_success(chronicle_client):
    """Test get_connector_instance issues GET request."""
    expected = {
        "name": "connectorInstances/ci1",
        "displayName": "Test Instance",
        "enabled": True,
    }

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "connectors/c1/connectorInstances/ci1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_connector_instance_error(chronicle_client):
    """Test get_connector_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to get connector instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_connector_instance(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
            )
        assert "Failed to get connector instance" in str(exc_info.value)


# -- delete_connector_instance tests --


def test_delete_connector_instance_success(chronicle_client):
    """Test delete_connector_instance issues DELETE request."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert "connectors/c1/connectorInstances/ci1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_delete_connector_instance_error(chronicle_client):
    """Test delete_connector_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to delete connector instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_connector_instance(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
            )
        assert "Failed to delete connector instance" in str(exc_info.value)


# -- create_connector_instance tests --


def test_create_connector_instance_required_fields_only(chronicle_client):
    """Test create_connector_instance with required fields only."""
    expected = {"name": "connectorInstances/new", "displayName": "New Instance"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            environment="production",
            display_name="New Instance",
            interval_seconds=3600,
            timeout_seconds=300,
        )

        assert result == expected

        mock_request.assert_called_once()
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert "connectors/c1/connectorInstances" in kwargs["endpoint_path"]
        assert kwargs["json"]["environment"] == "production"
        assert kwargs["json"]["displayName"] == "New Instance"
        assert kwargs["json"]["intervalSeconds"] == 3600
        assert kwargs["json"]["timeoutSeconds"] == 300


def test_create_connector_instance_with_optional_fields(chronicle_client):
    """Test create_connector_instance includes optional fields when provided."""
    expected = {"name": "connectorInstances/new"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            environment="production",
            display_name="New Instance",
            interval_seconds=3600,
            timeout_seconds=300,
            description="Test description",
            agent="agent-123",
            allow_list=["192.168.1.0/24"],
            product_field_name="product",
            event_field_name="event",
            integration_version="1.0.0",
            version="2.0.0",
            logging_enabled_until_unix_ms="1234567890000",
            connector_instance_id="custom-id",
            enabled=True,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["description"] == "Test description"
        assert kwargs["json"]["agent"] == "agent-123"
        assert kwargs["json"]["allowList"] == ["192.168.1.0/24"]
        assert kwargs["json"]["productFieldName"] == "product"
        assert kwargs["json"]["eventFieldName"] == "event"
        assert kwargs["json"]["integrationVersion"] == "1.0.0"
        assert kwargs["json"]["version"] == "2.0.0"
        assert kwargs["json"]["loggingEnabledUntilUnixMs"] == "1234567890000"
        assert kwargs["json"]["id"] == "custom-id"
        assert kwargs["json"]["enabled"] is True


def test_create_connector_instance_with_parameters(chronicle_client):
    """Test create_connector_instance with ConnectorInstanceParameter objects."""
    expected = {"name": "connectorInstances/new"}

    param = ConnectorInstanceParameter()
    param.value = "secret-key"

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            environment="production",
            display_name="New Instance",
            interval_seconds=3600,
            timeout_seconds=300,
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert len(kwargs["json"]["parameters"]) == 1
        assert kwargs["json"]["parameters"][0]["value"] == "secret-key"


def test_create_connector_instance_with_dict_parameters(chronicle_client):
    """Test create_connector_instance with dict parameters."""
    expected = {"name": "connectorInstances/new"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            environment="production",
            display_name="New Instance",
            interval_seconds=3600,
            timeout_seconds=300,
            parameters=[{"displayName": "API Key", "value": "secret-key"}],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["parameters"][0]["displayName"] == "API Key"


def test_create_connector_instance_error(chronicle_client):
    """Test create_connector_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to create connector instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_connector_instance(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                environment="production",
                display_name="New Instance",
                interval_seconds=3600,
                timeout_seconds=300,
            )
        assert "Failed to create connector instance" in str(exc_info.value)


# -- update_connector_instance tests --


def test_update_connector_instance_success(chronicle_client):
    """Test update_connector_instance updates fields."""
    expected = {"name": "connectorInstances/ci1", "displayName": "Updated"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            display_name="Updated",
            enabled=True,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PATCH"
        assert "connectors/c1/connectorInstances/ci1" in kwargs["endpoint_path"]
        assert kwargs["json"]["displayName"] == "Updated"
        assert kwargs["json"]["enabled"] is True
        # Check that update mask contains the expected fields
        assert "displayName" in kwargs["params"]["updateMask"]
        assert "enabled" in kwargs["params"]["updateMask"]


def test_update_connector_instance_with_custom_mask(chronicle_client):
    """Test update_connector_instance with custom update_mask."""
    expected = {"name": "connectorInstances/ci1"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            display_name="Updated",
            update_mask="displayName",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["params"]["updateMask"] == "displayName"


def test_update_connector_instance_with_parameters(chronicle_client):
    """Test update_connector_instance with parameters."""
    expected = {"name": "connectorInstances/ci1"}

    param = ConnectorInstanceParameter()
    param.value = "new-key"

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert len(kwargs["json"]["parameters"]) == 1
        assert kwargs["json"]["parameters"][0]["value"] == "new-key"


def test_update_connector_instance_error(chronicle_client):
    """Test update_connector_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to update connector instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_connector_instance(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
                display_name="Updated",
            )
        assert "Failed to update connector instance" in str(exc_info.value)


# -- get_connector_instance_latest_definition tests --


def test_get_connector_instance_latest_definition_success(chronicle_client):
    """Test get_connector_instance_latest_definition issues GET request."""
    expected = {
        "name": "connectorInstances/ci1",
        "displayName": "Refreshed Instance",
    }

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_instance_latest_definition(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "connectorInstances/ci1:fetchLatestDefinition" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_connector_instance_latest_definition_error(chronicle_client):
    """Test get_connector_instance_latest_definition raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to fetch latest definition"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_connector_instance_latest_definition(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
            )
        assert "Failed to fetch latest definition" in str(exc_info.value)


# -- set_connector_instance_logs_collection tests --


def test_set_connector_instance_logs_collection_enable(chronicle_client):
    """Test set_connector_instance_logs_collection enables logs."""
    expected = {"loggingEnabledUntilUnixMs": "1234567890000"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = set_connector_instance_logs_collection(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            enabled=True,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert "connectorInstances/ci1:setLogsCollection" in kwargs["endpoint_path"]
        assert kwargs["json"]["enabled"] is True


def test_set_connector_instance_logs_collection_disable(chronicle_client):
    """Test set_connector_instance_logs_collection disables logs."""
    expected = {}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = set_connector_instance_logs_collection(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            enabled=False,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["enabled"] is False


def test_set_connector_instance_logs_collection_error(chronicle_client):
    """Test set_connector_instance_logs_collection raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to set logs collection"),
    ):
        with pytest.raises(APIError) as exc_info:
            set_connector_instance_logs_collection(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
                enabled=True,
            )
        assert "Failed to set logs collection" in str(exc_info.value)


# -- run_connector_instance_on_demand tests --


def test_run_connector_instance_on_demand_success(chronicle_client):
    """Test run_connector_instance_on_demand triggers execution."""
    expected = {
        "debugOutput": "Execution completed",
        "success": True,
        "sampleCases": [],
    }

    connector_instance = {
        "name": "connectorInstances/ci1",
        "displayName": "Test Instance",
        "parameters": [{"displayName": "param1", "value": "value1"}],
    }

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = run_connector_instance_on_demand(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            connector_instance=connector_instance,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert "connectorInstances/ci1:runOnDemand" in kwargs["endpoint_path"]
        assert kwargs["json"]["connectorInstance"] == connector_instance


def test_run_connector_instance_on_demand_error(chronicle_client):
    """Test run_connector_instance_on_demand raises APIError on failure."""
    connector_instance = {"name": "connectorInstances/ci1"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        side_effect=APIError("Failed to run connector instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            run_connector_instance_on_demand(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                connector_instance_id="ci1",
                connector_instance=connector_instance,
            )
        assert "Failed to run connector instance" in str(exc_info.value)


# -- API version tests --


def test_list_connector_instances_custom_api_version(chronicle_client):
    """Test list_connector_instances with custom API version."""
    expected = {"connectorInstances": []}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_connector_instances(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_get_connector_instance_custom_api_version(chronicle_client):
    """Test get_connector_instance with custom API version."""
    expected = {"name": "connectorInstances/ci1"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_delete_connector_instance_custom_api_version(chronicle_client):
    """Test delete_connector_instance with custom API version."""
    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            api_version=APIVersion.V1ALPHA,
        )

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_create_connector_instance_custom_api_version(chronicle_client):
    """Test create_connector_instance with custom API version."""
    expected = {"name": "connectorInstances/new"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            environment="production",
            display_name="New Instance",
            interval_seconds=3600,
            timeout_seconds=300,
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_update_connector_instance_custom_api_version(chronicle_client):
    """Test update_connector_instance with custom API version."""
    expected = {"name": "connectorInstances/ci1"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_connector_instance(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            display_name="Updated",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_get_connector_instance_latest_definition_custom_api_version(chronicle_client):
    """Test get_connector_instance_latest_definition with custom API version."""
    expected = {"name": "connectorInstances/ci1"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_connector_instance_latest_definition(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_set_connector_instance_logs_collection_custom_api_version(chronicle_client):
    """Test set_connector_instance_logs_collection with custom API version."""
    expected = {}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = set_connector_instance_logs_collection(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            enabled=True,
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_run_connector_instance_on_demand_custom_api_version(chronicle_client):
    """Test run_connector_instance_on_demand with custom API version."""
    expected = {"success": True}
    connector_instance = {"name": "connectorInstances/ci1"}

    with patch(
        "secops.chronicle.integration.connector_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = run_connector_instance_on_demand(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            connector_instance_id="ci1",
            connector_instance=connector_instance,
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA




