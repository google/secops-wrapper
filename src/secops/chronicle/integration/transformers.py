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
"""Integration transformers functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion, TransformerDefinitionParameter
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


def list_integration_transformers(
    client: "ChronicleClient",
    integration_name: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    exclude_staging: bool | None = None,
    expand: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all transformer definitions for a specific integration.

    Use this method to browse the available transformers.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to list transformers for.
        page_size: Maximum number of transformers to return. Defaults to 100,
            maximum is 200.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter transformers.
        order_by: Field to sort the transformers by.
        exclude_staging: Whether to exclude staging transformers from the
            response. By default, staging transformers are included.
        expand: Expand the response with the full transformer details.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        If as_list is True: List of transformers.
        If as_list is False: Dict with transformers list and nextPageToken.

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
            f"transformers"
        ),
        items_key="transformers",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=False,
    )


def get_integration_transformer(
    client: "ChronicleClient",
    integration_name: str,
    transformer_id: str,
    expand: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Get a single transformer definition for a specific integration.

    Use this method to retrieve the Python script, input parameters, and
    expected input, output and usage example schema for a specific data
    transformation logic within an integration.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the transformer belongs to.
        transformer_id: ID of the transformer to retrieve.
        expand: Expand the response with the full transformer details.
            Optional.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing details of the specified TransformerDefinition.

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
            f"transformers/{transformer_id}"
        ),
        api_version=api_version,
        params=params if params else None,
    )


def delete_integration_transformer(
    client: "ChronicleClient",
    integration_name: str,
    transformer_id: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> None:
    """Delete a custom transformer definition from a given integration.

    Use this method to permanently remove an obsolete transformer from an
    integration.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the transformer belongs to.
        transformer_id: ID of the transformer to delete.
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
            f"transformers/{transformer_id}"
        ),
        api_version=api_version,
    )


def create_integration_transformer(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str,
    script: str,
    script_timeout: str,
    enabled: bool,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | TransformerDefinitionParameter] | None
    ) = None,
    usage_example: str | None = None,
    expected_output: str | None = None,
    expected_input: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Create a new transformer definition for a given integration.

    Use this method to define a transformer, specifying its functional Python
    script and necessary input parameters.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the transformer
            for.
        display_name: Transformer's display name. Maximum 150 characters.
            Required.
        script: Transformer's Python script. Required.
        script_timeout: Timeout in seconds for a single script run. Default
            is 60. Required.
        enabled: Whether the transformer is enabled or disabled. Required.
        description: Transformer's description. Maximum 2050 characters.
            Optional.
        parameters: List of TransformerDefinitionParameter instances or
            dicts. Optional.
        usage_example: Transformer's usage example. Optional.
        expected_output: Transformer's expected output. Optional.
        expected_input: Transformer's expected input. Optional.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the newly created TransformerDefinition resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, TransformerDefinitionParameter) else p
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
        "usageExample": usage_example,
        "expectedOutput": expected_output,
        "expectedInput": expected_input,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/transformers"
        ),
        api_version=api_version,
        json=body,
    )


def update_integration_transformer(
    client: "ChronicleClient",
    integration_name: str,
    transformer_id: str,
    display_name: str | None = None,
    script: str | None = None,
    script_timeout: str | None = None,
    enabled: bool | None = None,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | TransformerDefinitionParameter] | None
    ) = None,
    usage_example: str | None = None,
    expected_output: str | None = None,
    expected_input: str | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Update an existing transformer definition for a given integration.

    Use this method to modify a transformation's Python script, adjust its
    description, or refine its parameter definitions.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the transformer belongs to.
        transformer_id: ID of the transformer to update.
        display_name: Transformer's display name. Maximum 150 characters.
        script: Transformer's Python script.
        script_timeout: Timeout in seconds for a single script run.
        enabled: Whether the transformer is enabled or disabled.
        description: Transformer's description. Maximum 2050 characters.
        parameters: List of TransformerDefinitionParameter instances or
            dicts. When updating existing parameters, id must be provided
            in each TransformerDefinitionParameter.
        usage_example: Transformer's usage example.
        expected_output: Transformer's expected output.
        expected_input: Transformer's expected input.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,script".
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the updated TransformerDefinition resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, TransformerDefinitionParameter) else p
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
            ("usageExample", "usageExample", usage_example),
            ("expectedOutput", "expectedOutput", expected_output),
            ("expectedInput", "expectedInput", expected_input),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"transformers/{transformer_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def execute_integration_transformer_test(
    client: "ChronicleClient",
    integration_name: str,
    transformer: dict[str, Any],
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Execute a test run of a transformer's Python script.

    Use this method to verify transformation logic and ensure data is being
    parsed and formatted correctly before saving or deploying the transformer.
    The full transformer object is required as the test can be run without
    saving the transformer first.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the transformer belongs to.
        transformer: Dict containing the TransformerDefinition to test.
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
            f"transformers:executeTest"
        ),
        api_version=api_version,
        json={"transformer": transformer},
    )


def get_integration_transformer_template(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Retrieve a default Python script template for a new transformer.

    Use this method to jumpstart the development of a custom data
    transformation logic by providing boilerplate code.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the template for.
        api_version: API version to use for the request. Default is V1ALPHA.

    Returns:
        Dict containing the TransformerDefinition template.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"transformers:fetchTemplate"
        ),
        api_version=api_version,
    )
