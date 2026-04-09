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
"""Integrations functionality for Chronicle."""

from typing import TYPE_CHECKING, Any

from secops.chronicle.models import (
    APIVersion,
    DiffType,
    IntegrationParam,
    IntegrationType,
    PythonVersion,
    TargetMode,
)
from secops.chronicle.utils.format_utils import (
    build_patch_body,
    format_resource_id,
    remove_none_values,
)
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
    chronicle_request_bytes,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def list_integrations(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of integrations.

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve
        filter_string: Filter expression to filter integrations
        order_by: Field to sort the integrations by
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of integrations instead
            of a dict with integrations list and nextPageToken.

    Returns:
        If as_list is True: List of integrations.
        If as_list is False: Dict with integrations list and
            nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    param_fields = {
        "filter": filter_string,
        "orderBy": order_by,
    }

    # Remove keys with None values
    param_fields = {k: v for k, v in param_fields.items() if v is not None}

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path="integrations",
        items_key="integrations",
        page_size=page_size,
        page_token=page_token,
        extra_params=param_fields,
        as_list=as_list,
    )


def get_integration(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get details of a specific integration.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to retrieve
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified integration

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}",
        api_version=api_version,
    )


def delete_integration(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Deletes a specific custom Integration. Commercial integrations cannot
    be deleted via this method.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to delete
        api_version: API version to use for the request. Default is V1BETA.

    Raises:
        APIError: If the API request fails
    """
    chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}",
        api_version=api_version,
    )


def create_integration(
    client: "ChronicleClient",
    display_name: str,
    staging: bool,
    description: str | None = None,
    image_base64: str | None = None,
    svg_icon: str | None = None,
    python_version: PythonVersion | None = None,
    parameters: list[IntegrationParam | dict[str, Any]] | None = None,
    categories: list[str] | None = None,
    integration_type: IntegrationType | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Creates a new custom SOAR Integration.

    Args:
        client: ChronicleClient instance
        display_name: Required. The display name of the integration
            (max 150 characters)
        staging: Required. True if the integration is in staging mode
        description: Optional. The integration's description
            (max 1,500 characters)
        image_base64: Optional. The integration's image encoded as
            a base64 string (max 5 MB)
        svg_icon: Optional. The integration's SVG icon (max 1 MB)
        python_version: Optional. The integration's Python version
        parameters: Optional. Integration parameters (max 50). Each entry may
            be an IntegrationParam dataclass instance or a plain dict with
            keys: id, defaultValue, displayName, propertyName, type,
            description, mandatory.
        categories: Optional. Integration categories (max 50)
        integration_type: Optional. The integration's type (response/extension)
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the details of the newly created integration

    Raises:
        APIError: If the API request fails
    """
    serialized_params: list[dict[str, Any]] | None = None
    if parameters is not None:
        serialized_params = [
            p.to_dict() if isinstance(p, IntegrationParam) else p
            for p in parameters
        ]

    body_fields = remove_none_values(
        {
            "displayName": display_name,
            "staging": staging,
            "description": description,
            "imageBase64": image_base64,
            "svgIcon": svg_icon,
            "pythonVersion": python_version,
            "parameters": serialized_params,
            "categories": categories,
            "type": integration_type,
        }
    )

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="integrations",
        json=body_fields,
        api_version=api_version,
    )


def download_integration(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> bytes:
    """Exports the entire integration package as a ZIP file. Includes all
    scripts, definitions, and the manifest file. Use this method for backup
    or sharing.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to download
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Bytes of the ZIP file containing the integration package

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request_bytes(
        client,
        method="GET",
        endpoint_path=f"integrations/{integration_name}:export",
        api_version=api_version,
        params={"alt": "media"},
        headers={"Accept": "application/zip"},
    )


def download_integration_dependency(
    client: "ChronicleClient",
    integration_name: str,
    dependency_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Initiates the download of a Python dependency (e.g., a library from
    PyPI) for a custom integration.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration whose dependency to download
        dependency_name: The dependency name to download. It can contain the
            version or the repository.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Empty dict if the download was successful, or a dict containing error
        details if the download failed

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"integrations/{integration_name}:downloadDependency",
        json={"dependency": dependency_name},
        api_version=api_version,
    )


def export_integration_items(
    client: "ChronicleClient",
    integration_name: str,
    actions: list[str] | str | None = None,
    jobs: list[str] | str | None = None,
    connectors: list[str] | str | None = None,
    managers: list[str] | str | None = None,
    transformers: list[str] | str | None = None,
    logical_operators: list[str] | str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> bytes:
    """Exports specific items from an integration into a ZIP folder. Use
    this method to extract only a subset of capabilities (e.g., just the
    connectors) for reuse.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to export items from
        actions: Optional. IDs of the actions to export as a list or
                comma-separated string. Format: [1,2,3] or "1,2,3"
            jobs: Optional. IDs of the jobs to export as a list or
                comma-separated string.
            connectors: Optional. IDs of the connectors to export as a
                list or comma-separated string.
            managers: Optional. IDs of the managers to export as a list
                or comma-separated string.
            transformers: Optional. IDs of the transformers to export as
                a list or comma-separated string.
            logical_operators: Optional. IDs of the logical operators to
                export as a list or comma-separated string.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Bytes of the ZIP file containing the exported integration items

    Raises:
        APIError: If the API request fails
    """
    export_items = remove_none_values(
        {
            "actions": (
                ",".join(actions)
                if isinstance(actions, list)
                else actions if actions else None
            ),
            "jobs": (
                ",".join(jobs)
                if isinstance(jobs, list)
                else jobs if jobs else None
            ),
            "connectors": (
                ",".join(connectors)
                if isinstance(connectors, list)
                else connectors if connectors else None
            ),
            "managers": (
                ",".join(managers)
                if isinstance(managers, list)
                else managers if managers else None
            ),
            "transformers": (
                ",".join(transformers)
                if isinstance(transformers, list)
                else transformers if transformers else None
            ),
            "logicalOperators": (
                ",".join(logical_operators)
                if isinstance(logical_operators, list)
                else logical_operators if logical_operators else None
            ),
            "alt": "media",
        }
    )

    return chronicle_request_bytes(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}:"
            "exportItems"
        ),
        params=export_items,
        api_version=api_version,
        headers={"Accept": "application/zip"},
    )


def get_integration_affected_items(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Identifies all system items (e.g., connector instances, job instances,
    playbooks) that would be affected by a change to or deletion of this
    integration. Use this method to conduct impact analysis before making
    breaking changes.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to check for affected items
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the list of items affected by changes to the specified
            integration

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{integration_name}:fetchAffectedItems",
        api_version=api_version,
    )


def get_agent_integrations(
    client: "ChronicleClient",
    agent_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Returns the set of integrations currently installed and configured on
     a specific agent.

    Args:
        client: ChronicleClient instance
        agent_id: The agent identifier
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the list of agent-based integrations

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path="integrations:fetchAgentIntegrations",
        params={"agentId": agent_id},
        api_version=api_version,
    )


def get_integration_dependencies(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Returns the complete list of Python dependencies currently associated
    with a custom integration.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to check for dependencies
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the list of dependencies for the specified integration

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{integration_name}:fetchDependencies",
        api_version=api_version,
    )


def get_integration_restricted_agents(
    client: "ChronicleClient",
    integration_name: str,
    required_python_version: PythonVersion,
    push_request: bool = False,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Identifies remote agents that would be restricted from running an
    updated version of the integration, typically due to environment
    incompatibilities like unsupported Python versions.

    Args:
        client: ChronicleClient instance
        integration_name: name of the integration to check for restricted agents
        required_python_version: Python version required for the updated
            integration.
        push_request: Optional. Indicates whether the integration is
            pushed to a different mode (production/staging). False by default.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the list of agents that would be restricted from running

    Raises:
        APIError: If the API request fails
    """
    params_fields = remove_none_values(
        {
            "requiredPythonVersion": required_python_version.value,
            "pushRequest": push_request,
        }
    )

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{integration_name}:fetchRestrictedAgents",
        params=params_fields,
        api_version=api_version,
    )


def get_integration_diff(
    client: "ChronicleClient",
    integration_name: str,
    diff_type: DiffType = DiffType.COMMERCIAL,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get the configuration diff of a specific integration.

    Args:
        client: ChronicleClient instance
        integration_name: ID of the integration to retrieve the diff for
        diff_type: Type of diff to retrieve
            (Commercial, Production, or Staging). Default is Commercial.
            COMMERCIAL: Diff between the commercial version of the
                integration  and the current version in the environment.
            PRODUCTION: Returns the difference between the staging
                integration and its matching production version.
            STAGING: Returns the difference between the production
                integration  and its corresponding staging version.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the configuration diff of the specified integration

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f":fetch{diff_type.value}Diff",
        api_version=api_version,
    )


def transition_integration(
    client: "ChronicleClient",
    integration_name: str,
    target_mode: TargetMode,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Transition an integration to a different environment
    (e.g. staging to production).

    Args:
        client: ChronicleClient instance
        integration_name: ID of the integration to transition
        target_mode: Target mode to transition the integration to:
            PRODUCTION: Transition the integration to production environment.
            STAGING: Transition the integration to staging environment.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the details of the transitioned integration

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f":pushTo{target_mode.value}",
        api_version=api_version,
    )


def update_integration(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str | None = None,
    description: str | None = None,
    image_base64: str | None = None,
    svg_icon: str | None = None,
    python_version: PythonVersion | None = None,
    parameters: list[IntegrationParam | dict[str, Any]] | None = None,
    categories: list[str] | None = None,
    integration_type: IntegrationType | None = None,
    staging: bool | None = None,
    dependencies_to_remove: list[str] | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing integration.

    Args:
        client: ChronicleClient instance
        integration_name: ID of the integration to update
        display_name: Optional. The display name of the integration
            (max 150 characters)
        description: Optional. The integration's description
            (max 1,500 characters)
        image_base64: Optional. The integration's image encoded as a
            base64 string (max 5 MB)
        svg_icon: Optional. The integration's SVG icon (max 1 MB)
        python_version: Optional. The integration's Python version
        parameters: Optional. Integration parameters (max 50)
        categories: Optional. Integration categories (max 50)
        integration_type: Optional. The integration's type (response/extension)
        staging: Optional. True if the integration is in staging mode
        dependencies_to_remove: Optional. List of dependencies to
            remove from the integration.
        update_mask: Optional. Comma-separated list of fields to update.
            If not provided, all non-None fields will be updated.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the details of the updated integration

    Raises:
        APIError: If the API request fails
    """
    body, params = build_patch_body(
        field_map=[
            ("display_name", "displayName", display_name),
            ("description", "description", description),
            ("image_base64", "imageBase64", image_base64),
            ("svg_icon", "svgIcon", svg_icon),
            ("python_version", "pythonVersion", python_version),
            ("parameters", "parameters", parameters),
            ("categories", "categories", categories),
            ("integration_type", "integrationType", integration_type),
            ("staging", "staging", staging),
        ],
        update_mask=update_mask,
    )

    if dependencies_to_remove is not None:
        params = params or {}
        params["dependenciesToRemove"] = ",".join(dependencies_to_remove)

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}",
        json=body,
        params=params,
        api_version=api_version,
    )


def update_custom_integration(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str | None = None,
    description: str | None = None,
    image_base64: str | None = None,
    svg_icon: str | None = None,
    python_version: PythonVersion | None = None,
    parameters: list[dict[str, Any]] | None = None,
    categories: list[str] | None = None,
    integration_type: IntegrationType | None = None,
    staging: bool | None = None,
    dependencies_to_remove: list[str] | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Updates a custom integration definition, including its parameters and
    dependencies. Use this method to refine the operational behavior of a
    locally developed integration.

    Args:
        client: ChronicleClient instance
        integration_name: Name of the integration to update
        display_name: Optional. The display name of the integration
            (max 150 characters)
        description: Optional. The integration's description
            (max 1,500 characters)
        image_base64: Optional. The integration's image encoded as a
            base64 string (max 5 MB)
        svg_icon: Optional. The integration's SVG icon (max 1 MB)
        python_version: Optional. The integration's Python version
        parameters: Optional. Integration parameters (max 50)
        categories: Optional. Integration categories (max 50)
        integration_type: Optional. The integration's type (response/extension)
        staging: Optional. True if the integration is in staging mode
        dependencies_to_remove: Optional. List of dependencies to remove from
            the integration
        update_mask: Optional. Comma-separated list of fields to update.
            If not provided, all non-None fields will be updated.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing:
            - successful: Whether the integration was updated successfully
            - integration: The updated integration (populated if successful)
            - dependencies: Dependency installation statuses
                (populated if failed)

    Raises:
        APIError: If the API request fails
    """
    integration_fields = remove_none_values(
        {
            "name": integration_name,
            "displayName": display_name,
            "description": description,
            "imageBase64": image_base64,
            "svgIcon": svg_icon,
            "pythonVersion": python_version,
            "parameters": parameters,
            "categories": categories,
            "type": integration_type,
            "staging": staging,
        }
    )

    body = {"integration": integration_fields}

    if dependencies_to_remove is not None:
        body["dependenciesToRemove"] = dependencies_to_remove

    params = {"updateMask": update_mask} if update_mask else None

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"integrations/"
        f"{format_resource_id(integration_name)}:updateCustomIntegration",
        json=body,
        params=params,
        api_version=api_version,
    )
