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
"""Tests for the Dashboard module."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from secops.chronicle import dashboard
from secops.chronicle.client import ChronicleClient
from secops.chronicle.dashboard import DashboardAccessType, DashboardView
from secops.chronicle.models import InputInterval
from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def chronicle_client() -> Mock:
    """Create a mock Chronicle client for testing.

    Returns:
        A mock ChronicleClient instance.
    """
    client = Mock()
    client.instance_id = "test-project/locations/test-location"
    return client


class TestDashboardEnums:
    """Test the Dashboard enum classes."""

    def test_dashboard_view_enum(self) -> None:
        """Test DashboardView enum values."""
        assert DashboardView.BASIC == "NATIVE_DASHBOARD_VIEW_BASIC"
        assert DashboardView.FULL == "NATIVE_DASHBOARD_VIEW_FULL"

    def test_dashboard_access_type_enum(self) -> None:
        """Test DashboardAccessType enum values."""
        assert DashboardAccessType.PUBLIC == "DASHBOARD_PUBLIC"
        assert DashboardAccessType.PRIVATE == "DASHBOARD_PRIVATE"


class TestGetDashboard:
    """Test the get_dashboard function."""

    def test_get_dashboard_success(self, chronicle_client: Mock) -> None:
        """Test get_dashboard function with successful response."""
        dashboard_id = "test-dashboard"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.get_dashboard(chronicle_client, dashboard_id)

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"view": "NATIVE_DASHBOARD_VIEW_BASIC"}

    def test_get_dashboard_with_view(self, chronicle_client: Mock) -> None:
        """Test get_dashboard function with view parameter."""
        dashboard_id = "test-dashboard"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.get_dashboard(
                chronicle_client, dashboard_id, view=DashboardView.FULL
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"view": "NATIVE_DASHBOARD_VIEW_FULL"}

    def test_get_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test get_dashboard function with error response."""
        dashboard_id = "nonexistent-dashboard"

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to get dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to get dashboard"):
                dashboard.get_dashboard(chronicle_client, dashboard_id)


class TestUpdateDashboard:
    """Test the update_dashboard function."""

    def test_update_dashboard_display_name(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with display_name parameter."""
        dashboard_id = "test-dashboard"
        display_name = "Updated Dashboard"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.update_dashboard(
                chronicle_client, dashboard_id, display_name=display_name
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"updateMask": "display_name"}
        assert kwargs["json"] == {"displayName": display_name, "definition": {}}

    def test_update_dashboard_description(self, chronicle_client: Mock) -> None:
        """Test update_dashboard with description parameter."""
        dashboard_id = "test-dashboard"
        description = "Updated description"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.update_dashboard(
                chronicle_client, dashboard_id, description=description
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"updateMask": "description"}
        assert kwargs["json"] == {"description": description, "definition": {}}

    def test_update_dashboard_filters(self, chronicle_client: Mock) -> None:
        """Test update_dashboard with filters parameter."""
        dashboard_id = "test-dashboard"
        filters = [{"field": "event_type", "value": "PROCESS_LAUNCH"}]
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.update_dashboard(
                chronicle_client, dashboard_id, filters=filters
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"updateMask": "definition.filters"}
        assert kwargs["json"] == {"definition": {"filters": filters}}

    def test_update_dashboard_charts(self, chronicle_client: Mock) -> None:
        """Test update_dashboard with charts parameter."""
        dashboard_id = "test-dashboard"
        charts = [{"chart_id": "chart-1", "position": {"row": 0, "col": 0}}]
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.update_dashboard(
                chronicle_client, dashboard_id, charts=charts
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"updateMask": "definition.charts"}
        assert kwargs["json"] == {"definition": {"charts": charts}}

    def test_update_dashboard_multiple_fields(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with multiple parameters."""
        dashboard_id = "test-dashboard"
        display_name = "Updated Dashboard"
        description = "Updated description"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.update_dashboard(
                chronicle_client,
                dashboard_id,
                display_name=display_name,
                description=description,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"
        assert kwargs["params"] == {"updateMask": "display_name,description"}
        assert kwargs["json"] == {
            "displayName": display_name,
            "description": description,
            "definition": {},
        }

    def test_update_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test update_dashboard function with error response."""
        dashboard_id = "test-dashboard"

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to update dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to update dashboard"):
                dashboard.update_dashboard(
                    chronicle_client, dashboard_id, display_name="Test"
                )


class TestDeleteDashboard:
    """Test the delete_dashboard function."""

    def test_delete_dashboard_success(self, chronicle_client: Mock) -> None:
        """Test delete_dashboard function with successful response."""
        dashboard_id = "test-dashboard"
        expected = {"status": "success", "code": 200}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.delete_dashboard(chronicle_client, dashboard_id)

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "DELETE"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{dashboard_id}"

    def test_delete_dashboard_with_project_id(
        self, chronicle_client: Mock
    ) -> None:
        """Test delete_dashboard with project ID in dashboard_id."""
        dashboard_id = (
            "projects/test-project/locations/test-location"
            "/nativeDashboards/test-dashboard"
        )
        expected = {"status": "success", "code": 200}
        expected_id = (
            "test-project/locations/test-location/nativeDashboards/"
            "test-dashboard"
        )

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.delete_dashboard(chronicle_client, dashboard_id)

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "DELETE"
        assert kwargs["endpoint_path"] == f"nativeDashboards/{expected_id}"

    def test_delete_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test delete_dashboard function with error response."""
        dashboard_id = "nonexistent-dashboard"

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to delete dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to delete dashboard"):
                dashboard.delete_dashboard(chronicle_client, dashboard_id)


class TestRemoveChart:
    """Test the remove_chart function."""

    def test_remove_chart_success(self, chronicle_client: Mock) -> None:
        """Test remove_chart function with successful response."""
        dashboard_id = "test-dashboard"
        chart_id = "test-chart"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.remove_chart(
                chronicle_client, dashboard_id, chart_id
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:removeChart"
        )
        assert kwargs["json"] == {
            "dashboardChart": "test-project/locations/test-location/"
            "dashboardCharts/test-chart"
        }

    def test_remove_chart_with_full_ids(self, chronicle_client: Mock) -> None:
        """Test remove_chart with full project IDs."""
        dashboard_id = (
            "projects/test-project/locations/test-location/"
            "nativeDashboards/test-dashboard"
        )
        chart_id = (
            "projects/test-project/locations/test-location/"
            "dashboardCharts/test-chart"
        )
        expected = {"name": "test-dashboard"}
        expected_dashboard_id = (
            "test-project/locations/test-location/nativeDashboards/"
            "test-dashboard"
        )

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.remove_chart(
                chronicle_client, dashboard_id, chart_id
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{expected_dashboard_id}:removeChart"
        )
        assert kwargs["json"] == {"dashboardChart": chart_id}

    def test_remove_chart_error(self, chronicle_client: Mock) -> None:
        """Test remove_chart function with error response."""
        dashboard_id = "test-dashboard"
        chart_id = "test-chart"

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to remove chart"),
        ):
            with pytest.raises(APIError, match="Failed to remove chart"):
                dashboard.remove_chart(chronicle_client, dashboard_id, chart_id)


class TestListDashboards:
    """Test the list_dashboards function."""

    def test_list_dashboards_success(self, chronicle_client: Mock) -> None:
        """Test list_dashboards function with successful response."""
        expected = {
            "nativeDashboards": [
                {"name": "test-dashboard-1"},
                {"name": "test-dashboard-2"},
            ]
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_paginated_request",
            return_value=expected,
        ) as paged:
            result = dashboard.list_dashboards(chronicle_client)

        assert result == expected
        paged.assert_called_once()
        _, kwargs = paged.call_args
        assert kwargs["path"] == "nativeDashboards"
        assert kwargs["items_key"] == "nativeDashboards"

    def test_list_dashboards_with_pagination(
        self, chronicle_client: Mock
    ) -> None:
        """Test list_dashboards function with pagination parameters."""
        expected = {
            "nativeDashboards": [
                {"name": "test-dashboard-1"},
                {"name": "test-dashboard-2"},
            ],
            "nextPageToken": "next-page-token",
        }
        page_size = 10
        page_token = "current-page-token"

        with patch(
            "secops.chronicle.dashboard.chronicle_paginated_request",
            return_value=expected,
        ) as paged:
            result = dashboard.list_dashboards(
                chronicle_client, page_size=page_size, page_token=page_token
            )

        assert result == expected
        paged.assert_called_once()
        _, kwargs = paged.call_args
        assert kwargs["path"] == "nativeDashboards"
        assert kwargs["items_key"] == "nativeDashboards"
        assert kwargs["page_size"] == page_size
        assert kwargs["page_token"] == page_token

    def test_list_dashboards_error(self, chronicle_client: Mock) -> None:
        """Test list_dashboards function with error response."""
        with patch(
            "secops.chronicle.dashboard.chronicle_paginated_request",
            side_effect=APIError("Failed to list dashboards"),
        ):
            with pytest.raises(APIError, match="Failed to list dashboards"):
                dashboard.list_dashboards(chronicle_client)


class TestCreateDashboard:
    """Test the create_dashboard function."""

    def test_create_dashboard_minimal(self, chronicle_client: Mock) -> None:
        """Test create_dashboard with minimal required parameters."""
        display_name = "Test Dashboard"
        access_type = dashboard.DashboardAccessType.PRIVATE
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.create_dashboard(
                chronicle_client,
                display_name=display_name,
                access_type=access_type,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards"
        assert kwargs["json"] == {
            "displayName": display_name,
            "access": "DASHBOARD_PRIVATE",
            "type": "CUSTOM",
            "definition": {},
        }

    def test_create_dashboard_full(self, chronicle_client: Mock) -> None:
        """Test create_dashboard with all parameters."""
        display_name = "Test Dashboard"
        access_type = dashboard.DashboardAccessType.PUBLIC
        description = "Test description"
        filters = [{"field": "event_type", "value": "PROCESS_LAUNCH"}]
        charts = [{"chart_id": "chart-1", "position": {"row": 0, "col": 0}}]
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.create_dashboard(
                chronicle_client,
                display_name=display_name,
                access_type=access_type,
                description=description,
                filters=filters,
                charts=charts,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards"
        assert kwargs["json"] == {
            "displayName": display_name,
            "access": "DASHBOARD_PUBLIC",
            "type": "CUSTOM",
            "description": description,
            "definition": {"filters": filters, "charts": charts},
        }

    def test_create_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test create_dashboard function with error response."""
        display_name = "Test Dashboard"
        access_type = dashboard.DashboardAccessType.PRIVATE

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to create dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to create dashboard"):
                dashboard.create_dashboard(
                    chronicle_client,
                    display_name=display_name,
                    access_type=access_type,
                )


class TestImportDashboard:
    """Test the import_dashboard function."""

    def test_import_dashboard_success(self, chronicle_client: Mock) -> None:
        """Test import_dashboard function with successful response."""
        expected = {
            "name": "projects/test-project/locations/test-location/nativeDashboards/imported-dashboard",
            "displayName": "Imported Dashboard",
        }
        dashboard_data = {
            "dashboard": {
                "name": (
                    "projects/test-project/locations/test-location/"
                    "nativeDashboards/dashboard-to-import"
                ),
                "displayName": "test-dashboard",
            },
            "dashboardCharts": [{"displayName": "Test Chart"}],
            "dashboardQueries": [
                {
                    "query": "sample_query",
                    "input": {
                        "relativeTime": {
                            "timeUnit": "SECOND",
                            "startTimeVal": "20",
                        }
                    },
                }
            ],
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.import_dashboard(
                chronicle_client, dashboard_data
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards:import"
        assert kwargs["json"] == {"source": {"dashboards": [dashboard_data]}}

    def test_import_dashboard_minimal(self, chronicle_client: Mock) -> None:
        """Test import_dashboard function with minimal dashboard data."""
        expected = {"name": "test-dashboard"}
        dashboard_data = {
            "dashboard": {
                "name": (
                    "projects/test-project/locations/test-location/"
                    "nativeDashboards/dashboard-to-import"
                ),
                "displayName": "test-dashboard",
            },
            "dashboardCharts": [],
            "dashboardQueries": [],
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.import_dashboard(
                chronicle_client, dashboard_data
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards:import"
        assert kwargs["json"] == {"source": {"dashboards": [dashboard_data]}}

    def test_import_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test import_dashboard function with server error response."""
        dashboard_data = {
            "dashboard": {
                "name": (
                    "projects/test-project/locations/test-location/"
                    "nativeDashboards/dashboard-to-import"
                ),
                "displayName": "test-dashboard",
            },
            "dashboardCharts": [{"displayName": "Test Chart"}],
            "dashboardQueries": [
                {
                    "query": "sample_query",
                    "input": {
                        "relativeTime": {
                            "timeUnit": "SECOND",
                            "startTimeVal": "20",
                        }
                    },
                }
            ],
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to import dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to import dashboard"):
                dashboard.import_dashboard(chronicle_client, dashboard_data)

    def test_import_dashboard_invalid_data(
        self, chronicle_client: Mock
    ) -> None:
        """Test import_dashboard function with invalid dashboard data."""
        invalid_dashboard_data = {
            "displayName": "Invalid Dashboard",
            "access": "DASHBOARD_PUBLIC",
            "type": "CUSTOM",
        }

        with pytest.raises(
            SecOpsError,
            match=(
                "Dashboard must contain "
                "at least one of: dashboard, dashboardCharts, dashboardQueries"
            ),
        ):
            dashboard.import_dashboard(chronicle_client, invalid_dashboard_data)


class TestAddChart:
    """Test the add_chart function."""

    @pytest.fixture
    def chart_layout(self) -> Dict[str, Any]:
        """Create a sample chart layout for testing.

        Returns:
            A dictionary with chart layout configuration.
        """
        return {
            "position": {"row": 0, "column": 0},
            "size": {"width": 6, "height": 4},
        }

    def test_add_chart_minimal(
        self, chronicle_client: Mock, chart_layout: Dict[str, Any]
    ) -> None:
        """Test add_chart with minimal required parameters."""
        dashboard_id = "test-dashboard"
        display_name = "Test Chart"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.add_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                display_name=display_name,
                chart_layout=chart_layout,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:addChart"
        )
        assert kwargs["json"] == {
            "dashboardChart": {
                "displayName": "Test Chart",
                "tileType": "TILE_TYPE_VISUALIZATION",
            },
            "chartLayout": {
                "position": {"row": 0, "column": 0},
                "size": {"width": 6, "height": 4},
            },
        }

    def test_add_chart_with_query(
        self, chronicle_client: Mock, chart_layout: Dict[str, Any]
    ) -> None:
        """Test add_chart with query and interval parameters."""
        dashboard_id = "test-dashboard"
        display_name = "Test Chart"
        query = 'udm.metadata.event_type = "PROCESS_LAUNCH"'
        interval = InputInterval(
            relative_time={"timeUnit": "DAY", "startTimeVal": "1"}
        )
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.add_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                display_name=display_name,
                chart_layout=chart_layout,
                query=query,
                interval=interval,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:addChart"
        )
        assert kwargs["json"] == {
            "dashboardChart": {
                "displayName": "Test Chart",
                "tileType": "TILE_TYPE_VISUALIZATION",
            },
            "chartLayout": {
                "position": {"row": 0, "column": 0},
                "size": {"width": 6, "height": 4},
            },
            "dashboardQuery": {
                "query": 'udm.metadata.event_type = "PROCESS_LAUNCH"',
                "input": {
                    "relativeTime": {"timeUnit": "DAY", "startTimeVal": "1"}
                },
            },
        }

    def test_add_chart_with_string_json_params(
        self, chronicle_client: Mock
    ) -> None:
        """Test add_chart with string JSON parameters."""
        dashboard_id = "test-dashboard"
        display_name = "Test Chart"
        chart_layout_str = (
            '{"position": {"row": 0, "column": 0}, "size": '
            '{"width": 6, "height": 4}}'
        )
        visualization_str = '{"type": "BAR_CHART"}'
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.add_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                display_name=display_name,
                chart_layout=chart_layout_str,
                visualization=visualization_str,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:addChart"
        )
        assert kwargs["json"] == {
            "dashboardChart": {
                "displayName": "Test Chart",
                "tileType": "TILE_TYPE_VISUALIZATION",
                "visualization": {"type": "BAR_CHART"},
            },
            "chartLayout": {
                "position": {"row": 0, "column": 0},
                "size": {"width": 6, "height": 4},
            },
        }

    def test_add_chart_error(
        self, chronicle_client: Mock, chart_layout: Dict[str, Any]
    ) -> None:
        """Test add_chart function with error response."""
        dashboard_id = "test-dashboard"
        display_name = "Test Chart"

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to add chart"),
        ):
            with pytest.raises(APIError, match="Failed to add chart"):
                dashboard.add_chart(
                    chronicle_client,
                    dashboard_id=dashboard_id,
                    display_name=display_name,
                    chart_layout=chart_layout,
                )


class TestDuplicateDashboard:
    """Test the duplicate_dashboard function."""

    def test_duplicate_dashboard_minimal(self, chronicle_client: Mock) -> None:
        """Test duplicate_dashboard with minimal required parameters."""
        dashboard_id = "test-dashboard"
        display_name = "Duplicated Dashboard"
        access_type = dashboard.DashboardAccessType.PRIVATE
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.duplicate_dashboard(
                chronicle_client,
                dashboard_id=dashboard_id,
                display_name=display_name,
                access_type=access_type,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:duplicate"
        )
        assert kwargs["json"] == {
            "nativeDashboard": {
                "displayName": display_name,
                "access": "DASHBOARD_PRIVATE",
                "type": "CUSTOM",
            }
        }

    def test_duplicate_dashboard_with_description(
        self, chronicle_client: Mock
    ) -> None:
        """Test duplicate_dashboard with description parameter."""
        dashboard_id = "test-dashboard"
        display_name = "Duplicated Dashboard"
        access_type = dashboard.DashboardAccessType.PUBLIC
        description = "Duplicated dashboard description"
        expected = {"name": "test-dashboard"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.duplicate_dashboard(
                chronicle_client,
                dashboard_id=dashboard_id,
                display_name=display_name,
                access_type=access_type,
                description=description,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:duplicate"
        )
        assert kwargs["json"] == {
            "nativeDashboard": {
                "displayName": display_name,
                "access": "DASHBOARD_PUBLIC",
                "type": "CUSTOM",
                "description": description,
            }
        }

    def test_duplicate_dashboard_with_project_id(
        self, chronicle_client: Mock
    ) -> None:
        """Test duplicate_dashboard with project ID in dashboard_id."""
        dashboard_id = (
            "projects/test-project/locations/test-location"
            "/nativeDashboards/test-dashboard"
        )
        display_name = "Duplicated Dashboard"
        access_type = dashboard.DashboardAccessType.PRIVATE
        expected = {"name": "test-dashboard"}
        expected_id = (
            "test-project/locations/test-location/nativeDashboards/"
            "test-dashboard"
        )

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.duplicate_dashboard(
                chronicle_client,
                dashboard_id=dashboard_id,
                display_name=display_name,
                access_type=access_type,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{expected_id}:duplicate"
        )
        assert kwargs["json"] == {
            "nativeDashboard": {
                "displayName": display_name,
                "access": "DASHBOARD_PRIVATE",
                "type": "CUSTOM",
            }
        }

    def test_duplicate_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test duplicate_dashboard function with error response."""
        dashboard_id = "nonexistent-dashboard"
        display_name = "Duplicated Dashboard"
        access_type = dashboard.DashboardAccessType.PRIVATE

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to duplicate dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to duplicate dashboard"):
                dashboard.duplicate_dashboard(
                    chronicle_client,
                    dashboard_id=dashboard_id,
                    display_name=display_name,
                    access_type=access_type,
                )


class TestGetChart:
    """Test the get_chart function."""

    def test_get_chart_success(self, chronicle_client: Mock) -> None:
        """Test get_chart function with successful response."""
        chart_id = "test-chart"
        expected = {
            "name": "projects/test-project/locations/test-location/dashboardCharts/test-chart",
            "displayName": "Test Chart",
            "visualization": {"type": "BAR_CHART"},
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.get_chart(chronicle_client, chart_id)

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["endpoint_path"] == f"dashboardCharts/{chart_id}"

    def test_get_chart_with_full_id(self, chronicle_client: Mock) -> None:
        """Test get_chart with full project path chart ID."""
        chart_id = "projects/test-project/locations/test-location/dashboardCharts/test-chart"
        expected_id = "test-chart"
        expected = {
            "name": "projects/test-project/locations/test-location/dashboardCharts/test-chart",
            "displayName": "Test Chart",
            "visualization": {"type": "BAR_CHART"},
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.get_chart(chronicle_client, chart_id)

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["endpoint_path"] == f"dashboardCharts/{expected_id}"

    def test_get_chart_error(self, chronicle_client: Mock) -> None:
        """Test get_chart function with error response."""
        chart_id = "nonexistent-chart"

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to get chart details"),
        ):
            with pytest.raises(APIError, match="Failed to get chart details"):
                dashboard.get_chart(chronicle_client, chart_id)


class TestEditChart:
    """Test the edit_chart function."""

    def test_edit_chart_query(self, chronicle_client: Mock) -> None:
        """Test edit_chart with dashboard_query parameter."""
        dashboard_id = "test-dashboard"
        dashboard_query = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "etag": "123456789",
            "query": 'udm.metadata.event_type = "NETWORK_CONNECTION"',
            "input": {
                "relative_time": {"timeUnit": "DAY", "startTimeVal": "7"}
            },
        }
        expected = {"name": "updated-chart"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                dashboard_query=dashboard_query,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:editChart"
        )
        assert kwargs["json"] == {
            "dashboardQuery": dashboard_query,
            "editMask": "dashboard_query.query,dashboard_query.input",
        }

    def test_edit_chart_details(self, chronicle_client: Mock) -> None:
        """Test edit_chart with dashboard_chart parameter."""
        dashboard_id = "test-dashboard"
        dashboard_chart = {
            "name": "projects/test-project/locations/test-location/dashboardCharts/test-chart",
            "etag": "123456789",
            "display_name": "Updated Chart Title",
            "visualization": {"legends": [{"legendOrient": "HORIZONTAL"}]},
        }
        expected = {"name": "updated-chart"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                dashboard_chart=dashboard_chart,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:editChart"
        )
        assert kwargs["json"] == {
            "dashboardChart": dashboard_chart,
            "editMask": "dashboard_chart.display_name,dashboard_chart.visualization",
        }

    def test_edit_chart_both(self, chronicle_client: Mock) -> None:
        """Test edit_chart with both query and chart parameters."""
        dashboard_id = "test-dashboard"
        dashboard_query = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "etag": "123456789",
            "query": 'udm.metadata.event_type = "NETWORK_CONNECTION"',
            "input": {
                "relative_time": {"timeUnit": "DAY", "startTimeVal": "7"}
            },
        }
        dashboard_chart = {
            "name": "projects/test-project/locations/test-location/dashboardCharts/test-chart",
            "etag": "123456789",
            "display_name": "Updated Chart Title",
        }
        expected = {"name": "updated-chart"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                dashboard_query=dashboard_query,
                dashboard_chart=dashboard_chart,
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert (
            kwargs["endpoint_path"]
            == f"nativeDashboards/{dashboard_id}:editChart"
        )
        assert kwargs["json"] == {
            "dashboardQuery": dashboard_query,
            "dashboardChart": dashboard_chart,
            "editMask": (
                "dashboard_query.query,dashboard_query.input,"
                "dashboard_chart.display_name"
            ),
        }

    def test_edit_chart_with_model_objects(
        self, chronicle_client: Mock
    ) -> None:
        """Test edit_chart with model objects instead of dictionaries."""
        dashboard_id = "test-dashboard"
        interval = InputInterval(
            relative_time={"timeUnit": "DAY", "startTimeVal": "3"}
        )
        dashboard_query = dashboard.DashboardQuery(
            name="test-query",
            etag="123456789",
            query='udm.metadata.event_type = "PROCESS_LAUNCH"',
            input=interval,
        )
        dashboard_chart = dashboard.DashboardChart(
            name="test-chart",
            etag="123456789",
            display_name="Updated Chart",
            visualization={"type": "BAR_CHART"},
        )
        expected = {"name": "updated-chart"}

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id=dashboard_id,
                dashboard_query=dashboard_query,
                dashboard_chart=dashboard_chart,
            )

        assert result == expected
        req.assert_called_once()

    def test_edit_chart_error(self, chronicle_client: Mock) -> None:
        """Test edit_chart with error response."""
        dashboard_id = "test-dashboard"
        dashboard_query = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "etag": "123123123",
            "query": "invalid query",
            "input": {
                "relative_time": {"timeUnit": "DAY", "startTimeVal": "7"}
            },
        }

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to edit chart"),
        ):
            with pytest.raises(APIError, match="Failed to edit chart"):
                dashboard.edit_chart(
                    chronicle_client,
                    dashboard_id=dashboard_id,
                    dashboard_query=dashboard_query,
                )


class TestExportDashboard:
    """Test the export_dashboard function."""

    def test_export_dashboard_success(self, chronicle_client: Mock) -> None:
        """Test export_dashboard function with successful response."""
        dashboard_names = ["test-dashboard-1", "test-dashboard-2"]
        expected = {
            "inlineDestination": {
                "dashboards": [
                    {"dashboard": {"name": "test-dashboard-1"}},
                    {"dashboard": {"name": "test-dashboard-2"}},
                ]
            }
        }
        qualified_names = [
            f"{chronicle_client.instance_id}/nativeDashboards/test-dashboard-1",
            f"{chronicle_client.instance_id}/nativeDashboards/test-dashboard-2",
        ]

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value=expected,
        ) as req:
            result = dashboard.export_dashboard(
                chronicle_client, dashboard_names
            )

        assert result == expected
        req.assert_called_once()
        _, kwargs = req.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards:export"
        assert kwargs["json"] == {"names": qualified_names}

    def test_export_dashboard_error(self, chronicle_client: Mock) -> None:
        """Test export_dashboard function with error response."""
        dashboard_names = ["test-dashboard-1"]

        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            side_effect=APIError("Failed to export dashboards"),
        ):
            with pytest.raises(APIError, match="Failed to export dashboards"):
                dashboard.export_dashboard(chronicle_client, dashboard_names)
