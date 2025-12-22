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
"""Natural language search functionality for Chronicle."""

import time
from datetime import datetime
from typing import Any

from secops.exceptions import APIError


def translate_nl_to_udm(client, text: str) -> str:
    """Translate natural language query to UDM search syntax.

    Args:
        client: ChronicleClient instance
        text: Natural language query text

    Returns:
        UDM search query string

    Raises:
        APIError: If the API request fails or no valid query can be
            generated after retries
    """
    max_retries = 10
    retry_count = 0
    wait_time = 5  # seconds, will double with each retry

    url = (
        f"https://{client.region}-chronicle.googleapis.com/v1alpha/projects"
        f"/{client.project_id}/locations/{client.region}/instances"
        f"/{client.customer_id}:translateUdmQuery"
    )

    payload = {"text": text}

    while retry_count <= max_retries:
        try:
            response = client.session.post(url, json=payload)

            if response.status_code != 200:
                # If it's a 429 error, handle it specially
                if (
                    response.status_code == 429
                    or "RESOURCE_EXHAUSTED" in response.text
                ):
                    if retry_count < max_retries:
                        retry_count += 1
                        print(
                            "Received 429 error in translation, retrying "
                            f"({retry_count}/{max_retries}) after "
                            f"{wait_time} seconds"
                        )
                        time.sleep(wait_time)
                        wait_time *= 2  # Double the wait time for next retry
                        continue
                # For non-429 errors or if we've exhausted retries
                raise APIError(f"Chronicle API request failed: {response.text}")

            result = response.json()

            if "message" in result:
                raise APIError(result["message"])

            return result.get("query", "")

        except APIError as e:
            # Only retry for 429 errors
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if retry_count < max_retries:
                    retry_count += 1
                    print(
                        "Received 429 error, retrying "
                        f"({retry_count}/{max_retries}) after "
                        f"{wait_time} seconds"
                    )
                    time.sleep(wait_time)
                    wait_time *= 2  # Double the wait time for next retry
                    continue
            # For other errors or if we've exhausted retries, raise the error
            raise e

    # This should not happen, but just in case
    raise APIError("Failed to translate query after retries")


def nl_search(
    client,
    text: str,
    start_time: datetime,
    end_time: datetime,
    max_events: int = 10000,
    case_insensitive: bool = True,
    max_attempts: int = 30,
) -> dict[str, Any]:
    """Perform a search using natural language that is translated to UDM.

    Args:
        client: ChronicleClient instance
        text: Natural language query text
        start_time: Search start time
        end_time: Search end time
        max_events: Maximum events to return
        case_insensitive: Whether to perform case-insensitive search
        max_attempts: Maximum number of polling attempts

    Returns:
        Dict containing the search results with events

    Raises:
        APIError: If the API request fails after retries
    """
    max_retries = 10
    retry_count = 0
    wait_time = 5  # seconds, will double with each retry

    last_error = None

    while retry_count <= max_retries:
        try:
            # First translate the natural language to UDM query
            udm_query = translate_nl_to_udm(client, text)

            # Then perform the UDM search
            return client.search_udm(
                query=udm_query,
                start_time=start_time,
                end_time=end_time,
                max_events=max_events,
                case_insensitive=case_insensitive,
                max_attempts=max_attempts,
            )
        except APIError as e:
            last_error = e
            # Check if it's a 429 error (too many requests)
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if retry_count < max_retries:
                    retry_count += 1
                    # Log retry attempt
                    print(
                        "Received 429 error, retrying "
                        f"({retry_count}/{max_retries}) after "
                        f"{wait_time} seconds"
                    )
                    time.sleep(wait_time)
                    wait_time *= 2  # Double the wait time for next retry
                    continue
            # For other errors or if we've exhausted retries, raise the error
            raise e

    # If we've reached here, we've exhausted retries
    if last_error:
        raise last_error

    # This should not happen, but just in case
    raise APIError("Failed to perform search after retries")
