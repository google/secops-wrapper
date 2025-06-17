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

from typing import Dict, Any, Optional
from secops.exceptions import APIError


def list_detections(
    client,
    rule_id: str,
    alert_state: Optional[str] = None,
    page_size: Optional[int] = None,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """List detections for a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule to list detections for. Options are:
            - {rule_id} (latest version)
            - {rule_id}@v_<seconds>_<nanoseconds> (specific version)
            - {rule_id}@- (all versions)
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
    url = f"{client.base_url}/{client.instance_id}/legacy:legacySearchDetections"

    # Define valid alert states
    valid_alert_states = ["UNSPECIFIED", "NOT_ALERTING", "ALERTING"]

    # Build request parameters
    params = {
        "rule_id": rule_id,
    }

    if alert_state:
        if alert_state not in valid_alert_states:
            raise ValueError(
                f"alert_state must be one of {valid_alert_states}, got {alert_state}"
            )
        params["alertState"] = alert_state

    if page_size:
        params["pageSize"] = page_size

    if page_token:
        params["pageToken"] = page_token

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to list detections: {response.text}")

    return response.json()


def list_errors(client, rule_id: str) -> Dict[str, Any]:
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
