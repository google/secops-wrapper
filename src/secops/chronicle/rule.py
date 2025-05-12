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
from secops.exceptions import APIError, SecOpsError
import re


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
    client
) -> Dict[str, Any]:
    """Gets a list of rules.
    
    Args:
        client: ChronicleClient instance
        
    Returns:
        Dictionary containing information about rules
        
    Raises:
        APIError: If the API request fails
    """
    more = True
    rules = {
        "rules": []
    }
    
    while more:
        url = f"{client.base_url}/{client.instance_id}/rules"

        params = {
            "pageSize": 1000,
            "view": "FULL"
        }
        
        response = client.session.get(url, params=params)
        
        if response.status_code != 200:
            raise APIError(f"Failed to list rules: {response.text}")
        
        data = response.json()
        
        rules["rules"].extend(data["rules"])
        
        if "next_page_token" in data:
            params['pageToken'] = data["next_page_token"]
        else:
            more = False
    
    return rules

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

def search_rules(
    client,
    query: str
    ) -> Dict[str, Any]:
    """Search for rules.

    Args:
        client: ChronicleClient instance
        query: Search query string that supports regex

    Returns:
        Dictionary containing search results
        
    Raises:
        APIError: If the API request fails
    """
    try:
        re.compile(query)
    except re.error:
        raise SecOpsError(f"Invalid regular expression: {query}")

    rules = list_rules(client)
    results = {
        "rules": []
    }
    for rule in rules['rules']:
        rule_text = rule.get('text', "")
        match = re.search(query, rule_text)

        if match:
            results['rules'].append(rule)

    return results

