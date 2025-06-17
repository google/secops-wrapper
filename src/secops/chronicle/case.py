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

from typing import Dict, Any, List, Optional
from datetime import datetime
from secops.exceptions import APIError
from secops.chronicle.models import CaseList, Case, SoarPlatformInfo


def get_cases(
    client,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page_size: int = 100,
    page_token: Optional[str] = None,
    case_ids: Optional[List[str]] = None,
    asset_identifiers: Optional[List[str]] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
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
        params["createTime.startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    if end_time:
        params["createTime.endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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
        raise APIError(f"Failed to parse cases response: {str(e)}")


def get_cases_from_list(client, case_ids: List[str]) -> CaseList:
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

    url = f"{client.base_url}/{client.instance_id}/cases:batchGet"

    params = {"case_id": case_ids}

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
