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
"""Integration connectors functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import (
    APIVersion,
    ConnectorParameter,
    ConnectorRule,
)
from secops.chronicle.utils.format_utils import (
    format_resource_id,
    build_patch_body,
)
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def list_integration_connectors(
    client: "ChronicleClient",
    integration_name: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    exclude_staging: bool | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all connectors defined for a specific integration.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to list connectors for.
        page_size: Maximum number of connectors to return. Defaults to 50,
            maximum is 1000.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter connectors.
        order_by: Field to sort the connectors by.
        exclude_staging: Whether to exclude staging connectors from the
            response. By default, staging connectors are included.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of connectors instead of a dict with
            connectors list and nextPageToken.

    Returns:
        If as_list is True: List of connectors.
        If as_list is False: Dict with connectors list and nextPageToken.

    Raises:
        APIError: If the API request fails.
    """
    extra_params = {
        "filter": filter_string,
        "orderBy": order_by,
        "excludeStaging": exclude_staging,
    }

    # Remove keys with None values
    extra_params = {k: v for k, v in extra_params.items() if v is not None}

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path=f"integrations/{format_resource_id(integration_name)}/connectors",
        items_key="connectors",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_connector(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single connector for a given integration.

    Use this method to retrieve the Python script, configuration parameters,
    and field mapping logic for a specific connector.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified IntegrationConnector.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}"
        ),
        api_version=api_version,
    )


def delete_integration_connector(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific custom connector from a given integration.

    Only custom connectors can be deleted; commercial connectors are
    immutable.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector to delete.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        None

    Raises:
        APIError: If the API request fails.
    """
    chronicle_request(
        client,
        method="DELETE",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}"
        ),
        api_version=api_version,
    )


def create_integration_connector(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str,
    script: str,
    timeout_seconds: int,
    enabled: bool,
    product_field_name: str,
    event_field_name: str,
    description: str | None = None,
    parameters: list[dict[str, Any] | ConnectorParameter] | None = None,
    rules: list[dict[str, Any] | ConnectorRule] | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new custom connector for a given integration.

    Use this method to define how to fetch and parse alerts from a unique or
    unofficial data source. Each connector must have a unique display name
    and a functional Python script.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the connector for.
        display_name: Connector's display name. Required.
        script: Connector's Python script. Required.
        timeout_seconds: Timeout in seconds for a single script run. Required.
        enabled: Whether the connector is enabled or disabled. Required.
        product_field_name: Field name used to determine the device product.
            Required.
        event_field_name: Field name used to determine the event name
            (sub-type). Required.
        description: Connector's description. Optional.
        parameters: List of ConnectorParameter instances or dicts. Optional.
        rules: List of ConnectorRule instances or dicts. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationConnector resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, ConnectorParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )
    resolved_rules = (
        [r.to_dict() if isinstance(r, ConnectorRule) else r for r in rules]
        if rules is not None
        else None
    )

    body = {
        "displayName": display_name,
        "script": script,
        "timeoutSeconds": timeout_seconds,
        "enabled": enabled,
        "productFieldName": product_field_name,
        "eventFieldName": event_field_name,
        "description": description,
        "parameters": resolved_parameters,
        "rules": resolved_rules,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors"
        ),
        api_version=api_version,
        json=body,
    )


def update_integration_connector(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    display_name: str | None = None,
    script: str | None = None,
    timeout_seconds: int | None = None,
    enabled: bool | None = None,
    product_field_name: str | None = None,
    event_field_name: str | None = None,
    description: str | None = None,
    parameters: list[dict[str, Any] | ConnectorParameter] | None = None,
    rules: list[dict[str, Any] | ConnectorRule] | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing custom connector for a given integration.

    Only custom connectors can be updated; commercial connectors are
    immutable.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector to update.
        display_name: Connector's display name.
        script: Connector's Python script.
        timeout_seconds: Timeout in seconds for a single script run.
        enabled: Whether the connector is enabled or disabled.
        product_field_name: Field name used to determine the device product.
        event_field_name: Field name used to determine the event name
            (sub-type).
        description: Connector's description.
        parameters: List of ConnectorParameter instances or dicts.
        rules: List of ConnectorRule instances or dicts.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,script".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated IntegrationConnector resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, ConnectorParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )
    resolved_rules = (
        [r.to_dict() if isinstance(r, ConnectorRule) else r for r in rules]
        if rules is not None
        else None
    )

    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("script", "script", script),
            ("timeoutSeconds", "timeoutSeconds", timeout_seconds),
            ("enabled", "enabled", enabled),
            ("productFieldName", "productFieldName", product_field_name),
            ("eventFieldName", "eventFieldName", event_field_name),
            ("description", "description", description),
            ("parameters", "parameters", resolved_parameters),
            ("rules", "rules", resolved_rules),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def execute_integration_connector_test(
    client: "ChronicleClient",
    integration_name: str,
    connector: dict[str, Any],
    agent_identifier: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Execute a test run of a connector's Python script.

    Use this method to verify data fetching logic, authentication, and parsing
    logic before enabling the connector for production ingestion. The full
    connector object is required as the test can be run without saving the
    connector first.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector: Dict containing the IntegrationConnector to test.
        agent_identifier: Agent identifier for remote testing. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the test execution results with the following fields:
            - outputMessage: Human-readable output message set by the script.
            - debugOutputMessage: The script debug output.
            - resultJson: The result JSON if it exists (optional).

    Raises:
        APIError: If the API request fails.
    """
    body = {"connector": connector}

    if agent_identifier is not None:
        body["agentIdentifier"] = agent_identifier

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/connectors:executeTest",
        api_version=api_version,
        json=body,
    )


def get_integration_connector_template(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Retrieve a default Python script template for a
    new integration connector.

    Use this method to rapidly initialize the development of a new connector.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the template for.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the IntegrationConnector template.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors:fetchTemplate"
        ),
        api_version=api_version,
    )
