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
"""Integration jobs functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion, JobParameter
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


def list_integration_jobs(
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
    """List all jobs defined for a specific integration.

    Use this method to browse the available background and scheduled automation
    capabilities provided by a third-party connection.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to list jobs for.
        page_size: Maximum number of jobs to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter jobs. Allowed filters are:
            id, custom, system, author, version, integration.
        order_by: Field to sort the jobs by.
        exclude_staging: Whether to exclude staging jobs from the response.
            By default, staging jobs are included.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of jobs instead of a dict with jobs
            list and nextPageToken.

    Returns:
        If as_list is True: List of jobs.
        If as_list is False: Dict with jobs list and nextPageToken.

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
        path=f"integrations/{format_resource_id(integration_name)}/jobs",
        items_key="jobs",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_job(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single job for a given integration.

    Use this method to retrieve the Python script, execution parameters, and
    versioning information for a background automation task.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified IntegrationJob.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs/{job_id}"
        ),
        api_version=api_version,
    )


def delete_integration_job(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific custom job from a given integration.

    Only custom jobs can be deleted; commercial and system jobs are immutable.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to delete.
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
            f"jobs/{job_id}"
        ),
        api_version=api_version,
    )


def create_integration_job(
    client: "ChronicleClient",
    integration_name: str,
    display_name: str,
    script: str,
    version: int,
    enabled: bool,
    custom: bool,
    description: str | None = None,
    parameters: list[dict[str, Any] | JobParameter] | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new custom job for a given integration.

    Each job must have a unique display name and a functional Python script
    for its background execution.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the job for.
        display_name: Job's display name. Maximum 400 characters. Required.
        script: Job's Python script. Required.
        version: Job's version. Required.
        enabled: Whether the job is enabled. Required.
        custom: Whether the job is custom or commercial. Required.
        description: Job's description. Optional.
        parameters: List of JobParameter instances or dicts. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationJob resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [p.to_dict() if isinstance(p, JobParameter) else p for p in parameters]
        if parameters is not None
        else None
    )

    body = {
        "displayName": display_name,
        "script": script,
        "version": version,
        "enabled": enabled,
        "custom": custom,
        "description": description,
        "parameters": resolved_parameters,
    }

    # Remove keys with None values
    body = {k: v for k, v in body.items() if v is not None}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/jobs"
        ),
        api_version=api_version,
        json=body,
    )


def update_integration_job(
    client: "ChronicleClient",
    integration_name: str,
    job_id: str,
    display_name: str | None = None,
    script: str | None = None,
    version: int | None = None,
    enabled: bool | None = None,
    custom: bool | None = None,
    description: str | None = None,
    parameters: list[dict[str, Any] | JobParameter] | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing custom job for a given integration.

    Use this method to modify the Python script or adjust the parameter
    definitions for a job.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job_id: ID of the job to update.
        display_name: Job's display name. Maximum 400 characters.
        script: Job's Python script.
        version: Job's version.
        enabled: Whether the job is enabled.
        custom: Whether the job is custom or commercial.
        description: Job's description.
        parameters: List of JobParameter instances or dicts.
        update_mask: Comma-separated list of fields to update. If omitted,
            the mask is auto-generated from whichever fields are provided.
            Example: "displayName,script".
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the updated IntegrationJob resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [p.to_dict() if isinstance(p, JobParameter) else p for p in parameters]
        if parameters is not None
        else None
    )

    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("script", "script", script),
            ("version", "version", version),
            ("enabled", "enabled", enabled),
            ("custom", "custom", custom),
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
            f"jobs/{job_id}"
        ),
        api_version=api_version,
        json=body,
        params=params,
    )


def execute_integration_job_test(
    client: "ChronicleClient",
    integration_name: str,
    job: dict[str, Any],
    agent_identifier: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Execute a test run of an integration job's Python script.

    Use this method to verify background automation logic and connectivity
    before deploying the job to an instance for recurring execution.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the job belongs to.
        job: Dict containing the IntegrationJob to test.
        agent_identifier: Agent identifier for remote testing. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the test execution results with the following fields:
            - output: The script output.
            - debugOutput: The script debug output.
            - resultObjectJson: The result JSON if it exists (optional).
            - resultName: The script result name (optional).
            - resultValue: The script result value (optional).

    Raises:
        APIError: If the API request fails.
    """
    body = {"job": job}

    if agent_identifier is not None:
        body["agentIdentifier"] = agent_identifier

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs:executeTest"
        ),
        api_version=api_version,
        json=body,
    )


def get_integration_job_template(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Retrieve a default Python script template for a new integration job.

    Use this method to rapidly initialize the development of a new job.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the template for.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the IntegrationJob template.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"jobs:fetchTemplate"
        ),
        api_version=api_version,
    )
