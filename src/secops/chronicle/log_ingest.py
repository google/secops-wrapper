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
"""Chronicle log ingestion functionality."""

import base64
import uuid
import copy
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from secops.exceptions import APIError
from secops.chronicle.log_types import is_valid_log_type

def create_forwarder(
    client,
    display_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    upload_compression: bool = False,
    enable_server: bool = False
) -> Dict[str, Any]:
    """Create a new forwarder in Chronicle.
    
    Args:
        client: ChronicleClient instance
        display_name: User-specified name for the forwarder
        metadata: Optional forwarder metadata (asset_namespace, labels)
        upload_compression: Whether uploaded data should be compressed
        enable_server: Whether server functionality is enabled on the forwarder
        
    Returns:
        Dictionary containing the created forwarder details
        
    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders"
    
    # Create request payload
    payload = {
        "displayName": display_name,
        "config": {
            "uploadCompression": upload_compression,
            "metadata": metadata or {},
            "serverSettings": {
                "enabled": enable_server,
                "httpSettings": {
                    "routeSettings": {}
                }
            }
        }
    }
    
    # Send the request
    response = client.session.post(url, json=payload)
    
    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to create forwarder: {response.text}")
    
    return response.json()


def list_forwarders(
    client,
    page_size: int = 50,
    page_token: Optional[str] = None
) -> Dict[str, Any]:
    """List forwarders in Chronicle.
    
    Args:
        client: ChronicleClient instance
        page_size: Maximum number of forwarders to return (1-1000)
        page_token: Token for pagination
        
    Returns:
        Dictionary containing list of forwarders and next page token
        
    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders"
    
    # Add query parameters
    params = {}
    if page_size:
        params["pageSize"] = min(1000, max(1, page_size))
    if page_token:
        params["pageToken"] = page_token
    
    # Send the request
    response = client.session.get(url, params=params)
    
    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to list forwarders: {response.text}")
    
    result = response.json()
    
    # If there's a next page token, fetch additional pages and combine results
    if "nextPageToken" in result and result["nextPageToken"]:
        next_page = list_forwarders(client, page_size, result["nextPageToken"])
        if "forwarders" in next_page and next_page["forwarders"]:
            # Combine the forwarders from both pages
            result["forwarders"].extend(next_page["forwarders"])
        # Remove the nextPageToken since we've fetched all pages
        result.pop("nextPageToken")
    
    return result


def get_forwarder(
    client,
    forwarder_id: str
) -> Dict[str, Any]:
    """Get a forwarder by ID.
    
    Args:
        client: ChronicleClient instance
        forwarder_id: ID of the forwarder to retrieve
        
    Returns:
        Dictionary containing the forwarder details
        
    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders/{forwarder_id}"
    
    # Send the request
    response = client.session.get(url)
    
    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to get forwarder: {response.text}")
    
    return response.json()


def get_or_create_forwarder(
    client,
    display_name: str = "Wrapper-SDK-Forwarder"
) -> Dict[str, Any]:
    """Get an existing forwarder by name or create a new one if none exists.
    
    Args:
        client: ChronicleClient instance
        display_name: Name of the forwarder to find or create
        
    Returns:
        Dictionary containing the forwarder details
        
    Raises:
        APIError: If the API request fails
    """
    try:
        # List existing forwarders
        forwarders = list_forwarders(client, page_size=1000)
        
        # Try to find a forwarder with the given display name
        for forwarder in forwarders.get("forwarders", []):
            if forwarder.get("displayName") == display_name:
                return forwarder
        
        # No matching forwarder found, create a new one
        return create_forwarder(client, display_name=display_name)
    
    except APIError as e:
        # Handle permission issues or other API errors
        if "permission" in str(e).lower():
            raise APIError(f"Insufficient permissions to manage forwarders: {str(e)}")
        raise
  
  
def extract_forwarder_id(forwarder_name: str) -> str:
    """Extract the forwarder ID from a full forwarder name.
    
    Args:
        forwarder_name: Full resource name of the forwarder
            Example: "projects/123/locations/us/instances/abc/forwarders/xyz"
            If already just an ID (no slashes), returns it as is.
        
    Returns:
        The forwarder ID (the last segment of the path)
        
    Raises:
        ValueError: If the name is not in the expected format
    """
    # Check for empty strings
    if not forwarder_name:
        raise ValueError("Forwarder name cannot be empty")
    
    # If it's just an ID (no slashes), return it as is
    if '/' not in forwarder_name:
        # Validate that it looks like a UUID or a simple string identifier
        return forwarder_name
    
    segments = forwarder_name.split('/')
    # Filter out empty segments (handles cases like "/")
    segments = [s for s in segments if s]
    
    if not segments:
        raise ValueError(f"Invalid forwarder name format: {forwarder_name}")
    
    # Return the last segment of the path
    return segments[-1]


def ingest_log(
    client,
    log_type: str,
    log_message: Union[str, List[str]],
    log_entry_time: Optional[datetime] = None,
    collection_time: Optional[datetime] = None,
    namespace: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    forwarder_id: Optional[str] = None,
    force_log_type: bool = False
) -> Dict[str, Any]:
    """Ingest one or more logs into Chronicle.
    
    Args:
        client: ChronicleClient instance
        log_type: Chronicle log type (e.g., "OKTA", "WINDOWS", etc.)
        log_message: Either a single log message string or a list of log message strings
        log_entry_time: The time the log entry was created (defaults to current time)
        collection_time: The time the log was collected (defaults to current time)
        namespace: The user-configured environment namespace to identify the data domain 
            the logs originated from. This namespace will be used as a tag to identify
            the appropriate data domain for indexing and enrichment functionality.
        labels: Dictionary of custom metadata labels to attach to the log entries.
        forwarder_id: ID of the forwarder to use (creates or uses default if None)
        force_log_type: Whether to force using the log type even if not in the valid list
        
    Returns:
        Dictionary containing the operation details for the ingestion
        
    Raises:
        ValueError: If the log type is invalid or timestamps are invalid
        APIError: If the API request fails
    """
    # Validate log type
    if not is_valid_log_type(log_type) and not force_log_type:
        raise ValueError(f"Invalid log type: {log_type}. Use force_log_type=True to override.")
    
    # Get current time as default for log_entry_time and collection_time
    now = datetime.now()
    
    # If log_entry_time is not provided, use current time
    if log_entry_time is None:
        log_entry_time = now
    
    # If collection_time is not provided, use current time
    if collection_time is None:
        collection_time = now
    
    # Validate that collection_time is not before log_entry_time
    if collection_time < log_entry_time:
        raise ValueError("Collection time must be same or after log entry time")
    
    # Format timestamps for API
    log_entry_time_str = log_entry_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    collection_time_str = collection_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # If forwarder_id is not provided, get or create default forwarder
    if forwarder_id is None:
        forwarder = get_or_create_forwarder(client)
        forwarder_id = extract_forwarder_id(forwarder["name"])
    
    # Construct the full forwarder resource name if needed
    if '/' not in forwarder_id:
        forwarder_resource = f"{client.instance_id}/forwarders/{forwarder_id}"
    else:
        forwarder_resource = forwarder_id
    
    # Construct the import URL
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/logs:import"
    
    # Convert single log message to a list for unified processing
    log_messages = log_message if isinstance(log_message, list) else [log_message]
    
    # Prepare logs for the payload
    logs = []
    for msg in log_messages:
        # Encode log message in base64
        log_data = base64.b64encode(msg.encode('utf-8')).decode('utf-8')
        
        log_data = {
            "data": log_data,
            "log_entry_time": log_entry_time_str,
            "collection_time": collection_time_str,
        }

        if namespace:
            log_data["environment_namespace"] = namespace
        
        # Fix for labels: API expects a map where values are LogLabel objects
        if labels:
            log_data["labels"] = {key: {"value": value} for key, value in labels.items()}

        logs.append(log_data)
    
    # Construct the request payload
    payload = {
        "inline_source": {
            "logs": logs,
            "forwarder": forwarder_resource
        }
    }
    
    # Send the request
    response = client.session.post(url, json=payload)
    
    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to ingest log: {response.text}")
    
    return response.json()


def ingest_udm(
    client,
    udm_events: Union[Dict[str, Any], List[Dict[str, Any]]],
    add_missing_ids: bool = True
) -> Dict[str, Any]:
    """Ingest UDM events directly into Chronicle.
    
    Args:
        client: ChronicleClient instance
        udm_events: A single UDM event dictionary or a list of UDM event dictionaries
        add_missing_ids: Whether to automatically add unique IDs to events missing them
        
    Returns:
        Dictionary containing the operation details for the ingestion
        
    Raises:
        ValueError: If any required fields are missing or events are malformed
        APIError: If the API request fails
        
    Example:
        ```python
        # Ingest a single UDM event
        single_event = {
            "metadata": {
                "event_type": "NETWORK_CONNECTION",
                "product_name": "My Security Product"
            },
            "principal": {"ip": "192.168.1.100"},
            "target": {"ip": "10.0.0.1"}
        }
        
        result = chronicle.ingest_udm(single_event)
        
        # Ingest multiple UDM events
        events = [
            {
                "metadata": {
                    "event_type": "NETWORK_CONNECTION",
                    "product_name": "My Security Product"
                },
                "principal": {"ip": "192.168.1.100"},
                "target": {"ip": "10.0.0.1"}
            },
            {
                "metadata": {
                    "event_type": "PROCESS_LAUNCH",
                    "product_name": "My Security Product"
                },
                "principal": {
                    "hostname": "workstation1",
                    "process": {"command_line": "./malware.exe"}
                }
            }
        ]
        
        result = chronicle.ingest_udm(events)
        ```
    """
    # Ensure we have a list of events
    if isinstance(udm_events, dict):
        udm_events = [udm_events]
    
    if not udm_events:
        raise ValueError("No UDM events provided")
    
    # Create deep copies to avoid modifying the original objects
    events_copy = copy.deepcopy(udm_events)
    
    # Process each event: validate and add IDs if needed
    for event in events_copy:
        # Validate basic structure
        if not isinstance(event, dict):
            raise ValueError(f"Invalid UDM event type: {type(event)}. Events must be dictionaries.")
        
        # Check for required metadata section
        if "metadata" not in event:
            raise ValueError("UDM event missing required 'metadata' section")
        
        if not isinstance(event["metadata"], dict):
            raise ValueError("UDM 'metadata' must be a dictionary")
        
        # Add event timestamp if missing
        if "event_timestamp" not in event["metadata"]:
            current_time = datetime.now().astimezone()
            event["metadata"]["event_timestamp"] = current_time.isoformat().replace("+00:00", "Z")
        
        # Add ID if needed
        if add_missing_ids and "id" not in event["metadata"]:
            event["metadata"]["id"] = str(uuid.uuid4())
    
    # Prepare the request
    parent = f"projects/{client.project_id}/locations/{client.region}/instances/{client.customer_id}"
    url = f"https://{client.region}-chronicle.googleapis.com/v1alpha/{parent}/events:import"
    
    # Format the request body
    body = {
        "inline_source": {
            "events": [{"udm": event} for event in events_copy]
        }
    }
    
    # Make the API request
    response = client.session.post(url, json=body)
    
    # Check for errors
    if response.status_code >= 400:
        error_message = f"Failed to ingest UDM events: {response.text}"
        raise APIError(error_message)
    
    response_data = {}
    
    # Parse response if it has content
    if response.text.strip():
        try:
            response_data = response.json()
        except ValueError:
            # If JSON parsing fails, provide the raw text in the return value
            response_data = {"raw_response": response.text}
    
    return response_data 
