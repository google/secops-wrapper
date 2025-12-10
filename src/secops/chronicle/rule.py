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
    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules"
    )

    body = {
        "text": rule_text,
    }

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to create rule: {response.text}")

    return response.json()


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
    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules/{rule_id}"
    )

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get rule: {response.text}")

    return response.json()


def list_rules(
    client,
    view: str | None = "FULL",
    page_size: int | None = None,
    page_token: str | None = None,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
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

    Returns:
        Dictionary containing information about rules

    Raises:
        APIError: If the API request fails
    """
    more = True
    rules = {"rules": []}
    params = {"pageSize": 1000 if not page_size else page_size, "view": view}
    if page_token:
        params["pageToken"] = page_token

    while more:
        url = (
            f"{client.base_url(api_version, list(APIVersion))}/"
            f"{client.instance_id}/rules"
        )
        response = client.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Failed to list rules: {response.text}")

        data = response.json()
        if not data:
            # no rules, api returns {}
            return rules

        # If Page size is provided return fetched rules as user expects
        # only that many rules in the response
        if page_size:
            rules.update(**data)
            more = False
            break
        else:  # Else auto fetch rest pages (Backward Compatibility)
            rules["rules"].extend(data["rules"])

        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
        else:
            if "pageToken" in params:
                del params["pageToken"]
            more = False

    return rules


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
    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules/{rule_id}"
    )

    body = {
        "text": rule_text,
    }

    params = {"update_mask": "text"}

    response = client.session.patch(url, params=params, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to update rule: {response.text}")

    return response.json()


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
    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules/{rule_id}"
    )

    params = {}
    if force:
        params["force"] = "true"

    response = client.session.delete(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to delete rule: {response.text}")

    # The API returns an empty JSON object on success
    return response.json()


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
    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules/{rule_id}/deployment"
    )
    response = client.session.get(url)
    if response.status_code != 200:
        raise APIError(f"Failed to get rule deployment: {response.text}")
    return response.json()


def list_rule_deployments(
    client,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_query: str | None = None,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Lists rule deployments for the instance.

    Args:
        client: ChronicleClient instance.
        page_size: Maximum number of deployments to return per page. If omitted,
            all pages are fetched and aggregated.
        page_token: Token for the next page of results, if available.
        filter_query: Optional filter query to restrict results.
            Filters results based on expression matching specific fields.

    Returns:
        Dictionary containing rule deployment entries. If ``page_size`` is not
        provided, returns an aggregated object with a ``deployments`` list.

    Raises:
        APIError: If the API request fails.

    """
    params: dict[str, Any] = {}
    if page_size:
        params["pageSize"] = page_size
    if page_token:
        params["pageToken"] = page_token
    if filter_query:
        params["filter"] = filter_query

    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules/-/deployments"
    )

    if page_size:
        response = client.session.get(url, params=params)
        if response.status_code != 200:
            raise APIError(f"Failed to list rule deployments: {response.text}")
        return response.json()

    deployments: dict[str, Any] = {"ruleDeployments": []}
    more = True
    while more:
        response = client.session.get(url, params=params)
        if response.status_code != 200:
            raise APIError(f"Failed to list rule deployments: {response.text}")
        data = response.json()
        if not data:
            # no rule deployments, api returns {}
            return deployments

        deployments["ruleDeployments"].extend(data["ruleDeployments"])

        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
        else:
            params.pop("pageToken", None)
            more = False

    return deployments


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

    # Fix: Use the full path for the legacy API endpoint
    url = (
        f"{client.base_url}/projects/{client.project_id}/locations"
        f"/{client.region}/instances/{client.customer_id}"
        "/legacy:legacyRunTestRule"
    )

    body = {
        "ruleText": rule_text,
        "timeRange": {
            "startTime": start_time_str,
            "endTime": end_time_str,
        },
        "maxResults": max_results,
        "scope": "",  # Empty scope parameter
    }

    # Make the request and get the complete response
    try:
        response = client.session.post(url, json=body, timeout=timeout)

        if response.status_code != 200:
            raise APIError(f"Failed to test rule: {response.text}")

        # Parse the response as a JSON array
        try:
            json_array = json.loads(response.text)

            # Yield each item in the array
            for item in json_array:
                # Transform the response items to match the expected format
                if "detection" in item:
                    # Return the detection with proper type
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
                    # Unknown item type, yield as-is
                    yield item

        except json.JSONDecodeError as e:
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
    url = (
        f"{client.base_url(api_version, list(APIVersion))}/"
        f"{client.instance_id}/rules/{rule_id}/deployment"
    )

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

    response = client.session.patch(url, params=params, json=body)
    if response.status_code != 200:
        raise APIError(f"Failed to update rule deployment: {response.text}")

    return response.json()
