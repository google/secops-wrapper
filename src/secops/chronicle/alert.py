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
"""Alert functionality for Chronicle."""

import json
import re
import time
from datetime import datetime, timezone
from typing import Any

from secops.exceptions import APIError


def _fix_json_formatting(data):
    """Fix JSON formatting issues in the response.

    Args:
        data: String data that might have JSON formatting issues

    Returns:
        String with JSON formatting fixed
    """
    if not data:
        return data

    # Fix missing commas between JSON objects
    data = data.replace("}\n{", "},\n{")

    # Fix trailing commas in arrays
    data = re.sub(r",\s*]", "]", data)

    # Fix trailing commas in objects
    data = re.sub(r",\s*}", "}", data)

    # Fix JSON array formatting
    if not data.startswith("[") and not data.endswith("]"):
        data = f"[{data}]"

    return data


def get_alerts(
    client,
    start_time: datetime,
    end_time: datetime,
    snapshot_query: str | None = 'feedback_summary.status != "CLOSED"',
    baseline_query: str | None = None,
    max_alerts: int | None = 1000,
    enable_cache: bool | None = None,
    max_attempts: int = 30,
    poll_interval: float = 1.0,
) -> dict[str, Any]:
    """Get alerts from Chronicle.

    This function uses the legacy:legacyFetchAlertsView endpoint to retrieve
    alerts that match the provided query parameters. The function will poll for
    results until the response is complete or the maximum number of attempts is
    reached.

    Args:
        client: ChronicleClient instance start_time: Start time for alert search
        (inclusive) end_time: End time for alert search (exclusive)
        snapshot_query: Query for filtering alerts. Uses a syntax similar to UDM
        search, with supported fields
            including: detection.rule_set, detection.rule_id,
            detection.rule_name, case_name, feedback_summary.status,
            feedback_summary.priority, etc.
        baseline_query: Optional baseline query to search for. The baseline
        query is used for this request and
            its results are cached for subsequent requests, so supplying
            additional filters in the snapshot_query will not require re-running
            the baseline query.
        max_alerts: Maximum number of alerts to return in results enable_cache:
        Whether to use cached results for the same baseline query and time range
        max_attempts: Maximum number of polling attempts poll_interval: Time in
        seconds between polling attempts

    Returns:
        Dictionary containing alert data including: - progress: Progress of the
        query (0-1) - complete: Whether the query is complete - alerts:
        Dictionary containing list of alerts - fieldAggregations: Aggregated
        alert fields - filteredAlertsCount: Count of alerts matching the
        snapshot query - baselineAlertsCount: Count of alerts matching the
        baseline query

    Raises:
        APIError: If the API request fails or times out
    """
    url = f"{client.base_url}/{client.instance_id}/legacy:legacyFetchAlertsView"

    # Build the request parameters
    # Ensure timezone awareness and convert to UTC
    start_time_utc = (
        start_time
        if start_time.tzinfo
        else start_time.replace(tzinfo=timezone.utc)
    )
    end_time_utc = (
        end_time if end_time.tzinfo else end_time.replace(tzinfo=timezone.utc)
    )

    params = {
        "timeRange.startTime": start_time_utc.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "timeRange.endTime": end_time_utc.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "snapshotQuery": snapshot_query,
    }

    # Add optional parameters
    if baseline_query:
        params["baselineQuery"] = baseline_query

    if max_alerts:
        params["alertListOptions.maxReturnedAlerts"] = max_alerts

    if enable_cache is not None:
        params["enableCache"] = (
            "ALERTS_FEATURE_PREFERENCE_ENABLED"
            if enable_cache
            else "ALERTS_FEATURE_PREFERENCE_DISABLED"
        )

    # Initialize for polling
    complete = False
    attempts = 0
    final_result = {}

    # Poll until we get a complete response or hit max attempts
    while not complete and attempts < max_attempts:
        attempts += 1

        # Make the request
        response = client.session.get(url, params=params, stream=True)

        if response.status_code != 200:
            raise APIError(f"Failed to get alerts: {response.text}")

        # Process the response
        try:
            # Handle streaming response
            if hasattr(response, "iter_lines"):
                result_text = ""
                for line in response.iter_lines():
                    if line:
                        # Convert bytes to string if needed
                        if isinstance(line, bytes):
                            line = line.decode("utf-8")
                        result_text += line + "\n"
            else:
                result_text = response.text

            # Fix any JSON formatting issues
            result_text = _fix_json_formatting(result_text)

            # Parse the JSON response
            result = json.loads(result_text)

            # Handle list response
            if isinstance(result, list) and len(result) > 0:
                # Merge multiple responses if needed
                merged_result = {}
                for item in result:
                    for key, value in item.items():
                        if key not in merged_result:
                            merged_result[key] = value
                        elif isinstance(value, dict) and isinstance(
                            merged_result[key], dict
                        ):
                            # Merge nested dictionaries
                            merged_result[key].update(value)
                        elif isinstance(value, list) and isinstance(
                            merged_result[key], list
                        ):
                            # Merge lists
                            merged_result[key].extend(value)
                result = merged_result

            # Check if the response is complete
            final_result = result
            complete = result.get("complete", False)

            # If not complete, wait before polling again
            if not complete:
                time.sleep(poll_interval)

        except ValueError as e:
            raise APIError(f"Failed to parse alerts response: {str(e)}") from e

    if not complete and attempts >= max_attempts:
        raise APIError(f"Alert search timed out after {max_attempts} attempts")

    return final_result
