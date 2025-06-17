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
"""Chronicle Data Export API functionality.

This module provides functions to interact with the Chronicle Data Export API,
allowing users to export Chronicle data to Google Cloud Storage buckets.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from secops.exceptions import APIError


@dataclass
class AvailableLogType:
    """Represents an available log type for export.

    Attributes:
        log_type: The log type identifier
        display_name: Human-readable display name of the log type
        start_time: Earliest time the log type is available for export
        end_time: Latest time the log type is available for export
    """

    log_type: str
    display_name: str
    start_time: datetime
    end_time: datetime


def get_data_export(client, data_export_id: str) -> Dict[str, Any]:
    """Get information about a specific data export.

    Args:
        client: ChronicleClient instance
        data_export_id: ID of the data export to retrieve

    Returns:
        Dictionary containing data export details

    Raises:
        APIError: If the API request fails

    Example:
        ```python
        export = chronicle.get_data_export("export123")
        print(f"Export status: {export['data_export_status']['stage']}")
        ```
    """
    url = f"{client.base_url}/{client.instance_id}/dataExports/{data_export_id}"

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get data export: {response.text}")

    return response.json()


def create_data_export(
    client,
    gcs_bucket: str,
    start_time: datetime,
    end_time: datetime,
    log_type: Optional[str] = None,
    export_all_logs: bool = False,
) -> Dict[str, Any]:
    """Create a new data export job.

    Args:
        client: ChronicleClient instance
        gcs_bucket: GCS bucket path in format "projects/{project}/buckets/{bucket}"
        start_time: Start time for the export (inclusive)
        end_time: End time for the export (exclusive)
        log_type: Optional specific log type to export. If None and export_all_logs is False,
                  no logs will be exported
        export_all_logs: Whether to export all log types

    Returns:
        Dictionary containing details of the created data export

    Raises:
        APIError: If the API request fails
        ValueError: If invalid parameters are provided

    Example:
        ```python
        from datetime import datetime, timedelta

        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)

        # Export a specific log type
        export = chronicle.create_data_export(
            gcs_bucket="projects/my-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS"
        )

        # Export all logs
        export = chronicle.create_data_export(
            gcs_bucket="projects/my-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            export_all_logs=True
        )
        ```
    """
    # Validate parameters
    if not gcs_bucket:
        raise ValueError("GCS bucket must be provided")

    if not gcs_bucket.startswith("projects/"):
        raise ValueError(
            "GCS bucket must be in format: projects/{project}/buckets/{bucket}"
        )

    if end_time <= start_time:
        raise ValueError("End time must be after start time")

    if not export_all_logs and not log_type:
        raise ValueError(
            "Either log_type must be specified or export_all_logs must be True"
        )

    if export_all_logs and log_type:
        raise ValueError("Cannot specify both log_type and export_all_logs=True")

    # Format times in RFC 3339 format
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Construct the request payload
    payload = {
        "start_time": start_time_str,
        "end_time": end_time_str,
        "gcs_bucket": gcs_bucket,
    }

    # Add log_type if provided
    if log_type:
        # Check if we need to prefix with logTypes
        if "/" not in log_type:
            # First check if log type exists
            try:
                # Try to fetch available log types to validate
                available_logs = fetch_available_log_types(
                    client, start_time=start_time, end_time=end_time
                )
                found = False
                for lt in available_logs.get("available_log_types", []):
                    if lt.log_type.endswith("/" + log_type) or lt.log_type.endswith(
                        "/logTypes/" + log_type
                    ):
                        # If we found the log type in the list, use its exact format
                        payload["log_type"] = lt.log_type
                        found = True
                        break

                if not found:
                    # If log type isn't in the list, try the standard format
                    # Format log_type as required by the API - the complete format
                    formatted_log_type = f"projects/{client.project_id}/locations/{client.region}/instances/{client.customer_id}/logTypes/{log_type}"
                    payload["log_type"] = formatted_log_type
            except Exception:
                # If we can't validate, just use the standard format
                formatted_log_type = f"projects/{client.project_id}/locations/{client.region}/instances/{client.customer_id}/logTypes/{log_type}"
                payload["log_type"] = formatted_log_type
        else:
            # Log type is already formatted
            payload["log_type"] = log_type

    # Add export_all_logs if True
    if export_all_logs:
        payload["export_all_logs"] = True

    # Construct the URL and send the request
    url = f"{client.base_url}/{client.instance_id}/dataExports"

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(f"Failed to create data export: {response.text}")

    return response.json()


def cancel_data_export(client, data_export_id: str) -> Dict[str, Any]:
    """Cancel an in-progress data export.

    Args:
        client: ChronicleClient instance
        data_export_id: ID of the data export to cancel

    Returns:
        Dictionary containing details of the cancelled data export

    Raises:
        APIError: If the API request fails

    Example:
        ```python
        result = chronicle.cancel_data_export("export123")
        print("Export cancellation request submitted")
        ```
    """
    url = f"{client.base_url}/{client.instance_id}/dataExports/{data_export_id}:cancel"

    response = client.session.post(url)

    if response.status_code != 200:
        raise APIError(f"Failed to cancel data export: {response.text}")

    return response.json()


def fetch_available_log_types(
    client,
    start_time: datetime,
    end_time: datetime,
    page_size: Optional[int] = None,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch available log types for export within a time range.

    Args:
        client: ChronicleClient instance
        start_time: Start time for the time range (inclusive)
        end_time: End time for the time range (exclusive)
        page_size: Optional maximum number of results to return
        page_token: Optional page token for pagination

    Returns:
        Dictionary containing:
            - available_log_types: List of AvailableLogType objects
            - next_page_token: Token for fetching the next page of results

    Raises:
        APIError: If the API request fails
        ValueError: If invalid parameters are provided

    Example:
        ```python
        from datetime import datetime, timedelta

        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)

        result = chronicle.fetch_available_log_types(
            start_time=start_time,
            end_time=end_time
        )

        for log_type in result["available_log_types"]:
            print(f"{log_type.display_name} ({log_type.log_type})")
            print(f"  Available from {log_type.start_time} to {log_type.end_time}")
        ```
    """
    # Validate parameters
    if end_time <= start_time:
        raise ValueError("End time must be after start time")

    # Format times in RFC 3339 format
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Construct the request payload
    payload = {"start_time": start_time_str, "end_time": end_time_str}

    # Add optional parameters if provided
    if page_size:
        payload["page_size"] = page_size

    if page_token:
        payload["page_token"] = page_token

    # Construct the URL and send the request
    url = f"{client.base_url}/{client.instance_id}/dataExports:fetchavailablelogtypes"

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(f"Failed to fetch available log types: {response.text}")

    # Parse the response
    result = response.json()

    # Convert the API response to AvailableLogType objects
    available_log_types = []
    for log_type_data in result.get("available_log_types", []):
        # Parse datetime strings to datetime objects
        start_time = datetime.fromisoformat(
            log_type_data.get("start_time").replace("Z", "+00:00")
        )
        end_time = datetime.fromisoformat(
            log_type_data.get("end_time").replace("Z", "+00:00")
        )

        available_log_type = AvailableLogType(
            log_type=log_type_data.get("log_type"),
            display_name=log_type_data.get("display_name", ""),
            start_time=start_time,
            end_time=end_time,
        )
        available_log_types.append(available_log_type)

    return {
        "available_log_types": available_log_types,
        "next_page_token": result.get("next_page_token", ""),
    }
