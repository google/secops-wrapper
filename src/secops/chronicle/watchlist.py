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

from typing import Dict, Any, Optional

from secops.chronicle.utils.request_utils import paginated_request


def list_watchlists(
    client,
    page_size: Optional[str] = None,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Get a list of all watchlists

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve

    Returns:
        List of watchlists

    Raises:
        APIError: If the API request fails
    """
    return paginated_request(
        client,
        base_url=client.base_v1_url,
        path="watchlists",
        items_key="watchlists",
        page_size=page_size,
        page_token=page_token,
    )


def get_watchlist(client, watchlist_id: str) -> Dict[str, Any]:
    """Get a watchlist by ID

    Args:
        client: ChronicleClient instance
        watchlist_id: ID of the watchlist to retrieve

    Returns:
        Watchlist

    Raises:
        APIError: If the API request fails
    """
    return client.session.get(
        f"{client.base_v1_url}/{client.instance_id}/watchlists/{watchlist_id}",
    ).json()


def delete_watchlist(
    client, watchlist_id: str, force: Optional[bool] = None
) -> Dict[str, Any]:
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
    params = {"force": force}
    return client.session.delete(
        f"{client.base_v1_url}/{client.instance_id}/watchlists/{watchlist_id}",
        params=params,
    ).json()


def create_watchlist(
    client,
    name: str,
    display_name: str,
    multiplying_factor: float,
    description: Optional[str] = None,
) -> Dict[str, Any]:
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

    return client.session.post(
        f"{client.base_v1_url}/{client.instance_id}/watchlists",
        json={
            "name": name,
            "displayName": display_name,
            "multiplyingFactor": multiplying_factor,
            "description": description,
            "entityPopulationMechanism": {"manual": {}},
        },
    ).json()
