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
from typing import Any

from secops.exceptions import APIError
from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import chronicle_request


def fetch_udm_search_csv(
    client,
    query: str,
    start_time: datetime,
    end_time: datetime,
    fields: list[str],
    case_insensitive: bool = True,
) -> dict[str, Any]:
    """Fetch UDM search results in CSV format.

    Args:
        client: ChronicleClient instance
        query: Chronicle search query
        start_time: Search start time
        end_time: Search end time
        fields: List of fields to include in results
        case_insensitive: Whether to perform case-insensitive search

    Returns:
        CSV formatted string of results

    Raises:
        APIError: If the API request fails
    """
    search_query = {
        "baselineQuery": query,
        "baselineTimeRange": {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
        "fields": {"fields": fields},
        "caseInsensitive": case_insensitive,
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="legacy:legacyFetchUdmSearchCsv",
        api_version=APIVersion.V1ALPHA,
        json=search_query,
        headers={"Accept": "*/*"},
    )


def find_udm_field_values(
    client, query: str, page_size: int | None = None
) -> dict[str, Any]:
    """Fetch UDM field values that match a query.

    Args:
        client: ChronicleClient instance
        query: The partial UDM field value to match
        page_size: The maximum number of value matches to return

    Returns:
        Dictionary containing field values that match the query

    Raises:
        APIError: If the API request fails
    """
    params = {"query": query}
    if page_size is not None:
        params["pageSize"] = page_size

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=":findUdmFieldValues",
        api_version=APIVersion.V1ALPHA,
        params=params,
    )


def fetch_udm_search_view(
    client,
    query: str,
    start_time: datetime,
    end_time: datetime,
    snapshot_query: str | None = 'feedback_summary.status != "CLOSED"',
    max_events: int | None = 10000,
    max_detections: int | None = 1000,
    case_insensitive: bool = True,
) -> list[dict[str, Any]]:
    """Fetch UDM search result view.

    Args:
        client: The ChronicleClient instance.
        query: Chronicle search query to search for. The baseline
            query is used for this request and its results are cached for
            subsequent requests, so supplying additional filters in the
            snapshot_query will not require re-running the baseline query.
        start_time: Search start time.
        end_time: Search end time.
        snapshot_query: Query for filtering alerts. Uses a syntax similar to UDM
            search, with supported fields including: detection.rule_set,
            detection.rule_id, detection.rule_name, case_name,
            feedback_summary.status, feedback_summary.priority, etc.
        max_events: Maximum number of events to return. If not specified, a
            default of 10000 events will be returned.
        max_detections: Maximum number of detections to return. If not
            specified, a default of 1000 detections will be returned.
        case_insensitive: Whether to perform case-insensitive search or not.

    Returns:
        List of udm search results.

    Raises:
        APIError: If the API request fails
    """
    search_query = {
        "baselineQuery": query,
        "baselineTimeRange": {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        },
        "caseInsensitive": case_insensitive,
    }

    if snapshot_query:
        search_query["detectionOptions"] = {"snapshotQuery": snapshot_query}

    if max_detections:
        search_query["detectionOptions"] = {
            "detectionList": {
                "maxReturnedDetections": max_detections,
            }
        }

    if max_events:
        search_query["eventList"] = {
            "maxReturnedEvents": max_events,
        }

    json_resp = chronicle_request(
        client,
        method="POST",
        endpoint_path="legacy:legacyFetchUdmSearchView",
        api_version=APIVersion.V1ALPHA,
        json=search_query,
        headers={"Accept": "*/*"},
    )

    final_resp: list[dict[str, Any]] = []
    complete = False

    for resp in json_resp:
        if not resp.get("complete") and not resp.get("error"):
            continue

        if resp.get("error"):
            raise APIError(
                f'Chronicle API request failed: {resp.get("error", "")}'
            )

        final_resp.append(resp)
        complete = True

    if not complete:
        final_resp = json_resp

    return final_resp
