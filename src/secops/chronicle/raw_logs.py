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
"""Raw logs search functionality for Chronicle."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from secops.exceptions import APIError


def find_raw_logs(
    client,
    start_time: datetime,
    end_time: datetime,
    log_source: Optional[str] = None,
    log_type: Optional[str] = None,
    query: Optional[str] = None,
    page_size: int = 100,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Find raw logs in Chronicle.

    Args:
        client: ChronicleClient instance
        start_time: Search start time
        end_time: Search end time
        log_source: Filter by log source (optional)
        log_type: Filter by log type (optional)
        query: Raw log search query (optional)
        page_size: Number of results per page
        page_token: Token for pagination

    Returns:
        Dict containing raw logs and pagination info

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/legacy:legacyFindRawLogs"

    # Ensure times are timezone-aware
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    request_body = {
        "timeRange": {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
        "pageSize": page_size,
    }

    if log_source:
        request_body["logSource"] = log_source

    if log_type:
        request_body["logType"] = log_type

    if query:
        request_body["query"] = query

    if page_token:
        request_body["pageToken"] = page_token

    response = client.session.post(url, json=request_body)

    if response.status_code != 200:
        raise APIError(f"Chronicle API request failed: {response.text}")

    return response.json()
