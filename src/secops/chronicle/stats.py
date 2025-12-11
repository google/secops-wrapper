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
"""Statistics functionality for Chronicle searches."""
from datetime import datetime
from typing import Any

from secops.exceptions import APIError


def get_stats(
    client,
    query: str,
    start_time: datetime,
    end_time: datetime,
    max_values: int = 60,
    timeout: int = 120,
    max_events: int = 10000,
    case_insensitive: bool = True,
    max_attempts: int = 30,
) -> dict[str, Any]:
    """
    Get statistics from a Chronicle search query using
    the Chronicle V1alpha API.

    Args:
        client: ChronicleClient instance
        query: Chronicle search query in stats format
        start_time: Search start time
        end_time: Search end time
        max_values: Maximum number of values to return per field
        timeout: Timeout in seconds for API request (default: 120)
        max_events: Maximum number of events to process
        case_insensitive: Whether to perform case-insensitive search
                (legacy parameter, not used by new API)
        max_attempts: Legacy parameter kept for backwards compatibility

    Returns:
        Dictionary with search statistics including columns, rows,
        and total_rows

    Raises:
        APIError: If the API request fails
    """
    # Unused parameters, kept for backward compatibility
    _ = (max_events, case_insensitive, max_attempts)

    # Format the instance ID for the API call
    instance = client.instance_id

    # Endpoint for UDM search
    url = f"{client.base_url}/{instance}:udmSearch"

    # Format times for the API
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Query parameters for the API call
    params = {
        "query": query,
        "timeRange.start_time": start_time_str,
        "timeRange.end_time": end_time_str,
        "limit": max_values,  # Limit to specified number of results
    }

    # Make the API request
    response = client.session.get(url, params=params, timeout=timeout)
    if response.status_code != 200:
        raise APIError(
            f"Error executing stats search: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    results = response.json()

    # Check if stats data is available in the response
    if "stats" not in results:
        raise APIError("No stats found in response")

    # Process the stats results
    return process_stats_results(results["stats"])


def process_stats_results(stats: dict[str, Any]) -> dict[str, Any]:
    """Process stats search results.

    Args:
        stats: Stats search results from API

    Returns:
        Processed statistics with columns, rows, and total_rows
    """
    processed_results = {"total_rows": 0, "columns": [], "rows": []}

    # Return early if no results
    if not stats or "results" not in stats:
        return processed_results

    # Extract columns
    columns = []
    column_data = {}

    for col_data in stats["results"]:
        col_name = col_data.get("column", "")
        columns.append(col_name)

        # Process values for this column
        values = []
        for val_data in col_data.get("values", []):
            # Handle regular single value cells
            if "value" in val_data:
                val = val_data["value"]
                if "int64Val" in val:
                    values.append(int(val["int64Val"]))
                elif "doubleVal" in val:
                    values.append(float(val["doubleVal"]))
                elif "stringVal" in val:
                    values.append(val["stringVal"])
                else:
                    values.append(None)
            # Handle list value cells (like those from array_distinct)
            elif "list" in val_data and "values" in val_data["list"]:
                list_values = []
                for list_val in val_data["list"]["values"]:
                    if "int64Val" in list_val:
                        list_values.append(int(list_val["int64Val"]))
                    elif "doubleVal" in list_val:
                        list_values.append(float(list_val["doubleVal"]))
                    elif "stringVal" in list_val:
                        list_values.append(list_val["stringVal"])
                values.append(list_values)
            else:
                values.append(None)

        column_data[col_name] = values

    # Build result rows
    rows = []
    if columns and all(col in column_data for col in columns):
        max_rows = (
            max(len(column_data[col]) for col in columns) if column_data else 0
        )
        processed_results["total_rows"] = max_rows

        for i in range(max_rows):
            row = {}
            for col in columns:
                col_values = column_data[col]
                row[col] = col_values[i] if i < len(col_values) else None
            rows.append(row)

    processed_results["columns"] = columns
    processed_results["rows"] = rows

    return processed_results
