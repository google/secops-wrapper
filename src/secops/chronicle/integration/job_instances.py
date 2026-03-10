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
"""Integration job instances functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import (
    APIVersion,
    AdvancedConfig,
    IntegrationJobInstanceParameter,
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


def list_integration_job_instances(
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
    """List all job instances for a specific integration job.

    Use this method to browse the active job instances and their last
    execution status.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to list instances for.
        page_size: Maximum number of job instances to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter job instances.
        order_by: Field to sort the job instances by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of job instances instead of a dict
            with job instances list and nextPageToken.

    Returns:
        If as_list is True: List of job instances.
        If as_list is False: Dict with job instances list and nextPageToken.

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
            f"integrations/{format_resource_id(integration_name)}/jobs/"
            f"{job_id}/jobInstances"
        ),
        items_key="jobInstances",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_job_instance(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    job_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single job instance for a specific integration job.

    Use this method to retrieve the execution status, last run time, and
    active schedule for a specific background task.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the instance belongs to.
        job_instance_id: ID of the job instance to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified IntegrationJobInstance.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/jobs/"
            f"{job_id}/jobInstances/{job_instance_id}"
        ),
        api_version=api_version,
    )


def delete_integration_job_instance(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    job_instance_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific job instance for a given integration job.

    Use this method to permanently stop and remove a scheduled background task.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the instance belongs to.
        job_instance_id: ID of the job instance to delete.
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
            f"integrations/{format_resource_id(integration_name)}/jobs/"
            f"{job_id}/jobInstances/{job_instance_id}"
        ),
        api_version=api_version,
    )


# pylint: disable=line-too-long
def create_integration_job_instance(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    display_name: str,
    interval_seconds: int,
    enabled: bool,
    advanced: bool,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | IntegrationJobInstanceParameter] | None
    ) = None,
    advanced_config: dict[str, Any] | AdvancedConfig | None = None,
    agent: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    # pylint: enable=line-too-long
    """Create a new job instance for a specific integration job.

    Use this method to schedule a new recurring background job. You must
    provide a valid execution interval and any required script parameters.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to create an instance for.
        display_name: Job instance display name. Required.
        interval_seconds: Job execution interval in seconds. Minimum 60.
            Required.
        enabled: Whether the job instance is enabled. Required.
        advanced: Whether the job instance uses advanced scheduling. Required.
        description: Job instance description. Optional.
        parameters: List of IntegrationJobInstanceParameter instances or
            dicts. Optional.
        advanced_config: Advanced scheduling configuration. Accepts an
            AdvancedConfig instance or a raw dict. Optional.
        agent: Agent identifier for remote job execution. Cannot be patched
            after creation. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationJobInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, IntegrationJobInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )
    resolved_advanced_config = (
        advanced_config.to_dict()
        if isinstance(advanced_config, AdvancedConfig)
        else advanced_config
    )

    body = {
        "displayName": display_name,
        "intervalSeconds": interval_seconds,
        "enabled": enabled,
        "advanced": advanced,
        "description": description,
        "parameters": resolved_parameters,
        "advancedConfig": resolved_advanced_config,
        "agent": agent,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}"
            f"/jobs/{job_id}/jobInstances"
        ),
        api_version=api_version,
        json=body,
    )


# pylint: disable=line-too-long
def update_integration_job_instance(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    job_instance_id: str,
    display_name: str | None = None,
    interval_seconds: int | None = None,
    enabled: bool | None = None,
    advanced: bool | None = None,
    description: str | None = None,
    parameters: (
        list[dict[str, Any] | IntegrationJobInstanceParameter] | None
    ) = None,
    advanced_config: dict[str, Any] | AdvancedConfig | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    # pylint: enable=line-too-long
    """Update an existing job instance for a given integration job.

    Use this method to modify the execution interval, enable/disable the job
    instance, or adjust the parameters passed to the background script.

    Note: The agent field cannot be updated after creation.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the instance belongs to.
        job_instance_id: ID of the job instance to update.
        display_name: Job instance display name.
        interval_seconds: Job execution interval in seconds. Minimum 60.
        enabled: Whether the job instance is enabled.
        advanced: Whether the job instance uses advanced scheduling.
        description: Job instance description.
        parameters: List of IntegrationJobInstanceParameter instances or
            dicts.
        advanced_config: Advanced scheduling configuration. Accepts an
            AdvancedConfig instance or a raw dict.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,intervalSeconds".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated IntegrationJobInstance resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, IntegrationJobInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )
    resolved_advanced_config = (
        advanced_config.to_dict()
        if isinstance(advanced_config, AdvancedConfig)
        else advanced_config
    )

    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("intervalSeconds", "intervalSeconds", interval_seconds),
            ("enabled", "enabled", enabled),
            ("advanced", "advanced", advanced),
            ("description", "description", description),
            ("parameters", "parameters", resolved_parameters),
            ("advancedConfig", "advancedConfig", resolved_advanced_config),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs/{job_id}/jobInstances/{job_instance_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


# pylint: disable=line-too-long
def run_integration_job_instance_on_demand(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    job_instance_id: str,
    parameters: (
        list[dict[str, Any] | IntegrationJobInstanceParameter] | None
    ) = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    # pylint: enable=line-too-long
    """Execute a job instance immediately, bypassing its normal schedule.

    Use this method to trigger an on-demand run of a job for synchronization
    or troubleshooting purposes.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job the instance belongs to.
        job_instance_id: ID of the job instance to run on demand.
        parameters: List of IntegrationJobInstanceParameter instances or
            dicts. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing a success boolean indicating whether the job run
        completed successfully.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, IntegrationJobInstanceParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body = {}
    if resolved_parameters is not None:
        body["parameters"] = resolved_parameters

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}"
            f"/jobs/{job_id}/jobInstances/{job_instance_id}:runOnDemand"
        ),
        api_version=api_version,
        json=body,
    )
