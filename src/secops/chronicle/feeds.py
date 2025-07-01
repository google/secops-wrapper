from secops.exceptions import APIError
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, TypedDict, Optional, Union, Annotated
import sys
import os
import json

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


@dataclass
class CreateFeedModel:
    """Model for creating a feed.

    Args:
        display_name: Display name for the feed
        details: Feed details as either a JSON string or dict. If string, will be parsed as JSON.
    """

    display_name: Annotated[str, "Display name for the feed"]
    details: Annotated[
        Union[str, Dict[str, Any]], "Feed details as JSON string or dict"
    ]

    def __post_init__(self):
        """Convert string details to dict if needed"""
        if isinstance(self.details, str):
            try:
                self.details = json.loads(self.details)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string for details: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class UpdateFeedModel:
    """Model for updating a feed.

    Args:
        display_name: Optional display name for the feed
        details: Optional feed details as either a JSON string or dict. If string, will be parsed as JSON.
    """

    display_name: Annotated[Optional[str], "Optional display name for the feed"] = None
    details: Annotated[
        Optional[Union[str, Dict[str, Any]]],
        "Optional feed details as JSON string or dict",
    ] = None

    def __post_init__(self):
        """Convert string details to dict if needed"""
        if isinstance(self.details, str):
            try:
                self.details = json.loads(self.details)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string for details: {e}")

    def to_dict(self) -> Dict[str, Any]:
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


def list_feeds(client, page_size: int = 100, page_token: str = None) -> List[Feed]:
    """List feeds.

    Args:
        client: ChronicleClient instance
    """
    feeds: list[dict] = []

    url = f"{client.base_url}/{client.instance_id}/feeds"
    more = True
    while more:
        params = {"pageSize": page_size, "pageToken": page_token}
        response = client.session.get(url, params=params)
        if response.status_code != 200:
            raise APIError(f"Failed to list feeds: {response.text}")

        data = response.json()
        if "feeds" in data:
            feeds.extend(data["feeds"])

        if "next_page_token" in data:
            params["pageToken"] = data["next_page_token"]
        else:
            more = False

    return feeds


def get_feed(client, feed_id: str) -> Feed:
    feed_id = os.path.basename(feed_id)
    url = f"{client.base_url}/{client.instance_id}/feeds/{feed_id}"
    response = client.session.get(url)
    if response.status_code != 200:
        raise APIError(f"Failed to get feed: {response.text}")

    return response.json()


def create_feed(client, feed_config: CreateFeedModel) -> Feed:
    url = f"{client.base_url}/{client.instance_id}/feeds"
    response = client.session.post(url, json=feed_config.to_dict())
    if response.status_code != 200:
        raise APIError(f"Failed to create feed: {response.text}")

    return response.json()


def update_feed(
    client,
    feed_id: str,
    feed_config: CreateFeedModel,
    update_mask: Optional[Union[List[str], None]] = None,
) -> Feed:
    url = f"{client.base_url}/{client.instance_id}/feeds/{feed_id}"

    if update_mask is None:
        update_mask = []
        feed_dict = feed_config.to_dict()
        for k, v in feed_dict.items():
            if v:
                update_mask.append(k)

    params = {}
    if update_mask:
        params = {"updateMask": ",".join(update_mask)}

    response = client.session.patch(url, params=params, json=feed_config.to_dict())
    if response.status_code != 200:
        raise APIError(f"Failed to update feed: {response.text}")

    return response.json()


def delete_feed(client, feed_id: str) -> None:
    url = f"{client.base_url}/{client.instance_id}/feeds/{feed_id}"
    response = client.session.delete(url)
    if response.status_code != 200:
        raise APIError(f"Failed to delete feed: {response.text}")


def disable_feed(client, feed_id: str) -> None:
    url = f"{client.base_url}/{client.instance_id}/feeds/{feed_id}:disable"
    response = client.session.post(url)
    if response.status_code != 200:
        raise APIError(f"Failed to disable feed: {response.text}")


def enable_feed(client, feed_id: str) -> None:
    url = f"{client.base_url}/{client.instance_id}/feeds/{feed_id}:enable"
    response = client.session.post(url)
    if response.status_code != 200:
        raise APIError(f"Failed to enable feed: {response.text}")


def generate_secret(client, feed_id: str) -> FeedSecret:
    url = f"{client.base_url}/{client.instance_id}/feeds/{feed_id}:generateSecret"
    response = client.session.post(url)
    if response.status_code != 200:
        raise APIError(f"Failed to generate secret: {response.text}")

    return response.json()
