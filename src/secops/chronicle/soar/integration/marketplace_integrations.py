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
"""Integrations functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.format_utils import (
    remove_none_values,
    format_resource_id,
)
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def list_marketplace_integrations(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """Get a list of marketplace integrations.

    Args:
        client: ChronicleClient instance
        page_size: Number of results to return per page
        page_token: Token for the page to retrieve
        filter_string: Filter expression to filter marketplace integrations
        order_by: Field to sort the marketplace integrations by
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of marketplace integrations instead
            of a dict with marketplace integrations list and nextPageToken.

    Returns:
        If as_list is True: List of marketplace integrations.
        If as_list is False: Dict with marketplace integrations list and
            nextPageToken.

    Raises:
        APIError: If the API request fails
    """
    field_map = remove_none_values(
        {
            "filter": filter_string,
            "orderBy": order_by,
        }
    )

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path="marketplaceIntegrations",
        items_key="marketplaceIntegrations",
        page_size=page_size,
        page_token=page_token,
        extra_params=field_map,
        as_list=as_list,
    )


def get_marketplace_integration(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a marketplace integration by integration name

    Args:
        client: ChronicleClient instance
        integration_name: Name of the marketplace integration to retrieve
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Marketplace integration details

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            "marketplaceIntegrations/" f"{format_resource_id(integration_name)}"
        ),
        api_version=api_version,
    )


def get_marketplace_integration_diff(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get the differences between the currently installed version of
        an integration and the commercial version available in the marketplace.

    Args:
        client: ChronicleClient instance
        integration_name: Name of the marketplace integration to compare
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Marketplace integration diff details

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            "marketplaceIntegrations/"
            f"{format_resource_id(integration_name)}:fetchCommercialDiff"
        ),
        api_version=api_version,
    )


def install_marketplace_integration(
    client: "ChronicleClient",
    integration_name: str,
    override_mapping: bool | None = None,
    staging: bool | None = None,
    version: str | None = None,
    restore_from_snapshot: bool | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Install a marketplace integration by integration name

    Args:
        client: ChronicleClient instance
        integration_name: Name of the marketplace integration to install
        override_mapping: Optional. Determines if the integration should
            override the ontology if already installed, if not provided, set to
            false by default.
        staging: Optional. Determines if the integration should be installed
            as staging or production, if not provided, installed as production.
        version: Optional. Determines which version of the integration
            should be installed.
        restore_from_snapshot: Optional. Determines if the integration
            should be installed from existing integration snapshot.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Installed marketplace integration details

    Raises:
        APIError: If the API request fails
    """
    field_map = remove_none_values(
        {
            "overrideMapping": override_mapping,
            "staging": staging,
            "version": version,
            "restoreFromSnapshot": restore_from_snapshot,
        }
    )

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            "marketplaceIntegrations/"
            f"{format_resource_id(integration_name)}:install"
        ),
        json=field_map,
        api_version=api_version,
    )


def uninstall_marketplace_integration(
    client: "ChronicleClient",
    integration_name: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Uninstall a marketplace integration by integration name

    Args:
        client: ChronicleClient instance
        integration_name: Name of the marketplace integration to uninstall
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Empty dictionary if uninstallation is successful

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            "marketplaceIntegrations/"
            f"{format_resource_id(integration_name)}:uninstall"
        ),
        api_version=api_version,
    )
