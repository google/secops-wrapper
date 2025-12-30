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

# def chronicle_paginated_request(
#     client: "ChronicleClient",
#     api_version: str,
#     path: str,
#     items_key: str,
#     *,
#     page_size: int | None = None,
#     page_token: str | None = None,
#     extra_params: dict[str, Any] | None = None,
#     list_only: bool = False,
# ) -> dict[str, Any] | list[Any]:
#     """Helper to get items from endpoints that use pagination.
#
#     Function behaviour:
#       - If `page_size` OR `page_token` is provided: single page is returned.
#         - list_only=False: return upstream JSON as-is (dict or list)
#         - list_only=True: return only the list of items (drops metadata/tokens)
#       - Else: auto-paginate until all pages are consumed.
#         - list_only=False: return dict shaped like first response with aggregated items and no token
#         - list_only=True: return aggregated flat list (drops metadata/tokens)
#
#     Notes:
#       - list_only=True intentionally discards pagination metadata (e.g. nextPageToken).
#         If callers need page tokens, they should use list_only=False in single-page mode.
#     """
#     single_page_mode = (page_size is not None) or (page_token is not None)
#     effective_page_size = DEFAULT_PAGE_SIZE if page_size is None else page_size
#
#     aggregated_results: list[Any] = []
#     first_response_dict: dict[str, Any] | None = None
#     next_token = page_token
#
#     while True:
#         params: dict[str, Any] = {"pageSize": effective_page_size}
#         if next_token:
#             params["pageToken"] = next_token
#         if extra_params:
#             params.update(dict(extra_params))
#
#         data = chronicle_request(
#             client=client,
#             method="GET",
#             api_version=api_version,
#             endpoint_path=path,
#             params=params,
#         )
#
#         # --- Single-page mode: return immediately ---
#         if single_page_mode:
#             if not list_only:
#                 return data
#
#             # list_only=True: extract list from dict responses, or pass through lists
#             if isinstance(data, list):
#                 return data
#             if isinstance(data, dict):
#                 page_results = data.get(items_key, [])
#                 if page_results and not isinstance(page_results, list):
#                     raise APIError(
#                         f"Expected '{items_key}' to be a list for {path}, got {type(page_results).__name__}"
#                     )
#                 return page_results
#             raise APIError(f"Unexpected response type for {path}: {type(data).__name__}")
#
#         # --- Auto-pagination mode ---
#         if isinstance(data, list):
#             # Top-level list responses can't expose nextPageToken; return as-is
#             return data
#
#         if not isinstance(data, dict):
#             raise APIError(f"Unexpected response type for {path}: {type(data).__name__}")
#
#         if first_response_dict is None:
#             first_response_dict = data
#
#         page_results = data.get(items_key, [])
#         if page_results:
#             if not isinstance(page_results, list):
#                 raise APIError(
#                     f"Expected '{items_key}' to be a list for {path}, got {type(page_results).__name__}"
#                 )
#             aggregated_results.extend(page_results)
#
#         next_token = data.get("nextPageToken")
#         if not next_token:
#             break
#
#     # If list_only=True, return just the aggregated list.
#     if list_only:
#         return aggregated_results
#
#     # No dict pages? Return minimal dict.
#     if first_response_dict is None:
#         return {items_key: aggregated_results}
#
#     output = dict(first_response_dict)
#     output[items_key] = aggregated_results
#     output.pop("nextPageToken", None)
#     return output
#
#
# def chronicle_request(
#     client: "ChronicleClient",
#     method: str,
#     endpoint_path: str,
#     *,
#     api_version: str = APIVersion.V1,
#     params: dict[str, Any] | None = None,
#     json: dict[str, Any] | None = None,
#     expected_status: int = 200,
#     error_message: str | None = None,
# ) -> dict[str, Any]:
#     # (unchanged)
#     url = f"{client.base_url(api_version)}/{client.instance_id}/{endpoint_path}"
#     response = client.session.request(method=method, url=url, params=params, json=json)
#
#     try:
#         data = response.json()
#     except ValueError:
#         data = None
#
#     if response.status_code != expected_status:
#         base_msg = error_message or "API request failed"
#         if data is not None:
#             raise APIError(f"{base_msg}: status={response.status_code}, response={data}") from None
#
#         raise APIError(
#             f"{base_msg}: status={response.status_code}, response_text={response.text}"
#         ) from None
#
#     if data is None:
#         raise APIError(
#             f"Expected JSON response from {url} but got non-JSON body: {response.text}"
#         )
#
#     return data


def chronicle_paginated_request(
    client: "ChronicleClient",
    api_version: str,
    path: str,
    items_key: str,
    *,
    page_size: int | None = None,
    page_token: str | None = None,
    extra_params: dict[str, Any] | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """Helper to get items from endpoints that use pagination.

    Function behaviour:
      - If `page_size` OR `page_token` is provided: a single page is returned with the
        upstream JSON as-is, including all potential metadata.
        - If `as_list` is True, return only the list of items (drops metadata/tokens)
        - If `as_list` is False, return the upstream JSON as-is (dict or list)
      - Else: auto-paginate responses until all pages are consumed:
        - If `as_list` is True, return a list of items directly, without the
                 pagination metadata.
        - If `as_list` is False, return a dict shaped like the first response with aggregated items and no tokens or metadata.

    Notes:
      - as_list=True intentionally discards pagination metadata (e.g. nextPageToken).
        If callers need page tokens, they should use list_only=False in single-page mode.

    Args:
        client: ChronicleClient instance
        api_version: The API version to use, as a string. options:
            - v1 (secops.chronicle.models.APIVersion.V1)
            - v1alpha (secops.chronicle.models.APIVersion.V1ALPHA)
            - v1beta (secops.chronicle.models.APIVersion.V1BETA)
        path: URL path after {base_url}/{instance_id}/
        items_key: JSON key holding the array of items (e.g. 'curatedRules')
        page_size: Maximum number of rules to return per page.
        page_token: Token for the next page of results, if available.
        extra_params: extra query params to include on every request
        as_list: If True, return a list of items directly, without the
                 pagination metadata in a dict.

    Returns:
        Union[Dict[str, List[Any]], List[Any]]: List of items from the
        paginated collection. If the API returns a dictionary, it will
        return the dictionary. Otherwise, it will return the list of items.

    Raises:
        APIError: If the HTTP request fails.
    """
    # Determine if we should return a single page or aggregate results from all pages
    single_page_mode = (page_size is not None) or (page_token is not None)

    effective_page_size = DEFAULT_PAGE_SIZE if page_size is None else page_size

    aggregated_results = []
    first_response_dict = None
    next_token = page_token

    while True:
        # Build params each loop to prevent stale keys being
        # included in the next request
        params = {"pageSize": effective_page_size}
        if next_token:
            params["pageToken"] = next_token
        if extra_params:
            # copy to avoid passed dict being mutated
            params.update(dict(extra_params))

        data = chronicle_request(
            client=client,
            method="GET",
            api_version=api_version,
            endpoint_path=path,
            params=params,
        )

        print(as_list)

        # If single page mode return immediately
        if single_page_mode:
            # Return the upstream JSON as-is if not as_list
            if not as_list:
                return data

            # Return a list if the API returns a list
            if isinstance(data, list):
                return data

            # Return a list of items if the API returns a dict
            if isinstance(data, dict):
                page_results = data.get(items_key, [])
                if page_results and not isinstance(page_results, list):
                    raise APIError(
                        f"Expected '{items_key}' to be a list for {path}, got {type(page_results).__name__}"
                    )
                return page_results
            raise APIError(
                f"Unexpected response type for {path}: {type(data).__name__}"
            )

        if isinstance(data, list):
            # Top-level list responses can't expose nextPageToken; return as-is
            return data

        if not isinstance(data, dict):
            raise APIError(
                f"Unexpected response type for {path}: {type(data).__name__}"
            )

        if first_response_dict is None:
            first_response_dict = data

        page_results = data.get(items_key, [])
        if page_results:
            if not isinstance(page_results, list):
                raise APIError(
                    f"Expected '{items_key}' to be a list for {path}, got {type(page_results).__name__}"
                )
            aggregated_results.extend(page_results)

        next_token = data.get("nextPageToken")
        if not next_token:
            break

    # Return the aggregated list if as_list is True
    if as_list:
        return aggregated_results

    # Return a dict with the item key and an empty list if no results were returned
    if first_response_dict is None:
        return {items_key: aggregated_results}

    output = dict(first_response_dict)
    # Build a dict object with the aggregated results using the key
    output[items_key] = aggregated_results
    # Remove nextPageToken from the response
    output.pop("nextPageToken", None)
    return output


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
        api_version: The API version to use, as a string. options:
            - v1 (secops.chronicle.models.APIVersion.V1)
            - v1alpha (secops.chronicle.models.APIVersion.V1ALPHA)
            - v1beta (secops.chronicle.models.APIVersion.V1BETA)
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
