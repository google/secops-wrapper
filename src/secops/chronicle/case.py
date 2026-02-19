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

from datetime import datetime
from typing import Any

from secops.chronicle.models import (
    APIVersion,
    Case,
    CaseCloseReason,
    CaseList,
    CasePriority,
)
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)


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
    params: dict[str, Any] = {"pageSize": str(page_size)}

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

    return chronicle_request(
        client,
        method="GET",
        endpoint_path="legacy:legacyListCases",
        api_version=APIVersion.V1ALPHA,
        params=params,
        error_message="Failed to retrieve cases",
    )


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
    if len(case_ids) > 1000:
        raise ValueError("Maximum of 1000 cases can be retrieved in a batch")

    data = chronicle_request(
        client,
        method="GET",
        endpoint_path="legacy:legacyBatchGetCases",
        api_version=APIVersion.V1ALPHA,
        params={"names": case_ids},
        error_message="Failed to get cases",
    )

    cases = []
    if "cases" in data:
        for case_data in data["cases"]:
            cases.append(Case.from_dict(case_data))

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
    body = {"casesIds": case_ids, "tags": tags}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:executeBulkAddTag",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to add tags to cases",
    )


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
    body = {"casesIds": case_ids, "username": username}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:executeBulkAssign",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to assign cases",
    )


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
    if isinstance(priority, str):
        original_priority_value = priority
        try:
            priority = CasePriority[original_priority_value]
        except KeyError:
            try:
                priority = CasePriority(original_priority_value)
            except ValueError as ve:
                valid_values = ", ".join([p.name for p in CasePriority])
                raise ValueError(
                    f"Invalid priority '{priority}'. "
                    f"Valid values: {valid_values}"
                ) from ve

    body = {"casesIds": case_ids, "priority": priority}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:executeBulkChangePriority",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to change case priority",
    )


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
    body = {"casesIds": case_ids, "stage": stage}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:executeBulkChangeStage",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to change case stage",
    )


def execute_bulk_close(
    client,
    case_ids: list[int],
    close_reason: str | CaseCloseReason,
    root_cause: str | None = None,
    close_comment: str | None = None,
    dynamic_parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Close multiple cases in bulk.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to close
        close_reason: Reason for closing the cases.
            Can be CaseCloseReason enum or string.
            Valid values: MALICIOUS, NOT_MALICIOUS, MAINTENANCE,
            INCONCLUSIVE, UNKNOWN, CLOSE_REASON_UNSPECIFIED
        root_cause: Optional root cause for closing cases
        close_comment: Optional comment to add when closing
        dynamic_parameters: Optional dynamic parameters for close action

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
        ValueError: If an invalid close_reason value is provided
    """
    if isinstance(close_reason, str):
        original_close_reason = close_reason
        try:
            close_reason = CaseCloseReason[original_close_reason]
        except KeyError:
            try:
                close_reason = CaseCloseReason(original_close_reason)
            except ValueError as ve:
                valid_values = ", ".join([r.name for r in CaseCloseReason])
                raise ValueError(
                    f"Invalid close_reason '{close_reason}'. "
                    f"Valid values: {valid_values}"
                ) from ve

    body: dict[str, Any] = {
        "casesIds": case_ids,
        "closeReason": close_reason,
    }

    if root_cause is not None:
        body["rootCause"] = root_cause
    if close_comment is not None:
        body["closeComment"] = close_comment
    if dynamic_parameters is not None:
        body["dynamicParameters"] = dynamic_parameters

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:executeBulkClose",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to close cases",
    )


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
    body = {"casesIds": case_ids, "reopenComment": reopen_comment}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:executeBulkReopen",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to reopen cases",
    )


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
    if not case_name.startswith("projects/"):
        endpoint_path = f"cases/{case_name}"
    else:
        endpoint_path = case_name

    params: dict[str, Any] = {}
    if expand:
        params["expand"] = expand

    data = chronicle_request(
        client,
        method="GET",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1BETA,
        params=params,
        error_message="Failed to get case",
    )

    return Case.from_dict(data)


def list_cases(
    client,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_query: str | None = None,
    order_by: str | None = None,
    expand: str | None = None,
    distinct_by: str | None = None,
    as_list: bool = False,
) -> list[dict[str, Any]] | dict[str, Any]:
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
        as_list: If True, return a list of cases instead of a dict
            with cases list, nextPageToken, and totalSize.

    Returns:
        If as_list is True: A list of case dictionaries.
        If as_list is False: A dictionary containing:
            - cases: List of case dictionaries
            - nextPageToken: Token for next page (empty if auto-paginated)
            - totalSize: Total number of matching cases

    Raises:
        APIError: If the API request fails
    """
    extra_params: dict[str, Any] = {}
    if filter_query:
        extra_params["filter"] = filter_query
    if order_by:
        extra_params["orderBy"] = order_by
    if expand:
        extra_params["expand"] = expand
    if distinct_by:
        extra_params["distinctBy"] = distinct_by

    return chronicle_paginated_request(
        client,
        api_version=APIVersion.V1BETA,
        path="cases",
        items_key="cases",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params if extra_params else None,
        as_list=as_list,
    )


def merge_cases(
    client, case_ids: list[int], case_to_merge_with: int
) -> dict[str, Any]:
    """Merge multiple cases into a single case.

    Args:
        client: ChronicleClient instance
        case_ids: List of case IDs to merge (source cases)
        case_to_merge_with: ID of the target case to merge into

    Returns:
        Dictionary containing:
            - newCaseId: ID of the merged case if successful
            - isRequestValid: Whether the request was valid
            - errors: List of errors if request was invalid

    Raises:
        APIError: If the API request fails

    Note:
        The API requires all cases (including target) in casesIds.
        The target case is specified separately in caseToMergeWith.
    """
    all_case_ids = list(set(case_ids + [case_to_merge_with]))
    body = {"casesIds": all_case_ids, "caseToMergeWith": case_to_merge_with}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="cases:merge",
        api_version=APIVersion.V1BETA,
        json=body,
        error_message="Failed to merge cases",
    )


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
        case_data: Dictionary containing case fields to update.
        update_mask: Optional comma-separated list of fields to update

    Returns:
        Updated Case object

    Raises:
        APIError: If the API request fails
        ValueError: If an invalid priority value is provided
    """
    if not case_name.startswith("projects/"):
        endpoint_path = f"cases/{case_name}"
    else:
        endpoint_path = case_name

    if "priority" in case_data and isinstance(case_data["priority"], str):
        case_priority = case_data["priority"]
        try:
            case_data["priority"] = CasePriority[case_priority]
        except KeyError:
            try:
                case_data["priority"] = CasePriority(case_priority)
            except ValueError as ve:
                valid_values = ", ".join([p.name for p in CasePriority])
                raise ValueError(
                    f"Invalid priority '{case_data['priority']}'. "
                    f"Valid values: {valid_values}"
                ) from ve

    params: dict[str, Any] = {}
    if update_mask:
        params["updateMask"] = update_mask

    data = chronicle_request(
        client,
        method="PATCH",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1BETA,
        json=case_data,
        params=params if params else None,
        error_message="Failed to patch case",
    )

    return Case.from_dict(data)
