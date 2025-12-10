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

from secops.exceptions import APIError


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
) -> dict[str, Any]:
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

    Returns:
        Dictionary containing detection information

    Raises:
        APIError: If the API request fails
        ValueError: If an invalid alert_state is provided
    """
    url = (
        f"{client.base_url}/{client.instance_id}/legacy:legacySearchDetections"
    )

    # Define valid alert states
    valid_alert_states = ["UNSPECIFIED", "NOT_ALERTING", "ALERTING"]
    valid_list_basis = [
        "LIST_BASIS_UNSPECIFIED",
        "CREATED_TIME",
        "DETECTION_TIME",
    ]

    # Build request parameters
    params = {
        "rule_id": rule_id,
    }

    if alert_state:
        if alert_state not in valid_alert_states:
            raise ValueError(
                f"alert_state must be one of {valid_alert_states}, "
                f"got {alert_state}"
            )
        params["alertState"] = alert_state

    if list_basis:
        if list_basis not in valid_list_basis:
            raise ValueError(
                f"list_basis must be one of {valid_list_basis}, "
                f"got {list_basis}"
            )
        params["listBasis"] = list_basis

    if start_time:
        params["startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if end_time:
        params["endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    if page_size:
        params["pageSize"] = page_size

    if page_token:
        params["pageToken"] = page_token

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to list detections: {response.text}")

    return response.json()


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
    url = f"{client.base_url}/{client.instance_id}/ruleExecutionErrors"

    # Create the filter for the specific rule
    rule_filter = f'rule = "{client.instance_id}/rules/{rule_id}"'

    params = {
        "filter": rule_filter,
    }

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to list rule errors: {response.text}")

    return response.json()
