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

import platform
from importlib.metadata import version as _metadata_version
from typing import TYPE_CHECKING, Any, Optional

import requests
from google.auth.exceptions import GoogleAuthError

from secops.chronicle.models import APIVersion
from secops.exceptions import APIError

_LIBRARY_VERSION = _metadata_version("secops")

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


DEFAULT_PAGE_SIZE = 1000
MAX_BODY_CHARS = 2000


def _build_api_client_header(endpoint_path: str) -> str:
    """Build the x-goog-api-client header value for a request.

    Constructs a space-separated token string following the Google API client
    header convention. A leading ':' is stripped from RPC-style endpoint paths
    (e.g. ':udmSearch' becomes 'udmSearch').

    Args:
        endpoint_path: The API endpoint path passed to the request function,
            e.g. 'rules/rule123:copy' or ':udmSearch'.

    Returns:
        Header value string in the format:
        'gl-python/{version} rest/requests@{version} secops-wrapper/{version}
        api/{endpoint}'.
    """
    endpoint = endpoint_path.lstrip(":")
    return (
        f"gl-python/{platform.python_version()}"
        f" rest/requests@{requests.__version__}"
        f" secops-wrapper/{_LIBRARY_VERSION}"
        f" api/{endpoint}"
    )


def _safe_body_preview(text: str | None, limit: int = MAX_BODY_CHARS) -> str:
    """Generate a safe, truncated preview of body contents for error messages.

    Args:
        text: The text to preview
        limit: The maximum number of characters to include in the preview

    Returns:
        str: The preview of the text
    """
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return f"{text[:limit]}… (truncated, {len(text)} chars)"


# pylint: disable=line-too-long
def chronicle_paginated_request(
    client: "ChronicleClient",
    path: str,
    items_key: str,
    *,
    api_version: APIVersion | str | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
    extra_params: dict[str, Any] | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """Helper to get items from endpoints that use pagination.

    Function behavior:
      - If `page_size` OR `page_token` is provided: a single page is returned with the
        upstream JSON as-is, including all potential metadata.
        - If `as_list` is True, return only the list of items (drops metadata/tokens)
        - If `as_list` is False, return the upstream JSON as-is (dict or list)
      - Else: auto-paginate responses until all pages are consumed:
        - If `as_list` is True, return a list of items directly, without the
                 pagination metadata.
        - If `as_list` is False, return a dict shaped like the first response with aggregated items and no tokens.

    Notes:
      - as_list=True intentionally discards pagination metadata (e.g. nextPageToken).
        If callers need page tokens, they should use as_list=False in single-page mode.

    Args:
        client: ChronicleClient instance
        path: URL path after {base_url}/{instance_id}/
        items_key: JSON key holding the array of items (e.g. 'curatedRules')
        api_version: The API version to use, as a string. If not provided,
            uses the client's default_api_version. Options:
            - v1 (secops.chronicle.models.APIVersion.V1)
            - v1alpha (secops.chronicle.models.APIVersion.V1ALPHA)
            - v1beta (secops.chronicle.models.APIVersion.V1BETA)
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


# pylint: disable=line-too-long
def chronicle_request(
    client: "ChronicleClient",
    method: str,
    endpoint_path: str,
    *,
    api_version: APIVersion | str | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    expected_status: int | set[int] | tuple[int, ...] | list[int] = 200,
    error_message: str | None = None,
    timeout: int | None = None,
) -> dict[str, Any] | list[Any]:
    """Perform an HTTP request and return JSON, raising APIError on failure.

    Args:
        client: requests.Session (or compatible) instance
        method: HTTP method, e.g. 'GET', 'POST', 'PATCH'
        endpoint_path: URL path after {base_url}/{instance_id}/
        api_version: The API version to use, as a string. If not provided,
            uses the client's default_api_version. Options:
            - v1 (secops.chronicle.models.APIVersion.V1)
            - v1alpha (secops.chronicle.models.APIVersion.V1ALPHA)
            - v1beta (secops.chronicle.models.APIVersion.V1BETA)
        params: Optional query parameters
        headers: Optional headers
        json: Optional JSON body
        expected_status: Expected HTTP status code(s). May be a single int
            (e.g. 200) or an iterable of acceptable status codes (e.g. {200, 204}).
            If the response status is not acceptable, an APIError is raised.
        error_message: Optional base error message to include on failure
        timeout: Optional timeout in seconds for the request

    Returns:
        Parsed JSON response.

    Raises:
        APIError: If the request fails, returns a non-JSON body, or status
                  code is not in expected_status.
    """
    # Build URL based on endpoint type:
    # - RPC-style methods e.g: ":validateQuery" -> .../{instance_id}:validateQuery
    # - Legacy paths e.g: "legacy:..." -> .../{instance_id}/legacy:...
    # - normal paths e.g: "curatedRules/..." -> .../{instance_id}/curatedRules/...
    if api_version:
        base = f"{client.base_url(api_version)}/{client.instance_id}"
    else:
        base = f"{client.base_url}/{client.instance_id}"

    if endpoint_path.startswith(":"):
        url = f"{base}{endpoint_path}"
    else:
        url = f'{base}/{endpoint_path.lstrip("/")}'

    # Merge x-goog-api-client with any caller-supplied headers.
    # Caller-supplied values take precedence.
    merged_headers = {"x-goog-api-client": _build_api_client_header(endpoint_path)}
    if headers:
        merged_headers.update(headers)

    # init request response
    response = None

    try:
        response = client.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=merged_headers,
            timeout=timeout,
        )
    except GoogleAuthError as exc:
        base_msg = error_message or "Google authentication failed"
        raise APIError(f"{base_msg}: authentication_error={exc}") from exc
    except requests.RequestException as exc:
        base_msg = error_message or "API request failed"
        raise APIError(
            f"{base_msg}: method={method}, url={url}, "
            f"request_error={exc.__class__.__name__}, detail={exc}, "
            f"status_code={exc.response.status_code if exc.response else None},"
            f"response_message={exc.response.text if exc.response else None}"
        ) from exc

    # Try to parse JSON even on error, so we can get more details
    try:
        data = response.json()
    except ValueError:
        data = None

    # Determine whether the status code is acceptable
    if isinstance(expected_status, (set, tuple, list)):
        status_ok = response.status_code in expected_status
    else:
        status_ok = response.status_code == expected_status

    if not status_ok:
        base_msg = error_message or "API request failed"
        if data is not None:
            raise APIError(
                f"{base_msg}: method={method}, url={url}, "
                f"status={response.status_code}, response={data}"
            ) from None

        preview = _safe_body_preview(
            getattr(response, "text", ""), limit=MAX_BODY_CHARS
        )

        raise APIError(
            f"{base_msg}: method={method}, url={url}, status={response.status_code}, "
            f"response_text={preview}"
        ) from None

    if data is None:
        content_type = response.headers.get("Content-Type", "unknown")
        preview = _safe_body_preview(
            getattr(response, "text", ""), limit=MAX_BODY_CHARS
        )

        raise APIError(
            f"Expected JSON response: method={method}, url={url}, status={response.status_code}, "
            f"content_type={content_type}, body_preview={preview}"
        )

    return data


def chronicle_request_bytes(
    client: "ChronicleClient",
    method: str,
    endpoint_path: str,
    *,
    api_version: str = APIVersion.V1,
    params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, Any]] = None,
    expected_status: int | set[int] | tuple[int, ...] | list[int] = 200,
    error_message: str | None = None,
    timeout: int | None = None,
) -> bytes:
    """Perform an HTTP request and return the raw response bytes.

    Use this helper for endpoints that return binary content such as ZIP
    files or other non-JSON payloads. The response is streamed to avoid
    loading large payloads into memory unnecessarily.

    Args:
        client: ChronicleClient instance.
        method: HTTP method, e.g. 'GET', 'POST'.
        endpoint_path: URL path after {base_url}/{instance_id}/. RPC-style
            methods starting with ':' are appended directly to the instance
            URL without a path separator.
        api_version: The API version to use. Default is V1.
        params: Optional query parameters.
        headers: Optional request headers.
        expected_status: Expected HTTP status code(s). May be a single int
            or an iterable of acceptable status codes. Raises APIError if
            the response status is not acceptable.
        error_message: Optional base error message to include on failure.
        timeout: Optional timeout in seconds for the request.

    Returns:
        Raw response bytes.

    Raises:
        APIError: If the request fails, the status code is not in
            expected_status, or a network or authentication error occurs.
    """

    base = f"{client.base_url(api_version)}/{client.instance_id}"

    if endpoint_path.startswith(":"):
        url = f"{base}{endpoint_path}"
    else:
        url = f'{base}/{endpoint_path.lstrip("/")}'

    merged_headers = {"x-goog-api-client": _build_api_client_header(endpoint_path)}
    if headers:
        merged_headers.update(headers)

    try:
        response = client.session.request(
            method=method,
            url=url,
            params=params,
            headers=merged_headers,
            timeout=timeout,
            stream=True,
        )
    except GoogleAuthError as exc:
        base_msg = error_message or "Google authentication failed"
        raise APIError(f"{base_msg}: authentication_error={exc}") from exc
    except requests.RequestException as exc:
        base_msg = error_message or "API request failed"
        raise APIError(
            f"{base_msg}: method={method}, url={url}, "
            f"request_error={exc.__class__.__name__}, detail={exc}"
        ) from exc

    if isinstance(expected_status, (set, tuple, list)):
        status_ok = response.status_code in expected_status
    else:
        status_ok = response.status_code == expected_status

    if not status_ok:
        # try json for detail, else preview text
        try:
            data = response.json()
            raise APIError(
                f"{error_message or 'API request failed'}: method={method}, url={url}, "
                f"status={response.status_code}, response={data}"
            ) from None
        except ValueError:
            preview = _safe_body_preview(
                getattr(response, "text", ""), limit=MAX_BODY_CHARS
            )
            raise APIError(
                f"{error_message or 'API request failed'}: method={method}, url={url}, "
                f"status={response.status_code}, response_text={preview}"
            ) from None

    return response.content
