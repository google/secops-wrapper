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

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)
from secops.exceptions import SecOpsError

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
    client, page_size: int | None = None, page_token: str | None = None
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
    return chronicle_paginated_request(
        client,
        path="findingsRefinements",
        items_key="findingsRefinements",
        api_version=APIVersion.V1ALPHA,
        page_size=page_size,
        page_token=page_token,
    )


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
    if not exclusion_id.startswith("projects/"):
        endpoint_path = f"findingsRefinements/{exclusion_id}"
    else:
        endpoint_path = exclusion_id

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1ALPHA,
        error_message="Failed to get rule exclusion",
    )


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
    body = {
        "display_name": display_name,
        "type": refinement_type,
        "query": query,
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="findingsRefinements",
        api_version=APIVersion.V1ALPHA,
        json=body,
        error_message="Failed to create rule exclusion",
    )


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
    if not exclusion_id.startswith("projects/"):
        endpoint_path = f"findingsRefinements/{exclusion_id}"
    else:
        endpoint_path = exclusion_id

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

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1ALPHA,
        params=params,
        json=body,
        error_message="Failed to update rule exclusion",
    )


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
    if not exclusion_id.startswith("projects/"):
        endpoint_path = (
            f"findingsRefinements/{exclusion_id}"
            ":computeFindingsRefinementActivity"
        )
    else:
        endpoint_path = f"{exclusion_id}:computeFindingsRefinementActivity"

    body = {}
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

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1ALPHA,
        json=body,
        error_message="Failed to compute rule exclusion activity",
    )


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
    if not exclusion_id.startswith("projects/"):
        endpoint_path = f"findingsRefinements/{exclusion_id}/deployment"
    else:
        endpoint_path = f"{exclusion_id}/deployment"

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1ALPHA,
        error_message="Failed to get rule exclusion deployment",
    )


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
    if not exclusion_id.startswith("projects/"):
        endpoint_path = f"findingsRefinements/{exclusion_id}/deployment"
    else:
        endpoint_path = f"{exclusion_id}/deployment"

    params = {}
    if update_mask:
        params["updateMask"] = update_mask
    else:
        fields = []
        for k, v in deployment_details.to_dict().items():
            if v is not None:
                fields.append(k)
        params["updateMask"] = ",".join(fields)

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=endpoint_path,
        api_version=APIVersion.V1ALPHA,
        params=params,
        json=deployment_details.to_dict(),
        error_message="Failed to update rule exclusion deployment",
    )
