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
"""Formatting helper functions for Chronicle."""

import json
from typing import Any

from secops.exceptions import APIError


def format_resource_id(resource_id: str) -> str:
    """Extracts the correct ID for a resource string when the full
    resource name is provided.

    Example:
        full resource string:
            "projects/12345/locations/eu/instances/.../123-ID-abc"
        extracted ID: "123-ID-abc"

    Args:
        resource_id: The full resource string or just the ID.

    Returns:
        The extracted ID from the resource string, or the original string if it doesn't match the expected format.
    """
    if resource_id.startswith("projects/"):
        return resource_id.split("projects/")[-1]
    return resource_id


def parse_json_list(
    value: list[dict[str, Any]] | str, field_name: str
) -> list[dict[str, Any]]:
    """Parse a JSON string into a list, or return the list as-is.

    Args:
        value: A list of dictionaries or a JSON string representing a list of dictionaries.
        field_name: The name of the field being parsed, used for error messages.

    Returns:
        A list of dictionaries parsed from the JSON string, or the original list if it was already a list.

    Raises:
        APIError: If the input is a string but cannot be parsed as valid JSON.
    """
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [parsed]
        except ValueError as e:
            raise APIError(f"Invalid {field_name} JSON") from e
    return value
