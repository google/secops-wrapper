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
"""UDM search functionality for Chronicle."""

from datetime import datetime
from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def search_udm(
    client: "ChronicleClient",
    query: str,
    start_time: datetime,
    end_time: datetime,
    max_events: int = 10000,
    case_insensitive: bool = True,
    max_attempts: int = 30,
    timeout: int = 30,
    debug: bool = False,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Perform a UDM search query using the Chronicle V1alpha API.

    Args:
        client: ChronicleClient instance
        query: The UDM search query
        start_time: Search start time
        end_time: Search end time
        max_events: Maximum events to return
        case_insensitive: Whether to perform case-insensitive search
        max_attempts: Maximum number of polling attempts (legacy parameter, kept
                        for backwards compatibility)
        timeout: Timeout in seconds for each API request (default: 30)
        debug: Print debug information during execution
        as_list: Whether to return results as a list or dictionary

    Returns:
        Dict containing the search results with events

    Raises:
        APIError: If the API request fails
    """
    # Unused parameters, kept for backward compatibility
    _ = (case_insensitive, max_attempts, timeout)

    # Format times for the API
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Query parameters for the API call
    params = {
        "query": query,
        "timeRange.start_time": start_time_str,
        "timeRange.end_time": end_time_str,
        "limit": max_events,  # Limit to specified number of results
    }

    if debug:
        print(f"Executing UDM search: {query}")
        print(f"Time range: {start_time_str} to {end_time_str}")

    result = chronicle_request(
        client,
        method="GET",
        endpoint_path=":udmSearch",
        api_version=APIVersion.V1ALPHA,
        params=params,
        timeout=timeout,
    )

    if as_list:
        return result.get("events", [])
    return {
        "events": result.get("events", []),
        "total_events": len(result.get("events", [])),
        "more_data_available": result.get("moreDataAvailable", False),
    }
