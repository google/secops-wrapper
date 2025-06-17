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
"""Retrohunt functionality for Chronicle rules."""

from datetime import datetime
from typing import Dict, Any
from secops.exceptions import APIError


def create_retrohunt(
    client, rule_id: str, start_time: datetime, end_time: datetime
) -> Dict[str, Any]:
    """Creates a retrohunt for a rule.

    A retrohunt applies a rule to historical data within the specified time range.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule to run retrohunt for ("ru_<UUID>")
        start_time: Start time for retrohunt analysis
        end_time: End time for retrohunt analysis

    Returns:
        Dictionary containing operation information for the retrohunt

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules/{rule_id}/retrohunts"

    body = {
        "process_interval": {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    }

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to create retrohunt: {response.text}")

    return response.json()


def get_retrohunt(client, rule_id: str, operation_id: str) -> Dict[str, Any]:
    """Get retrohunt status and results.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule the retrohunt is for ("ru_<UUID>" or
          "ru_<UUID>@v_<seconds>_<nanoseconds>")
        operation_id: Operation ID of the retrohunt

    Returns:
        Dictionary containing retrohunt information

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules/{rule_id}/retrohunts/{operation_id}"

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get retrohunt: {response.text}")

    return response.json()
