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
import json
import logging
from typing import Any

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.format_utils import remove_none_values
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)
from secops.exceptions import APIError, SecOpsError

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
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"logTypes/{log_type}/parsers/{id}:activate",
        json={},
        error_message="Failed to activate parser",
    )


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
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"logTypes/{log_type}/parsers/{id}"
            ":activateReleaseCandidateParser"
        ),
        json={},
        error_message="Failed to activate parser",
    )


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
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"logTypes/{log_type}/parsers/{id}:copy",
        json={},
        error_message="Failed to copy parser",
    )


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
    body = {
        "cbn": base64.b64encode(parser_code.encode("utf-8")).decode("utf-8"),
        "validated_on_empty_logs": validated_on_empty_logs,
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"logTypes/{log_type}/parsers",
        json=body,
        error_message="Failed to create parser",
    )


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
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"logTypes/{log_type}/parsers/{id}:deactivate",
        json={},
        error_message="Failed to deactivate parser",
    )


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
    params = {"force": force}

    return chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"logTypes/{log_type}/parsers/{id}",
        params=params,
        error_message="Failed to delete parser",
    )


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
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"logTypes/{log_type}/parsers/{id}",
        error_message="Failed to get parser",
    )


def list_parsers(
    client: "ChronicleClient",
    log_type: str = "-",
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str = None,  # pylint: disable=redefined-builtin
    as_list: bool = True,
) -> dict[str, Any] | list[Any]:
    """List parsers.

    Args:
        client: ChronicleClient instance
        log_type: Log type to filter by
        page_size: The maximum number of parsers to return per page.
            If provided, returns raw API response with pagination info.
            If None (default), auto-paginates and returns all parsers.
        page_token: A page token, received from a previous ListParsers call.
        filter: Optional filter expression
        as_list: If True, return only the list of parsers.
            If False, return dict with metadata and pagination tokens.
            Defaults to True. When page_size is None, this is automatically
            set to True for backward compatibility.

    Returns:
        If as_list is True: List of parsers.
        If as_list is False: Dict with parsers list and pagination metadata.

    Raises:
        APIError: If the API request fails
    """
    extra_params = remove_none_values(
        {
            "filter": filter,
        }
    )

    # For backward compatibility: if page_size is None, force as_list to True
    effective_as_list = True if page_size is None else as_list

    return chronicle_paginated_request(
        client,
        path=f"logTypes/{log_type}/parsers",
        items_key="parsers",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params if extra_params else None,
        as_list=effective_as_list,
    )


def run_parser(
    client: "ChronicleClient",
    log_type: str,
    parser_code: str,
    parser_extension_code: str | None,
    logs: list[str],
    statedump_allowed: bool = False,
    parse_statedump: bool = False,
) -> dict[str, Any]:
    """Run parser against sample logs.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser (e.g., "WINDOWS_AD", "OKTA")
        parser_code: Content of the parser code to evaluate logs
        parser_extension_code: Optional content of the parser extension
        logs: List of log strings to test parser against
        statedump_allowed: Whether statedump filter is enabled for the config
        parse_statedump: Whether to parse statedump results into structured
            format.

    Returns:
        Dictionary containing the parser evaluation results with structure:
        {
            "runParserResults": [
                {
                    "parsedEvents": [...],
                    "errors": [...],
                    "statedumpResults": [...] (if statedump_allowed=True)
                }
            ]
        }
        If parse_statedump is True, statedumpResult strings are converted
        to structured objects.

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

    result = chronicle_request(
        client,
        method="POST",
        endpoint_path=f"logTypes/{log_type}:runParser",
        json=body,
        error_message=f"Failed to evaluate parser for log type '{log_type}'",
    )

    if parse_statedump and "runParserResults" in result:
        for run_result in result["runParserResults"]:
            if "statedumpResults" in run_result:
                for statedump_item in run_result["statedumpResults"]:
                    if "statedumpResult" in statedump_item:
                        try:
                            dump_str = statedump_item["statedumpResult"]
                            if isinstance(dump_str, str):
                                stripped = dump_str.strip()
                                if ":" in stripped:
                                    parts = stripped.split("\n", 1)
                                    info_line = parts[0].strip()
                                    if "Internal State" in info_line:
                                        info = info_line
                                        if len(parts) > 1:
                                            state_json = parts[1].strip()
                                            state = json.loads(state_json)
                                        else:
                                            state = {}
                                        statedump_item["statedumpResult"] = {
                                            "info": info,
                                            "state": state,
                                        }
                        except (
                            ValueError,
                            json.JSONDecodeError,
                        ) as e:
                            print(f"Warning: Failed to parse statedump: {e}")

    return result


def trigger_github_checks(
    client: "ChronicleClient",
    associated_pr: str,
    log_type: str,
    timeout: int = 60,
) -> dict[str, Any]:
    """Trigger GitHub checks for a parser.

    Args:
        client: ChronicleClient instance
        associated_pr: The PR string (e.g., "owner/repo/pull/123").
        log_type: The string name of the LogType enum.
        timeout: Optional request timeout in seconds (default: 60).

    Returns:
        Dictionary containing the response details.

    Raises:
        SecOpsError: If input is invalid.
        APIError: If the API request fails.
    """

    if not isinstance(log_type, str) or len(log_type.strip()) < 2:
        raise SecOpsError("log_type must be a valid string of length >= 2")

    if not isinstance(associated_pr, str) or not associated_pr.strip():
        raise SecOpsError("associated_pr must be a non-empty string")

    pr_parts = associated_pr.split("/")
    if len(pr_parts) != 4 or pr_parts[2] != "pull" or not pr_parts[3].isdigit():
        raise SecOpsError(
            "associated_pr must be in the format 'owner/repo/pull/<number>'"
        )
    if not isinstance(timeout, int) or timeout < 0:
        raise SecOpsError("timeout must be a non-negative integer")

    try:
        parsers = list_parsers(client, log_type=log_type)
    except APIError as e:
        raise APIError(
            f"Failed to fetch parsers for log type {log_type}: {e}"
        ) from e

    if not parsers:
        logging.info(
            "No parsers found for log type %s. Using fallback parser ID.",
            log_type,
        )
        parser_name = f"logTypes/{log_type}/parsers/-"
    else:
        if len(parsers) > 1:
            logging.warning(
                "Multiple parsers found for log type %s. Using the first one.",
                log_type,
            )
        parser_name = parsers[0]["name"]

    endpoint_path = f"{parser_name}:runAnalysis"
    payload = {
        "report_type": "GITHUB_PARSER_VALIDATION",
        "pull_request": associated_pr,
    }

    return chronicle_request(
        client=client,
        method="POST",
        api_version="v1alpha",
        endpoint_path=endpoint_path,
        json=payload,
        timeout=timeout,
    )


def get_analysis_report(
    client: "ChronicleClient",
    log_type: str,
    parser_id: str,
    report_id: str,
    timeout: int = 60,
) -> dict[str, Any]:
    """Get a parser analysis report.

    Args:
        client: ChronicleClient instance
        log_type: Log type of the parser.
        parser_id: The ID of the parser.
        report_id: The ID of the analysis report.
        timeout: Optional timeout in seconds (default: 60).

    Returns:
        Dictionary containing the analysis report.

    Raises:
        SecOpsError: If input is invalid.
        APIError: If the API request fails.
    """
    if not isinstance(log_type, str) or not log_type.strip():
        raise SecOpsError("log_type must be a non-empty string")
    if not isinstance(parser_id, str) or not parser_id.strip():
        raise SecOpsError("parser_id must be a non-empty string")
    if not isinstance(report_id, str) or not report_id.strip():
        raise SecOpsError("report_id must be a non-empty string")
    if not isinstance(timeout, int) or timeout < 0:
        raise SecOpsError("timeout must be a non-negative integer")

    endpoint_path = (
        f"logTypes/{log_type}/parsers/{parser_id}/analysisReports/{report_id}"
    )

    return chronicle_request(
        client=client,
        method="GET",
        api_version=APIVersion.V1ALPHA,
        endpoint_path=endpoint_path,
        timeout=timeout,
    )
