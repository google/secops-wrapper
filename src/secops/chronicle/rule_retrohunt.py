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
"""Retrohunt functionality for Chronicle rules."""

from datetime import datetime
from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_request,
    chronicle_paginated_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def create_retrohunt(
    client: "ChronicleClient",
    rule_id: str,
    start_time: datetime,
    end_time: datetime,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Creates a retrohunt for a rule.

    A retrohunt applies a rule to historical data within the specified
    time range.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule to run retrohunt for ("ru_<UUID>")
        start_time: Start time for retrohunt analysis
        end_time: End time for retrohunt analysis
        api_version: Preferred API version to use. Defaults to V1

    Returns:
        Dictionary containing operation information for the retrohunt

    Raises:
        APIError: If the API request fails
    """
    body = {
        "process_interval": {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"rules/{rule_id}/retrohunts",
        json=body,
        api_version=api_version,
    )


def get_retrohunt(
    client,
    rule_id: str,
    operation_id: str,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Get retrohunt status and results.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule the retrohunt is for ("ru_<UUID>" or
          "ru_<UUID>@v_<seconds>_<nanoseconds>")
        operation_id: Operation ID of the retrohunt
        api_version: Preferred API version to use. Defaults to V1

    Returns:
        Dictionary containing retrohunt information

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"rules/{rule_id}/retrohunts/{operation_id}",
        api_version=api_version,
    )


def list_retrohunts(
    client: "ChronicleClient",
    rule_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    api_version: APIVersion | None = APIVersion.V1,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of retrohunts for a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the rule to list retrohunts for
        page_size: Page size to use for paginated results
        page_token: Page token to use for paginated results
        api_version: Preferred API version to use. Defaults to V1
        as_list: Whether to return results as a list or dictionary

    Returns:
        If as_list is True: List of retrohunts.
        If as_list is False: Dict with retrohunts list and nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path=f"rules/{rule_id}/retrohunts",
        items_key="retrohunts",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )
