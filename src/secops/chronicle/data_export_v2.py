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


def get_data_export_v2(client, data_export_id: str) -> Dict[str, Any]:
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


def create_data_export_v2(
    client,
    gcs_bucket: str,
    start_time: datetime,
    end_time: datetime,
    log_types: List[str] = [],
    export_all_logs: bool = False,
) -> Dict[str, Any]:
    """Create a new data export job.

    Args:
        client: ChronicleClient instance
        gcs_bucket: GCS bucket path in format
            "projects/{project}/buckets/{bucket}"
        start_time: Start time for the export (inclusive)
        end_time: End time for the export (exclusive)
        log_type: Optional specific log type to export.
            If None and export_all_logs is False, no logs will be exported
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

    if not export_all_logs and len(log_types) == 0:
        raise ValueError(
            "Either log_type must be specified or export_all_logs must be True"
        )

    if export_all_logs and len(log_types) != 0:
        raise ValueError(
            "Cannot specify both log_type and export_all_logs=True"
        )

    # Format times in RFC 3339 format
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Construct the request payload
    payload = {
        "startTime": start_time_str,
        "endTime": end_time_str,
        "gcsBucket": gcs_bucket,
    }

    # Add log_type if provided
    payload_log_types = []
    for log_type in log_types:
        # Check if we need to prefix with logTypes
        if "/" not in log_type:
            # If log type isn't in the list, try the standard format
            # Format log_type as required by the API -
            # the complete format
            formatted_log_type = (
                f"projects/{client.project_id}/"
                f"locations/{client.region}/instances/"
                f"{client.customer_id}/logTypes/{log_type}"
            )
            payload_log_types.append(formatted_log_type)
        else:
            # Log type is already formatted
            payload_log_types.append(log_type)

    payload["includeLogTypes"] = payload_log_types

    # Add export_all_logs if True
    if export_all_logs:
        # Setting log type as empty list
        payload["includeLogTypes"] = []

    # Construct the URL and send the request
    url = f"{client.base_url}/{client.instance_id}/dataExports"

    response = client.session.post(url, json=payload)

    return response.json()


def update_data_export_v2(
    client,
    data_export_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    gcs_bucket: Optional[str] = None,
    log_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Update an existing data export job.

    Note: The job must be in the "IN_QUEUE" state to be updated.

    Args:
        client: ChronicleClient instance
        data_export_id: ID of the data export to update
        start_time: Optional new start time for the export
        end_time: Optional new end time for the export
        gcs_bucket: Optional new GCS bucket path
        log_types: Optional new list of log types to export

    Returns:
        Dictionary containing details of the updated data export

    Raises:
        APIError: If the API request fails
        ValueError: If invalid parameters are provided
    """
    # Construct the request payload and update mask
    payload = {}
    update_mask = []

    if start_time:
        payload["startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        update_mask.append("startTime")

    if end_time:
        payload["endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        update_mask.append("endTime")

    if gcs_bucket:
        if not gcs_bucket.startswith("projects/"):
            raise ValueError(
                "GCS bucket must be in format: "
                "projects/{project}/buckets/{bucket}"
            )
        payload["gcsBucket"] = gcs_bucket
        update_mask.append("gcsBucket")

    if log_types is not None:
        payload["includeLogTypes"] = log_types
        update_mask.append("includeLogTypes")

    if not payload:
        raise ValueError("At least one field to update must be provided.")

    # Construct the URL and send the request
    url = (
        f"{client.base_url}/{client.instance_id}/dataExports/"
        f"{data_export_id}"
    )
    params = {"update_mask": ",".join(update_mask)}

    response = client.session.patch(url, json=payload, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to update data export: {response.text}")

    return response.json()



def cancel_data_export_v2(client, data_export_id: str) -> Dict[str, Any]:
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
    url = (
        f"{client.base_url}/{client.instance_id}/dataExports/"
        f"{data_export_id}:cancel"
    )

    response = client.session.post(url)

    if response.status_code != 200:
        raise APIError(f"Failed to cancel data export: {response.text}")

    return response.json()


def list_data_export_v2(client, filter: Optional[str] = None, page_size: Optional[int] = None, page_token: Optional[str] = None) -> Dict[str, Any]:
    """List data export jobs.

    Args:
        client: ChronicleClient instance

    Returns:
        Dictionary containing data export list

    Raises:
        APIError: If the API request fails

    Example:
        ```python
        export = chronicle.list_data_export()
        ```
    """
    url = f"{client.base_url}/{client.instance_id}/dataExports"

    params = {
        "pageSize": page_size,
        "pageToken": page_token,
        "filter": filter,
    }

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to get data export: {response.text}")

    return response.json()