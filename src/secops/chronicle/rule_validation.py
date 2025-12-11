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
"""Rule validation functionality for Chronicle."""

from typing import NamedTuple

from secops.exceptions import APIError


class ValidationResult(NamedTuple):
    """Result of a rule validation.

    Attributes:
        success: Whether the rule is valid
        message: Error message if validation failed, None if successful
        position: Dictionary containing position information for errors,
            if available
    """

    success: bool
    message: str | None = None
    position: dict[str, int] | None = None


def validate_rule(client, rule_text: str) -> ValidationResult:
    """Validates a YARA-L2 rule against the Chronicle API.

    Args:
        client: ChronicleClient instance
        rule_text: Content of the rule to validate

    Returns:
        ValidationResult containing:
            - success: Whether the rule is valid
            - message: Error message if validation failed, None if successful
            - position: Dictionary containing position information for errors,
                if available

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}:verifyRuleText"

    # Clean up the rule text by removing leading/trailing backticks and
    # whitespace
    cleaned_rule = rule_text.strip("` \n\t\r")

    body = {"ruleText": cleaned_rule}

    response = client.session.post(url, json=body)

    if response.status_code != 200:
        raise APIError(f"Failed to validate rule: {response.text}")

    result = response.json()

    # Check if the response indicates success
    if result.get("success", False):
        return ValidationResult(success=True)

    # Extract error information
    diagnostics = result.get("compilationDiagnostics", [])
    if not diagnostics:
        return ValidationResult(
            success=False, message="Unknown validation error"
        )

    # Get the first error message and position information
    first_error = diagnostics[0]
    error_message = first_error.get("message")
    position = first_error.get("position")

    return ValidationResult(
        success=False, message=error_message, position=position
    )
