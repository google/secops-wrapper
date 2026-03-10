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
"""Integration logical operators functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import (
    APIVersion,
    IntegrationLogicalOperatorParameter,
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


def list_integration_logical_operators(
    client: "ChronicleClient",
    integration_name: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    exclude_staging: bool | None = None,
    expand: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all logical operator definitions for a specific integration.

    Use this method to discover the custom logic operators available for use
    within playbook decision steps.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to list logical operators
            for.
        page_size: Maximum number of logical operators to return. Defaults
            to 100, maximum is 200.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter logical operators.
        order_by: Field to sort the logical operators by.
        exclude_staging: Whether to exclude staging logical operators from
            the response. By default, staging logical operators are included.
        expand: Expand the response with the full logical operator details.
        api_version: API version to use for the request. Default is V1ALPHA.
        as_list: If True, return a list of logical operators instead of a
            dict with logical operators list and nextPageToken.

    Returns:
        If as_list is True: List of logical operators.
        If as_list is False: Dict with logical operators list and
            nextPageToken.

    Raises:
        APIError: If the API request fails.
    """
    extra_params = {
        "filter": filter_string,
        "orderBy": order_by,
        "excludeStaging": exclude_staging,
        "expand": expand,
    }

    # Remove keys with None values
    extra_params = {k: v for k, v in extra_params.items() if v is not None}

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"logicalOperators"
        ),
        items_key="logicalOperators",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_logical_operator(
    client: "ChronicleClient",
    integration_name: str,
    logical_operator_id: str,
    expand: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Get a single logical operator definition for a specific integration.

    Use this method to retrieve the Python script, evaluation parameters,
    and description for a custom logical operator.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the logical operator
            belongs to.
        logical_operator_id: ID of the logical operator to retrieve.
        expand: Expand the response with the full logical operator details.
            Optional.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing details of the specified IntegrationLogicalOperator.

    Raises:
        APIError: If the API request fails.
    """
    params = {}
    if expand is not None:
        params["expand"] = expand

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"logicalOperators/{logical_operator_id}"
        ),
        api_version=api_version,
        params=params if params else None,
    )


def delete_integration_logical_operator(
    client: "ChronicleClient",
    integration_name: str,
    logical_operator_id: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> None:
    """Delete a specific custom logical operator from a given integration.

    Only custom logical operators can be deleted; predefined built-in
    operators are immutable.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the logical operator
            belongs to.
        logical_operator_id: ID of the logical operator to delete.
        api_version: API version to use for the request. Default is V1ALPHA.

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
            f"logicalOperators/{logical_operator_id}"
        ),
        api_version=api_version,
    )


def create_integration_logical_operator(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str,
    script: str,
    script_timeout: str,
    enabled: bool,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | IntegrationLogicalOperatorParameter] | None
    ) = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Create a new custom logical operator for a given integration.

    Each operator must have a unique display name and a functional Python
    script that returns a boolean result.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the logical
            operator for.
        display_name: Logical operator's display name. Maximum 150
            characters. Required.
        script: Logical operator's Python script. Required.
        script_timeout: Timeout in seconds for a single script run. Default
            is 60. Required.
        enabled: Whether the logical operator is enabled or disabled.
            Required.
        description: Logical operator's description. Maximum 2050 characters.
            Optional.
        parameters: List of IntegrationLogicalOperatorParameter instances or
            dicts. Optional.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the newly created IntegrationLogicalOperator resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            (
                p.to_dict()
                if isinstance(p, IntegrationLogicalOperatorParameter)
                else p
            )
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body = {
        "displayName": display_name,
        "script": script,
        "scriptTimeout": script_timeout,
        "enabled": enabled,
        "description": description,
        "parameters": resolved_parameters,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"logicalOperators"
        ),
        api_version=api_version,
        json=body,
    )


def update_integration_logical_operator(
    client: "ChronicleClient",
    integration_name: str,
    logical_operator_id: str,
    display_name: str | None = None,
    script: str | None = None,
    script_timeout: str | None = None,
    enabled: bool | None = None,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | IntegrationLogicalOperatorParameter] | None
    ) = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Update an existing custom logical operator for a given integration.

    Use this method to modify the logical operator script, refine parameter
    descriptions, or adjust the timeout for a logical operator.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the logical operator
            belongs to.
        logical_operator_id: ID of the logical operator to update.
        display_name: Logical operator's display name. Maximum 150 characters.
        script: Logical operator's Python script.
        script_timeout: Timeout in seconds for a single script run.
        enabled: Whether the logical operator is enabled or disabled.
        description: Logical operator's description. Maximum 2050 characters.
        parameters: List of IntegrationLogicalOperatorParameter instances or
            dicts. When updating existing parameters, id must be provided
            in each IntegrationLogicalOperatorParameter.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,script".
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the updated IntegrationLogicalOperator resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            (
                p.to_dict()
                if isinstance(p, IntegrationLogicalOperatorParameter)
                else p
            )
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("script", "script", script),
            ("scriptTimeout", "scriptTimeout", script_timeout),
            ("enabled", "enabled", enabled),
            ("description", "description", description),
            ("parameters", "parameters", resolved_parameters),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"logicalOperators/{logical_operator_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def execute_integration_logical_operator_test(
    client: "ChronicleClient",
    integration_name: str,
    logical_operator: dict[str, Any],
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Execute a test run of a logical operator's evaluation script.

    Use this method to verify decision logic and ensure it correctly handles
    various input data before deployment in a playbook. The full logical
    operator object is required as the test can be run without saving the
    logical operator first.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the logical operator
            belongs to.
        logical_operator: Dict containing the IntegrationLogicalOperator to
            test.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the test execution results with the following fields:
            - outputMessage: Human-readable output message set by the script.
            - debugOutputMessage: The script debug output.
            - resultValue: The script result value.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"logicalOperators:executeTest"
        ),
        api_version=api_version,
        json={"logicalOperator": logical_operator},
    )


def get_integration_logical_operator_template(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Retrieve a default Python script template for a new logical operator.

    Use this method to rapidly initialize the development of a new logical
    operator.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the template for.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the IntegrationLogicalOperator template.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"logicalOperators:fetchTemplate"
        ),
        api_version=api_version,
    )
