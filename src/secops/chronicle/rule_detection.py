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
"""Detection functionality for Chronicle rules."""

from datetime import datetime
from typing import Any, Literal

from secops.chronicle.utils.request_utils import (
    chronicle_request,
    chronicle_paginated_request,
)


def list_detections(
    client,
    rule_id: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    list_basis: Literal[
        "LIST_BASIS_UNSPECIFIED", "CREATED_TIME", "DETECTION_TIME"
    ] = "LIST_BASIS_UNSPECIFIED",
    alert_state: str | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """List detections for a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule to list detections for. Options are:
            - {rule_id} (latest version)
            - {rule_id}@v_<seconds>_<nanoseconds> (specific version)
            - {rule_id}@- (all versions)
        start_time: If provided, filter by start time.
        end_time: If provided, filter by end time.
        list_basis: If provided, sort detections by list basis. Valid values
          are:
            - "LIST_BASIS_UNSPECIFIED"
            - "CREATED_TIME"
            - "DETECTION_TIME"
        alert_state: If provided, filter by alert state. Valid values are:
            - "UNSPECIFIED"
            - "NOT_ALERTING"
            - "ALERTING"
        page_size: If provided, maximum number of detections to return
        page_token: If provided, continuation token for pagination
        as_list: If True, return only the list of detections.
            If False, return dict with metadata and pagination tokens.

    Returns:
        If as_list is True: List of detections.
        If as_list is False: Dict with detections list and pagination metadata.

    Raises:
        APIError: If the API request fails
        ValueError: If an invalid alert_state is provided
    """
    valid_alert_states = ["UNSPECIFIED", "NOT_ALERTING", "ALERTING"]
    valid_list_basis = [
        "LIST_BASIS_UNSPECIFIED",
        "CREATED_TIME",
        "DETECTION_TIME",
    ]

    extra_params = {"rule_id": rule_id}

    if alert_state:
        if alert_state not in valid_alert_states:
            raise ValueError(
                f"alert_state must be one of {valid_alert_states}, "
                f"got {alert_state}"
            )
        extra_params["alertState"] = alert_state

    if list_basis:
        if list_basis not in valid_list_basis:
            raise ValueError(
                f"list_basis must be one of {valid_list_basis}, "
                f"got {list_basis}"
            )
        extra_params["listBasis"] = list_basis

    if start_time:
        extra_params["startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if end_time:
        extra_params["endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    return chronicle_paginated_request(
        client,
        path="legacy:legacySearchDetections",
        items_key="detections",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def list_errors(client, rule_id: str) -> dict[str, Any]:
    """List execution errors for a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule to list errors for. Options are:
            - {rule_id} (latest version)
            - {rule_id}@v_<seconds>_<nanoseconds> (specific version)
            - {rule_id}@- (all versions)

    Returns:
        Dictionary containing rule execution errors

    Raises:
        APIError: If the API request fails
    """
    rule_filter = f'rule = "{client.instance_id}/rules/{rule_id}"'
    params = {"filter": rule_filter}

    return chronicle_request(
        client,
        method="GET",
        endpoint_path="ruleExecutionErrors",
        params=params,
        error_message="Failed to list rule errors",
    )
