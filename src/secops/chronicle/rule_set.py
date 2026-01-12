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
"""Curated rule set functionality for Chronicle."""

from datetime import datetime
from typing import Any

from secops.chronicle.models import AlertState, ListBasis, APIVersion
from secops.exceptions import SecOpsError
from secops.chronicle.utils.request_utils import (
    chronicle_request,
    chronicle_paginated_request,
)


def list_curated_rule_sets(
    client,
    page_size: str | None = None,
    page_token: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of all curated rule sets

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page.
        page_token: Token for the page to retrieve
        as_list: If True, return a list of curated rule sets
            instead of a dict with curatedRuleSets list and nextPageToken.

    Returns:
        If page_size is None: List of all curated rule sets.
        If page_size is provided: Dict with curatedRuleSets list
            and nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRuleSetCategories/-/curatedRuleSets",
        items_key="curatedRuleSets",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )


def get_curated_rule_set(client, rule_set_id: str) -> dict[str, Any]:
    """Get a curated rule set by ID

    Args:
        client: ChronicleClient instance
        rule_set_id: Unique ID of the curated rule set

    Returns:
        Dictionary containing the curated rule set

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"curatedRuleSetCategories/-/" f"curatedRuleSets/{rule_set_id}"
        ),
        api_version=APIVersion.V1ALPHA,
        error_message=f"Failed to get rule set: {rule_set_id}",
    )


def list_curated_rule_set_categories(
    client,
    page_size: str | None = None,
    page_token: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of all curated rule set categories

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page.
        page_token: Token for the page to retrieve
        as_list: If True, return a list of curated rule set categories
            instead of a dict with curatedRuleSetCategories list
            and nextPageToken.

    Returns:
        If page_size is None: List of all categories.
        If page_size is provided: Dict with curatedRuleSetCategories
            list and nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRuleSetCategories",
        items_key="curatedRuleSetCategories",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )


def get_curated_rule_set_category(client, category_id: str) -> dict[str, Any]:
    """Get a curated rule set category by ID

    Args:
        client: ChronicleClient instance
        category_id: Unique ID of the curated rule set category

    Returns:
        Dictionary containing the curated rule set category

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"curatedRuleSetCategories/{category_id}",
        api_version=APIVersion.V1ALPHA,
        error_message=f"Failed to get rule set category: {category_id}",
    )


def list_curated_rules(
    client,
    page_size: str | None = None,
    page_token: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of all curated rules

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page.
        page_token: Token for the page to retrieve
        as_list: If True, return a list of curated rules
            instead of a dict with curatedRules list and nextPageToken.

    Returns:
        If page_size is None: List of all curated rules.
        If page_size is provided: Dict with curatedRules list and
            nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )


def get_curated_rule(client, rule_id: str) -> dict[str, Any]:
    """Get a curated rule by ID

    Args:
        client: ChronicleClient instance
        rule_id: Unique ID of the curated rule to retrieve ("ur_<UUID>"
            or "ur_<RULE_NAME>).
            Examples:
                `ur_ffac5fa0-5b0b-463e-9f92-2443f8f1b6fd`
                `ur_ttp_GCP_MassSecretDeletion`

    Returns:
        Dictionary containing the curated rule

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"curatedRules/{rule_id}",
        api_version=APIVersion.V1ALPHA,
        error_message=f"Failed to get curated rule: {rule_id}",
    )


def get_curated_rule_by_name(
    client, display_name: str
) -> dict[str, Any] | None:
    """Get a curated rule by display name
        NOTE: This is a linear scan of all curated rules,
        so it may be inefficient for large rule sets.

    Args:
        client: ChronicleClient instance
        display_name: Display name of the curated rule

    Returns:
        Dictionary containing the curated rule

    Raises:
        APIError: If the API request fails
    """
    rule = None
    for r in list_curated_rules(client).get("curatedRules", []):
        if r.get("displayName", "").lower() == display_name.lower():
            rule = r
            break
    if not rule:
        raise SecOpsError(f"Rule with name '{display_name}' not found")

    return rule


def list_curated_rule_set_deployments(
    client,
    page_size: str | None = None,
    page_token: str | None = None,
    only_enabled: bool | None = False,
    only_alerting: bool | None = False,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of all curated rule set deployment statuses

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page.
        page_token: Token for the page to retrieve
        only_enabled: Only return enabled rule set deployments
        only_alerting: Only return alerting rule set deployments
        as_list: If True, return a list of curated rule set deployments
            instead of a dict with curatedRuleSetDeployments list
            and nextPageToken.

    Returns:
        If page_size is None: List of all deployments.
        If page_size is provided: Dict with curatedRuleSetDeployments
            list and nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    result = chronicle_paginated_request(
        client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRuleSetCategories/-/curatedRuleSets/"
        "-/curatedRuleSetDeployments",
        items_key="curatedRuleSetDeployments",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )

    # Extract deployments from response
    if isinstance(result, list):
        rule_set_deployments = result
    else:
        rule_set_deployments = result.get("curatedRuleSetDeployments", [])
    # Enrich the deployment data with the rule set displayName
    all_rule_sets = list_curated_rule_sets(client)

    for deployment in rule_set_deployments:
        rule_set_id = (
            deployment.get("name", "")
            .split("curatedRuleSetDeployment")[0]
            .rstrip("/")
        )
        for rule_set in all_rule_sets.get("curatedRuleSets", []):
            if rule_set.get("name", "") == rule_set_id:
                deployment["displayName"] = rule_set.get("displayName", "")
    # Apply filters for only enabled and/or alerting rule sets
    if only_enabled:
        rule_set_deployments = [
            deployment
            for deployment in rule_set_deployments
            if deployment.get("enabled", False)
        ]
    if only_alerting:
        rule_set_deployments = [
            deployment
            for deployment in rule_set_deployments
            if deployment.get("alerting", False)
        ]

    if as_list:
        return rule_set_deployments

    # Update result with filtered deployments
    result["curatedRuleSetDeployments"] = rule_set_deployments
    return result


def get_curated_rule_set_deployment(
    client,
    rule_set_id: str,
    precision: str = "precise",
) -> dict[str, Any]:
    """Get the deployment status of a curated rule set by ID

    Args:
        client: ChronicleClient instance
        rule_set_id: Unique ID of the curated rule set
        precision: Precision level ("precise" or "broad")

    Returns:
        Dictionary containing the curated rule set deployment

    Raises:
        APIError: If the API request fails
        SecOpsError: If the rule set is not found or precision is invalid
    """
    if precision not in ["precise", "broad"]:
        raise SecOpsError("Precision must be 'precise' or 'broad'")

    # Get the rule set by ID
    rule_set = get_curated_rule_set(client, rule_set_id)

    rule_set_id = rule_set.get("name", "").split("curatedRuleSetCategories")[-1]
    response = chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"curatedRuleSetCategories{rule_set_id}"
            f"/curatedRuleSetDeployments/{precision}"
        ),
        api_version=APIVersion.V1ALPHA,
        error_message=(
            f"Failed to get curated rule set deployment: {rule_set_id}"
        ),
    )

    # Enrich the deployment data with the rule set displayName
    response["displayName"] = rule_set.get("displayName", "")

    return response


def get_curated_rule_set_deployment_by_name(
    client,
    display_name: str,
    precision: str = "precise",
) -> dict[str, Any]:
    """Get the deployment status of a curated rule set by its display name
        NOTE: This is a linear scan of all curated rule sets,
        so it may be inefficient for large rule sets.

    Args:
        client: ChronicleClient instance
        display_name: Display name of the curated rule set (case-insensitive)
        precision: Precision level ("precise" or "broad")

    Returns:
        Dictionary containing the curated rule set deployment

    Raises:
        APIError: If the API request fails
        SecOpsError: If the rule set is not found or precision is invalid
    """
    if precision not in ["precise", "broad"]:
        raise SecOpsError("Precision must be 'precise' or 'broad'")

    rule_set = None
    for rs in list_curated_rule_sets(client).get("curatedRuleSets", []):
        # Names normalised as lowercase
        if rs.get("displayName", "").lower() == display_name.lower():
            rule_set = rs
            break

    if not rule_set:
        raise SecOpsError(f"Rule set with name '{display_name}' not found")

    # Extract the rule set ID from the resource name
    name_parts = rule_set["name"].split("/")
    rule_set_id = name_parts[-1]

    # Get the deployment status using existing function
    return get_curated_rule_set_deployment(client, rule_set_id, precision)


def _make_deployment_name(
    category_id: str, rule_set_id: str, precision: str, instance_id: str = None
):
    """Helper function to create a deployment name"""
    if instance_id:
        return (
            f"{instance_id}/curatedRuleSetCategories/{category_id}"
            f"/curatedRuleSets/{rule_set_id}"
            f"/curatedRuleSetDeployments/{precision}"
        )
    else:
        return (
            f"curatedRuleSetCategories/{category_id}"
            f"/curatedRuleSets/{rule_set_id}"
            f"/curatedRuleSetDeployments/{precision}"
        )


def update_curated_rule_set_deployment(
    client, deployment: dict[str, Any]
) -> dict[str, Any]:
    """Update a curated rule set deployment to enable or disable
            alerting or change precision.

    Args:
        client: ChronicleClient instance
        deployment: Dict of deployment configuration containing:
            - category_id: UUID of the category
            - rule_set_id: UUID of the rule set
            - precision: Precision level either "broad" or "precise"
            - enabled: Whether the rule set should be enabled
            - alerting: Whether alerting should be enabled for the rule set

    Returns:
        Dictionary containing the updated curated rule set deployment

    Raises:
        APIError: If the API request fails
        SecOpsError: If the rule set is not found or precision is invalid
    """
    # Check required fields
    required_fields = ["category_id", "rule_set_id", "precision", "enabled"]
    missing_fields = [
        field for field in required_fields if field not in deployment
    ]

    if missing_fields:
        raise ValueError(
            f"Deployment missing required fields: {missing_fields}"
        )

    # Get deployment configuration
    category_id = deployment["category_id"]
    rule_set_id = deployment["rule_set_id"]
    precision = deployment["precision"]
    enabled = deployment["enabled"]
    alerting = deployment.get("alerting", False)

    deployment_name = _make_deployment_name(category_id, rule_set_id, precision)

    deployment = {
        "name": f"{client.instance_id}/{deployment_name}",
        "precision": precision,
        "enabled": enabled,
        "alerting": alerting,
    }

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=deployment_name,
        api_version=APIVersion.V1ALPHA,
        json=deployment,
        expected_status=200,
        error_message=(
            f"Failed to patch curated rule set deployment: {deployment_name}"
        ),
    )


def batch_update_curated_rule_set_deployments(
    client, deployments: list[dict[str, Any]]
) -> dict[str, Any]:
    """Batch update curated rule set deployments.

    Args:
        client: ChronicleClient instance
        deployments: List of deployment configurations where each item contains:
            - category_id: UUID of the category
            - rule_set_id: UUID of the rule set
            - precision: Precision level (e.g., "broad", "precise")
            - enabled: Whether the rule set should be enabled
            - alerting: Whether alerting should be enabled for the rule set

    Returns:
        Dictionary containing information about the modified deployments

    Raises:
        APIError: If the API request fails
        ValueError: If required fields are missing from the deployments
    """
    # Build the request data
    request_items = []

    for deployment in deployments:
        # Check required fields
        required_fields = ["category_id", "rule_set_id", "precision", "enabled"]
        missing_fields = [
            field for field in required_fields if field not in deployment
        ]

        if missing_fields:
            raise ValueError(
                f"Deployment missing required fields: {missing_fields}"
            )

        # Get deployment configuration
        category_id = deployment["category_id"]
        rule_set_id = deployment["rule_set_id"]
        precision = deployment["precision"]
        enabled = deployment["enabled"]
        alerting = deployment.get("alerting", False)

        # Create the request item
        request_item = {
            "curated_rule_set_deployment": {
                "name": _make_deployment_name(
                    category_id, rule_set_id, precision, client.instance_id
                ),
                "enabled": enabled,
                "alerting": alerting,
            },
            "update_mask": {
                "paths": ["alerting", "enabled"],
            },
        }

        request_items.append(request_item)

    # Create the complete request payload
    json_data = {
        "parent": (
            f"{client.instance_id}/curatedRuleSetCategories/-"
            "/curatedRuleSets/-"
        ),
        "requests": request_items,
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            "curatedRuleSetCategories/-/curatedRuleSets"
            "/-/curatedRuleSetDeployments:batchUpdate"
        ),
        api_version=APIVersion.V1ALPHA,
        json=json_data,
        expected_status=200,
        error_message="Failed to batch update curated rule set deployments",
    )


def search_curated_detections(
    client,
    rule_id: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    list_basis: ListBasis | str = None,
    alert_state: AlertState | str | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
    max_resp_size_bytes: int | None = None,
    include_nested_detections: bool | None = False,
) -> dict[str, Any]:
    """Search for detections generated by a specific curated rule.

    Args:
        client: ChronicleClient instance
        rule_id: ID of the curated rule to search detections for.
        start_time: The time to start searching detections
            from (inclusive). Applied based on list_basis parameter.
        end_time: The time to end searching detections to
            (exclusive). Applied based on list_basis parameter.
        list_basis: Basis for determining whether to apply time
            filters. Can be ListBasis enum or string. Valid values:
                - ListBasis.LIST_BASIS_UNSPECIFIED
                - ListBasis.DETECTION_TIME
                - ListBasis.CREATED_TIME
        alert_state: Filter detections by alert state.
            Can be AlertState enum or string. Valid values:
                - AlertState.UNSPECIFIED
                - AlertState.NOT_ALERTING
                - AlertState.ALERTING
        page_size: Maximum number of detections to return.
            Maximum value is 1000. If provided, only returns that page.
        page_token: Token for retrieving the next page of results.
        max_resp_size_bytes: Maximum size of response in bytes.
            If set to 0 or omitted, no limit is enforced.
        include_nested_detections: If True, include one level
            of nested detections in the response. Default is False.

    Returns:
        Dictionary containing:
            - curatedDetections: List of detections (if
                include_nested_detections is False)
            - nestedDetectionSamples: List of detections with nested
                data (if include_nested_detections is True)
            - nextPageToken: Token for retrieving the next page
                (only if page_size was provided)
            - respTooLargeDetectionsTruncated: Boolean indicating if
                results were truncated

    Raises:
        APIError: If the API request fails
        ValueError: If invalid alert_state or list_basis is provided
    """
    extra_params = {
        "ruleId": rule_id,
    }

    if alert_state:
        if isinstance(alert_state, AlertState):
            extra_params["alertState"] = alert_state.value
        else:
            try:
                extra_params["alertState"] = AlertState(alert_state).value
            except ValueError as e:
                raise ValueError("Invalid alert_state") from e

    if list_basis:
        if isinstance(list_basis, ListBasis):
            extra_params["listBasis"] = list_basis.value
        else:
            try:
                extra_params["listBasis"] = ListBasis(list_basis).value
            except ValueError as e:
                raise ValueError("Invalid list_basis") from e

    if start_time:
        extra_params["startTime"] = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if end_time:
        extra_params["endTime"] = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    if max_resp_size_bytes:
        extra_params["maxRespSizeBytes"] = max_resp_size_bytes

    if include_nested_detections:
        extra_params["includeNestedDetections"] = include_nested_detections

    # Determine the items key based on include_nested_detections
    items_key = (
        "nestedDetectionSamples"
        if include_nested_detections
        else "curatedDetections"
    )

    return chronicle_paginated_request(
        client,
        api_version=APIVersion.V1ALPHA,
        path="legacy:legacySearchCuratedDetections",
        items_key=items_key,
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
    )
