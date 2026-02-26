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
    """Minimal client shape expected by chronicle_request() helper."""
    client = Mock()
    client.instance_id = "projects/test-project/locations/test-location/instances/test-customer"
    client.base_url = Mock(return_value="https://testapi.com")
    client.session = Mock()
    return client


@pytest.fixture
def response_mock() -> Mock:
    """Create a mock API response object.

    Returns:
        A mock response object.
    """
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"name": "test-dashboard"}
    return mock


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

    def test_get_dashboard_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test get_dashboard function with successful response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.get_dashboard(chronicle_client, "test-dashboard")

        assert result == {"name": "test-dashboard"}
        mock_req.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="nativeDashboards/test-dashboard",
            api_version=dashboard.APIVersion.V1ALPHA,
            params={"view": DashboardView.BASIC},
            error_message="Failed to get dashboard with ID test-dashboard",
        )

    def test_get_dashboard_with_view(self, chronicle_client: Mock) -> None:
        """Test get_dashboard function with view parameter."""
        with patch(
            "secops.chronicle.dashboard.chronicle_request",
            return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.get_dashboard(
                chronicle_client, "test-dashboard", view=DashboardView.FULL
            )

        assert result == {"name": "test-dashboard"}
        mock_req.assert_called_once()
        assert mock_req.call_args.kwargs["params"] == {"view": DashboardView.FULL}

    def test_get_dashboard_error(self, chronicle_client: Mock) -> None:
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to get dashboard with ID nonexistent-dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to get dashboard"):
                dashboard.get_dashboard(chronicle_client, "nonexistent-dashboard")


class TestUpdateDashboard:
    """Test the update_dashboard function."""

    def test_update_dashboard_display_name(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with display_name parameter."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.update_dashboard(
                chronicle_client, "test-dashboard", display_name="Updated Dashboard"
            )

        assert result == {"name": "test-dashboard"}
        mock_req.assert_called_once()
        kwargs = mock_req.call_args.kwargs
        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == "nativeDashboards/test-dashboard"
        assert kwargs["params"] == {"updateMask": "display_name"}
        assert kwargs["json"] == {"displayName": "Updated Dashboard"}
        assert "Failed to update dashboard" in kwargs["error_message"]

    def test_update_dashboard_description(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with description parameter."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.update_dashboard(
                chronicle_client, "test-dashboard", description="Updated description"
            )

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["params"] == {"updateMask": "description"}
        assert kwargs["json"] == {"description": "Updated description"}

    def test_update_dashboard_filters(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with filters parameter."""
        filters = [{"field": "event_type", "value": "PROCESS_LAUNCH"}]
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.update_dashboard(chronicle_client, "test-dashboard", filters=filters)

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["params"] == {"updateMask": "definition.filters"}
        assert kwargs["json"] == {"definition": {"filters": filters}}

    def test_update_dashboard_charts(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with charts parameter."""
        charts = [{"chart_id": "chart-1", "position": {"row": 0, "col": 0}}]
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.update_dashboard(chronicle_client, "test-dashboard", charts=charts)

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["params"] == {"updateMask": "definition.charts"}
        assert kwargs["json"] == {"definition": {"charts": charts}}

    def test_update_dashboard_multiple_fields(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard with multiple parameters."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.update_dashboard(
                chronicle_client,
                "test-dashboard",
                display_name="Updated Dashboard",
                description="Updated description",
            )

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        # order matters because implementation appends in a fixed order
        assert kwargs["params"] == {"updateMask": "display_name,description"}
        assert kwargs["json"] == {
            "displayName": "Updated Dashboard",
            "description": "Updated description",
        }

    def test_update_dashboard_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test update_dashboard function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to update dashboard with ID test-dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to update dashboard"):
                dashboard.update_dashboard(chronicle_client, "test-dashboard", display_name="Test")


class TestDeleteDashboard:
    """Test the delete_dashboard function."""

    def test_delete_dashboard_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test delete_dashboard function with successful response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"status": "success", "code": 200},
        ) as mock_req:
            result = dashboard.delete_dashboard(chronicle_client, "test-dashboard")

        assert result == {"status": "success", "code": 200}
        mock_req.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="nativeDashboards/test-dashboard",
            api_version=dashboard.APIVersion.V1ALPHA,
            error_message="Failed to delete dashboard with ID test-dashboard",
        )

    def test_delete_dashboard_with_project_id(
        self, chronicle_client: Mock
    ) -> None:
        """Test delete_dashboard with project ID in dashboard_id."""
        full_id = "projects/test-project/locations/test-location/nativeDashboards/test-dashboard"
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"status": "success", "code": 200},
        ) as mock_req:
            result = dashboard.delete_dashboard(chronicle_client, full_id)

        assert result["status"] == "success"
        assert mock_req.call_args.kwargs["endpoint_path"] == "nativeDashboards/test-dashboard"

    def test_delete_dashboard_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test delete_dashboard function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to delete dashboard with ID nonexistent-dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to delete dashboard"):
                dashboard.delete_dashboard(chronicle_client, "nonexistent-dashboard")


class TestRemoveChart:
    """Test the remove_chart function."""

    def test_remove_chart_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test remove_chart function with successful response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.remove_chart(chronicle_client, "test-dashboard", "test-chart")

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards/test-dashboard:removeChart"
        assert "Failed to remove chart" in kwargs["error_message"]

    def test_remove_chart_with_full_ids(
        self, chronicle_client: Mock
    ) -> None:
        """Test remove_chart with full project IDs."""
        dashboard_id = "projects/test-project/locations/test-location/nativeDashboards/test-dashboard"
        chart_id = "projects/test-project/locations/test-location/dashboardCharts/test-chart"

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.remove_chart(chronicle_client, dashboard_id, chart_id)

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["endpoint_path"] == "nativeDashboards/test-dashboard:removeChart"

    def test_remove_chart_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test remove_chart function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to remove chart"),
        ):
            with pytest.raises(APIError, match="Failed to remove chart"):
                dashboard.remove_chart(chronicle_client, "test-dashboard", "test-chart")


class TestListDashboards:
    """Test the list_dashboards function."""

    def test_list_dashboards_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test list_dashboards function with successful response."""
        upstream = {
            "nativeDashboards": [{"name": "test-dashboard-1"}, {"name": "test-dashboard-2"}]
        }
        with patch(
                "secops.chronicle.dashboard.chronicle_paginated_request",
                return_value=upstream,
        ) as mock_paged:
            result = dashboard.list_dashboards(chronicle_client)

        assert result == upstream
        mock_paged.assert_called_once_with(
            chronicle_client,
            api_version=dashboard.APIVersion.V1ALPHA,
            path="nativeDashboards",
            items_key="nativeDashboards",
            page_size=None,
            page_token=None,
            as_list=False,
        )

    def test_list_dashboards_with_pagination(
        self, chronicle_client: Mock
    ) -> None:
        """Test list_dashboards function with pagination parameters."""
        upstream = {
            "nativeDashboards": [{"name": "test-dashboard-1"}, {"name": "test-dashboard-2"}],
            "nextPageToken": "next-page-token",
        }
        with patch(
                "secops.chronicle.dashboard.chronicle_paginated_request",
                return_value=upstream,
        ) as mock_paged:
            result = dashboard.list_dashboards(chronicle_client, page_size=10, page_token="t1")

        assert result == upstream
        kwargs = mock_paged.call_args.kwargs
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "t1"

    def test_list_dashboards_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test list_dashboards function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_paginated_request",
                side_effect=APIError("Failed to list dashboards"),
        ):
            with pytest.raises(APIError, match="Failed to list dashboards"):
                dashboard.list_dashboards(chronicle_client)

    def test_list_dashboards_as_list(
        self, chronicle_client: Mock
    ) -> None:
        """Test list_dashboards function with as_list=True."""
        upstream = [{"name": "test-dashboard-1"}, {"name": "test-dashboard-2"}]
        with patch(
                "secops.chronicle.dashboard.chronicle_paginated_request",
                return_value=upstream,
        ) as mock_paged:
            result = dashboard.list_dashboards(chronicle_client, as_list=True)

        assert result == [{"name": "test-dashboard-1"}, {"name": "test-dashboard-2"}]
        kwargs = mock_paged.call_args.kwargs
        assert kwargs["as_list"] is True

    def test_dashboard_as_list_missing_events(
            self, chronicle_client: Mock
    ) -> None:
        """Test that as_list=True returns empty list when events missing."""
        with patch(
                "secops.chronicle.dashboard.chronicle_paginated_request",
                return_value=[],
        ) as mock_paged:
            result = dashboard.list_dashboards(chronicle_client, as_list=True)

        assert result == []
        assert len(result) == 0
        assert isinstance(result, list)
        kwargs = mock_paged.call_args.kwargs
        assert kwargs["as_list"] is True



class TestCreateDashboard:
    """Test the create_dashboard function."""

    def test_create_dashboard_minimal(
        self, chronicle_client: Mock
    ) -> None:
        """Test create_dashboard with minimal required parameters."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.create_dashboard(
                chronicle_client,
                display_name="Test Dashboard",
                access_type=dashboard.DashboardAccessType.PRIVATE,
            )

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards"
        assert kwargs["json"] == {
            "displayName": "Test Dashboard",
            "access": "DASHBOARD_PRIVATE",
            "type": "CUSTOM",
            "definition": {},
        }

    def test_create_dashboard_full(
        self, chronicle_client: Mock
    ) -> None:
        """Test create_dashboard with all parameters."""
        filters = [{"field": "event_type", "value": "PROCESS_LAUNCH"}]
        charts = [{"chart_id": "chart-1", "position": {"row": 0, "col": 0}}]

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.create_dashboard(
                chronicle_client,
                display_name="Test Dashboard",
                access_type=dashboard.DashboardAccessType.PUBLIC,
                description="Test description",
                filters=filters,
                charts=charts,
            )

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["json"] == {
            "displayName": "Test Dashboard",
            "access": "DASHBOARD_PUBLIC",
            "type": "CUSTOM",
            "description": "Test description",
            "definition": {"filters": filters, "charts": charts},
        }

    def test_create_dashboard_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test create_dashboard function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to create dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to create dashboard"):
                dashboard.create_dashboard(
                    chronicle_client,
                    display_name="Test Dashboard",
                    access_type=dashboard.DashboardAccessType.PRIVATE,
                )


class TestImportDashboard:
    """Test the import_dashboard function."""

    def test_import_dashboard_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test import_dashboard function with successful response."""
        dashboard_data = {
            "dashboard": {
                "name": "projects/test-project/locations/test-location/nativeDashboards/dashboard-to-import",
                "displayName": "test-dashboard",
            },
            "dashboardCharts": [{"displayName": "Test Chart"}],
            "dashboardQueries": [
                {
                    "query": "sample_query",
                    "input": {"relativeTime": {"timeUnit": "SECOND", "startTimeVal": "20"}},
                }
            ],
        }

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={
                    "name": "projects/test-project/locations/test-location/nativeDashboards/imported-dashboard",
                    "displayName": "Imported Dashboard",
                },
        ) as mock_req:
            result = dashboard.import_dashboard(chronicle_client, dashboard_data)

        assert result["displayName"] == "Imported Dashboard"
        kwargs = mock_req.call_args.kwargs
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards:import"
        assert kwargs["json"] == {"source": {"dashboards": [dashboard_data]}}

    def test_import_dashboard_minimal(
        self, chronicle_client: Mock
    ) -> None:
        """Test import_dashboard function with minimal dashboard data."""
        dashboard_data = {
            "dashboard": {
                "name": "projects/test-project/locations/test-location/nativeDashboards/dashboard-to-import",
                "displayName": "test-dashboard",
            },
            "dashboardCharts": [],
            "dashboardQueries": [],
        }

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.import_dashboard(chronicle_client, dashboard_data)

        assert result == {"name": "test-dashboard"}
        assert mock_req.call_args.kwargs["json"] == {"source": {"dashboards": [dashboard_data]}}

    def test_import_dashboard_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test import_dashboard function with server error response."""
        dashboard_data = {
            "dashboard": {
                "name": "projects/test-project/locations/test-location/nativeDashboards/dashboard-to-import",
                "displayName": "test-dashboard",
            },
            "dashboardCharts": [{"displayName": "Test Chart"}],
            "dashboardQueries": [
                {"query": "sample_query", "input": {"relativeTime": {"timeUnit": "SECOND", "startTimeVal": "20"}}}],
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

        with pytest.raises(SecOpsError) as exc:
            dashboard.import_dashboard(chronicle_client, invalid_dashboard_data)

        # Avoid depending on set ordering in the error message.
        msg = str(exc.value)
        assert "Dashboard must contain at least one of" in msg
        assert "dashboard" in msg
        assert "dashboardCharts" in msg
        assert "dashboardQueries" in msg


class TestAddChart:
    """Test the add_chart function."""

    @pytest.fixture
    def chart_layout(self) -> Dict[str, Any]:
        return {"position": {"row": 0, "column": 0}, "size": {"width": 6, "height": 4}}

    def test_add_chart_minimal(
        self,
        chronicle_client: Mock,
        chart_layout: Dict[str, Any],
    ) -> None:
        """Test add_chart with minimal required parameters."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.add_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                display_name="Test Chart",
                chart_layout=chart_layout,
            )

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards/test-dashboard:addChart"
        assert kwargs["json"]["dashboardChart"]["displayName"] == "Test Chart"
        assert kwargs["json"]["chartLayout"] == chart_layout

    def test_add_chart_with_query(
        self,
        chronicle_client: Mock,
        chart_layout: Dict[str, Any],
    ) -> None:
        """Test add_chart with query and interval parameters."""
        interval = InputInterval(relative_time={"timeUnit": "DAY", "startTimeVal": "1"})

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.add_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                display_name="Test Chart",
                chart_layout=chart_layout,
                query='udm.metadata.event_type = "PROCESS_LAUNCH"',
                interval=interval,
            )

        assert result == {"name": "test-dashboard"}
        body = mock_req.call_args.kwargs["json"]
        assert body["dashboardQuery"]["query"] == 'udm.metadata.event_type = "PROCESS_LAUNCH"'
        assert body["dashboardQuery"]["input"] == {
            "relativeTime": {"timeUnit": "DAY", "startTimeVal": "1"}
        }

    def test_add_chart_with_string_json_params(
        self, chronicle_client: Mock
    ) -> None:
        """Test add_chart with string JSON parameters."""
        chart_layout_str = '{"position": {"row": 0, "column": 0}, "size": {"width": 6, "height": 4}}'
        visualization_str = '{"type": "BAR_CHART"}'

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.add_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                display_name="Test Chart",
                chart_layout=chart_layout_str,
                visualization=visualization_str,
            )

        assert result == {"name": "test-dashboard"}
        body = mock_req.call_args.kwargs["json"]
        assert body["dashboardChart"]["visualization"] == {"type": "BAR_CHART"}
        assert body["chartLayout"]["size"]["width"] == 6

    def test_add_chart_error(
        self,
        chronicle_client: Mock,
        chart_layout: Dict[str, Any],
    ) -> None:
        """Test add_chart function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to add chart"),
        ):
            with pytest.raises(APIError, match="Failed to add chart"):
                dashboard.add_chart(
                    chronicle_client,
                    dashboard_id="test-dashboard",
                    display_name="Test Chart",
                    chart_layout=chart_layout,
                )


class TestDuplicateDashboard:
    """Test the duplicate_dashboard function."""

    def test_duplicate_dashboard_minimal(
        self, chronicle_client: Mock
    ) -> None:
        """Test duplicate_dashboard with minimal required parameters."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.duplicate_dashboard(
                chronicle_client,
                dashboard_id="test-dashboard",
                display_name="Duplicated Dashboard",
                access_type=dashboard.DashboardAccessType.PRIVATE,
            )

        assert result == {"name": "test-dashboard"}
        kwargs = mock_req.call_args.kwargs
        assert kwargs["endpoint_path"] == "nativeDashboards/test-dashboard:duplicate"
        assert kwargs["json"]["nativeDashboard"]["access"] == "DASHBOARD_PRIVATE"

    def test_duplicate_dashboard_with_description(
        self, chronicle_client: Mock
    ) -> None:
        """Test duplicate_dashboard with description parameter."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            result = dashboard.duplicate_dashboard(
                chronicle_client,
                dashboard_id="test-dashboard",
                display_name="Duplicated Dashboard",
                access_type=dashboard.DashboardAccessType.PUBLIC,
                description="Duplicated dashboard description",
            )

        assert result == {"name": "test-dashboard"}
        body = mock_req.call_args.kwargs["json"]["nativeDashboard"]
        assert body["access"] == "DASHBOARD_PUBLIC"
        assert body["description"] == "Duplicated dashboard description"

    def test_duplicate_dashboard_with_project_id(
        self, chronicle_client: Mock
    ) -> None:
        """Test duplicate_dashboard with project ID in dashboard_id."""
        full_id = "projects/test-project/locations/test-location/nativeDashboards/test-dashboard"

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "test-dashboard"},
        ) as mock_req:
            _ = dashboard.duplicate_dashboard(
                chronicle_client,
                dashboard_id=full_id,
                display_name="Duplicated Dashboard",
                access_type=dashboard.DashboardAccessType.PRIVATE,
            )

        assert mock_req.call_args.kwargs["endpoint_path"] == "nativeDashboards/test-dashboard:duplicate"

    def test_duplicate_dashboard_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test duplicate_dashboard function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to duplicate dashboard"),
        ):
            with pytest.raises(APIError, match="Failed to duplicate dashboard"):
                dashboard.duplicate_dashboard(
                    chronicle_client,
                    dashboard_id="nonexistent-dashboard",
                    display_name="Duplicated Dashboard",
                    access_type=dashboard.DashboardAccessType.PRIVATE,
                )


class TestGetChart:
    """Test the get_chart function."""

    def test_get_chart_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test get_chart function with successful response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "dashboardCharts/test-chart", "displayName": "Test Chart"},
        ) as mock_req:
            result = dashboard.get_chart(chronicle_client, "test-chart")

        assert result["displayName"] == "Test Chart"
        assert mock_req.call_args.kwargs["endpoint_path"] == "dashboardCharts/test-chart"

    def test_get_chart_with_full_id(
        self, chronicle_client: Mock
    ) -> None:
        """Test get_chart with full project path chart ID."""
        full = "projects/test-project/locations/test-location/dashboardCharts/test-chart"
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"displayName": "Test Chart"},
        ) as mock_req:
            result = dashboard.get_chart(chronicle_client, full)

        assert result["displayName"] == "Test Chart"
        assert mock_req.call_args.kwargs["endpoint_path"] == "dashboardCharts/test-chart"

    def test_get_chart_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test get_chart function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to get chart details"),
        ):
            with pytest.raises(APIError, match="Failed to get chart details"):
                dashboard.get_chart(chronicle_client, "nonexistent-chart")


class TestEditChart:
    """Test the edit_chart function."""

    def test_edit_chart_query(
        self, chronicle_client: Mock
    ) -> None:
        """Test edit_chart with dashboard_query parameter."""
        dashboard_query = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "etag": "123456789",
            "query": 'udm.metadata.event_type = "NETWORK_CONNECTION"',
            "input": {"relative_time": {"timeUnit": "DAY", "startTimeVal": "7"}},
        }

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "updated-chart"},
        ) as mock_req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                dashboard_query=dashboard_query,
            )

        assert result == {"name": "updated-chart"}
        body = mock_req.call_args.kwargs["json"]
        assert body["dashboardQuery"] == dashboard_query
        assert body["editMask"] == "dashboard_query.query,dashboard_query.input"

    def test_edit_chart_details(
        self, chronicle_client: Mock
    ) -> None:
        """Test edit_chart with dashboard_chart parameter."""
        dashboard_chart = {
            "name": "projects/test-project/locations/test-location/dashboardCharts/test-chart",
            "etag": "123456789",
            "display_name": "Updated Chart Title",
            "visualization": {"legends": [{"legendOrient": "HORIZONTAL"}]},
        }

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "updated-chart"},
        ) as mock_req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                dashboard_chart=dashboard_chart,
            )

        assert result == {"name": "updated-chart"}
        body = mock_req.call_args.kwargs["json"]
        assert body["dashboardChart"] == dashboard_chart
        assert body["editMask"] == "dashboard_chart.display_name,dashboard_chart.visualization"

    def test_edit_chart_both(
        self, chronicle_client: Mock
    ) -> None:
        """Test edit_chart with both query and chart parameters."""
        dashboard_query = {
            "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
            "etag": "123456789",
            "query": 'udm.metadata.event_type = "NETWORK_CONNECTION"',
            "input": {"relative_time": {"timeUnit": "DAY", "startTimeVal": "7"}},
        }
        dashboard_chart = {
            "name": "projects/test-project/locations/test-location/dashboardCharts/test-chart",
            "etag": "123456789",
            "display_name": "Updated Chart Title",
        }

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "updated-chart"},
        ) as mock_req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                dashboard_query=dashboard_query,
                dashboard_chart=dashboard_chart,
            )

        assert result == {"name": "updated-chart"}
        body = mock_req.call_args.kwargs["json"]
        assert body["dashboardQuery"] == dashboard_query
        assert body["dashboardChart"] == dashboard_chart
        assert body["editMask"] == (
            "dashboard_query.query,dashboard_query.input,dashboard_chart.display_name"
        )

    def test_edit_chart_with_model_objects(
        self, chronicle_client: Mock
    ) -> None:
        """Test edit_chart with model objects instead of dictionaries."""
        # Use the model classes from the module (exercise conversion paths)
        interval = InputInterval(relative_time={"timeUnit": "DAY", "startTimeVal": "3"})
        dq = dashboard.DashboardQuery(
            name="test-query",
            etag="123456789",
            query='udm.metadata.event_type = "PROCESS_LAUNCH"',
            input=interval,
        )
        dc = dashboard.DashboardChart(
            name="test-chart",
            etag="123456789",
            display_name="Updated Chart",
            visualization={"type": "BAR_CHART"},
        )

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value={"name": "updated-chart"},
        ) as mock_req:
            result = dashboard.edit_chart(
                chronicle_client,
                dashboard_id="test-dashboard",
                dashboard_query=dq,
                dashboard_chart=dc,
            )

        assert result == {"name": "updated-chart"}
        # Basic sanity: ensure we passed a dict payload (not model objects)
        body = mock_req.call_args.kwargs["json"]
        assert isinstance(body, dict)
        assert "editMask" in body

    def test_edit_chart_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test edit_chart with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to edit chart"),
        ):
            with pytest.raises(APIError, match="Failed to edit chart"):
                dashboard.edit_chart(
                    chronicle_client,
                    dashboard_id="test-dashboard",
                    dashboard_query={
                        "name": "projects/test-project/locations/test-location/dashboardQueries/test-query",
                        "etag": "123123123",
                        "query": "invalid query",
                        "input": {
                            "relative_time": {
                                "timeUnit": "DAY",
                                "startTimeVal": "7"
                            },
                        },
                    },
                )


class TestExportDashboard:
    """Test the export_dashboard function."""

    def test_export_dashboard_success(
        self, chronicle_client: Mock
    ) -> None:
        """Test export_dashboard function with successful response."""
        upstream = {
            "inlineDestination": {
                "dashboards": [{"dashboard": {"name": "test-dashboard-1"}}, {"dashboard": {"name": "test-dashboard-2"}}]
            }
        }

        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                return_value=upstream,
        ) as mock_req:
            result = dashboard.export_dashboard(chronicle_client, ["test-dashboard-1", "test-dashboard-2"])

        assert result == upstream

        kwargs = mock_req.call_args.kwargs
        assert kwargs["method"] == "POST"
        assert kwargs["endpoint_path"] == "nativeDashboards:export"

        # Ensure names are qualified the way export_dashboard builds them
        names = kwargs["json"]["names"]
        assert names[0].endswith("/nativeDashboards/test-dashboard-1")
        assert names[1].endswith("/nativeDashboards/test-dashboard-2")

    def test_export_dashboard_error(
        self, chronicle_client: Mock
    ) -> None:
        """Test export_dashboard function with error response."""
        with patch(
                "secops.chronicle.dashboard.chronicle_request",
                side_effect=APIError("Failed to export dashboards"),
        ):
            with pytest.raises(APIError, match="Failed to export dashboards"):
                dashboard.export_dashboard(chronicle_client, ["test-dashboard-1"])
