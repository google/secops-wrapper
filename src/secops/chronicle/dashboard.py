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
"""
Module for managing Google SecOps Native Dashboards.

This module provides functions to manage dashboard and charts.
"""

import json
import sys
from typing import TYPE_CHECKING, Any

from secops.chronicle.models import (
    DashboardChart,
    DashboardQuery,
    InputInterval,
    TileType,
)
from secops.exceptions import APIError, SecOpsError
from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_request,
    chronicle_paginated_request,
)
from secops.chronicle.utils.format_utils import (
    format_resource_id,
    parse_json_list,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


class DashboardAccessType(StrEnum):
    """Valid dashboard access types."""

    PUBLIC = "DASHBOARD_PUBLIC"
    PRIVATE = "DASHBOARD_PRIVATE"


class DashboardView(StrEnum):
    """Valid dashboard views."""

    BASIC = "NATIVE_DASHBOARD_VIEW_BASIC"
    FULL = "NATIVE_DASHBOARD_VIEW_FULL"


_VALID_DASHBOARD_KEYS = frozenset(
    {"dashboard", "dashboardCharts", "dashboardQueries"}
)


def create_dashboard(
    client: "ChronicleClient",
    display_name: str,
    access_type: DashboardAccessType,
    description: str | None = None,
    filters: list[dict[str, Any]] | str | None = None,
    charts: list[dict[str, Any]] | str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Create a new native dashboard.

    Args:
        client: ChronicleClient instance
        display_name: Name of the dashboard to create
        access_type: Access type for the dashboard (Public or Private)
        description: Description for the dashboard
        filters: List of filters to apply to the dashboard
        charts: List of charts to include in the dashboard
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the created dashboard details

    Raises:
        APIError: If the API request fails
    """
    if filters is not None:
        filters = parse_json_list(filters, "filters")

    if charts is not None:
        charts = parse_json_list(charts, "charts")

    definition: dict[str, Any] = {}
    if filters is not None:
        definition["filters"] = filters
    if charts is not None:
        definition["charts"] = charts

    payload = {
        "displayName": display_name,
        "definition": definition,
        "access": access_type,
        "type": "CUSTOM",
    }

    if description is not None:
        payload["description"] = description

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="nativeDashboards",
        api_version=api_version,
        json=payload,
        error_message="Failed to create dashboard",
    )


def import_dashboard(
    client: "ChronicleClient",
    dashboard: dict[str, Any],
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Import a native dashboard.

    Args:
        client: ChronicleClient instance
        dashboard: Dashboard data to import, must contain at least one of:
            'dashboard', 'dashboardCharts', or 'dashboardQueries'
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the imported dashboard details

    Raises:
        SecOpsError: If the dashboard data contains none of the required keys
        APIError: If the API request fails
    """
    if not any(key in dashboard for key in _VALID_DASHBOARD_KEYS):
        raise SecOpsError(
            f'Dashboard must contain at least one of: {", ".join(_VALID_DASHBOARD_KEYS)}'
        )

    payload = {"source": {"dashboards": [dashboard]}}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="nativeDashboards:import",
        api_version=api_version,
        json=payload,
        error_message="Failed to import dashboard",
    )


def export_dashboard(
    client: "ChronicleClient",
    dashboard_names: list[str],
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Export native dashboards.
    It supports single dashboard export operation only.

    Args:
        client: ChronicleClient instance
        dashboard_names: List of dashboard resource names to export.
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the exported dashboards.

    Raises:
        APIError: If the API request fails.
    """
    # Ensure dashboard names are fully qualified
    qualified_names = []
    for name in dashboard_names:
        if not name.startswith("projects/"):
            name = f"{client.instance_id}/nativeDashboards/{name}"
        qualified_names.append(name)

    payload = {"names": qualified_names}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="nativeDashboards:export",
        api_version=api_version,
        json=payload,
        error_message="Failed to export dashboards",
    )


def list_dashboards(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
    as_list: bool = False,
) -> dict[str, Any]:
    """List all available dashboards in Basic View.

    Args:
        client: ChronicleClient instance
        page_size: Maximum number of results to return
        page_token: Token for pagination
        api_version: Preferred API version to use. Defaults to V1ALPHA
        as_list: Whether to return results as a list or dictionary

    Returns:
        If as_list is True: List of dashboards.
        If as_list is False: Dictionary containing list of dashboards and pagination info.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path="nativeDashboards",
        items_key="nativeDashboards",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )


def get_dashboard(
    client: "ChronicleClient",
    dashboard_id: str,
    view: DashboardView | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Get information about a specific dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to retrieve
        view: Level of detail to include in the response
            Defaults to BASIC
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing dashboard details

    Raises:
        APIError: If the API request fails
    """
    dashboard_id = format_resource_id(dashboard_id)

    view = view or DashboardView.BASIC
    params = {"view": view.value}

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"nativeDashboards/{dashboard_id}",
        api_version=api_version,
        params=params,
        error_message=f"Failed to get dashboard with ID {dashboard_id}",
    )


# Updated update_dashboard function
def update_dashboard(
    client: "ChronicleClient",
    dashboard_id: str,
    display_name: str | None = None,
    description: str | None = None,
    filters: list[dict[str, Any]] | str | None = None,
    charts: list[dict[str, Any]] | str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Update an existing dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to update
        display_name: New name for the dashboard (optional)
        description: New description for the dashboard (optional)
        filters: New filters for the dashboard (optional)
        charts: New charts for the dashboard (optional)
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the updated dashboard details

    Raises:
        ValueError: If no fields are provided to update
        APIError: If filters or charts JSON is invalid, or if the API request fails
    """
    dashboard_id = format_resource_id(dashboard_id)

    if filters is not None:
        filters = parse_json_list(filters, "filters")

    if charts is not None:
        charts = parse_json_list(charts, "charts")

    payload = {}
    update_mask = []

    if display_name is not None:
        payload["displayName"] = display_name
        update_mask.append("display_name")

    if description is not None:
        payload["description"] = description
        update_mask.append("description")

    definition = {}
    if filters is not None:
        definition["filters"] = filters
        update_mask.append("definition.filters")

    if charts is not None:
        definition["charts"] = charts
        update_mask.append("definition.charts")

    if definition:
        payload["definition"] = definition

    if not update_mask:
        raise ValueError("At least one field must be provided to update")

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"nativeDashboards/{dashboard_id}",
        api_version=api_version,
        json=payload,
        params={"updateMask": ",".join(update_mask)},
        error_message=f"Failed to update dashboard with ID {dashboard_id}",
    )


def delete_dashboard(
    client: "ChronicleClient",
    dashboard_id: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Delete a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to delete
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Empty dictionary on success

    Raises:
        APIError: If the API request fails
    """
    dashboard_id = format_resource_id(dashboard_id)

    return chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"nativeDashboards/{dashboard_id}",
        api_version=api_version,
        error_message=f"Failed to delete dashboard with ID {dashboard_id}",
    )


def duplicate_dashboard(
    client: "ChronicleClient",
    dashboard_id: str,
    display_name: str,
    access_type: DashboardAccessType,
    description: str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Duplicate a existing dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to duplicate
        display_name: New name for the duplicated dashboard
        access_type: Access type for the duplicated dashboard
                    (DashboardAccessType.PRIVATE or DashboardAccessType.PUBLIC)
        description: Description for the duplicated dashboard
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the duplicated dashboard details

    Raises:
        APIError: If the API request fails
    """
    dashboard_id = format_resource_id(dashboard_id)

    payload = {
        "nativeDashboard": {
            "displayName": display_name,
            "access": access_type.value,
            "type": "CUSTOM",
        }
    }

    if description:
        payload["nativeDashboard"]["description"] = description

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"nativeDashboards/{dashboard_id}:duplicate",
        api_version=api_version,
        json=payload,
        error_message=f"Failed to duplicate dashboard with ID {dashboard_id}",
    )


def add_chart(
    client: "ChronicleClient",
    dashboard_id: str,
    display_name: str,
    chart_layout: dict[str, Any] | str,
    tile_type: TileType | None = None,
    chart_datasource: dict[str, Any] | str | None = None,
    visualization: dict[str, Any] | str | None = None,
    drill_down_config: dict[str, Any] | str | None = None,
    description: str | None = None,
    query: str | None = None,
    interval: InputInterval | dict[str, Any] | str | None = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
    **kwargs,
) -> dict[str, Any]:
    """Add a chart to a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to add the chart to
        display_name: The display name for the chart
        chart_layout: The chart layout for the chart
        tile_type: The tile type for the chart
            Defaults to TileType.VISUALIZATION
        chart_datasource: The chart datasource for the chart
        visualization: The visualization for the chart
        drill_down_config: The drill down config for the chart
        description: The description for the chart
        query: The search query for chart
        interval: The time interval for the query
        api_version: Preferred API version to use. Defaults to V1ALPHA
        **kwargs: Additional keyword arguments
            (It will be added to the request payload)

    Returns:
        Dictionary containing the updated dashboard with new chart

    Raises:
        APIError: If the API request fails or if JSON parsing fails
    """
    dashboard_id = format_resource_id(dashboard_id)

    tile_type = TileType.VISUALIZATION if tile_type is None else tile_type

    # Convert JSON string to dictionary
    try:
        if isinstance(chart_layout, str):
            chart_layout = json.loads(chart_layout)
        if chart_datasource and isinstance(chart_datasource, str):
            chart_datasource = json.loads(chart_datasource)
        if visualization and isinstance(visualization, str):
            visualization = json.loads(visualization)
        if drill_down_config and isinstance(drill_down_config, str):
            drill_down_config = json.loads(drill_down_config)
        if interval and isinstance(interval, str):
            interval = json.loads(interval)
    except ValueError as e:
        raise APIError(
            f"Failed to parse JSON. Must be a valid JSON string: {e}"
        ) from e

    payload = {
        "dashboardChart": {
            "displayName": display_name,
            "tileType": tile_type.value,
        },
        "chartLayout": chart_layout,
    }

    if description:
        payload["dashboardChart"]["description"] = description
    if chart_datasource:
        payload["dashboardChart"]["chartDatasource"] = chart_datasource
    if visualization:
        payload["dashboardChart"]["visualization"] = visualization
    if drill_down_config:
        payload["dashboardChart"]["drillDownConfig"] = drill_down_config

    if kwargs:
        payload.update(kwargs)

    if interval and isinstance(interval, dict):
        interval = InputInterval.from_dict(interval)

    if query and interval:
        payload.update(
            {
                "dashboardQuery": {
                    "query": query,
                    "input": interval.to_dict(),
                }
            }
        )

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"nativeDashboards/{dashboard_id}:addChart",
        api_version=api_version,
        json=payload,
        error_message=f"Failed to add chart to dashboard with ID {dashboard_id}",
    )


def get_chart(
    client: "ChronicleClient",
    chart_id: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Get detail for dashboard chart.

    Args:
        client: ChronicleClient instance
        chart_id: ID of the chart
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dict[str, Any]: Dictionary containing chart details

    Raises:
        APIError: If the API request fails
    """
    chart_id = format_resource_id(chart_id)
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"dashboardCharts/{chart_id}",
        api_version=api_version,
        error_message=f"Failed to get chart with ID {chart_id}",
    )


def remove_chart(
    client: "ChronicleClient",
    dashboard_id: str,
    chart_id: str,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Remove a chart from a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard containing the chart
        chart_id: ID of the chart to remove
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the updated dashboard

    Raises:
        APIError: If the API request fails
    """
    dashboard_id = format_resource_id(dashboard_id)
    chart_id = format_resource_id(chart_id)

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"nativeDashboards/{dashboard_id}:removeChart",
        api_version=api_version,
        json={"dashboardChart": chart_id},
        error_message=f"Failed to remove chart with ID {chart_id} from dashboard with ID {dashboard_id}",
    )


def edit_chart(
    client: "ChronicleClient",
    dashboard_id: str,
    dashboard_query: None | (dict[str, Any] | DashboardQuery | str) = None,
    dashboard_chart: None | (dict[str, Any] | DashboardChart | str) = None,
    api_version: APIVersion | None = APIVersion.V1ALPHA,
) -> dict[str, Any]:
    """Edit an existing chart in a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard containing the chart
        dashboard_query: Chart Query to edit in JSON or JSON String
            eg:{
                "name": "<query_id>",
                "query": "<chart query>",
                "input": {},
                "etag":"123131231321321"
            }
        dashboard_chart: Chart to edit in JSON or JSON string
            eg:{
                "name": "<chart_id>"
                "displayName": "<chart display name>",
                "description": "<chart description>",
                "visualization": {},
                "chartDatasource": { "dataSources":[]},
                "etag": "123131231321321"
            }
        api_version: Preferred API version to use. Defaults to V1ALPHA

    Returns:
        Dictionary containing the updated dashboard with edited chart

    Raises:
        APIError: If the API request fails or if JSON parsing fails
    """
    dashboard_id = format_resource_id(dashboard_id)

    payload = {}
    update_fields = []

    if dashboard_query:
        if isinstance(dashboard_query, str):
            try:
                dashboard_query = DashboardQuery.from_dict(
                    json.loads(dashboard_query)
                )
            except ValueError as e:
                raise SecOpsError("Invalid dashboard query JSON") from e
        if isinstance(dashboard_query, dict):
            dashboard_query = DashboardQuery.from_dict(dashboard_query)

        if not dashboard_query.name.startswith("projects/"):
            dashboard_query.name = (
                f"{client.instance_id}/dashboardQueries/{dashboard_query.name}"
            )
        payload["dashboardQuery"] = dashboard_query.to_dict()
        update_fields.extend(dashboard_query.update_fields())

    if dashboard_chart:
        if isinstance(dashboard_chart, str):
            try:
                dashboard_chart = DashboardChart.from_dict(
                    json.loads(dashboard_chart)
                )
            except ValueError as e:
                raise SecOpsError("Invalid dashboard chart JSON") from e
        if isinstance(dashboard_chart, dict):
            dashboard_chart = DashboardChart.from_dict(dashboard_chart)

        if not dashboard_chart.name.startswith("projects/"):
            dashboard_chart.name = (
                f"{client.instance_id}/dashboardCharts/{dashboard_chart.name}"
            )
        payload["dashboardChart"] = dashboard_chart.to_dict()
        update_fields.extend(dashboard_chart.update_fields())

    payload["editMask"] = ",".join(update_fields)

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"nativeDashboards/{dashboard_id}:editChart",
        api_version=api_version,
        json=payload,
        error_message=f"Failed to edit chart in dashboard with ID {dashboard_id}",
    )
