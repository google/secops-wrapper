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
"""
Provides ingestion feed management functionality for Chronicle.
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from typing import Annotated, Any, TypedDict

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


# List of Allowed version for feed endpoints
ALLOWED_ENDPOINT_VERSIONS = [APIVersion.V1ALPHA, APIVersion.V1BETA]


@dataclass
class CreateFeedModel:
    """Model for creating a feed.

    Args:
        display_name: Display name for the feed
        details: Feed details as either a JSON string or dict.
            If string, will be parsed as JSON.
    """

    display_name: Annotated[str, "Display name for the feed"]
    details: Annotated[
        str | dict[str, Any], "Feed details as JSON string or dict"
    ]

    def __post_init__(self):
        """Convert string details to dict if needed"""
        if isinstance(self.details, str):
            try:
                self.details = json.loads(self.details)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string for details: {e}") from e

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class UpdateFeedModel:
    """Model for updating a feed.

    Args:
        display_name: Optional display name for the feed
        details: Optional feed details as either a JSON string or dict.
            If string, will be parsed as JSON.
    """

    display_name: Annotated[
        str | None, "Optional display name for the feed"
    ] = None
    details: Annotated[
        str | dict[str, Any] | None,
        "Optional feed details as JSON string or dict",
    ] = None

    def __post_init__(self):
        """Convert string details to dict if needed"""
        if isinstance(self.details, str):
            try:
                self.details = json.loads(self.details)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string for details: {e}") from e

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class FeedState(StrEnum):
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class FeedFailureDetails(TypedDict):
    error_code: str
    http_error_code: int
    error_cause: str
    error_action: str


class Feed(CreateFeedModel):
    name: str
    state: FeedState
    failure_msg: str
    read_only: bool
    last_feed_initiation_time: str
    failure_details: FeedFailureDetails


class FeedSecret(TypedDict):
    secret: str


def list_feeds(
    client,
    page_size: int = 100,
    page_token: str = None,
    api_version: APIVersion | None = None,
    as_list: bool = True,
) -> dict[str, Any] | list[Feed]:
    """List feeds.

    Args:
        client: ChronicleClient instance
        page_size: The maximum number of feeds to return
        page_token: A page token, received from a previous ListFeeds call
        api_version: (Optional) Preferred API version to use.
        as_list: If True, return only the list of feeds.
            If False, return dict with metadata and pagination tokens.
            Defaults to True for backward compatibility.

    Returns:
        If as_list is True: List of feed dictionaries.
        If as_list is False: Dict with feeds list and pagination metadata.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        path="feeds",
        items_key="feeds",
        api_version=api_version,
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )


def get_feed(
    client, feed_id: str, api_version: APIVersion | None = None
) -> Feed:
    """Get a feed by ID.

    Args:
        client: ChronicleClient instance
        feed_id: Feed ID
        api_version: (Optional) Preferred API version to use.

    Returns:
        Feed dictionary

    Raises:
        APIError: If the API request fails
    """
    feed_id = os.path.basename(feed_id)
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"feeds/{feed_id}",
        api_version=api_version,
        error_message="Failed to get feed",
    )


def create_feed(
    client,
    feed_config: CreateFeedModel,
    api_version: APIVersion | None = None,
) -> Feed:
    """Create a new feed.

    Args:
        client: ChronicleClient instance
        feed_config: Feed configuration model
        api_version: (Optional) Preferred API version to use.

    Returns:
        Created feed dictionary

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path="feeds",
        api_version=api_version,
        json=feed_config.to_dict(),
        error_message="Failed to create feed",
    )


def update_feed(
    client,
    feed_id: str,
    feed_config: CreateFeedModel,
    update_mask: list[str] | None | None = None,
    api_version: APIVersion | None = None,
) -> Feed:
    """Update an existing feed.

    Args:
        client: ChronicleClient instance
        feed_id: Feed ID
        feed_config: Feed configuration model
        update_mask: Optional list of fields to update
        api_version: (Optional) Preferred API version to use.

    Returns:
        Updated feed dictionary

    Raises:
        APIError: If the API request fails
    """
    if update_mask is None:
        update_mask = []
        feed_dict = feed_config.to_dict()
        for k, v in feed_dict.items():
            if v:
                update_mask.append(k)

    params = {}
    if update_mask:
        params = {"updateMask": ",".join(update_mask)}

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"feeds/{feed_id}",
        api_version=api_version,
        params=params if params else None,
        json=feed_config.to_dict(),
        error_message="Failed to update feed",
    )


def delete_feed(
    client, feed_id: str, api_version: APIVersion | None = None
) -> None:
    """Delete a feed.

    Args:
        client: ChronicleClient instance
        feed_id: Feed ID
        api_version: (Optional) Preferred API version to use.

    Raises:
        APIError: If the API request fails
    """
    chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"feeds/{feed_id}",
        api_version=api_version,
        error_message="Failed to delete feed",
    )


def disable_feed(
    client, feed_id: str, api_version: APIVersion | None = None
) -> Feed:
    """Disable a feed.

    Args:
        client: ChronicleClient instance
        feed_id: Feed ID
        api_version: (Optional) Preferred API version to use.

    Returns:
        Disabled feed dictionary

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"feeds/{feed_id}:disable",
        api_version=api_version,
        error_message="Failed to disable feed",
    )


def enable_feed(
    client, feed_id: str, api_version: APIVersion | None = None
) -> Feed:
    """Enable a feed.

    Args:
        client: ChronicleClient instance
        feed_id: Feed ID
        api_version: (Optional) Preferred API version to use.

    Returns:
        Enabled feed dictionary

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"feeds/{feed_id}:enable",
        api_version=api_version,
        error_message="Failed to enable feed",
    )


def generate_secret(
    client, feed_id: str, api_version: APIVersion | None = None
) -> FeedSecret:
    """Generate a secret for a feed.

    Args:
        client: ChronicleClient instance
        feed_id: Feed ID
        api_version: (Optional) Preferred API version to use.

    Returns:
        Dictionary containing the generated secret

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"feeds/{feed_id}:generateSecret",
        api_version=api_version,
        error_message="Failed to generate secret",
    )
