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
"""Helper functions for Chronicle."""

from typing import Any

from secops.exceptions import APIError
from secops.chronicle.models import APIVersion


DEFAULT_PAGE_SIZE = 1000


def chronicle_paginated_request(
    client: "ChronicleClient",
    base_url: str,
    path: str,
    items_key: str,
    *,
    page_size: int | None = None,
    page_token: str | None = None,
    extra_params: dict[str, Any] | None = None,
) -> dict[str, list[Any]] | list[Any]:
    """Helper to get items from endpoints that use pagination.

    Args:
        client: ChronicleClient instance
        base_url: The base URL to use, example:
            - v1alpha (ChronicleClient.base_url)
            - v1 (ChronicleClient.base_v1_url)
        path: URL path after {base_url}/{instance_id}/
        items_key: JSON key holding the array of items (e.g., 'curatedRules')
        page_size: Maximum number of rules to return per page.
        page_token: Token for the next page of results, if available.
        extra_params: extra query params to include on every request

    Returns:
        Union[Dict[str, List[Any]], List[Any]]: List of items from the
        paginated collection. If the API returns a dictionary, it will
        return the dictionary. Otherwise, it will return the list of items.

    Raises:
        APIError: If the HTTP request fails.
    """
    url = f"{base_url}/{client.instance_id}/{path}"
    results = []
    next_token = page_token

    while True:
        # Build params each loop to prevent stale keys being
        # included in the next request
        params = {"pageSize": DEFAULT_PAGE_SIZE if not page_size else page_size}
        if next_token:
            params["pageToken"] = next_token
        if extra_params:
            # copy to avoid passed dict being mutated
            params.update(dict(extra_params))

        response = client.session.get(url, params=params)
        if response.status_code != 200:
            raise APIError(f"Failed to list {items_key}: {response.text}")

        data = response.json()
        results.extend(data.get(items_key, []))

        # If caller provided page_size, return only this page
        if page_size is not None:
            break

        # Otherwise, auto-paginate
        next_token = data.get("nextPageToken")
        if not next_token:
            break

    # Return a list if the API returns a list, otherwise return a dict
    if isinstance(data, list):
        return results
    response = {items_key: results}

    if data.get("nextPageToken"):
        response["nextPageToken"] = data.get("nextPageToken")

    return response


def chronicle_request(
    client: "ChronicleClient",
    method: str,
    endpoint_path: str,
    *,
    api_version: str = APIVersion.V1,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    expected_status: int = 200,
    error_message: str | None = None,
) -> dict[str, Any]:
    """Perform an HTTP request and return JSON, raising APIError on failure.

    Args:
        client: requests.Session (or compatible) instance
        method: HTTP method, e.g. 'GET', 'POST', 'PATCH'
        endpoint_path: URL path after {base_url}/{instance_id}/
        api_version: API version to use
        params: Optional query parameters
        json: Optional JSON body
        expected_status: Expected HTTP status code (default: 200)
        error_message: Optional base error message to include on failure

    Returns:
        Parsed JSON response.

    Raises:
        APIError: If the request fails, returns a non-JSON body, or status
                  code does not match expected_status.
    """
    url = f"{client.base_url(api_version)}/{client.instance_id}/{endpoint_path}"
    response = client.session.request(
        method=method, url=url, params=params, json=json
    )

    # Try to parse JSON even on error, so we can get more details
    try:
        data = response.json()
    except ValueError:
        data = None

    if response.status_code != expected_status:
        base_msg = error_message or "API request failed"
        if data is not None:
            raise APIError(
                f"{base_msg}: status={response.status_code}, response={data}"
            ) from None

        raise APIError(
            f"{base_msg}: status={response.status_code},"
            f" response_text={response.text}"
        ) from None

    if data is None:
        raise APIError(
            f"Expected JSON response from {url}"
            f" but got non-JSON body: {response.text}"
        )

    return data
