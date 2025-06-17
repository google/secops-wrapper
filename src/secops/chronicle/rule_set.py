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
"""Rule set functionality for Chronicle."""

from typing import Dict, Any, List
from secops.exceptions import APIError


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
    url = f"{client.base_url}/{client.instance_id}/curatedRuleSetCategories/-/curatedRuleSets/-/curatedRuleSetDeployments:batchUpdate"

    # Helper function to create a deployment name
    def make_deployment_name(category_id, rule_set_id, precision):
        return f"{client.instance_id}/curatedRuleSetCategories/{category_id}/curatedRuleSets/{rule_set_id}/curatedRuleSetDeployments/{precision}"

    # Build the request data
    request_items = []

    for deployment in deployments:
        # Check required fields
        required_fields = ["category_id", "rule_set_id", "precision", "enabled"]
        missing_fields = [field for field in required_fields if field not in deployment]

        if missing_fields:
            raise ValueError(f"Deployment missing required fields: {missing_fields}")

        # Get deployment configuration
        category_id = deployment["category_id"]
        rule_set_id = deployment["rule_set_id"]
        precision = deployment["precision"]
        enabled = deployment["enabled"]
        alerting = deployment.get("alerting", False)

        # Create the request item
        request_item = {
            "curated_rule_set_deployment": {
                "name": make_deployment_name(category_id, rule_set_id, precision),
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
        "parent": f"{client.instance_id}/curatedRuleSetCategories/-/curatedRuleSets/-",
        "requests": request_items,
    }

    response = client.session.post(url, json=json_data)

    if response.status_code != 200:
        raise APIError(f"Failed to batch update rule set deployments: {response.text}")

    return response.json()
