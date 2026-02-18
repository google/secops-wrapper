# Copyright 2026 Google LLC
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
"""Raw log search functionality for Chronicle."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import chronicle_request

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def search_raw_logs(
    client: "ChronicleClient",
    query: str,
    start_time: datetime,
    end_time: datetime,
    snapshot_query: str | None = None,
    case_sensitive: bool = False,
    log_types: list[str] | None = None,
    max_aggregations_per_field: int | None = None,
    page_size: int | None = None,
    allow_partial_results: bool = False,
) -> dict[str, Any]:
    """Search for raw logs in Chronicle.

    Args:
        client: The ChronicleClient instance.
        query: Query to search for raw logs.
        start_time: Search start time (inclusive).
        end_time: Search end time (exclusive).
        snapshot_query: Optional. Query to filter results.
        case_sensitive: Optional. Whether search is case-sensitive.
        log_types: Optional. Limit results to specific log types (e.g. ["OKTA"]).
        max_aggregations_per_field: Optional. Max values for a UDM field.
        page_size: Optional. Maximum number of results to return.
        allow_partial_results: Optional. Whether to allow partial results.

    Returns:
        Dictionary containing search results.

    Raises:
        APIError: If the API request fails.
    """
    search_query: dict[str, Any] = {
        "baselineQuery": query,
        "baselineTimeRange": {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
        "caseSensitive": case_sensitive,
    }

    if snapshot_query:
        search_query["snapshotQuery"] = snapshot_query

    if log_types:
        # The API expects a list of LogType objects, filtering by displayName
        search_query["logTypes"] = [{"displayName": lt} for lt in log_types]

    if max_aggregations_per_field is not None:
        search_query["maxAggregationsPerField"] = max_aggregations_per_field

    if page_size is not None:
        search_query["pageSize"] = page_size

    if allow_partial_results:
        search_query["allowPartialResults"] = allow_partial_results

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=":searchRawLogs",
        api_version=APIVersion.V1ALPHA,
        json=search_query,
    )
