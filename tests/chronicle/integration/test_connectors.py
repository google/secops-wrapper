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
"""Tests for Chronicle marketplace integration connectors functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import (
    APIVersion,
    ConnectorParameter,
    ParamType,
    ConnectorParamMode,
    ConnectorRule,
    ConnectorRuleType,
)
from secops.chronicle.integration.connectors import (
    list_integration_connectors,
    get_integration_connector,
    delete_integration_connector,
    create_integration_connector,
    update_integration_connector,
    execute_integration_connector_test,
    get_integration_connector_template,
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


# -- list_integration_connectors tests --


def test_list_integration_connectors_success(chronicle_client):
    """Test list_integration_connectors delegates to chronicle_paginated_request."""
    expected = {"connectors": [{"name": "c1"}, {"name": "c2"}], "nextPageToken": "t"}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.connectors.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_connectors(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/My Integration/connectors",
            items_key="connectors",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_connectors_default_args(chronicle_client):
    """Test list_integration_connectors with default args."""
    expected = {"connectors": []}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_connectors(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected


def test_list_integration_connectors_with_filters(chronicle_client):
    """Test list_integration_connectors with filter and order_by."""
    expected = {"connectors": [{"name": "c1"}]}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_connectors(
            chronicle_client,
            integration_name="test-integration",
            filter_string="enabled=true",
            order_by="displayName",
            exclude_staging=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": "enabled=true",
            "orderBy": "displayName",
            "excludeStaging": True,
        }


def test_list_integration_connectors_as_list(chronicle_client):
    """Test list_integration_connectors returns list when as_list=True."""
    expected = [{"name": "c1"}, {"name": "c2"}]

    with patch(
        "secops.chronicle.integration.connectors.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_connectors(
            chronicle_client,
            integration_name="test-integration",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_integration_connectors_error(chronicle_client):
    """Test list_integration_connectors raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_paginated_request",
        side_effect=APIError("Failed to list integration connectors"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_connectors(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to list integration connectors" in str(exc_info.value)


# -- get_integration_connector tests --


def test_get_integration_connector_success(chronicle_client):
    """Test get_integration_connector issues GET request."""
    expected = {
        "name": "connectors/c1",
        "displayName": "My Connector",
        "script": "print('hello')",
    }

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/connectors/c1",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_connector_error(chronicle_client):
    """Test get_integration_connector raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        side_effect=APIError("Failed to get integration connector"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_connector(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
            )
        assert "Failed to get integration connector" in str(exc_info.value)


# -- delete_integration_connector tests --


def test_delete_integration_connector_success(chronicle_client):
    """Test delete_integration_connector issues DELETE request."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration/connectors/c1",
            api_version=APIVersion.V1BETA,
        )


def test_delete_integration_connector_error(chronicle_client):
    """Test delete_integration_connector raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        side_effect=APIError("Failed to delete integration connector"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_connector(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
            )
        assert "Failed to delete integration connector" in str(exc_info.value)


# -- create_integration_connector tests --


def test_create_integration_connector_required_fields_only(chronicle_client):
    """Test create_integration_connector sends only required fields when optionals omitted."""
    expected = {"name": "connectors/new", "displayName": "My Connector"}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Connector",
            script="print('hi')",
            timeout_seconds=300,
            enabled=True,
            product_field_name="product",
            event_field_name="event",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/connectors",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Connector",
                "script": "print('hi')",
                "timeoutSeconds": 300,
                "enabled": True,
                "productFieldName": "product",
                "eventFieldName": "event",
            },
        )


def test_create_integration_connector_with_optional_fields(chronicle_client):
    """Test create_integration_connector includes optional fields when provided."""
    expected = {"name": "connectors/new"}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Connector",
            script="print('hi')",
            timeout_seconds=300,
            enabled=True,
            product_field_name="product",
            event_field_name="event",
            description="Test connector",
            parameters=[{"name": "p1", "type": "STRING"}],
            rules=[{"name": "r1", "type": "MAPPING"}],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["description"] == "Test connector"
        assert kwargs["json"]["parameters"] == [{"name": "p1", "type": "STRING"}]
        assert kwargs["json"]["rules"] == [{"name": "r1", "type": "MAPPING"}]


def test_create_integration_connector_with_dataclass_parameters(chronicle_client):
    """Test create_integration_connector converts ConnectorParameter dataclasses."""
    expected = {"name": "connectors/new"}

    param = ConnectorParameter(
        display_name="API Key",
        type=ParamType.STRING,
        mode=ConnectorParamMode.REGULAR,
        mandatory=True,
        description="API key for authentication",
    )

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Connector",
            script="print('hi')",
            timeout_seconds=300,
            enabled=True,
            product_field_name="product",
            event_field_name="event",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["displayName"] == "API Key"
        assert params_sent[0]["type"] == "STRING"


def test_create_integration_connector_with_dataclass_rules(chronicle_client):
    """Test create_integration_connector converts ConnectorRule dataclasses."""
    expected = {"name": "connectors/new"}

    rule = ConnectorRule(
        display_name="Mapping Rule",
        type=ConnectorRuleType.ALLOW_LIST,
    )

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Connector",
            script="print('hi')",
            timeout_seconds=300,
            enabled=True,
            product_field_name="product",
            event_field_name="event",
            rules=[rule],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        rules_sent = kwargs["json"]["rules"]
        assert len(rules_sent) == 1
        assert rules_sent[0]["displayName"] == "Mapping Rule"
        assert rules_sent[0]["type"] == "ALLOW_LIST"


def test_create_integration_connector_error(chronicle_client):
    """Test create_integration_connector raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        side_effect=APIError("Failed to create integration connector"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_connector(
                chronicle_client,
                integration_name="test-integration",
                display_name="My Connector",
                script="print('hi')",
                timeout_seconds=300,
                enabled=True,
                product_field_name="product",
                event_field_name="event",
            )
        assert "Failed to create integration connector" in str(exc_info.value)


# -- update_integration_connector tests --


def test_update_integration_connector_with_explicit_update_mask(chronicle_client):
    """Test update_integration_connector passes through explicit update_mask."""
    expected = {"name": "connectors/c1", "displayName": "New Name"}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            display_name="New Name",
            update_mask="displayName",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="integrations/test-integration/connectors/c1",
            api_version=APIVersion.V1BETA,
            json={"displayName": "New Name"},
            params={"updateMask": "displayName"},
        )


def test_update_integration_connector_auto_update_mask(chronicle_client):
    """Test update_integration_connector auto-generates updateMask based on fields."""
    expected = {"name": "connectors/c1"}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            enabled=False,
            timeout_seconds=600,
        )

        assert result == expected

        assert mock_request.call_count == 1
        _, kwargs = mock_request.call_args

        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == "integrations/test-integration/connectors/c1"
        assert kwargs["api_version"] == APIVersion.V1BETA

        assert kwargs["json"] == {"enabled": False, "timeoutSeconds": 600}

        update_mask = kwargs["params"]["updateMask"]
        assert set(update_mask.split(",")) == {"enabled", "timeoutSeconds"}


def test_update_integration_connector_with_parameters(chronicle_client):
    """Test update_integration_connector with parameters field."""
    expected = {"name": "connectors/c1"}

    param = ConnectorParameter(
        display_name="Auth Token",
        type=ParamType.STRING,
        mode=ConnectorParamMode.REGULAR,
        mandatory=True,
    )

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["displayName"] == "Auth Token"


def test_update_integration_connector_with_rules(chronicle_client):
    """Test update_integration_connector with rules field."""
    expected = {"name": "connectors/c1"}

    rule = ConnectorRule(
        display_name="Filter Rule",
        type=ConnectorRuleType.BLOCK_LIST,
    )

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_connector(
            chronicle_client,
            integration_name="test-integration",
            connector_id="c1",
            rules=[rule],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        rules_sent = kwargs["json"]["rules"]
        assert len(rules_sent) == 1
        assert rules_sent[0]["displayName"] == "Filter Rule"


def test_update_integration_connector_error(chronicle_client):
    """Test update_integration_connector raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        side_effect=APIError("Failed to update integration connector"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration_connector(
                chronicle_client,
                integration_name="test-integration",
                connector_id="c1",
                display_name="New Name",
            )
        assert "Failed to update integration connector" in str(exc_info.value)


# -- execute_integration_connector_test tests --


def test_execute_integration_connector_test_success(chronicle_client):
    """Test execute_integration_connector_test sends POST request with connector."""
    expected = {
        "outputMessage": "Success",
        "debugOutputMessage": "Debug info",
        "resultJson": {"status": "ok"},
    }

    connector = {
        "displayName": "Test Connector",
        "script": "print('test')",
        "enabled": True,
    }

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = execute_integration_connector_test(
            chronicle_client,
            integration_name="test-integration",
            connector=connector,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/connectors:executeTest",
            api_version=APIVersion.V1BETA,
            json={"connector": connector},
        )


def test_execute_integration_connector_test_with_agent_identifier(chronicle_client):
    """Test execute_integration_connector_test includes agent_identifier when provided."""
    expected = {"outputMessage": "Success"}

    connector = {"displayName": "Test", "script": "print('test')"}

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = execute_integration_connector_test(
            chronicle_client,
            integration_name="test-integration",
            connector=connector,
            agent_identifier="agent-123",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["agentIdentifier"] == "agent-123"


def test_execute_integration_connector_test_error(chronicle_client):
    """Test execute_integration_connector_test raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        side_effect=APIError("Failed to execute connector test"),
    ):
        with pytest.raises(APIError) as exc_info:
            execute_integration_connector_test(
                chronicle_client,
                integration_name="test-integration",
                connector={"displayName": "Test"},
            )
        assert "Failed to execute connector test" in str(exc_info.value)


# -- get_integration_connector_template tests --


def test_get_integration_connector_template_success(chronicle_client):
    """Test get_integration_connector_template issues GET request."""
    expected = {
        "script": "# Template script\nprint('hello')",
        "displayName": "Template Connector",
    }

    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_connector_template(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/connectors:fetchTemplate",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_connector_template_error(chronicle_client):
    """Test get_integration_connector_template raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.connectors.chronicle_request",
        side_effect=APIError("Failed to get connector template"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_connector_template(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to get connector template" in str(exc_info.value)

