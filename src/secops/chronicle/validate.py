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
"""Query validation functionality for Chronicle."""

from typing import Any

from secops.exceptions import APIError


def validate_query(client, query: str) -> dict[str, Any]:
    """Validate a UDM query against the Chronicle API.

    Args:
        client: ChronicleClient instance
        query: Query string to validate

    Returns:
        Dictionary containing query validation results, including:
        - isValid: Boolean indicating if the query is valid
        - queryType: Type of query
            (e.g., QUERY_TYPE_UDM_QUERY, QUERY_TYPE_STATS_QUERY)
        - validationMessage: Error message if the query is invalid

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}:validateQuery"

    # Replace special characters with Unicode escapes
    encoded_query = query.replace("!", "\u0021")

    params = {
        "rawQuery": encoded_query,
        "dialect": "DIALECT_UDM_SEARCH",
        "allowUnreplacedPlaceholders": "false",
    }

    response = client.session.get(url, params=params)

    # Handle successful validation
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return {"isValid": True, "queryType": "QUERY_TYPE_UNKNOWN"}

    # If validation failed, return structured error
    # For any status code other than 200, return an error structure
    if response.status_code == 400:
        try:
            # Try to parse the error message
            error_data = response.json()
            validation_message = error_data.get("error", {}).get(
                "message", "Invalid query syntax"
            )
            return {
                "isValid": False,
                "queryType": "QUERY_TYPE_UNKNOWN",
                "validationMessage": validation_message,
            }
        except ValueError:
            pass

    # For any other status codes, raise an APIError
    raise APIError(f"Query validation failed: {response.text}")
