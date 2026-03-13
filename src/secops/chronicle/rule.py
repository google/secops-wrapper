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
"""Rule management functionality for Chronicle."""

import json
import re
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any, Literal

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)
from secops.exceptions import APIError, SecOpsError


def create_rule(
    client, rule_text: str, api_version: APIVersion | None = APIVersion.V1
) -> dict[str, Any]:
    """Creates a new detection rule to find matches in logs.

    Args:
        client: ChronicleClient instance
        rule_text: Content of the new detection rule, used to evaluate logs.
        api_version: Preferred API version to use. Defaults to V1
    Returns:
        Dictionary containing the created rule information

    Raises:
        APIError: If the API request fails
    """

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="rules",
        api_version=api_version if api_version else None,
        json={"text": rule_text},
        error_message="Failed to create rule",
    )


def get_rule(
    client, rule_id: str, api_version: APIVersion | None = APIVersion.V1
) -> dict[str, Any]:
    """Get a rule by ID.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to retrieve ("ru_<UUID>" or
          "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version suffix isn't
          specified we use the rule's latest version.

    Returns:
        Dictionary containing rule information

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"rules/{rule_id}",
        api_version=api_version,
        error_message="Failed to get rule",
    )


def list_rules(
    client,
    view: str | None = "FULL",
    page_size: int | None = None,
    page_token: str | None = None,
    api_version: APIVersion | None = APIVersion.V1,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """Gets a list of rules.

    Args:
        client: ChronicleClient instance
        view: Scope of fields to populate for the rules being returned.
            allowed values are:
            - "BASIC"
            - "FULL"
            - "REVISION_METADATA_ONLY"
            - "RULE_VIEW_UNSPECIFIED"
            Defaults to "FULL".
        page_size: Maximum number of rules to return per page.
        page_token: Token for the next page of results, if available.
        api_version: (Optional) Preferred API version to use.
        as_list: If True, return only the list of rules.
            If False, return dict with metadata and pagination tokens.

    Returns:
        If as_list is True: List of rules.
        If as_list is False: Dict with rules list and pagination metadata.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        path="rules",
        items_key="rules",
        api_version=api_version,
        page_size=page_size,
        page_token=page_token,
        extra_params={"view": view} if view else {},
        as_list=as_list,
    )


def update_rule(
    client,
    rule_id: str,
    rule_text: str,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Updates a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to update ("ru_<UUID>")
        rule_text: Updated content of the detection rule

    Returns:
        Dictionary containing the updated rule information

    Raises:
        APIError: If the API request fails
    """
    body = {"text": rule_text}
    params = {"update_mask": "text"}

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"rules/{rule_id}",
        api_version=api_version,
        params=params,
        json=body,
        error_message="Failed to update rule",
    )


def delete_rule(
    client,
    rule_id: str,
    force: bool = False,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Deletes a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to delete ("ru_<UUID>")
        force: If True, deletes the rule even if it has associated retrohunts

    Returns:
        Empty dictionary or deletion confirmation

    Raises:
        APIError: If the API request fails
    """
    params = {}
    if force:
        params["force"] = "true"

    return chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"rules/{rule_id}",
        api_version=api_version,
        params=params,
        error_message="Failed to delete rule",
    )


def enable_rule(client, rule_id: str, enabled: bool = True) -> dict[str, Any]:
    """Enables or disables a rule.

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the detection rule to enable/disable ("ru_<UUID>")
        enabled: Whether to enable (True) or disable (False) the rule

    Returns:
        Dictionary containing rule deployment information

    Raises:
        APIError: If the API request fails
    """
    return update_rule_deployment(client, rule_id, enabled=enabled)


def set_rule_alerting(
    client, rule_id: str, alerting_enabled: bool = True
) -> dict[str, Any]:
    """Enables or disables alerting for a rule deployment.

    Args:
        client: ChronicleClient instance.
        rule_id: Unique ID of the detection rule (e.g., "ru_<UUID>").
        alerting_enabled: Whether to enable (True) or disable (False) alerting.

    Returns:
        Dictionary containing rule deployment information.

    Raises:
        APIError: If the API request fails.
    """
    return update_rule_deployment(client, rule_id, alerting=alerting_enabled)


def get_rule_deployment(
    client, rule_id: str, api_version: APIVersion | None = APIVersion.V1
) -> dict[str, Any]:
    """Gets the current deployment for a rule.

    Args:
        client: ChronicleClient instance.
        rule_id: Unique ID of the detection rule (for example, "ru_<UUID>" or
            "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version suffix isn't
            specified, the latest version is used.

    Returns:
        Dictionary containing the rule deployment information.

    Raises:
        APIError: If the API request fails.

    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"rules/{rule_id}/deployment",
        api_version=api_version,
        error_message="Failed to get rule deployment",
    )


def list_rule_deployments(
    client,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_query: str | None = None,
    api_version: APIVersion | None = APIVersion.V1,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """Lists rule deployments for the instance.

    Args:
        client: ChronicleClient instance.
        page_size: Maximum number of deployments to return per page. If omitted,
            all pages are fetched and aggregated.
        page_token: Token for the next page of results, if available.
        filter_query: Optional filter query to restrict results.
            Filters results based on expression matching specific fields.
        api_version: (Optional) Preferred API version to use.
        as_list: If True, return only the list of rule deployments.
            If False, return dict with metadata and pagination tokens.

    Returns:
        If as_list is True: List of rule deployments.
        If as_list is False: Dict with ruleDeployments list and
            pagination metadata.

    Raises:
        APIError: If the API request fails.

    """
    extra_params = {}
    if filter_query:
        extra_params["filter"] = filter_query

    return chronicle_paginated_request(
        client,
        path="rules/-/deployments",
        items_key="ruleDeployments",
        api_version=api_version,
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params if extra_params else None,
        as_list=as_list,
    )


def search_rules(
    client, query: str, api_version: APIVersion | None = APIVersion.V1
) -> dict[str, Any]:
    """Search for rules.

    Args:
        client: ChronicleClient instance
        query: Search query string that supports regex

    Returns:
        Dictionary containing search results

    Raises:
        APIError: If the API request fails
    """
    try:
        re.compile(query)
    except re.error as e:
        raise SecOpsError(f"Invalid regular expression: {query}") from e

    rules = list_rules(client, api_version=api_version)
    results = {"rules": []}
    for rule in rules["rules"]:
        rule_text = rule.get("text", "")
        match = re.search(query, rule_text)

        if match:
            results["rules"].append(rule)

    return results


def run_rule_test(
    client,
    rule_text: str,
    start_time: datetime,
    end_time: datetime,
    max_results: int = 100,
    timeout: int = 300,
) -> Iterator[dict[str, Any]]:
    """Tests a rule against historical data and returns matches.

    This function connects to the legacy:legacyRunTestRule streaming
    API endpoint and processes the response which contains progress updates
    and detection results.

    Args:
        client: ChronicleClient instance
        rule_text: Content of the detection rule to test
        start_time: Start time for the test range
        end_time: End time for the test range
        max_results: Maximum number of results to return
            (default 100, max 10000)
        timeout: Request timeout in seconds (default 300)

    Yields:
        Dictionaries containing detection results, progress updates
        or error information, depending on the response type.

    Raises:
        APIError: If the API request fails
        SecOpsError: If the input parameters are invalid
        ValueError: If max_results is outside valid range
    """
    # Validate input parameters
    if max_results < 1 or max_results > 10000:
        raise ValueError("max_results must be between 1 and 10000")

    # Convert datetime objects to ISO format strings required by the API
    # API expects timestamps in RFC3339 format with UTC timezone
    if not start_time.tzinfo:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if not end_time.tzinfo:
        end_time = end_time.replace(tzinfo=timezone.utc)

    # Format as RFC3339 with Z suffix
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    body = {
        "ruleText": rule_text,
        "timeRange": {
            "startTime": start_time_str,
            "endTime": end_time_str,
        },
        "maxResults": max_results,
        "scope": "",
    }

    try:
        json_array = chronicle_request(
            client,
            method="POST",
            endpoint_path="legacy:legacyRunTestRule",
            json=body,
            timeout=timeout,
            error_message="Failed to test rule",
        )

        try:
            # Process the response as a JSON array

            # Yield each item in the array
            for item in json_array:
                if "detection" in item:
                    yield {"type": "detection", "detection": item["detection"]}
                elif "progressPercent" in item:
                    yield {
                        "type": "progress",
                        "percentDone": item["progressPercent"],
                    }
                elif "ruleCompilationError" in item:
                    yield {
                        "type": "error",
                        "message": item["ruleCompilationError"],
                        "isCompilationError": True,
                    }
                elif "ruleError" in item:
                    yield {"type": "error", "message": item["ruleError"]}
                elif "tooManyDetections" in item and item["tooManyDetections"]:
                    yield {
                        "type": "info",
                        "message": (
                            "Too many detections found, "
                            "results may be incomplete"
                        ),
                    }
                else:
                    yield item

        except (json.JSONDecodeError, TypeError) as e:
            raise APIError(
                f"Failed to parse rule test response: {str(e)}"
            ) from e

    except Exception as e:
        raise APIError(f"Error testing rule: {str(e)}") from e


def update_rule_deployment(
    client,
    rule_id: str,
    *,
    enabled: bool | None = None,
    alerting: bool | None = None,
    archived: bool | None = None,
    run_frequency: Literal["LIVE", "HOURLY", "DAILY"] | None = None,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Update deployment settings for a rule.

    This wraps the RuleDeployment update behavior and supports partial updates
    by sending only provided fields with an appropriate ``update_mask``.

    Args:
        client: ChronicleClient instance.
        rule_id: Rule identifier (for example, ``"ru_<UUID>"``).
        enabled: Whether the rule is continuously executed against incoming
            data.
        alerting: Whether detections from this deployment should generate
            alerts.
        archived: Archive state. Must be set with ``enabled=False`` when
            ``True``; setting ``archived=True`` implicitly disables
            ``alerting`` per API semantics.
        run_frequency: Run cadence for the rule (for example, ``"LIVE"``,
            ``"HOURLY"``, or ``"DAILY"``).

    Returns:
        Dictionary representing the updated RuleDeployment.

    Raises:
        APIError: If no fields are provided or the API request fails.
        SecOpsError: If the input parameters are invalid

    Notes:
        - Only fields explicitly provided are updated; others remain unchanged.
        - The ``update_mask`` is derived from provided fields in the same order
          they are specified by the caller.
    """
    body: dict[str, Any] = {}
    fields: list[str] = []

    if enabled is not None:
        body["enabled"] = enabled
        fields.append("enabled")
    if alerting is not None:
        body["alerting"] = alerting
        fields.append("alerting")
    if archived is not None:
        body["archived"] = archived
        fields.append("archived")
    if run_frequency is not None:
        body["runFrequency"] = run_frequency
        fields.append("runFrequency")

    if not fields:
        raise SecOpsError("No deployment fields provided to update")

    params = {"update_mask": ",".join(fields)}

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"rules/{rule_id}/deployment",
        api_version=api_version,
        params=params,
        json=body,
        error_message="Failed to update rule deployment",
    )
