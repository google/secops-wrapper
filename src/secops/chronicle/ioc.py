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
"""IOC functionality for Chronicle."""

from datetime import datetime
from typing import Any

from secops.exceptions import APIError


def list_iocs(
    client,
    start_time: datetime,
    end_time: datetime,
    max_matches: int = 1000,
    add_mandiant_attributes: bool = True,
    prioritized_only: bool = False,
) -> dict[str, Any]:
    """List IoCs from Chronicle.

    Args:
        client: ChronicleClient instance
        start_time: Start time for the IoC search
        end_time: End time for the IoC search
        max_matches: Maximum number of matches to return
        add_mandiant_attributes: Whether to add Mandiant attributes
        prioritized_only: Whether to only include prioritized IoCs

    Returns:
        Dictionary with IoC matches

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}"
        "/legacy:legacySearchEnterpriseWideIoCs"
    )

    params = {
        "timestampRange.startTime": start_time.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "timestampRange.endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "maxMatchesToReturn": max_matches,
        "addMandiantAttributes": add_mandiant_attributes,
        "fetchPrioritizedIocsOnly": prioritized_only,
    }

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(f"Failed to list IoCs: {response.text}")

    try:
        data = response.json()

        # Process each IoC match to ensure consistent field names
        if "matches" in data:
            for match in data["matches"]:
                # Convert timestamps if present
                for ts_field in [
                    "iocIngestTimestamp",
                    "firstSeenTimestamp",
                    "lastSeenTimestamp",
                ]:
                    if ts_field in match:
                        match[ts_field] = match[ts_field].rstrip("Z")

                # Ensure consistent field names
                if (
                    "filterProperties" in match
                    and "stringProperties" in match["filterProperties"]
                ):
                    props = match["filterProperties"]["stringProperties"]
                    match["properties"] = {
                        k: [v["rawValue"] for v in values["values"]]
                        for k, values in props.items()
                    }

                # Process associations
                if "associationIdentifier" in match:
                    # Remove duplicate associations
                    # (some have same name but different regionCode)
                    seen = set()
                    unique_associations = []
                    for assoc in match["associationIdentifier"]:
                        key = (assoc["name"], assoc["associationType"])
                        if key not in seen:
                            seen.add(key)
                            unique_associations.append(assoc)
                    match["associationIdentifier"] = unique_associations

        return data

    except Exception as e:
        raise APIError(f"Failed to process IoCs response: {str(e)}") from e
