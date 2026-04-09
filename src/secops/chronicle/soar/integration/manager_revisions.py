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
"""Integration manager revisions functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.format_utils import (
    format_resource_id,
)
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def list_integration_manager_revisions(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all revisions for a specific integration manager.

    Use this method to browse the version history and identify previous
    functional states of a manager.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager to list revisions for.
        page_size: Maximum number of revisions to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter revisions.
        order_by: Field to sort the revisions by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of revisions instead of a dict with
            revisions list and nextPageToken.

    Returns:
        If as_list is True: List of revisions.
        If as_list is False: Dict with revisions list and nextPageToken.

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
            f"managers/{manager_id}/revisions"
        ),
        items_key="revisions",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_integration_manager_revision(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    revision_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single revision for a specific integration manager.

    Use this method to retrieve a specific snapshot of an
    IntegrationManagerRevision for comparison or review.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager the revision belongs to.
        revision_id: ID of the revision to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified IntegrationManagerRevision.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"managers/{manager_id}/revisions/"
            f"{format_resource_id(revision_id)}"
        ),
        api_version=api_version,
    )


def delete_integration_manager_revision(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    revision_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific revision for a given integration manager.

    Use this method to clean up obsolete snapshots and manage the historical
    record of managers.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager the revision belongs to.
        revision_id: ID of the revision to delete.
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
            f"managers/{manager_id}/revisions/"
            f"{format_resource_id(revision_id)}"
        ),
        api_version=api_version,
    )


def create_integration_manager_revision(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    manager: dict[str, Any],
    comment: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new revision snapshot of the current integration manager.

    Use this method to establish a recovery point before making significant
    updates to a manager.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager to create a revision for.
        manager: Dict containing the IntegrationManager to snapshot.
        comment: Comment describing the revision. Maximum 400 characters.
            Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationManagerRevision resource.

    Raises:
        APIError: If the API request fails.
    """
    body = {"manager": manager}

    if comment is not None:
        body["comment"] = comment

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"managers/{manager_id}/revisions"
        ),
        api_version=api_version,
        json=body,
    )


def rollback_integration_manager_revision(
    client: "ChronicleClient",
    integration_name: str,
    manager_id: str,
    revision_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Revert the current manager definition to a previously saved revision.

    Use this method to rapidly recover a functional state for common code if
    an update causes operational issues in dependent actions or jobs.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the manager belongs to.
        manager_id: ID of the manager to rollback.
        revision_id: ID of the revision to rollback to.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the IntegrationManagerRevision rolled back to.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"managers/{manager_id}/revisions/"
            f"{format_resource_id(revision_id)}:rollback"
        ),
        api_version=api_version,
    )
