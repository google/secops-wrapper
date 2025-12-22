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
"""Curated Rule exclusions functionality for Chronicle."""

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Annotated, Any

from secops.exceptions import APIError, SecOpsError

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


class RuleExclusionType(StrEnum):
    """Valid rule exclusion types."""

    DETECTION_EXCLUSION = "DETECTION_EXCLUSION"
    FINDINGS_REFINEMENT_TYPE_UNSPECIFIED = (
        "FINDINGS_REFINEMENT_TYPE_UNSPECIFIED"
    )


@dataclass
class UpdateRuleDeployment:
    """Model for updating rule deployment."""

    enabled: Annotated[bool | None, "Optional enabled flag of rule"] = None
    archived: Annotated[bool | None, "Optional archived flag of rule"] = None
    detection_exclusion_application: Annotated[
        str | dict[str, Any] | None,
        "Optional detection exclusion application of rule",
    ] = None

    def __post_init__(self):
        """Post initilizaiton for validating/converting attributes"""
        if self.enabled is True and self.archived is True:
            raise ValueError(
                "enabled and archived flags cannot be true at same time"
            )
        if isinstance(self.detection_exclusion_application, str):
            try:
                self.detection_exclusion_application = json.loads(
                    self.detection_exclusion_application
                )
            except json.JSONDecodeError as e:
                raise ValueError(
                    "Invalid JSON string for detection_exclusion_application: "
                    f"{e}"
                ) from e

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def list_rule_exclusions(
    client, page_size: int = 100, page_token: str | None = None
) -> dict[str, Any]:
    """List rule exclusions.

    Args:
        client: ChronicleClient instance
        page_size: Maximum number of rule exclusions to return per page
        page_token: Page token for pagination

    Returns:
        Dictionary containing the list of rule exclusions

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/findingsRefinements"

    params = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to list rule exclusions: {response.text}")

    return response.json()


def get_rule_exclusion(client, exclusion_id: str) -> dict[str, Any]:
    """Get a rule exclusion by name.

    Args:
        client: ChronicleClient instance
        exclusion_id: Id of the rule exclusion to retrieve

    Returns:
        Dictionary containing rule exclusion information

    Raises:
        APIError: If the API request fails
    """
    # Check if name is a full resource name or just an ID
    name = exclusion_id
    if not exclusion_id.startswith("projects/"):
        name = f"{client.instance_id}/findingsRefinements/{exclusion_id}"

    url = f"{client.base_url}/{name}"

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(f"Failed to get rule exclusion: {response.text}")

    return response.json()


def create_rule_exclusion(
    client, display_name: str, refinement_type: RuleExclusionType, query: str
) -> dict[str, Any]:
    """Creates a new rule exclusion.

    Args:
        client: ChronicleClient instance
        display_name: The display name to use for the rule exclusion
        refinement_type: The type of the Findings refinement
                  Must be one of:
                  - DETECTION_EXCLUSION
                  - FINDINGS_REFINEMENT_TYPE_UNSPECIFIED
        query: The query for the findings refinement.

    Returns:
        Dictionary containing the created rule exclusion

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/findingsRefinements"

    body = {
        "display_name": display_name,
        "type": refinement_type,
        "query": query,
    }

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to create rule exclusion: {response.text}")

    return response.json()


def patch_rule_exclusion(
    client,
    exclusion_id: str,
    display_name: str | None = None,
    refinement_type: RuleExclusionType | None = None,
    query: str | None = None,
    update_mask: str | None = None,
) -> dict[str, Any]:
    """Updates a rule exclusion using provided id.

    Args:
        client: ChronicleClient instance
        name: Name of the rule exclusion to update
        display_name: The display name to use for the rule exclusion
        refinement_type: The type of the Findings refinement
                  Must be one of:
                  - DETECTION_EXCLUSION
                  - FINDINGS_REFINEMENT_TYPE_UNSPECIFIED
        query: The query for the findings refinement.
        update_mask: Comma-separated list of fields to update

    Returns:
        Dictionary containing the updated rule exclusion

    Raises:
        APIError: If the API request fails
    """
    name = exclusion_id
    # Check if name is a full resource name or just an ID
    if not exclusion_id.startswith("projects/"):
        name = f"{client.instance_id}/findingsRefinements/{exclusion_id}"

    url = f"{client.base_url}/{name}"

    body = {}

    if display_name:
        body["display_name"] = display_name
    if refinement_type:
        body["type"] = refinement_type
    if query:
        body["query"] = query

    params = {}
    if update_mask:
        params["updateMask"] = update_mask

    response = client.session.patch(url, params=params, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to update rule exclusion: {response.text}")

    return response.json()


def compute_rule_exclusion_activity(
    client,
    exclusion_id: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> dict[str, Any]:
    """Compute activity statistics for rule exclusions.

    Args:
        client: ChronicleClient instance
        exclusion_id: Id of a specific rule exclusion
        start_time: Optional start of the time window
        end_time: Optional end of the time window

    Returns:
        Dictionary containing activity statistics

    Raises:
        APIError: If the API request fails
    """
    name = exclusion_id
    # Check if name is a full resource name or just an ID
    if not name.startswith("projects/"):
        name = f"{client.instance_id}/findingsRefinements/{exclusion_id}"

    url = f"{client.base_url}/{name}:computeFindingsRefinementActivity"

    body = {}

    # Add time range if provided
    if start_time or end_time:
        time_range = {}
        try:
            if start_time:
                time_range["start_time"] = start_time.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

            if end_time:
                time_range["end_time"] = end_time.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )

            body["interval"] = time_range
        except ValueError as e:
            raise SecOpsError(
                "Failed to convert time interval to required format"
            ) from e

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(
            f"Failed to compute rule exclusion activity: {response.text}"
        )

    return response.json()


def get_rule_exclusion_deployment(client, exclusion_id: str) -> dict[str, Any]:
    """Get deployment information for a rule exclusion.

    Args:
        client: ChronicleClient instance
        exclusion_id: Id of the rule exclusion

    Returns:
        Dictionary containing deployment information

    Raises:
        APIError: If the API request fails
    """
    name = exclusion_id
    # Check if name is a full resource name or just an ID
    if not name.startswith("projects/"):
        name = f"{client.instance_id}/findingsRefinements/{name}"

    url = f"{client.base_url}/{name}/deployment"

    response = client.session.get(url)

    if response.status_code != 200:
        raise APIError(
            f"Failed to get rule exclusion deployment: {response.text}"
        )

    return response.json()


def update_rule_exclusion_deployment(
    client,
    exclusion_id: str,
    deployment_details: UpdateRuleDeployment,
    update_mask: str | None = None,
) -> dict[str, Any]:
    """Update deployment settings for a rule exclusion.

    Args:
        client: ChronicleClient instance
        exclusion_id: Id of the rule exclusion
        deployment_details: Rule deployment update details with
            enabled, archived and detection exclusion application
        update_mask: Comma-separated list of fields to update.

    Returns:
        Dictionary containing updated deployment information

    Raises:
        APIError: If the API request fails
    """
    name = exclusion_id
    # Check if name is a full resource name or just an ID
    if not name.startswith("projects/"):
        name = f"{client.instance_id}/findingsRefinements/{name}"

    url = f"{client.base_url}/{name}/deployment"

    params = {}
    if update_mask:
        params["updateMask"] = update_mask
    else:
        fields = []
        for k, v in deployment_details.to_dict().items():
            if v is not None:
                fields.append(k)
        params["updateMask"] = ",".join(fields)

    response = client.session.patch(
        url, params=params, json=deployment_details.to_dict()
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to update rule exclusion deployment: {response.text}"
        )

    return response.json()
