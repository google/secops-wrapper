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
"""Integration job context property functionality for Chronicle."""

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


def list_job_context_properties(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all context properties for a specific integration job.

    Use this method to discover all custom data points associated with a job.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to list context properties for.
        page_size: Maximum number of context properties to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter context properties.
        order_by: Field to sort the context properties by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of context properties instead of a
            dict with context properties list and nextPageToken.

    Returns:
        If as_list is True: List of context properties.
        If as_list is False: Dict with context properties list and
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
            f"jobs/{job_id}/contextProperties"
        ),
        items_key="contextProperties",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_job_context_property(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    context_property_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single context property for a specific integration job.

    Use this method to retrieve the value of a specific key within a job's
    context.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the context property belongs to.
        context_property_id: ID of the context property to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified ContextProperty.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs/{job_id}/contextProperties/{context_property_id}"
        ),
        api_version=api_version,
    )


def delete_job_context_property(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    context_property_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific context property for a given integration job.

    Use this method to remove a custom data point that is no longer relevant
    to the job's context.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the context property belongs to.
        context_property_id: ID of the context property to delete.
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
            f"jobs/{job_id}/contextProperties/{context_property_id}"
        ),
        api_version=api_version,
    )


def create_job_context_property(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    value: str,
    key: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new context property for a specific integration job.

    Use this method to attach custom data to a job's context. Property keys
    must be unique within their context. Key values must be 4-63 characters
    and match /[a-z][0-9]-/.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to create the context property for.
        value: The property value. Required.
        key: The context property ID to use. Must be 4-63 characters and
            match /[a-z][0-9]-/. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created ContextProperty resource.

    Raises:
        APIError: If the API request fails.
    """
    body = {"value": value}

    if key is not None:
        body["key"] = key

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs/{job_id}/contextProperties"
        ),
        api_version=api_version,
        json=body,
    )


def update_job_context_property(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    context_property_id: str,
    value: str,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing context property for a given integration job.

    Use this method to modify the value of a previously saved key.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the context property belongs to.
        context_property_id: ID of the context property to update.
        value: The new property value. Required.
        update_mask: Comma-separated list of fields to update. Only "value"
            is supported. If omitted, defaults to "value".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated ContextProperty resource.

    Raises:
        APIError: If the API request fails.
    """
    body, params = build_patch_body(
        field_map=[
            ("value", "value", value),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs/{job_id}/contextProperties/{context_property_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def delete_all_job_context_properties(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    context_id: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete all context properties for a specific integration job.

    Use this method to quickly clear all supplemental data from a job's
    context.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to clear context properties from.
        context_id: The context ID to remove context properties from. Must be
            4-63 characters and match /[a-z][0-9]-/. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        None

    Raises:
        APIError: If the API request fails.
    """
    body = {}

    if context_id is not None:
        body["contextId"] = context_id

    chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs/{job_id}/contextProperties:clearAll"
        ),
        api_version=api_version,
        json=body,
    )
