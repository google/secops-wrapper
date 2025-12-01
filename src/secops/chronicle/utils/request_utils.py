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

from typing import Dict, Any, Optional, List, Union
from secops.exceptions import APIError


def paginated_request(
    client,
    base_url: str,
    path: str,
    items_key: str,
    *,
    page_size: Optional[int] = None,
    page_token: Optional[str] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> Union[Dict[str, List[Any]], List[Any]]:
    """
    Helper to get items from endpoints that use pagination.

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
        params = {"pageSize": 1000 if not page_size else page_size}
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
    return {items_key: results}
