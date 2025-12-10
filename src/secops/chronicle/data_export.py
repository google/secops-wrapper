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

from dataclasses import dataclass
from datetime import datetime
from typing import Any

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


def _get_base_url(client) -> str:
    """Get the enhanced/new base URL for the Chronicle Data Export API for
    region other then dev and staging.
    Args:
        client: ChronicleClient instance

    Returns:
        The base URL for the Chronicle Data Export API
    """
    if client.region not in ["dev", "staging"]:
        return f"https://chronicle.{client.region}.rep.googleapis.com/v1alpha"
    return client.base_url


def _get_formatted_log_type(client, log_type: str) -> str:
    """Get the formatted log type for the given log type.

    Args:
        client: ChronicleClient instance
        log_type: The log type to format

    Returns:
        The formatted log type
    """
    if "/" not in log_type:
        return (
            f"projects/{client.project_id}/locations/{client.region}/"
            f"instances/{client.customer_id}/logTypes/{log_type}"
        )

    return log_type


def get_data_export(client, data_export_id: str) -> dict[str, Any]:
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
    url = (
        f"{_get_base_url(client)}/{client.instance_id}/"
        f"dataExports/{data_export_id}"
    )

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get data export: {response.text}")

    return response.json()


def create_data_export(
    client,
    gcs_bucket: str,
    start_time: datetime,
    end_time: datetime,
    log_type: str | None = None,
    log_types: list[str] | None = None,
    export_all_logs: bool = False,
) -> dict[str, Any]:
    """Create a new data export job.

    Args:
        client: ChronicleClient instance
        gcs_bucket: GCS bucket path in format
            "projects/{project}/buckets/{bucket}"
        start_time: Start time for the export (inclusive)
        end_time: End time for the export (exclusive)
        log_type: Optional specific log type to export (deprecated).
            Use log_types instead.
        log_types: Optional list of log types to export.
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
            log_types=["WINDOWS"]
        )

        # Export all logs
        export = chronicle.create_data_export(
            gcs_bucket="projects/my-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            export_all_logs=True
        )
    """
    # Validate that the user hasn't provided both log_type and log_types
    if log_type is not None and log_types is not None:
        raise ValueError("Use either log_type or log_types, not both")

    # Handle both log_type and log_types for backward compatibility
    if log_type is not None:
        log_types = [log_type]

    # Initialize log_types if None
    log_types = [] if log_types is None else log_types

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

    if export_all_logs and len(log_types) > 0:
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

    # Process log types
    payload["includeLogTypes"] = list(
        map(lambda x: _get_formatted_log_type(client, x), log_types)
    )

    # Add export_all_logs if True
    if export_all_logs:
        # Setting log types as empty list for all log export
        payload["includeLogTypes"] = []

    # Construct the URL and send the request
    url = f"{_get_base_url(client)}/{client.instance_id}/dataExports"

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(f"Failed to create data export: {response.text}")

    return response.json()


def cancel_data_export(client, data_export_id: str) -> dict[str, Any]:
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
        f"{_get_base_url(client)}/{client.instance_id}/dataExports/"
        f"{data_export_id}:cancel"
    )

    response = client.session.post(url)

    if response.status_code != 200:
        raise APIError(f"Failed to cancel data export: {response.text}")

    return response.json()


def fetch_available_log_types(
    client,
    start_time: datetime,
    end_time: datetime,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
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
            print(
                f"Available from {log_type.start_time} "
                f"to {log_type.end_time}"
            )
        ```
    """
    # Validate parameters
    if end_time <= start_time:
        raise ValueError("End time must be after start time")

    # Format times in RFC 3339 format
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Construct the request payload
    payload = {"startTime": start_time_str, "endTime": end_time_str}

    # Add optional parameters if provided
    if page_size:
        payload["pageSize"] = page_size

    if page_token:
        payload["pageToken"] = page_token

    # Construct the URL and send the request
    url = (
        f"{_get_base_url(client)}/{client.instance_id}/"
        "dataExports:fetchavailablelogtypes"
    )

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


def update_data_export(
    client,
    data_export_id: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    gcs_bucket: str | None = None,
    log_types: list[str] | None = None,
) -> dict[str, Any]:
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
        payload["includeLogTypes"] = list(
            map(lambda x: _get_formatted_log_type(client, x), log_types)
        )
        update_mask.append("includeLogTypes")

    if not payload:
        raise ValueError("At least one field to update must be provided.")

    # Construct the URL and send the request
    url = (
        f"{_get_base_url(client)}/{client.instance_id}/dataExports/"
        f"{data_export_id}"
    )
    params = {"update_mask": ",".join(update_mask)}

    response = client.session.patch(url, json=payload, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to update data export: {response.text}")

    return response.json()


def list_data_export(
    client,
    filters: str | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    """List data export jobs.

    Args:
        client: ChronicleClient instance
        filters: Filter string
        page_size: Page size
        page_token: Page token

    Returns:
        Dictionary containing data export list

    Raises:
        APIError: If the API request fails

    Example:
        ```python
        export = chronicle.list_data_export()
        ```
    """
    url = f"{_get_base_url(client)}/{client.instance_id}/dataExports"

    params = {
        "pageSize": page_size,
        "pageToken": page_token,
        "filter": filters,
    }

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to get data export: {response.text}")

    return response.json()
