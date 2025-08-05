"""
Module for managing Google SecOps Native Dashboards.

This module provides functions to 
create, list, retrieve, update, delete dashboards, and manage dashboard charts.
"""

import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union

from secops.exceptions import APIError

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


class TileType(StrEnum):
    """Valid tile types."""

    VISUALIZATION = "TILE_TYPE_VISUALIZATION"
    BUTTON = "TILE_TYPE_BUTTON"


@dataclass
class InputInterval:
    """Input interval values to query for chart."""

    time_window: Optional[Dict[str, Any]] = None
    relative_time: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from a dictionary."""
        return cls(
            time_window=data.get("time_window") or data.get("timeWindow"),
            relative_time=data.get("relative_time") or data.get("relativeTime"),
        )

    def __post_init__(self):
        """Validate that only one of `time_window` or `relative_time` is set."""
        if self.time_window is not None and self.relative_time is not None:
            raise ValueError(
                "Only one of `time_window` or `relative_time` can be set."
            )
        if self.time_window is None and self.relative_time is None:
            raise ValueError(
                "One of `time_window` or `relative_time` must be set."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        result = {}
        if self.time_window:
            result["timeWindow"] = self.time_window
        if self.relative_time:
            result["relativeTime"] = self.relative_time
        return result


def create_dashboard(
    client,
    display_name: str,
    access_type: DashboardAccessType,
    description: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    charts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Create a new native dashboard.

    Args:
        client: ChronicleClient instance
        display_name: Name of the dashboard to create
        access_type: Access type for the dashboard (Public or Private)
        description: Description for the dashboard
        filters: Dictionary of filters to apply to the dashboard
        charts: List of charts to include in the dashboard

    Returns:
        Dictionary containing the created dashboard details

    Raises:
        APIError: If the API request fails
    """
    url = f"{client.base_url}/{client.instance_id}/nativeDashboards"

    payload = {
        "displayName": display_name,
        "definition": {},
        "access": access_type,
        "type": "CUSTOM",
    }

    if description:
        payload["description"] = description

    if filters:
        payload["definition"]["filters"] = filters

    if charts:
        payload["definition"]["charts"] = charts

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(
            f"Failed to create dashboard: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def list_dashboards(
    client,
    page_size: Optional[int] = None,
    page_token: Optional[str] = None,
) -> Dict[str, Any]:
    """List all available dashboards in Basic View.

    Args:
        client: ChronicleClient instance
        page_size: Maximum number of results to return
        page_token: Token for pagination

    Returns:
        Dictionary containing dashboard list and pagination info
    """
    url = f"{client.base_url}/{client.instance_id}/nativeDashboards"
    params = {}
    if page_size:
        params["pageSize"] = page_size
    if page_token:
        params["pageToken"] = page_token

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(
            f"Failed to list dashboards: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def get_dashboard(
    client,
    dashboard_id: str,
    view: Optional[DashboardView] = None,
) -> Dict[str, Any]:
    """Get information about a specific dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to retrieve
        view: Level of detail to include in the response
            Defaults to BASIC

    Returns:
        Dictionary containing dashboard details
    """

    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"nativeDashboards/{dashboard_id}"
    )
    view = view or DashboardView.BASIC
    params = {"view": view.value}

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(
            f"Failed to get dashboard: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


# Updated update_dashboard function
def update_dashboard(
    client,
    dashboard_id: str,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    charts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Update an existing dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to update
        display_name: New name for the dashboard (optional)
        description: New description for the dashboard (optional)
        filters: New filters for the dashboard (optional)
        charts: New charts for the dashboard (optional)

    Returns:
        Dictionary containing the updated dashboard details
    """
    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"nativeDashboards/{dashboard_id}"
    )

    payload = {"definition": {}}
    update_mask = []

    if display_name is not None:
        payload["displayName"] = display_name
        update_mask.append("display_name")

    if description is not None:
        payload["description"] = description
        update_mask.append("description")

    if filters is not None:
        payload["definition"]["filters"] = filters
        update_mask.append("definition.filters")

    if charts is not None:
        payload["definition"]["charts"] = charts
        update_mask.append("definition.charts")

    params = {"updateMask": ",".join(update_mask)}

    response = client.session.patch(url, json=payload, params=params)

    if response.status_code != 200:
        raise APIError(
            f"Failed to update dashboard: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def delete_dashboard(client, dashboard_id: str) -> Dict[str, Any]:
    """Delete a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to delete

    Returns:
        Empty dictionary on success
    """

    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    url = (
        f"{client.base_url}/{client.instance_id}"
        f"/nativeDashboards/{dashboard_id}"
    )

    response = client.session.delete(url)

    if response.status_code != 200:
        raise APIError(
            f"Failed to delete dashboard: Status {response.status_code}, "
            f"Response: {response.text}"
        )


def add_chart(
    client,
    dashboard_id: str,
    display_name: str,
    chart_layout: Dict[str, Any],
    tile_type: Optional[TileType] = None,
    chart_datasource: Optional[Dict[str, Any]] = None,
    visualization: Optional[Dict[str, Any]] = None,
    drill_down_config: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    query: Optional[str] = None,
    interval: Optional[Union[InputInterval, Dict[str, Any]]] = None,
    **kwargs,
) -> Dict[str, Any]:
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
        **kwargs: Additional keyword arguments
            (It will be added to the request payload)


    Returns:
        Dictionary containing the updated dashboard with new chart
    """
    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"nativeDashboards/{dashboard_id}:addChart"
    )

    tile_type = TileType.VISUALIZATION if tile_type is None else tile_type

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

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(
            f"Failed to add chart: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def remove_chart(
    client,
    dashboard_id: str,
    chart_id: str,
) -> Dict[str, Any]:
    """Remove a chart from a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard containing the chart
        chart_id: ID of the chart to remove

    Returns:
        Dictionary containing the updated dashboard

    Raises:
        APIError: If the API request fails
    """
    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    if not chart_id.startswith("projects/"):
        chart_id = f"{client.instance_id}/dashboardCharts/{chart_id}"

    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"nativeDashboards/{dashboard_id}:removeChart"
    )

    payload = {"dashboardChart": chart_id}

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(
            f"Failed to remove chart: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def execute_query(
    client,
    query: str,
    interval: Union[InputInterval, Dict[str, Any]],
    filters: Optional[List[Dict[str, Any]]] = None,
    clear_cache: Optional[bool] = None,
) -> Dict[str, Any]:
    """Execute a dashboard query and retrieve results.

    Args:
        client: ChronicleClient instance
        query: The UDM search query to execute
        interval: The time interval for the query
        filters: Filters to apply to the query
        clear_cache: Flag to read from database instead of cache

    Returns:
        Dictionary containing query results
    """
    url = f"{client.base_url}/{client.instance_id}/dashboardQueries:execute"

    if isinstance(interval, dict):
        interval = InputInterval.from_dict(interval)

    payload = {"query": {"query": query, "input": interval.to_dict()}}

    if clear_cache is not None:
        payload["clearCache"] = clear_cache
    if filters:
        payload["filters"] = filters

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(
            f"Failed to execute query: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def duplicate_dashboard(
    client,
    dashboard_id: str,
    display_name: str,
    access_type: DashboardAccessType,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Duplicate a existing dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard to duplicate
        display_name: New name for the duplicated dashboard
        access_type: Access type for the duplicated dashboard
                    (DashboardAccessType.PRIVATE or DashboardAccessType.PUBLIC)
        description: Description for the duplicated dashboard

    Returns:
        Dictionary containing the duplicated dashboard details
    """
    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"nativeDashboards/{dashboard_id}:duplicate"
    )

    payload = {
        "nativeDashboard": {
            "displayName": display_name,
            "access": access_type.value,
            "type": "CUSTOM",
        }
    }

    if description:
        payload["nativeDashboard"]["description"] = description

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(
            f"Failed to duplicate dashboard: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()


def edit_chart(
    client,
    dashboard_id: str,
    chart_id: str,
    display_name: Optional[str] = None,
    chart_datasource: Optional[Dict[str, Any]] = None,
    visualization: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    query: Optional[str] = None,
    interval: Optional[Union[InputInterval, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Edit an existing chart in a dashboard.

    Args:
        client: ChronicleClient instance
        dashboard_id: ID of the dashboard containing the chart
        chart_id: ID of the chart to edit
        display_name: New display name for the chart
        chart_datasource: New chart datasource configuration
        visualization: New visualization configuration
        description: New description for the chart
        query: New search query for the chart
        interval: New time interval for the query
    Returns:
        Dictionary containing the updated dashboard with edited chart
    """
    if dashboard_id.startswith("projects/"):
        dashboard_id = dashboard_id.split("projects/")[-1]

    if not chart_id.startswith("projects/"):
        chart_id = f"{client.instance_id}/dashboardCharts/{chart_id}"

    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"nativeDashboards/{dashboard_id}:editChart"
    )
    payload = {"dashboard_query": {"name": chart_id}, "dashboard_chart": {}}

    # Track update mask fields
    update_mask = []

    if display_name:
        payload["dashboard_chart"]["displayName"] = display_name
        update_mask.append("dashboard_chart.display_name")

    if description:
        payload["dashboard_chart"]["description"] = description
        update_mask.append("dashboard_chart.description")

    if chart_datasource:
        payload["dashboard_chart"]["chartDatasource"] = chart_datasource
        update_mask.append("dashboard_chart.chart_datasource.data_sources")

    if visualization:
        payload["dashboard_chart"]["visualization"] = visualization
        update_mask.append("dashboard_chart.visualization")

    # Handle query and interval if provided
    if query and interval:
        if isinstance(interval, dict):
            interval = InputInterval.from_dict(interval)

        payload["dashboard_query"].update(
            {
                "query": query,
                "input": interval.to_dict(),
            }
        )
        update_mask.append("dashboard_query.query")
        update_mask.append("dashboard_query.input")

    # Add update mask query parameter
    if update_mask:
        payload["edit_mask"] = ",".join(update_mask)

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(
            f"Failed to edit chart: Status {response.status_code}, "
            f"Response: {response.text}"
        )

    return response.json()
