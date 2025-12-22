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
"""Watchlist functionality for Chronicle."""

from typing import Any

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)


def list_watchlists(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    """Get a list of watchlists.

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve

    Returns:
        List of watchlists

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        base_url=client.base_url(APIVersion.V1),
        path="watchlists",
        items_key="watchlists",
        page_size=page_size,
        page_token=page_token,
    )


def get_watchlist(
    client: "ChronicleClient", watchlist_id: str
) -> dict[str, Any]:
    """Get a watchlist by ID

    Args:
        client: ChronicleClient instance
        watchlist_id: ID of the watchlist to retrieve

    Returns:
        Watchlist

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"watchlists/{watchlist_id}",
        api_version=APIVersion.V1,
    )


def delete_watchlist(
    client: "ChronicleClient", watchlist_id: str, force: bool | None = None
) -> dict[str, Any]:
    """Delete a watchlist by ID

    Args:
        client: ChronicleClient instance
        watchlist_id: ID of the watchlist to delete
        force: Optional. If set to true, any entities under this
         watchlist will also be deleted.
          (Otherwise, the request will only work if the
           watchlist has no entities.)

    Returns:
        Deleted watchlist

    Raises:
        APIError: If the API request fails
    """
    params = {}

    if force is not None:
        params["force"] = force

    return chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"watchlists/{watchlist_id}",
        api_version=APIVersion.V1,
        params=params,
    )


def create_watchlist(
    client: "ChronicleClient",
    name: str,
    display_name: str,
    multiplying_factor: float,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a watchlist

    Args:
        client: ChronicleClient instance
        name: Name of the watchlist
        display_name: Display name of the watchlist
        multiplying_factor: Multiplying factor for the watchlist
        description: Optional. Description of the watchlist

    Returns:
        Created watchlist

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path="watchlists",
        api_version=APIVersion.V1,
        json={
            "name": name,
            "displayName": display_name,
            "multiplyingFactor": multiplying_factor,
            "description": description,
            "entityPopulationMechanism": {"manual": {}},
        },
    )


def update_watchlist(
    client: "ChronicleClient",
    watchlist_id: str,
    display_name: str | None = None,
    description: str | None = None,
    multiplying_factor: float | None = None,
    entity_population_mechanism: dict[str, Any] | None = None,
    watchlist_user_preferences: dict[str, Any] | None = None,
    update_mask: str | None = None,
) -> dict[str, Any]:
    """Update a watchlist.

    Args:
        client: ChronicleClient instance.
        watchlist_id: ID of the watchlist to update.
        display_name: Optional. Display name of the watchlist.
            Must be 1-63 characters.
        description: Optional. Description of the watchlist.
        multiplying_factor: Optional. Weight applied to risk score
            for entities in this watchlist. Default is 1.0.
        entity_population_mechanism: Optional. Mechanism to populate
            entities in the watchlist. Example: {"manual": {}}.
        watchlist_user_preferences: Optional. User preferences for
            watchlist configuration. Example: {"pinned": True}.
        update_mask: Optional. Comma-separated list of fields to update.
            If not provided, all non-None fields will be updated.

    Returns:
        Updated watchlist.

    Raises:
        APIError: If the API request fails.
    """
    body = {}
    mask_fields = []

    if display_name is not None:
        body["displayName"] = display_name
        mask_fields.append("display_name")

    if description is not None:
        body["description"] = description
        mask_fields.append("description")

    if multiplying_factor is not None:
        body["multiplyingFactor"] = multiplying_factor
        mask_fields.append("multiplying_factor")

    if entity_population_mechanism is not None:
        body["entityPopulationMechanism"] = entity_population_mechanism
        mask_fields.append("entity_population_mechanism")

    if watchlist_user_preferences is not None:
        body["watchlistUserPreferences"] = watchlist_user_preferences
        mask_fields.append("watchlist_user_preferences")

    params = {}
    if update_mask is not None:
        params["updateMask"] = update_mask
    elif mask_fields:
        params["updateMask"] = ",".join(mask_fields)

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"watchlists/{watchlist_id}",
        api_version=APIVersion.V1,
        params=params if params else None,
        json=body,
    )
