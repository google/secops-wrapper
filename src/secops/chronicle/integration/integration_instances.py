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
"""Integration instances functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion, IntegrationInstanceParameter
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


def list_integration_instances(
    client: "ChronicleClient",
    integration_name: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all instances for a specific integration.

    Use this method to browse the configured integration instances available
    for a custom or third-party product across different environments.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to list instances for.
        page_size: Maximum number of integration instances to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter integration instances.
        order_by: Field to sort the integration instances by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of integration instances instead of a
            dict with integration instances list and nextPageToken.

    Returns:
        If as_list is True: List of integration instances.
        If as_list is False: Dict with integration instances list and
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
            f"integrationInstances"
        ),
        items_key="integrationInstances",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_instance(
    client: "ChronicleClient",
    integration_name: str,
    integration_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single instance for a specific integration.

    Use this method to retrieve the specific configuration, connection status,
    and environment mapping for an active integration.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the instance belongs to.
        integration_instance_id: ID of the integration instance to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified IntegrationInstance.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"integrationInstances/{integration_instance_id}"
        ),
        api_version=api_version,
    )


def delete_integration_instance(
    client: "ChronicleClient",
    integration_name: str,
    integration_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific integration instance.

    Use this method to permanently remove an integration instance and stop all
    associated automated tasks (connectors or jobs) using this instance.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the instance belongs to.
        integration_instance_id: ID of the integration instance to delete.
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
            f"integrationInstances/{integration_instance_id}"
        ),
        api_version=api_version,
    )


def create_integration_instance(
    client: "ChronicleClient",
    integration_name: str,
    environment: str,
    display_name: str | None = None,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | IntegrationInstanceParameter] | None
    ) = None,
    agent: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new integration instance for a specific integration.

    Use this method to establish a new integration instance to a custom or
    third-party security product for a specific environment. All mandatory
    parameters required by the integration definition must be provided.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the instance for.
        environment: The integration instance environment. Required.
        display_name: The display name of the integration instance.
            Automatically generated if not provided. Maximum 110 characters.
        description: The integration instance description. Maximum 1500
            characters.
        parameters: List of IntegrationInstanceParameter instances or dicts.
        agent: Agent identifier for a remote integration instance.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, IntegrationInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body = {
        "environment": environment,
        "displayName": display_name,
        "description": description,
        "parameters": resolved_parameters,
        "agent": agent,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"integrationInstances"
        ),
        api_version=api_version,
        json=body,
    )


def update_integration_instance(
    client: "ChronicleClient",
    integration_name: str,
    integration_instance_id: str,
    environment: str | None = None,
    display_name: str | None = None,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | IntegrationInstanceParameter] | None
    ) = None,
    agent: str | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing integration instance.

    Use this method to modify connection parameters (e.g., rotate an API
    key), change the display name, or update the description of a configured
    integration instance.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the instance belongs to.
        integration_instance_id: ID of the integration instance to update.
        environment: The integration instance environment.
        display_name: The display name of the integration instance. Maximum
            110 characters.
        description: The integration instance description. Maximum 1500
            characters.
        parameters: List of IntegrationInstanceParameter instances or dicts.
        agent: Agent identifier for a remote integration instance.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,description".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated IntegrationInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, IntegrationInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body, params = build_patch_body(
        field_map=[
            ("environment", "environment", environment),
            ("displayName", "displayName", display_name),
            ("description", "description", description),
            ("parameters", "parameters", resolved_parameters),
            ("agent", "agent", agent),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"integrationInstances/{integration_instance_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def execute_integration_instance_test(
    client: "ChronicleClient",
    integration_name: str,
    integration_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Execute a connectivity test for a specific integration instance.

    Use this method to verify that SecOps can successfully communicate with
    the third-party security product using the provided credentials.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the instance belongs to.
        integration_instance_id: ID of the integration instance to test.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the test results with the following fields:
            - successful: Indicates if the test was successful.
            - message: Test result message (optional).

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"integrationInstances/{integration_instance_id}:executeTest"
        ),
        api_version=api_version,
    )


def get_integration_instance_affected_items(
    client: "ChronicleClient",
    integration_name: str,
    integration_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """List all playbooks that depend on a specific integration instance.

    Use this method to perform impact analysis before deleting or
    significantly changing a connection configuration.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the instance belongs to.
        integration_instance_id: ID of the integration instance to fetch
            affected items for.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing a list of AffectedPlaybookResponse objects that
        depend on the specified integration instance.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"integrationInstances/{integration_instance_id}:fetchAffectedItems"
        ),
        api_version=api_version,
    )


def get_default_integration_instance(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get the system default configuration for a specific integration.

    Use this method to retrieve the baseline integration instance details
    provided for a commercial product.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the default
            instance for.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the default IntegrationInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"integrationInstances:fetchDefaultInstance"
        ),
        api_version=api_version,
    )
