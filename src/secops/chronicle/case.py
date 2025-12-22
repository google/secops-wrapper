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
"""Case functionality for Chronicle."""

import sys
from datetime import datetime
from typing import Any

from secops.chronicle.models import Case, CaseList
from secops.exceptions import APIError


if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python < 3.11."""

        def __str__(self) -> str:
            return self.value


class CasePriority(StrEnum):
    """Priority levels for cases."""

    UNSPECIFIED = "PRIORITY_UNSPECIFIED"
    INFO = "PRIORITY_INFO"
    LOW = "PRIORITY_LOW"
    MEDIUM = "PRIORITY_MEDIUM"
    HIGH = "PRIORITY_HIGH"
    CRITICAL = "PRIORITY_CRITICAL"


def get_cases(
    client,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page_size: int = 100,
    page_token: str | None = None,
    case_ids: list[str] | None = None,
    asset_identifiers: list[str] | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """Get case data from Chronicle.

    Args:
        client: ChronicleClient instance
        start_time: Start time for the case search (optional)
        end_time: End time for the case search (optional)
        page_size: Maximum number of results to return per page
        page_token: Token for pagination
        case_ids: List of case IDs to retrieve
        asset_identifiers: List of asset identifiers to filter by
        tenant_id: Tenant ID to filter by

    Returns:
        Dictionary containing cases data and pagination info

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/legacy:legacyListCases"

    params = {"pageSize": str(page_size)}

    # Add optional parameters
    if page_token:
        params["pageToken"] = page_token

    if start_time:
        params["createTime.startTime"] = start_time.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    if end_time:
        params["createTime.endTime"] = end_time.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

    if case_ids:
        for case_id in case_ids:
            params["caseId"] = case_id

    if asset_identifiers:
        for asset in asset_identifiers:
            params["assetId"] = asset

    if tenant_id:
        params["tenantId"] = tenant_id

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to retrieve cases: {response.text}")

    try:
        data = response.json()

        return {
            "cases": data.get("cases", []),
            "next_page_token": data.get("nextPageToken", ""),
        }
    except ValueError as e:
        raise APIError(f"Failed to parse cases response: {str(e)}") from e


def get_cases_from_list(client, case_ids: list[str]) -> CaseList:
    """Get cases from Chronicle.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to retrieve

    Returns:
        CaseList object with case details

    Raises:
        APIError: If the API request fails
        ValueError: If too many case IDs are provided
    """
    # Check that we don't exceed the maximum number of cases
    if len(case_ids) > 1000:
        raise ValueError("Maximum of 1000 cases can be retrieved in a batch")

    url = f"{client.base_url}/{client.instance_id}/legacy:legacyBatchGetCases"

    params = {"names": case_ids}

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to get cases: {response.text}")

    # Parse the response
    cases = []
    response_data = response.json()

    if "cases" in response_data:
        for case_data in response_data["cases"]:
            # Create Case object
            case = Case.from_dict(case_data)
            cases.append(case)

    return CaseList(cases)


def execute_bulk_add_tag(
    client, case_ids: list[int], tags: list[str]
) -> dict[str, Any]:
    """Add tags to multiple cases in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to add tags to
        tags: List of tags to add to the cases

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/cases:executeBulkAddTag"

    body = {"casesIds": case_ids, "tags": tags}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to add tags to cases: {response.text}")

    try:
        return response.json()
    except ValueError as e:
        raise APIError(
            f"Failed to parse bulk add tag response: {str(e)}"
        ) from e


def execute_bulk_assign(
    client, case_ids: list[int], username: str
) -> dict[str, Any]:
    """Assign multiple cases to a user in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to assign
        username: Username to assign the cases to

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/cases:executeBulkAssign"

    body = {"casesIds": case_ids, "username": username}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to assign cases: {response.text}")

    try:
        return response.json()
    except ValueError as e:
        raise APIError(f"Failed to parse bulk assign response: {str(e)}") from e


def execute_bulk_change_priority(
    client, case_ids: list[int], priority: str | CasePriority
) -> dict[str, Any]:
    """Change priority of multiple cases in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to change priority for
        priority: Priority level.

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"cases:executeBulkChangePriority"
    )

    # Convert enum to string if needed
    priority_str = (
        f"{priority}" if isinstance(priority, CasePriority) else priority
    )

    body = {"casesIds": case_ids, "priority": priority_str}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to change case priority: {response.text}")

    try:
        return response.json()
    except ValueError as e:
        raise APIError(
            f"Failed to parse bulk change priority response: {str(e)}"
        ) from e


def execute_bulk_change_stage(
    client, case_ids: list[int], stage: str
) -> dict[str, Any]:
    """Change stage of multiple cases in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to change stage for
        stage: Stage to set for the cases

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"cases:executeBulkChangeStage"
    )

    body = {"casesIds": case_ids, "stage": stage}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to change case stage: {response.text}")

    try:
        return response.json()
    except ValueError as e:
        raise APIError(
            f"Failed to parse bulk change stage response: {str(e)}"
        ) from e


def execute_bulk_close(
    client,
    case_ids: list[int],
    close_reason: str,
    root_cause: str | None = None,
    close_comment: str | None = None,
    dynamic_parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Close multiple cases in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to close
        close_reason: Reason for closing the cases
        root_cause: Optional root cause for closing cases
        close_comment: Optional comment to add when closing
        dynamic_parameters: Optional dynamic parameters for close action

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/cases:executeBulkClose"

    body = {"casesIds": case_ids, "closeReason": close_reason}

    if root_cause is not None:
        body["rootCause"] = root_cause
    if close_comment is not None:
        body["closeComment"] = close_comment
    if dynamic_parameters is not None:
        body["dynamicParameters"] = dynamic_parameters

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to close cases: {response.text}")

    try:
        return response.json() if response.text else {}
    except ValueError as e:
        raise APIError(f"Failed to parse bulk close response: {str(e)}") from e


def execute_bulk_reopen(
    client, case_ids: list[int], reopen_comment: str
) -> dict[str, Any]:
    """Reopen multiple cases in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to reopen
        reopen_comment: Comment to add when reopening cases

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/cases:executeBulkReopen"

    body = {"casesIds": case_ids, "reopenComment": reopen_comment}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to reopen cases: {response.text}")

    try:
        return response.json() if response.text else {}
    except ValueError as e:
        raise APIError(f"Failed to parse bulk reopen response: {str(e)}") from e


def get_case(client, case_name: str, expand: str | None = None) -> Case:
    """Get a single case details.

    Args:
        client: ChronicleClient instance
        case_name: Case resource name or case ID.
            Full format: projects/{project}/locations/{location}/
            instances/{instance}/cases/{case}
            Short format: {case_id} (e.g., "12345")
        expand: Optional expand field for getting related resources

    Returns:
        Case object with case details

    Raises:
        APIError: If the API request fails
    """
    # Check if case_name is just an ID or full resource name
    if "/cases/" not in case_name:
        full_case_name = f"{client.instance_id}/cases/{case_name}"
    else:
        full_case_name = case_name

    url = f"{client.base_url}/{full_case_name}"

    params = {}
    if expand:
        params["expand"] = expand

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to get case: {response.text}")

    try:
        data = response.json()
        return Case.from_dict(data)
    except ValueError as e:
        raise APIError(f"Failed to parse case response: {str(e)}") from e


def list_cases(
    client,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_query: str | None = None,
    order_by: str | None = None,
    expand: str | None = None,
    distinct_by: str | None = None,
) -> dict[str, Any]:
    """List cases with optional filtering and pagination.

    Args:
        client: ChronicleClient instance
        page_size: Maximum number of cases to return per page (1-1000).
            If None, automatically paginates through all results.
        page_token: Token for pagination from previous list call.
        filter_query: Filter expression for filtering cases
        order_by: Comma-separated list of fields to order by
        expand: Expand fields (e.g., "tags, products")
        distinct_by: Field to distinct cases by

    Returns:
        Dictionary containing:
            - cases: List of Case objects
            - nextPageToken: Token for next page
            - totalSize: Total number of matching cases

    Raises:
        APIError: If the API request fails
        ValueError: If page_size is invalid
    """
    url = f"{client.base_url}/{client.instance_id}/cases"
    all_cases = []
    total_size = 0
    next_token = page_token

    while True:
        params = {"pageSize": str(page_size if page_size else 1000)}

        if next_token:
            params["pageToken"] = next_token
        if filter_query:
            params["filter"] = filter_query
        if order_by:
            params["orderBy"] = order_by
        if expand:
            params["expand"] = expand
        if distinct_by:
            params["distinctBy"] = distinct_by

        response = client.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Failed to list cases: {response.text}")

        try:
            data = response.json()
            all_cases.extend(data.get("cases", []))
            total_size = data.get("totalSize", 0)
            next_token = data.get("nextPageToken", "")

            # If caller provided page_size, return only this page
            if page_size is not None:
                break

            # Otherwise, auto-paginate through all results
            if not next_token:
                break

        except ValueError as e:
            raise APIError(
                f"Failed to parse list cases response: {str(e)}"
            ) from e

    return {
        "cases": all_cases,
        "nextPageToken": next_token,
        "totalSize": total_size,
    }


def merge_cases(
    client, case_ids: list[int], case_to_merge_with: int
) -> dict[str, Any]:
    """Merge multiple cases into a single case.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to merge
        case_to_merge_with: ID of the case to merge with

    Returns:
        Dictionary containing:
            - newCaseId: ID of the merged case if successful
            - isRequestValid: Whether the request was valid
            - errors: List of errors if request was invalid

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/cases:merge"

    body = {"casesIds": case_ids, "caseToMergeWith": case_to_merge_with}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to merge cases: {response.text}")

    try:
        return response.json()
    except ValueError as e:
        raise APIError(f"Failed to parse merge cases response: {str(e)}") from e


def patch_case(
    client,
    case_name: str,
    case_data: dict[str, Any],
    update_mask: str | None = None,
) -> Case:
    """Update a case using partial update (PATCH).

    Args:
        client: ChronicleClient instance
        case_name: Case resource name or case ID.
            Full format: projects/{project}/locations/{location}/
            instances/{instance}/cases/{case}
            Short format: {case_id} (e.g., "12345")
        case_data: Dictionary containing case fields to update
        update_mask: Optional comma-separated list of fields to update

    Returns:
        Updated Case object

    Raises:
        APIError: If the API request fails
    """
    # Check if case_name is just an ID or full resource name
    if "/cases/" not in case_name:
        full_case_name = f"{client.instance_id}/cases/{case_name}"
    else:
        full_case_name = case_name

    url = f"{client.base_url}/{full_case_name}"

    params = {}
    if update_mask:
        params["updateMask"] = update_mask

    response = client.session.patch(url, json=case_data, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to patch case: {response.text}")

    try:
        data = response.json()
        return Case.from_dict(data)
    except ValueError as e:
        raise APIError(f"Failed to parse patch case response: {str(e)}") from e
