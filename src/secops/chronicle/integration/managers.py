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
"""Integration manager functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion
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


def list_integration_managers(
    client: "ChronicleClient",
    integration_name: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all managers defined for a specific integration.

    Use this method to discover the library of managers available within a
    particular integration's scope.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to list managers for.
        page_size: Maximum number of managers to return. Defaults to 100,
            maximum is 100.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter managers.
        order_by: Field to sort the managers by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of managers instead of a dict with
            managers list and nextPageToken.

    Returns:
        If as_list is True: List of managers.
        If as_list is False: Dict with managers list and nextPageToken.

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
        path=f"integrations/{format_resource_id(integration_name)}/managers",
        items_key="managers",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_manager(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single manager for a given integration.

    Use this method to retrieve the manager script and its metadata for
    review or reference.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified IntegrationManager.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"managers/{manager_id}"
        ),
        api_version=api_version,
    )


def delete_integration_manager(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific custom manager from a given integration.

    Note that deleting a manager may break components (actions, jobs) that
    depend on its code.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager to delete.
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
            f"managers/{manager_id}"
        ),
        api_version=api_version,
    )


def create_integration_manager(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str,
    script: str,
    description: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new custom manager for a given integration.

    Use this method to add a new shared code utility. Each manager must have
    a unique display name and a script containing valid Python logic for reuse
    across actions, jobs, and connectors.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the manager for.
        display_name: Manager's display name. Maximum 150 characters. Required.
        script: Manager's Python script. Maximum 5MB. Required.
        description: Manager's description. Maximum 400 characters. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationManager resource.

    Raises:
        APIError: If the API request fails.
    """
    body = {
        "displayName": display_name,
        "script": script,
    }

    if description is not None:
        body["description"] = description

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/managers"
        ),
        api_version=api_version,
        json=body,
    )


def update_integration_manager(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    display_name: str | None = None,
    script: str | None = None,
    description: str | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing custom manager for a given integration.

    Use this method to modify the shared code, adjust its description, or
    refine its logic across all components that import it.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager to update.
        display_name: Manager's display name. Maximum 150 characters.
        script: Manager's Python script. Maximum 5MB.
        description: Manager's description. Maximum 400 characters.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,script".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated IntegrationManager resource.

    Raises:
        APIError: If the API request fails.
    """
    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("script", "script", script),
            ("description", "description", description),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"managers/{manager_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def get_integration_manager_template(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Retrieve a default Python script template for a new integration manager.

    Use this method to quickly start developing new managers.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the template for.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the IntegrationManager template.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            "managers:fetchTemplate"
        ),
        api_version=api_version,
    )
