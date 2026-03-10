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
"""Integration connector instances functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import (
    APIVersion,
    ConnectorInstanceParameter,
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


def list_connector_instances(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all instances for a specific integration connector.

    Use this method to discover all configured instances of a connector.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector to list instances for.
        page_size: Maximum number of connector instances to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter connector instances.
        order_by: Field to sort the connector instances by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of connector instances instead of a
            dict with connector instances list and nextPageToken.

    Returns:
        If as_list is True: List of connector instances.
        If as_list is False: Dict with connector instances list and
            nextPageToken.

    Raises:
        APIError: If the API request fails.
    """
    extra_params = {
        "filter": filter_string,
        "orderBy": order_by,
    }

    # Remove keys with None values
    extra_params = {k: v for k, v in extra_params.items() if v is not None}

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances"
        ),
        items_key="connectorInstances",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_connector_instance(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single instance for a specific integration connector.

    Use this method to retrieve the configuration and status of a specific
    connector instance.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified ConnectorInstance.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}"
        ),
        api_version=api_version,
    )


def delete_connector_instance(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific connector instance.

    Use this method to permanently remove a data ingestion stream. For remote
    connectors, the associated agent must be live and have no pending packages.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to delete.
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
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}"
        ),
        api_version=api_version,
    )


def create_connector_instance(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    environment: str,
    display_name: str,
    interval_seconds: int,
    timeout_seconds: int,
    description: str | None = None,
    agent: str | None = None,
    allow_list: list[str] | None = None,
    product_field_name: str | None = None,
    event_field_name: str | None = None,
    integration_version: str | None = None,
    version: str | None = None,
    logging_enabled_until_unix_ms: str | None = None,
    parameters: list[dict[str, Any] | ConnectorInstanceParameter] | None = None,
    connector_instance_id: str | None = None,
    enabled: bool | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new connector instance for a specific integration connector.

    Use this method to establish a new data ingestion stream from a security
    product. Note that agent and remote cannot be patched after creation.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector to create an instance for.
        environment: Connector instance environment. Cannot be patched for
            remote connectors. Required.
        display_name: Connector instance display name. Required.
        interval_seconds: Connector instance execution interval in seconds.
            Required.
        timeout_seconds: Timeout of a single Python script run. Required.
        description: Connector instance description. Optional.
        agent: Agent identifier for a remote connector instance. Cannot be
            patched after creation. Optional.
        allow_list: Connector instance allow list. Optional.
        product_field_name: Connector's device product field. Optional.
        event_field_name: Connector's event name field. Optional.
        integration_version: The integration version. Optional.
        version: The connector instance version. Optional.
        logging_enabled_until_unix_ms: Timeout when log collecting will be
            disabled. Optional.
        parameters: List of ConnectorInstanceParameter instances or dicts.
            Optional.
        connector_instance_id: The connector instance id. Optional.
        enabled: Whether the connector instance is enabled. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created ConnectorInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, ConnectorInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body = {
        "environment": environment,
        "displayName": display_name,
        "intervalSeconds": interval_seconds,
        "timeoutSeconds": timeout_seconds,
        "description": description,
        "agent": agent,
        "allowList": allow_list,
        "productFieldName": product_field_name,
        "eventFieldName": event_field_name,
        "integrationVersion": integration_version,
        "version": version,
        "loggingEnabledUntilUnixMs": logging_enabled_until_unix_ms,
        "parameters": resolved_parameters,
        "id": connector_instance_id,
        "enabled": enabled,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances"
        ),
        api_version=api_version,
        json=body,
    )


def update_connector_instance(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    display_name: str | None = None,
    description: str | None = None,
    interval_seconds: int | None = None,
    timeout_seconds: int | None = None,
    allow_list: list[str] | None = None,
    product_field_name: str | None = None,
    event_field_name: str | None = None,
    integration_version: str | None = None,
    version: str | None = None,
    logging_enabled_until_unix_ms: str | None = None,
    parameters: list[dict[str, Any] | ConnectorInstanceParameter] | None = None,
    enabled: bool | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing connector instance.

    Use this method to enable or disable a connector, change its display
    name, or adjust its ingestion parameters. Note that agent, remote, and
    environment cannot be patched after creation.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to update.
        display_name: Connector instance display name.
        description: Connector instance description.
        interval_seconds: Connector instance execution interval in seconds.
        timeout_seconds: Timeout of a single Python script run.
        allow_list: Connector instance allow list.
        product_field_name: Connector's device product field.
        event_field_name: Connector's event name field.
        integration_version: The integration version. Required on patch if
            provided.
        version: The connector instance version.
        logging_enabled_until_unix_ms: Timeout when log collecting will be
            disabled.
        parameters: List of ConnectorInstanceParameter instances or dicts.
        enabled: Whether the connector instance is enabled.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,intervalSeconds".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated ConnectorInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, ConnectorInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("description", "description", description),
            ("intervalSeconds", "intervalSeconds", interval_seconds),
            ("timeoutSeconds", "timeoutSeconds", timeout_seconds),
            ("allowList", "allowList", allow_list),
            ("productFieldName", "productFieldName", product_field_name),
            ("eventFieldName", "eventFieldName", event_field_name),
            ("integrationVersion", "integrationVersion", integration_version),
            ("version", "version", version),
            (
                "loggingEnabledUntilUnixMs",
                "loggingEnabledUntilUnixMs",
                logging_enabled_until_unix_ms,
            ),
            ("parameters", "parameters", resolved_parameters),
            ("id", "id", connector_instance_id),
            ("enabled", "enabled", enabled),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def get_connector_instance_latest_definition(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Refresh a connector instance with the latest definition.

    Use this method to discover new parameters or updated scripts for an
    existing connector instance.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to refresh.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the refreshed ConnectorInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}:fetchLatestDefinition"
        ),
        api_version=api_version,
    )


def set_connector_instance_logs_collection(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    enabled: bool,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Enable or disable debug log collection for a connector instance.

    When enabled is set to True, existing logs are cleared and a new
    collection period is started.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to configure.
        enabled: Whether logs collection is enabled for the connector
            instance. Required.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the log enable expiration time in unix ms.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}:setLogsCollection"
        ),
        api_version=api_version,
        json={"enabled": enabled},
    )


def run_connector_instance_on_demand(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    connector_instance: dict[str, Any],
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Trigger an immediate, single execution of a connector instance.

    Use this method for testing configuration changes or manually
    force-starting a data ingestion cycle.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to run.
        connector_instance: Dict containing the ConnectorInstance with
            values to use for the run. Required.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the run results with the following fields:
            - debugOutput: The execution debug output message.
            - success: True if the execution was successful.
            - sampleCases: List of alerts produced by the connector run.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}:runOnDemand"
        ),
        api_version=api_version,
        json={"connectorInstance": connector_instance},
    )
