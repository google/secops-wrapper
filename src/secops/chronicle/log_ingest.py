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
import copy
import json
import re
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from secops.chronicle.log_types import is_valid_log_type
from secops.exceptions import APIError

# Forward declaration for type hinting to avoid circular import
if False:  # pylint: disable=using-constant-test
    from secops.chronicle.client import ChronicleClient


# Mapping of log types to their corresponding splitter functions
_LOG_SPLITTERS = {}

# Mapping of log type aliases to base formats
# (e.g. 'OKTA' -> 'JSON', 'CISCO_ASA' -> 'SYSLOG')
_LOG_TYPE_ALIASES = {}

# List of log formats that are known to contain multi-line log entries
# and require special handling beyond simple line splitting
MULTI_LINE_LOG_FORMATS = ["WINDOWS", "XML", "JSON"]


def register_log_splitter(log_types: str | list[str]) -> Callable:
    """Register a function as a log splitter for specific log types.

    Args:
        log_types: A list of log types this splitter handles,
                or a single log type string.

    Returns:
        Decorator function that registers the decorated function as a splitter

    Example:
        ```python
        @register_log_splitter(["WINDOWS", "WINDOWS_SECURITY"])
        def split_windows_logs(log_content):
            # Logic to split Windows log content
            return log_entries
        ```
    """
    # Handle single string
    if isinstance(log_types, str):
        log_types = [log_types]

    def decorator(func):
        # Register the function for each log type
        for log_type in log_types:
            _LOG_SPLITTERS[log_type.upper()] = func
        return func

    return decorator


def initialize_multi_line_formats() -> None:
    """Initialize mapping of log types to multi-line format handlers.

    This function identifies which log types require specialized multi-line
    log processing versus which can use simple line splitting.
    """
    # Define mappings of multi-line formats to their variants/aliases
    multi_line_variants = {
        "WINDOWS": [
            "WINDOWS",
            "WINEVTLOG",
            "WINDOWS_SYSMON",
            "WINDOWS_DHCP",
            "WINDOWS_SECURITY",
            "WINDOWS_DNS",
            "WINDOWS_FIREWALL",
        ],
        "XML": [
            "XML",
            "WINEVTLOG_XML",
            "MCAFEE_EPO_XML",
            "SYMANTEC_AV_XML",
            "CISCO_ISE",
            "VMWARE_ESX",
            "VMWARE_VCENTER",
            "VMRAY_FLOG_XML",
        ],
        "JSON": [
            "JSON",
            "AWS_CLOUDTRAIL",
            "OKTA",
            "GITHUB",
            "SALESFORCE",
            "SLACK_AUDIT",
            "CLOUDFLARE",
        ],
    }

    # Register all multi-line format variants
    for base_format, variants in multi_line_variants.items():
        # Make sure the base format itself is registered
        _LOG_TYPE_ALIASES[base_format.upper()] = base_format.upper()

        # Register all variants to their base format
        for variant in variants:
            _LOG_TYPE_ALIASES[variant.upper()] = base_format.upper()


def split_logs(log_type: str, log_content: str) -> list[str]:
    """Split a log content string into individual log entries based on log type.

    Args:
        log_type: Type of log (e.g., "SYSLOG", "WINDOWS", etc.)
        log_content: String containing log entries

    Returns:
        List of individual log entries
    """
    log_type = log_type.upper() if log_type else ""

    # Check if this log type has a direct specialized splitter
    if log_type in _LOG_SPLITTERS:
        return _LOG_SPLITTERS[log_type](log_content)

    # Check if it's an alias for a multi-line format
    if log_type in _LOG_TYPE_ALIASES:
        base_type = _LOG_TYPE_ALIASES[log_type]
        if base_type in _LOG_SPLITTERS:
            print(f"Using {base_type} splitter for {log_type} logs")
            return _LOG_SPLITTERS[base_type](log_content)

    # Default for all other log types: just split by newlines
    return [line for line in log_content.splitlines() if line.strip()]


@register_log_splitter(
    [
        "JSON",
        "AWS_CLOUDTRAIL",
        "OKTA",
        "GITHUB",
        "SALESFORCE",
        "SLACK_AUDIT",
        "CLOUDFLARE",
    ]
)
def split_json_logs(log_content: str) -> list[str]:
    """Split JSON log content into individual JSON objects.

    This splitter handles multi-line JSON formats:
    1. Single JSON object with line breaks (pretty-printed)
    2. JSON array of objects with line breaks
    3. JSON Lines format (one JSON object per line)

    Args:
        log_content: String containing JSON log entries

    Returns:
        List of individual JSON log entries as strings
    """
    log_content = log_content.strip()
    results = []

    # Single JSON object or array
    try:
        data = json.loads(log_content)
        if isinstance(data, list):
            for item in data:
                results.append(json.dumps(item))
            return results
        else:
            return [log_content]
    except json.JSONDecodeError:
        # Not a single valid JSON object or array, try other formats
        pass

    # JSON Lines (one object per line)
    lines = log_content.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
            results.append(line)
        except json.JSONDecodeError:
            # Not valid JSON
            continue

    # If we found valid JSON lines, return them
    if results:
        return results

    # If no valid JSON was found, just split by newlines
    return [line for line in lines if line.strip()]


@register_log_splitter(
    [
        "WINDOWS",
        "WINEVTLOG",
        "WINDOWS_SYSMON",
        "WINDOWS_DHCP",
        "WINDOWS_SECURITY",
        "WINDOWS_DNS",
        "WINDOWS_FIREWALL",
    ]
)
def split_windows_logs(log_content: str) -> list[str]:
    """Split Windows Event logs.

    This function handles various Windows log formats including single events
    and multiple events with different separator patterns.

    Args:
        log_content: String containing Windows Event log entries

    Returns:
        List of individual Windows Event log entries
    """
    if not log_content or not log_content.strip():
        return [log_content]

    # Only use FIRST known markers as the start of a log
    # - Event Viewer export: "Log Name:"
    # - wevtutil export: "LogName="
    # - XML export: "<Event"
    event_pattern = re.compile(r"^(Log Name:|LogName=|<Event)")

    lines = log_content.splitlines()

    # Find header indices (ignore blanks)
    header_indices = [
        i
        for i, line in enumerate(lines)
        if line.strip() and event_pattern.match(line.strip())
    ]

    if len(header_indices) <= 1:
        return [log_content.strip()]

    results = []
    for i, start_idx in enumerate(header_indices):
        end_idx = (
            header_indices[i + 1] if i + 1 < len(header_indices) else len(lines)
        )

        # Collect only non-empty lines
        event_lines = [ln for ln in lines[start_idx:end_idx] if ln.strip()]

        if event_lines:
            results.append("\n".join(event_lines))

    return results


@register_log_splitter(
    [
        "XML",
        "WINEVTLOG_XML",
        "MCAFEE_EPO_XML",
        "SYMANTEC_AV_XML",
        "CISCO_ISE",
        "VMWARE_ESX",
        "VMWARE_VCENTER",
        "VMRAY_FLOG_XML",
    ]
)
def split_xml_logs(log_content: str) -> list[str]:
    """Split XML format logs.

    Attempts to identify and separate individual XML documents.

    Args:
        log_content: String containing XML log entries

    Returns:
        List of individual XML log entries
    """
    # Pattern to find XML document boundaries
    xml_pattern = re.compile(
        r"(<\?xml[^>]*?>.*?</[\w\-]+>|<[\w\-]+[^>]*?>.*?</[\w\-]+>)", re.DOTALL
    )

    matches = list(xml_pattern.finditer(log_content))
    results = []

    if matches:
        for match in matches:
            results.append(match.group(0).strip())
        return results

    # If no XML was identified, fall back to line splitting
    return [line for line in log_content.splitlines() if line.strip()]


def create_forwarder(
    client: "ChronicleClient",
    display_name: str,
    metadata: dict[str, Any] | None = None,
    upload_compression: bool = False,
    enable_server: bool = False,
    regex_filters: list[dict[str, Any]] | None = None,
    graceful_timeout: str | None = None,
    drain_timeout: str | None = None,
    http_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new forwarder in Chronicle.

    Args:
        client: ChronicleClient instance
        display_name: User-specified name for the forwarder
        metadata: Optional forwarder metadata (asset_namespace, labels)
        upload_compression: Whether uploaded data should be compressed
        enable_server: Whether server functionality is enabled on the forwarder
        regex_filters: Regex filters applied at the forwarder level
        graceful_timeout: Timeout, after which the forwarder returns a bad
            readiness/health check and still accepts new connections
        drain_timeout: Timeout, after which the forwarder waits for active
            connections to successfully close on their own before being closed
            by the server
        http_settings: HTTP-specific server settings

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
                "gracefulTimeout": graceful_timeout,
                "drainTimeout": drain_timeout,
                "httpSettings": {"routeSettings": {}},
            },
        },
    }

    if regex_filters:
        payload["config"]["regexFilters"] = regex_filters

    if graceful_timeout:
        payload["config"]["serverSettings"][
            "gracefulTimeout"
        ] = graceful_timeout

    if drain_timeout:
        payload["config"]["serverSettings"]["drainTimeout"] = drain_timeout

    if http_settings:
        payload["config"]["serverSettings"]["httpSettings"] = http_settings

    # Send the request
    response = client.session.post(url, json=payload)

    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to create forwarder: {response.text}")

    return response.json()


def list_forwarders(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
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
    if not page_size and "nextPageToken" in result and result["nextPageToken"]:
        next_page = list_forwarders(client, page_size, result["nextPageToken"])
        if "forwarders" in next_page and next_page["forwarders"]:
            # Combine the forwarders from both pages
            result["forwarders"].extend(next_page["forwarders"])
        # Remove the nextPageToken since we've fetched all pages
        result.pop("nextPageToken")

    return result


def get_forwarder(
    client: "ChronicleClient", forwarder_id: str
) -> dict[str, Any]:
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


def update_forwarder(
    client: "ChronicleClient",
    forwarder_id: str,
    display_name: str | None = None,
    metadata: dict[str, Any] | None = None,
    upload_compression: bool | None = None,
    enable_server: bool | None = None,
    regex_filters: list[dict[str, Any]] | None = None,
    graceful_timeout: str | None = None,
    drain_timeout: str | None = None,
    http_settings: dict[str, Any] | None = None,
    update_mask: list[str] | None = None,
) -> dict[str, Any]:
    """Update an existing forwarder.

    Args:
        client: The initialized Chronicle client.
        forwarder_id: ID of the forwarder to update.
        display_name: Display name for the forwarder.
        metadata: Metadata key-value pairs for the forwarder.
        upload_compression: Upload compression setting.
        enable_server: Server enabled setting.
        regex_filters: Regex filter patterns and actions.
        graceful_timeout: Graceful timeout duration for server.
        drain_timeout: Drain timeout duration for server.
        http_settings: HTTP server settings.
        update_mask: List of field paths to update. If not provided, all fields
            with non-None values will be updated.

    Returns:
        Dict containing the updated forwarder details.

    Raises:
        APIError: If the API returns an error response.
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders/{forwarder_id}"

    auto_mask = []  # Update mask if not provided in argument
    payload = {}

    if display_name is not None:
        payload["displayName"] = display_name
        auto_mask.append("display_name")

    # Check if we need to include config and its fields
    has_config = any(
        param is not None
        for param in [
            metadata,
            upload_compression,
            regex_filters,
            enable_server,
            graceful_timeout,
            drain_timeout,
            http_settings,
        ]
    )

    if has_config:
        payload["config"] = {}

        # Add metadata if provided
        if metadata:
            payload["config"]["metadata"] = metadata
            auto_mask.append("config.metadata")

        # Add upload compression if provided
        if upload_compression is not None:
            payload["config"]["uploadCompression"] = upload_compression
            auto_mask.append("config.upload_compression")

        # Add regex filters if provided
        if regex_filters:
            payload["config"]["regexFilters"] = regex_filters
            auto_mask.append("config.regex_filters")

        # Initialize serverSettings if any server-related fields are provided
        if any(
            param is not None
            for param in [
                enable_server,
                graceful_timeout,
                drain_timeout,
                http_settings,
            ]
        ):
            payload["config"]["serverSettings"] = {}

            if enable_server is not None:
                payload["config"]["serverSettings"]["enabled"] = enable_server
                auto_mask.append("config.server_settings.enabled")

            if graceful_timeout:
                payload["config"]["serverSettings"][
                    "gracefulTimeout"
                ] = graceful_timeout
                auto_mask.append("config.server_settings.graceful_timeout")

            if drain_timeout:
                payload["config"]["serverSettings"][
                    "drainTimeout"
                ] = drain_timeout
                auto_mask.append("config.server_settings.drain_timeout")

            if http_settings:
                payload["config"]["serverSettings"][
                    "httpSettings"
                ] = http_settings
                auto_mask.append("config.server_settings.http_settings")

    # Prepare query parameters for update mask
    params = {}
    if update_mask:
        # Use user-provided update mask
        params["updateMask"] = ",".join(update_mask)
    else:
        params["updateMask"] = ",".join(auto_mask)

    # Send the request
    response = client.session.patch(url, json=payload, params=params)

    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to update forwarder: {response.text}")

    return response.json()


def delete_forwarder(
    client: "ChronicleClient",
    forwarder_id: str,
) -> dict[str, Any]:
    """Delete a forwarder from Chronicle.

    Args:
        client: ChronicleClient instance
        forwarder_id: ID of the forwarder to delete

    Returns:
        Dict containing the empty response (usually {})

    Raises:
        APIError: If the API returns an error response.
    """
    url = f"{client.base_url}/{client.instance_id}/forwarders/{forwarder_id}"

    response = client.session.delete(url)

    if response.status_code != 200:
        raise APIError(f"Failed to delete forwarder: {response.text}")

    return response.json()


def _find_forwarder_by_display_name(
    client: "ChronicleClient", display_name: str
) -> dict[str, Any] | None:
    """Find an existing forwarder by its display name.

    This function calls list_forwarders which handles pagination to get
    all forwarders.

    Args:
        client: ChronicleClient instance.
        display_name: Name of the forwarder to find.

    Returns:
        Dictionary containing the forwarder details if found, otherwise None.

    Raises:
        APIError: If the API request to list forwarders fails.
    """
    try:
        # list_forwarders internally handles pagination to get all forwarders
        # when no page_token is supplied initially.
        forwarders_response = list_forwarders(client, page_size=1000)
        for forwarder in forwarders_response.get("forwarders", []):
            if forwarder.get("displayName") == display_name:
                return forwarder
        return None
    except APIError as e:
        # Re-raise APIError if listing fails, to be handled by the caller
        raise APIError(
            f"Failed to list forwarders while searching for '{display_name}': "
            f"{str(e)}"
        ) from e


def get_or_create_forwarder(
    client: "ChronicleClient", display_name: str | None = None
) -> dict[str, Any]:
    """Get an existing forwarder by name or create a new one if none exists.

    This function now includes caching for the default forwarder to reduce
    API calls to list_forwarders.

    Args:
        client: ChronicleClient instance.
        display_name: Name of the forwarder to find or create.
                      If None, uses the default name "Wrapper-SDK-Forwarder".

    Returns:
        Dictionary containing the forwarder details.

    Raises:
        APIError: If the API request fails.
    """
    target_display_name = (
        display_name
        or client._default_forwarder_display_name  # pylint: disable=protected-access
    )
    is_default_forwarder_request = (
        target_display_name
        == client._default_forwarder_display_name  # pylint: disable=protected-access
    )

    if (
        is_default_forwarder_request
        and client._cached_default_forwarder_id  # pylint: disable=protected-access
    ):
        try:
            # Attempt to get the cached default forwarder directly
            forwarder = get_forwarder(
                client,
                client._cached_default_forwarder_id,  # pylint: disable=protected-access
            )
            if (
                forwarder.get("displayName")
                == client._default_forwarder_display_name  # pylint: disable=protected-access
            ):
                return forwarder  # Cache hit and valid
            else:
                # Cached ID points to a forwarder with
                # a different name (unexpected) or forwarder was modified.
                # Invalidate cache.
                client._cached_default_forwarder_id = (  # pylint: disable=protected-access
                    None
                )
        except APIError:
            # Forwarder might have been deleted or permissions changed.
            # Invalidate cache.
            client._cached_default_forwarder_id = (  # pylint: disable=protected-access
                None
            )
            # Proceed to find/create logic

    try:
        # Try to find the forwarder by its display name
        found_forwarder = _find_forwarder_by_display_name(
            client, target_display_name
        )

        if found_forwarder:
            if is_default_forwarder_request:
                # Cache the ID of the default forwarder if found
                # pylint: disable=protected-access
                client._cached_default_forwarder_id = extract_forwarder_id(
                    found_forwarder["name"]
                )
                # pylint: enable=protected-access
            return found_forwarder

        # No matching forwarder found, create a new one
        created_forwarder = create_forwarder(
            client, display_name=target_display_name
        )
        if is_default_forwarder_request:
            # Cache the ID of the newly created default forwarder
            # pylint: disable=protected-access
            client._cached_default_forwarder_id = extract_forwarder_id(
                created_forwarder["name"]
            )
            # pylint: enable=protected-access
        return created_forwarder

    except APIError as e:
        if "permission" in str(e).lower():
            raise APIError(
                f"Insufficient permissions to manage forwarders: {str(e)}"
            ) from e
        raise e


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
    if "/" not in forwarder_name:
        # Validate that it looks like a UUID or a simple string identifier
        return forwarder_name

    segments = forwarder_name.split("/")
    # Filter out empty segments (handles cases like "/")
    segments = [s for s in segments if s]

    if not segments:
        raise ValueError(f"Invalid forwarder name format: {forwarder_name}")

    # Return the last segment of the path
    return segments[-1]


def ingest_log(
    client: "ChronicleClient",
    log_type: str,
    log_message: str | list[str],
    log_entry_time: datetime | None = None,
    collection_time: datetime | None = None,
    namespace: str | None = None,
    labels: dict[str, str] | None = None,
    forwarder_id: str | None = None,
    force_log_type: bool = False,
) -> dict[str, Any]:
    """Ingest one or more logs into Chronicle.

    Args:
        client: ChronicleClient instance
        log_type: Chronicle log type (e.g., "OKTA", "WINDOWS", etc.)
        log_message: Can be one of:
            - A single log message string
            - A string containing multiple logs
                (will be split based on log type)
            - A list of log message strings
                (each item treated as a separate log)
        log_entry_time: The time the log entry was created
            (defaults to current time)
        collection_time: The time the log was collected
            (defaults to current time)
        namespace: The user-configured environment namespace to identify
            the data domain the logs originated from. This namespace will be
            used as a tag to identify the appropriate data domain for indexing
            and enrichment functionality.
        labels: Dictionary of custom metadata labels to attach to
            the log entries.
        forwarder_id: ID of the forwarder to use
            (creates or uses default if None)
        force_log_type: Whether to force using the log type even if not in
            the valid list

    Returns:
        Dictionary containing the operation details for the ingestion

    Raises:
        ValueError: If the log type is invalid or timestamps are invalid
        APIError: If the API request fails
    """
    # Validate log type
    if not is_valid_log_type(client, log_type) and not force_log_type:
        raise ValueError(
            f"Invalid log type: {log_type}. "
            "Use force_log_type=True to override."
        )

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
    if "/" not in forwarder_id:
        forwarder_resource = f"{client.instance_id}/forwarders/{forwarder_id}"
    else:
        forwarder_resource = forwarder_id

    # Construct the import URL
    url = (
        f"{client.base_url}/{client.instance_id}/logTypes"
        f"/{log_type}/logs:import"
    )

    if isinstance(log_message, str):
        initialize_multi_line_formats()
        # Split string into individual log entries based on log type
        log_messages = split_logs(log_type, log_message)
        if not log_messages:
            # If splitting resulted in empty list, treat as a single log
            log_messages = [log_message] if log_message.strip() else []
        print(
            f"Split {log_type} log into {len(log_messages)} "
            "individual log entries"
        )
    else:
        log_messages = log_message

    # Prepare logs for the payload
    logs = []
    for msg in log_messages:
        # Encode log message in base64
        log_data = base64.b64encode(msg.encode("utf-8")).decode("utf-8")

        log_data = {
            "data": log_data,
            "log_entry_time": log_entry_time_str,
            "collection_time": collection_time_str,
        }

        if namespace:
            log_data["environment_namespace"] = namespace

        # Fix for labels: API expects a map where values are LogLabel objects
        if labels:
            log_data["labels"] = {
                key: {"value": value} for key, value in labels.items()
            }

        logs.append(log_data)

    # Construct the request payload
    payload = {"inline_source": {"logs": logs, "forwarder": forwarder_resource}}

    # Send the request
    response = client.session.post(url, json=payload)

    # Check for errors
    if response.status_code != 200:
        raise APIError(f"Failed to ingest log: {response.text}")

    return response.json()


def ingest_udm(
    client: "ChronicleClient",
    udm_events: dict[str, Any] | list[dict[str, Any]],
    add_missing_ids: bool = True,
) -> dict[str, Any]:
    """Ingest UDM events directly into Chronicle.

    Args:
        client: ChronicleClient instance
        udm_events: A single UDM event dictionary
            or a list of UDM event dictionaries
        add_missing_ids: Whether to automatically add unique IDs to
            events missing them

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
            raise ValueError(
                f"Invalid UDM event type: {type(event)}. "
                "Events must be dictionaries."
            )

        # Check for required metadata section
        if "metadata" not in event:
            raise ValueError("UDM event missing required 'metadata' section")

        if not isinstance(event["metadata"], dict):
            raise ValueError("UDM 'metadata' must be a dictionary")

        # Add event timestamp if missing
        if "event_timestamp" not in event["metadata"]:
            current_time = datetime.now().astimezone()
            event["metadata"][
                "event_timestamp"
            ] = current_time.isoformat().replace("+00:00", "Z")

        # Add ID if needed
        if add_missing_ids and "id" not in event["metadata"]:
            event["metadata"]["id"] = str(uuid.uuid4())

    # Prepare the request
    parent = (
        f"projects/{client.project_id}/locations/{client.region}"
        f"/instances/{client.customer_id}"
    )
    url = (
        f"https://{client.region}-chronicle.googleapis.com/v1alpha/"
        f"{parent}/events:import"
    )

    # Format the request body
    body = {
        "inline_source": {"events": [{"udm": event} for event in events_copy]}
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


def import_entities(
    client: "ChronicleClient",
    entities: dict[str, Any] | list[dict[str, Any]],
    log_type: str,
) -> dict[str, Any]:
    """Import entities into Chronicle.

    Args:
        client: ChronicleClient instance
        entities: An entity dictionary or a list of entity dictionaries
        log_type: The log type of the log from which this entity is created

    Returns:
        Dictionary containing the operation details for the ingestion

    Raises:
        ValueError: If any required fields are missing or entities malformed
        APIError: If the API request fails
    """
    # Ensure we have a list of entities
    if isinstance(entities, dict):
        entities = [entities]

    if not entities:
        raise ValueError("No entities provided")

    if not log_type:
        raise ValueError("No log type provided")

    # Prepare the request
    url = f"{client.base_url}/{client.instance_id}/entities:import"

    # Format the request body
    body = {"inline_source": {"entities": entities, "log_type": log_type}}

    # Make the API request
    response = client.session.post(url, json=body)

    # Check for errors
    if response.status_code >= 400:
        error_message = f"Failed to import entities: {response.text}"
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
