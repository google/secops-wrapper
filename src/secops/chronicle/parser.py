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
"""Parser management functionality for Chronicle."""

from typing import Dict, Any, List
from ..exceptions import APIError, SecOpsError
import re


def activate_parser(
        client,
        log_type: str,
        id: str
) -> Dict[str, Any]:
    """Activate a custom parser.
    
    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID
        
    Returns:
        Empty JSON object
        
    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers/{id}:activate"
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to activate parser: {response.text}")

    return response.json()


def activate_release_candidate_parser(
        client,
        log_type: str,
        id: str
) -> Dict[str, Any]:
    """Activate the release candidate parser making it live for that customer.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers/{id}:activateReleaseCandidateParser"
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to activate parser: {response.text}")

    return response.json()


def copy_parser(
        client,
        log_type: str,
        id: str
) -> Dict[str, Any]:
    """Makes a copy of a prebuilt parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Newly copied Parser

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers/{id}:copy"
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to copy parser: {response.text}")

    return response.json()


def create_parser(
    client,
    log_type: str,
    parser_code: str,
    validated_on_empty_logs: bool = True
) -> Dict[str, Any]:
    """Creates a new parser.
    
    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        parser_code: Content of the new parser, used to evaluate logs.
        validated_on_empty_logs: Whether the parser is validated on empty logs.

    Returns:
        Dictionary containing the created parser information
        
    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers"
    
    body = {
        "cbn": parser_code,
        "validated_on_empty_logs": validated_on_empty_logs
    }
    
    response = client.session.post(url, json=body)
    
    if response.status_code != 200:
        raise APIError(f"Failed to create parser: {response.text}")
    
    return response.json()


def deactivate_parser(
        client,
        log_type: str,
        id: str
) -> Dict[str, Any]:
    """Deactivate a custom parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers/{id}:deactivate"
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to deactivate parser: {response.text}")

    return response.json()


def delete_parser(
        client,
        log_type: str,
        id: str,
        force: bool = False
) -> Dict[str, Any]:
    """Delete a parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID
        force: Flag to forcibly delete an ACTIVE parser.

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers/{id}"
    params = {
        "force": force
    }
    response = client.session.delete(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to deactivate parser: {response.text}")

    return response.json()


def get_parser(
    client,
    log_type: str,
    id: str
) -> Dict[str, Any]:
    """Get a Parser by ID.
    
    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID
          
    Returns:
        SecOps Parser
        
    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers/{id}"
    response = client.session.get(url)
    
    if response.status_code != 200:
        raise APIError(f"Failed to get parser: {response.text}")
    
    return response.json()


def list_parsers(
    client,
    log_type: str = "-",
    page_size: int = 100,
    page_token: str = None,
    filter: str = None
) -> List[Any]:
    """List parsers.
    
    Args:
        client: ChronicleClient instance
        log_type: Log type to filter by.
        page_size: The maximum number of parsers to return.
        page_token: A page token, received from a previous `ListParsers` call.

    Returns:
        Dictionary containing information about rules
        
    Raises:
        APIError: If the API request fails
    """
    more = True
    parsers = []
    
    while more:
        url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers"

        params = {
            "pageSize": page_size,
            "pageToken": page_token,
            "filter": filter
        }
        
        response = client.session.get(url, params=params)
        
        if response.status_code != 200:
            raise APIError(f"Failed to list parsers: {response.text}")
        
        data = response.json()

        if "parsers" in data:
            parsers.extend(data["parsers"])
        
        if "next_page_token" in data:
            params['pageToken'] = data["next_page_token"]
        else:
            more = False
    
    return parsers
