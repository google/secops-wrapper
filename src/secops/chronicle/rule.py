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
"""Rule management functionality for Chronicle."""

from typing import Dict, Any, Optional
from secops.exceptions import APIError


def create_rule(
    client,
    rule_text: str
) -> Dict[str, Any]:
    """Creates a new detection rule to find matches in logs.

    Args:
        client: ChronicleClient instance
        rule_text: Content of the new detection rule, used to evaluate logs.

    Returns:
        Dictionary containing the created rule information

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules"

    body = {
        "text": rule_text,
    }

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to create rule: {response.text}")

    return response.json()


def get_rule(
    client,
    rule_id: str
) -> Dict[str, Any]:
    """Get a rule by ID.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to retrieve ("ru_<UUID>" or
          "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version suffix isn't
          specified we use the rule's latest version.

    Returns:
        Dictionary containing rule information

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules/{rule_id}"

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get rule: {response.text}")

    return response.json()


def list_rules(
    client,
    page_size=None
) -> Dict[str, Any]:
    """Gets a list of rules.

    Args:
        client: ChronicleClient instance

    Returns:
        Dictionary containing information about rules

    Raises:
        APIError: If the API request fails
    """
    params = {}
    if page_size is not None:
        params["page_size"] = page_size
    url = f"{client.base_url}/{client.instance_id}/rules"

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to list rules: {response.text}")

    return response.json()


def update_rule(
    client,
    rule_id: str,
    rule_text: str
) -> Dict[str, Any]:
    """Updates a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to update ("ru_<UUID>")
        rule_text: Updated content of the detection rule

    Returns:
        Dictionary containing the updated rule information

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules/{rule_id}"

    body = {
        "text": rule_text,
    }

    params = {"update_mask": "text"}

    response = client.session.patch(url, params=params, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to update rule: {response.text}")

    return response.json()


def delete_rule(
    client,
    rule_id: str,
    force: bool = False
) -> Dict[str, Any]:
    """Deletes a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to delete ("ru_<UUID>")
        force: If True, deletes the rule even if it has associated retrohunts

    Returns:
        Empty dictionary or deletion confirmation

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules/{rule_id}"

    params = {}
    if force:
        params["force"] = "true"

    response = client.session.delete(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to delete rule: {response.text}")

    # The API returns an empty JSON object on success
    return response.json()


def enable_rule(
    client,
    rule_id: str,
    enabled: bool = True
) -> Dict[str, Any]:
    """Enables or disables a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to enable/disable ("ru_<UUID>")
        enabled: Whether to enable (True) or disable (False) the rule

    Returns:
        Dictionary containing rule deployment information

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/rules/{rule_id}/deployment"

    body = {
        "enabled": enabled,
    }

    params = {"update_mask": "enabled"}

    response = client.session.patch(url, params=params, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to {'enable' if enabled else 'disable'} rule: {response.text}")

    return response.json()