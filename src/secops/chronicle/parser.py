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
"""Parser management functionality for Chronicle."""

import base64
from typing import Any

from secops.exceptions import APIError

# Constants for size limits
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB per log
MAX_LOGS = 1000  # Maximum number of logs to process
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total


def activate_parser(
    client: "ChronicleClient",
    log_type: str,
    id: str,  # pylint: disable=redefined-builtin
) -> dict[str, Any]:
    """Activate a custom parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}/parsers/{id}:activate"
    )
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to activate parser: {response.text}")

    return response.json()


def activate_release_candidate_parser(
    client: "ChronicleClient",
    log_type: str,
    id: str,  # pylint: disable=redefined-builtin
) -> dict[str, Any]:
    """Activate the release candidate parser making it live for that customer.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}/parsers/{id}:activateReleaseCandidateParser"
    )
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to activate parser: {response.text}")

    return response.json()


def copy_parser(
    client: "ChronicleClient",
    log_type: str,
    id: str,  # pylint: disable=redefined-builtin
) -> dict[str, Any]:
    """Makes a copy of a prebuilt parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Newly copied Parser

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}/parsers/{id}:copy"
    )
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to copy parser: {response.text}")

    return response.json()


def create_parser(
    client: "ChronicleClient",
    log_type: str,
    parser_code: str,
    validated_on_empty_logs: bool = True,
) -> dict[str, Any]:
    """Creates a new parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        parser_code: Content of the new parser, used to evaluate logs.
        validated_on_empty_logs: Whether the parser is validated on empty logs.

    Returns:
        Dictionary containing the created parser information

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/logTypes/{log_type}/parsers"

    body = {
        "cbn": base64.b64encode(parser_code.encode("utf-8")).decode("utf-8"),
        "validated_on_empty_logs": validated_on_empty_logs,
    }

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to create parser: {response.text}")

    return response.json()


def deactivate_parser(
    client: "ChronicleClient",
    log_type: str,
    id: str,  # pylint: disable=redefined-builtin
) -> dict[str, Any]:
    """Deactivate a custom parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}/parsers/{id}:deactivate"
    )
    body = {}
    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to deactivate parser: {response.text}")

    return response.json()


def delete_parser(
    client: "ChronicleClient",
    log_type: str,
    id: str,  # pylint: disable=redefined-builtin
    force: bool = False,
) -> dict[str, Any]:
    """Delete a parser.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID
        force: Flag to forcibly delete an ACTIVE parser.

    Returns:
        Empty JSON object

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}/parsers/{id}"
    )
    params = {"force": force}
    response = client.session.delete(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to delete parser: {response.text}")

    return response.json()


def get_parser(
    client: "ChronicleClient",
    log_type: str,
    id: str,  # pylint: disable=redefined-builtin
) -> dict[str, Any]:
    """Get a Parser by ID.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser
        id: Parser ID

    Returns:
        SecOps Parser

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}/parsers/{id}"
    )
    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get parser: {response.text}")

    return response.json()


def list_parsers(
    client: "ChronicleClient",
    log_type: str = "-",
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str = None,  # pylint: disable=redefined-builtin
) -> list[Any] | dict[str, Any]:
    """List parsers.

    Args:
        client: ChronicleClient instance
        log_type: Log type to filter by
        page_size: The maximum number of parsers to return per page.
            If provided, returns raw API response with pagination info.
            If None (default), auto-paginates and returns all parsers.
        page_token: A page token, received from a previous ListParsers call.
        filter: Optional filter expression

    Returns:
        If page_size is None: List of all parsers.
        If page_size is provided: List of parsers with next page token if
            available.

    Raises:
        APIError: If the API request fails
    """
    more = True
    parsers = []

    while more:
        url = (
            f"{client.base_url}/{client.instance_id}"
            f"/logTypes/{log_type}/parsers"
        )

        params = {}

        if page_size:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token
        if filter:
            params["filter"] = filter

        response = client.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Failed to list parsers: {response.text}")

        data = response.json()

        if page_size is not None:
            return data

        if "parsers" in data:
            parsers.extend(data["parsers"])

        if "nextPageToken" in data:
            page_token = data["nextPageToken"]
        else:
            more = False

    return parsers


def run_parser(
    client: "ChronicleClient",
    log_type: str,
    parser_code: str,
    parser_extension_code: str | None,
    logs: list[str],
    statedump_allowed: bool = False,
) -> dict[str, Any]:
    """Run parser against sample logs.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser (e.g., "WINDOWS_AD", "OKTA")
        parser_code: Content of the parser code to evaluate logs
        parser_extension_code: Optional content of the parser extension
        logs: List of log strings to test parser against
        statedump_allowed: Whether statedump filter is enabled for the config

    Returns:
        Dictionary containing the parser evaluation results with structure:
        {
            "runParserResults": [
                {
                    "parsedEvents": [...],
                    "errors": [...]
                }
            ]
        }

    Raises:
        ValueError: If input parameters are invalid
        APIError: If the API request fails or returns an error
    """
    # Input validation
    if not log_type:
        raise ValueError("log_type cannot be empty")

    if not parser_code:
        raise ValueError("parser_code cannot be empty")

    if not isinstance(logs, list):
        raise TypeError(f"logs must be a list, got {type(logs).__name__}")

    if not logs:
        raise ValueError("At least one log must be provided")

    # Validate log entries
    total_size = 0
    for i, log in enumerate(logs):
        if not isinstance(log, str):
            raise TypeError(
                f"All logs must be strings, but log at index {i} is "
                f"{type(log).__name__}"
            )

        log_size = len(log.encode("utf-8"))
        if log_size > MAX_LOG_SIZE:
            raise ValueError(
                f"Log at index {i} exceeds maximum size of {MAX_LOG_SIZE} bytes"
                f" (actual size: {log_size} bytes)"
            )
        total_size += log_size

    # Check total size
    if total_size > MAX_TOTAL_SIZE:
        raise ValueError(
            f"Total size of all logs ({total_size} bytes) exceeds maximum of "
            f"{MAX_TOTAL_SIZE} bytes"
        )

    # Check number of logs
    if len(logs) > MAX_LOGS:
        raise ValueError(
            f"Number of logs ({len(logs)}) exceeds maximum of {MAX_LOGS}"
        )

    # Validate parser_extension_code type if provided
    if parser_extension_code is not None and not isinstance(
        parser_extension_code, str
    ):
        raise TypeError(
            "parser_extension_code must be a string or None, got "
            f"{type(parser_extension_code).__name__}"
        )

    # Build request
    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/logTypes/{log_type}:runParser"
    )

    parser = {
        "cbn": base64.b64encode(parser_code.encode("utf-8")).decode("utf-8")
    }

    parser_extension = None
    if parser_extension_code:
        parser_extension = {
            "cbn_snippet": base64.b64encode(
                parser_extension_code.encode("utf-8")
            ).decode("utf-8")
        }

    body = {
        "parser": parser,
        "parser_extension": parser_extension,
        "log": [
            base64.b64encode(log.encode("utf-8")).decode("utf-8")
            for log in logs
        ],
        "statedump_allowed": statedump_allowed,
    }

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        # Provide detailed error messages based on status code
        error_detail = f"Failed to evaluate parser for log type '{log_type}'"

        if response.status_code == 400:
            error_detail += f" - Bad request: {response.text}"
            if "Invalid log type" in response.text:
                error_detail += f". Log type '{log_type}' may not be valid."
            elif "Invalid parser" in response.text:
                error_detail += ". Parser code may contain syntax errors."
        elif response.status_code == 404:
            error_detail += f" - Log type '{log_type}' not found"
        elif response.status_code == 413:
            error_detail += (
                " - Request too large. Try reducing the number or size of logs."
            )
        elif response.status_code == 500:
            error_detail += f" - Internal server error: {response.text}"
        else:
            error_detail += f" - HTTP {response.status_code}: {response.text}"

        raise APIError(error_detail)

    return response.json()
