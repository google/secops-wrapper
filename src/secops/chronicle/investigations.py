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
"""Provides investigation management for Chronicle."""

from typing import Any

from secops.chronicle.models import APIVersion, DetectionType
from secops.chronicle.utils.format_utils import format_resource_id
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)


def fetch_associated_investigations(
    client: "ChronicleClient",
    detection_type: str,
    alert_ids: list[str] | None = None,
    case_ids: list[str] | None = None,
    association_limit_per_detection: int | None = None,
    order_by: str | None = None,
) -> dict[str, Any]:
    """Fetches investigations associated with alerts or cases.

    Args:
        client: ChronicleClient instance.
        detection_type: The type of the identifiers provided. Can be a
            DetectionType enum value or string. Valid values:
            - DetectionType.ALERT
            - DetectionType.CASE
            - DetectionType.UNSPECIFIED
        alert_ids: The alert IDs for which associated investigations need
            to be fetched. Maximum of 100 alert IDs.
        case_ids: The case IDs for which associated investigations need to
            be fetched. Maximum of 100 case IDs.
        association_limit_per_detection: Maximum number of associations to
            return per detection. Default is 1. Maximum value is 5.
        order_by: Configures ordering of associations. Supported fields:
            "createTime", "createTime desc", "updateTime", "updateTime desc".

    Returns:
        Dictionary containing:
            - associationsList: Map of alert/case ID to investigation list
            - experimentalAlert: Map of alert/case ID to experimental flag

    Raises:
        APIError: If the API request fails.
    """
    # Validate and convert detection_type to proper format
    if isinstance(detection_type, str):
        try:
            detection_type = DetectionType(detection_type)
        except ValueError:
            try:
                detection_type = DetectionType[detection_type.upper()]
            except KeyError as ke:
                valid = [f"{m.name} or {m.value}" for m in DetectionType]
                raise ValueError(
                    f'Invalid detection_type: "{detection_type}". '
                    f'Valid values: {", ".join(valid)}'
                ) from ke

    params = {
        "detectionType": detection_type,
        "alertIds": alert_ids,
        "caseIds": case_ids,
        "associationLimitPerDetection": association_limit_per_detection,
        "orderBy": order_by,
    }
    params = {k: v for k, v in params.items() if v is not None}

    return chronicle_request(
        client,
        method="GET",
        endpoint_path="investigations:fetchAssociated",
        api_version=APIVersion.V1ALPHA,
        params=params or None,
        error_message="Failed to fetch associated investigations",
    )


def get_investigation(
    client: "ChronicleClient", investigation_id: str
) -> dict[str, Any]:
    """Gets an investigation by ID.

    Args:
        client: ChronicleClient instance.
        investigation_id: ID of the investigation to retrieve. Can be
            either just the ID or the full resource name.

    Returns:
        Dictionary containing investigation information.

    Raises:
        APIError: If the API request fails.
    """
    inv_id = format_resource_id(investigation_id)

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"investigations/{inv_id}",
        api_version=APIVersion.V1ALPHA,
        error_message="Failed to get investigation",
    )


def list_investigations(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
    filter_expr: str | None = None,
    order_by: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """Lists investigations.

    Args:
        client: ChronicleClient instance.
        page_size: Maximum number of investigations to return. Default is
            100. Maximum value is 1000.
        page_token: Page token from a previous list call to retrieve the
            next page.
        filter_expr: Filter expression to restrict results.
            Note: Filters may not be fully supported by the API.
            Example: 'alertId="alert123"' (syntax may vary)
        order_by: Configures ordering of investigations. Default is by
            create time descending. Supported fields: "startTime",
            "endTime", "displayName".
        as_list: If True, return only the list of investigations.
            If False, return dict with metadata and pagination tokens.

    Returns:
        If as_list is True: List of investigations.
        If as_list is False: Dict with investigations list, nextPageToken,
            and totalSize.

    Raises:
        APIError: If the API request fails.
    """
    extra_params = {
        "filter": filter_expr,
        "orderBy": order_by,
    }
    extra_params = {k: v for k, v in extra_params.items() if v is not None}

    return chronicle_paginated_request(
        client,
        path="investigations",
        items_key="investigations",
        api_version=APIVersion.V1ALPHA,
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params or None,
        as_list=as_list,
    )


def trigger_investigation(
    client: "ChronicleClient", alert_id: str
) -> dict[str, Any]:
    """Triggers an investigation for a specific alert.

    Args:
        client: ChronicleClient instance.
        alert_id: The alert ID for which the investigation needs to be
            triggered.

    Returns:
        Dictionary containing the created investigation.

    Raises:
        APIError: If the API request fails.
    """
    body = {"alertId": alert_id}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="investigations:trigger",
        api_version=APIVersion.V1ALPHA,
        json=body,
        error_message="Failed to trigger investigation",
    )
