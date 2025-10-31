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

from typing import Dict, Any, List, Optional
from secops.exceptions import APIError, SecOpsError


def _paginated_request(
    client,
    path: str,
    items_key: str,
    *,
    page_size: Optional[int] = None,
    page_token: Optional[str] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Helper to get items from endpoints that use pagination.

    Args:
        client: ChronicleClient instance
        path: URL path after {base_url}/{instance_id}/
        items_key: JSON key holding the array of items (e.g., 'curatedRules')
        page_size: Maximum number of rules to return per page.
        page_token: Token for the next page of results, if available.
        extra_params: extra query params to include on every request

    Returns:
        List of items from the paginated collection.

    Raises:
        APIError: If the HTTP request fails.
    """
    url = f"{client.base_url}/{client.instance_id}/{path}"
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

    return results


def list_curated_rule_sets(
    client,
    page_size: Optional[str] = None,
    page_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get a list of all curated rule sets

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve

    Returns:
        List of curated rule sets

    Raises:
        APIError: If the API request fails
    """
    return _paginated_request(
        client,
        path="curatedRuleSetCategories/-/curatedRuleSets",
        items_key="curatedRuleSets",
        page_size=page_size,
        page_token=page_token,
    )


def get_curated_rule_set(client, rule_set_id: str) -> Dict[str, Any]:
    """Get a curated rule set by ID

    Args:
        client: ChronicleClient instance
        rule_set_id: Unique ID of the curated rule set

    Returns:
        Dictionary containing the curated rule set

    Raises:
        APIError: If the API request fails
    """
    base_url = (
        f"{client.base_url}/{client.instance_id}/"
        f"curatedRuleSetCategories/-/curatedRuleSets/{rule_set_id}"
    )

    response = client.session.get(base_url)
    if response.status_code != 200:
        raise APIError(f"Failed to get rule set: {response.text}")

    return response.json()


def list_curated_rule_set_categories(
    client,
    page_size: Optional[str] = None,
    page_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get a list of all curated rule set categories

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve

    Returns:
        List of curated rule set categories

    Raises:
        APIError: If the API request fails
    """
    return _paginated_request(
        client,
        path="curatedRuleSetCategories",
        items_key="curatedRuleSetCategories",
        page_size=page_size,
        page_token=page_token,
    )


def get_curated_rule_set_category(client, category_id: str) -> Dict[str, Any]:
    """Get a curated rule set category by ID

    Args:
        client: ChronicleClient instance
        category_id: Unique ID of the curated rule set category

    Returns:
        Dictionary containing the curated rule set category

    Raises:
        APIError: If the API request fails
    """
    base_url = (
        f"{client.base_url}/{client.instance_id}/"
        f"curatedRuleSetCategories/{category_id}"
    )

    response = client.session.get(base_url)
    if response.status_code != 200:
        raise APIError(
            f"Failed to get curated rule set category: {response.text}"
        )

    return response.json()


def list_curated_rules(
    client,
    page_size: Optional[str] = None,
    page_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get a list of all curated rules

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve

    Returns:
        List of curated rules

    Raises:
        APIError: If the API request fails
    """
    return _paginated_request(
        client,
        path="curatedRules",
        items_key="curatedRules",
        page_size=page_size,
        page_token=page_token,
    )


def get_curated_rule(client, rule_id: str) -> Dict[str, Any]:
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
    base_url = (
        f"{client.base_url}/{client.instance_id}/" f"curatedRules/{rule_id}"
    )

    response = client.session.get(base_url)
    if response.status_code != 200:
        raise APIError(f"Failed to get curated rule: {response.text}")

    return response.json()


def get_curated_rule_by_name(client, display_name: str) -> Dict[str, Any]:
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
    for r in list_curated_rules(client):
        if r.get("displayName", "").lower() == display_name.lower():
            rule = r
            break
    if not rule:
        raise SecOpsError(f"Rule with name '{display_name}' not found")

    return rule


def list_curated_rule_set_deployments(
    client,
    page_size: Optional[str] = None,
    page_token: Optional[str] = None,
    only_enabled: Optional[bool] = False,
    only_alerting: Optional[bool] = False,
) -> List[Dict[str, Any]]:
    """Get a list of all curated rule set deployment statuses

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve
        only_enabled: Only return enabled rule set deployments
        only_alerting: Only return alerting rule set deployments

    Returns:
        List of curated rule set deployments

    Raises:
        APIError: If the API request fails
    """
    rule_set_deployments = _paginated_request(
        client,
        path="curatedRuleSetCategories/-/curatedRuleSets/"
        "-/curatedRuleSetDeployments",
        items_key="curatedRuleSetDeployments",
        page_size=page_size,
        page_token=page_token,
    )

    # Enrich the deployment data with the rule set displayName
    all_rule_sets = list_curated_rule_sets(client)
    for deployment in rule_set_deployments:
        rule_set_id = (
            deployment.get("name", "")
            .split("curatedRuleSetDeployment")[0]
            .rstrip("/")
        )
        for rule_set in all_rule_sets:
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

    return rule_set_deployments


def get_curated_rule_set_deployment(
    client,
    rule_set_id: str,
    precision: str = "precise",
) -> Dict[str, Any]:
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

    url = (
        f"{client.base_url}/{rule_set.get('name', '')}/"
        f"curatedRuleSetDeployments/{precision}"
    )

    response = client.session.get(url)
    if response.status_code != 200:
        raise APIError(
            f"Failed to get curated rule set deployment: {response.text}"
        )

    # Enrich the deployment data with the rule set displayName
    deployment = response.json()
    deployment["displayName"] = rule_set.get("displayName", "")

    return deployment


def get_curated_rule_set_deployment_by_name(
    client,
    display_name: str,
    precision: str = "precise",
) -> Dict[str, Any]:
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
    for rs in list_curated_rule_sets(client):
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


def update_curated_rule_set_deployment(
    client, deployment: Dict[str, Any]
) -> Dict[str, Any]:
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

    deployment_name = (
        f"{client.instance_id}/curatedRuleSetCategories/{category_id}"
        f"/curatedRuleSets/{rule_set_id}"
        f"/curatedRuleSetDeployments/{precision}"
    )

    deployment = {
        "name": deployment_name,
        "precision": precision,
        "enabled": enabled,
        "alerting": alerting,
    }

    url = f"{client.base_url}/{deployment_name}"

    response = client.session.patch(url, json=deployment)
    if response.status_code != 200:
        raise APIError(
            f"Failed to patch curated rule set deployment: {response.text}"
        )

    return response.json()


def batch_update_curated_rule_set_deployments(
    client, deployments: List[Dict[str, Any]]
) -> Dict[str, Any]:
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
    url = (
        f"{client.base_url}/{client.instance_id}/curatedRuleSetCategories/-"
        "/curatedRuleSets/-/curatedRuleSetDeployments:batchUpdate"
    )

    # Helper function to create a deployment name
    def make_deployment_name(category_id, rule_set_id, precision):
        return (
            f"{client.instance_id}/curatedRuleSetCategories/{category_id}"
            f"/curatedRuleSets/{rule_set_id}"
            f"/curatedRuleSetDeployments/{precision}"
        )

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
                "name": make_deployment_name(
                    category_id, rule_set_id, precision
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

    response = client.session.post(url, json=json_data)

    if response.status_code != 200:
        raise APIError(
            f"Failed to batch update rule set deployments: {response.text}"
        )

    return response.json()
