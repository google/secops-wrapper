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
"""Chronicle log type utilities for raw log ingestion.

This module provides functions to help users select the correct Chronicle
log type for raw log ingestion. It includes functionality to search for
log types, validate log types, and suggest appropriate log types based on
product or vendor.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


# Cache for log types to avoid repeated API calls
_LOG_TYPES_CACHE: list[dict[str, Any]] | None = None


def _fetch_log_types_from_api(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch log types from Chronicle API with pagination.

    Args:
        client: ChronicleClient instance.
        page_size: Number of results per page.
        page_token: Token for fetching a specific page.

    Returns:
        List of log types.

    Raises:
        Exception: If request fails.
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes"
    all_log_types: list[dict[str, Any]] = []

    # Determine if we should fetch all pages or just one
    fetch_all_pages = page_size is None
    current_page_token = page_token

    while True:
        params: dict[str, Any] = {}

        # Set page size (use default of 1000 if fetching all pages)
        params["pageSize"] = page_size if page_size else 1000

        # Add page token if provided
        if current_page_token:
            params["pageToken"] = current_page_token

        response = client.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Add log types from response
        all_log_types.extend(data.get("logTypes", []))

        # Check for next page
        current_page_token = data.get("nextPageToken")

        # Stop if: no more pages OR page_size was specified (single page)
        if not current_page_token or not fetch_all_pages:
            break

    return all_log_types


def load_log_types(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
) -> list[dict[str, Any]]:
    """Load and cache log types from Chronicle.

    Args:
        client: ChronicleClient instance.
        page_size: Number of results per page (fetches single page).
        page_token: Page token for pagination.

    Returns:
        List of log types.

    Raises:
        ValueError: If client is None.
    """
    global _LOG_TYPES_CACHE

    # Return cached data if available (skip cache if pagination params)
    if _LOG_TYPES_CACHE is not None and not page_size and not page_token:
        return _LOG_TYPES_CACHE

    result = _fetch_log_types_from_api(
        client, page_size=page_size, page_token=page_token
    )

    # Only cache if fetching all (no pagination params)
    if not page_size and not page_token:
        _LOG_TYPES_CACHE = result

    return result


def get_all_log_types(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
) -> list[dict[str, Any]]:
    """Get all available Chronicle log types.

    Args:
        client: ChronicleClient instance.
        page_size: Number of results per page (fetches single page).
        page_token: Page token for pagination.

    Returns:
        List of log types.

    Raises:
        ValueError: If client is None.
    """
    return load_log_types(
        client=client,
        page_size=page_size,
        page_token=page_token,
    )


def is_valid_log_type(
    client: "ChronicleClient",
    log_type_id: str,
) -> bool:
    """Check if a log type ID is valid by querying.

    Args:
        log_type_id: The log type ID to validate.
        client: ChronicleClient instance.

    Returns:
        True if the log type exists, False otherwise.

    Raises:
        ValueError: If client is None.
    """
    log_types = load_log_types(client=client)
    for log_type_data in log_types:
        name = log_type_data.get("name", "")
        if name.endswith(f"/logTypes/{log_type_id}"):
            return True
    return False


def get_log_type_description(
    log_type_id: str,
    client: "ChronicleClient",
) -> str | None:
    """Get the description for a log type ID.

    Args:
        log_type_id: The log type ID to get the description for.
        client: ChronicleClient instance.

    Returns:
        Display name if the log type exists, None otherwise.

    Raises:
        ValueError: If client is None.
    """
    log_types = load_log_types(client=client)
    for log_type_data in log_types:
        name = log_type_data.get("name", "")
        if name.endswith(f"/logTypes/{log_type_id}"):
            return log_type_data.get("displayName")
    return None


def search_log_types(
    search_term: str,
    case_sensitive: bool = False,
    search_in_description: bool = True,
    client: "ChronicleClient" = None,
) -> list[dict[str, Any]]:
    """Search for log types matching a search term.

    Args:
        search_term: Term to search for in log type IDs and descriptions.
        case_sensitive: Whether the search should be case-sensitive.
        search_in_description: Whether to search in descriptions or IDs.
        client: ChronicleClient instance.

    Returns:
        List of log types matching the search criteria.

    Raises:
        ValueError: If client is None.
    """
    log_types = get_all_log_types(client=client)
    results = []

    # Convert search term to lowercase if case-insensitive
    if not case_sensitive:
        search_term = search_term.lower()

    for log_type_data in log_types:
        # Extract ID from resource name
        name = log_type_data.get("name", "")
        log_type_id = name.split("/")[-1] if name else ""

        # Check ID match
        check_id = log_type_id if case_sensitive else log_type_id.lower()
        if search_term in check_id:
            results.append(log_type_data)
            continue

        # Check description match if enabled
        if search_in_description:
            display_name = log_type_data.get("displayName", "")
            check_desc = (
                display_name if case_sensitive else display_name.lower()
            )
            if search_term in check_desc:
                results.append(log_type_data)

    return results
