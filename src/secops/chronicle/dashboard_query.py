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
"""
Module for Google SecOps Dashboard query.

This module provides functions to execute and get dashboard query.
"""

import json
from typing import Any

from secops.exceptions import APIError
from secops.chronicle.models import InputInterval
from secops.chronicle.utils.request_utils import chronicle_request
from secops.chronicle.utils.format_utils import (
    format_resource_id,
    parse_json_list,
    remove_none_values,
)


def execute_query(
    client,
    query: str,
    interval: InputInterval | dict[str, Any] | str,
    filters: list[dict[str, Any]] | str | None = None,
    clear_cache: bool | None = None,
) -> dict[str, Any]:
    """Execute a dashboard query and retrieve results.

    Args:
        client: ChronicleClient instance
        query: The UDM search query to execute
        interval: The time interval for the query
        filters: Filters to apply to the query
        clear_cache: Flag to read from database instead of cache

    Returns:
        Dictionary containing query results
    """
    try:
        if isinstance(interval, str):
            interval = json.loads(interval)
    except ValueError as e:
        raise APIError(
            f"Failed to parse JSON. Must be a valid JSON string: {e}"
        ) from e

    if isinstance(interval, dict):
        interval = InputInterval.from_dict(interval)

    if filters:
        filters = parse_json_list(filters, "filters")

    payload = remove_none_values(
        {
            "query": {"query": query, "input": interval.to_dict()},
            "clearCache": clear_cache,
            "filters": filters if filters else None,
        }
    )

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="dashboardQueries:execute",
        json=payload,
        error_message="Failed to execute query",
    )


def get_execute_query(client, query_id: str) -> dict[str, Any]:
    """Get a dashboard query details.

    Args:
        client: ChronicleClient instance
        query_id: ID of the query to retrieve details

    Returns:
        Dictionary containing query details
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"dashboardQueries/{format_resource_id(query_id)}",
        error_message="Failed to get query",
    )
