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
"""Integration tests for Chronicle Dashboard API.

These tests require valid credentials and API access.
"""
import time
import uuid

import pytest

from secops import SecOpsClient

from secops.exceptions import APIError
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_dashboard_list():
    """Test listing dashboards with real API."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)
    dashboard_ids = []

    # Generate unique dashboard name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Dashboard {unique_id}"
    description = "Integration test dashboard"
    try:
        for i in range(2):
            created_dashboard = chronicle.create_dashboard(
                display_name=f"{i}-{display_name}",
                description=description,
                access_type="PRIVATE",
            )

            assert created_dashboard is not None
            dashboard_ids.append(created_dashboard["name"].split("/")[-1])

        time.sleep(5)

        result = chronicle.list_dashboards(page_size=1)
        assert "nativeDashboards" in result
        assert result["nativeDashboards"]
        assert len(result["nativeDashboards"]) == 1
        assert "nextPageToken" in result
        assert result["nextPageToken"]

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.skip(f"Dashboard list test skipped due to API error: {str(e)}")

    finally:
        if dashboard_ids:
            print(f"Cleaning up dashboard ids: {dashboard_ids}")
            for dashboard_id in dashboard_ids:
                chronicle.delete_dashboard(dashboard_id=dashboard_id)
                print(f"Cleaned up dashboard id: {dashboard_id}")


@pytest.mark.integration
def test_dashboard_lifecycle():
    """Test full dashboard lifecycle: create, get, update, duplicate, delete."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique dashboard identifiers
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Dashboard {unique_id}"
    updated_name = f"Updated Dashboard {unique_id}"
    description = "Integration test dashboard"

    cleanup_dashboard_ids = []

    try:
        # 1. CREATE dashboard
        print(f"Creating dashboard: {display_name}")
        created_dashboard = chronicle.create_dashboard(
            display_name=display_name,
            description=description,
            access_type="PRIVATE",
        )

        assert created_dashboard is not None
        assert "name" in created_dashboard
        assert created_dashboard.get("displayName") == display_name
        dashboard_id = created_dashboard["name"].split("/")[-1]
        cleanup_dashboard_ids.append(dashboard_id)
        print(f"Dashboard created successfully: {dashboard_id}")

        # Wait a moment for the dashboard to be fully created
        time.sleep(2)

        # 2. GET dashboard details
        dashboard_details = chronicle.get_dashboard(
            dashboard_id=dashboard_id, view="FULL"
        )
        assert dashboard_details is not None
        assert dashboard_details.get("displayName") == display_name
        print("Successfully retrieved dashboard details")

        # 3. UPDATE dashboard
        updated_dashboard = chronicle.update_dashboard(
            dashboard_id=dashboard_id,
            display_name=updated_name,
            description="Updated description",
        )
        assert updated_dashboard.get("displayName") == updated_name
        print(f"Dashboard updated successfully to: {updated_name}")

        # Verify update with another GET
        updated_details = chronicle.get_dashboard(dashboard_id=dashboard_id)
        assert updated_details.get("displayName") == updated_name
        print("Verified dashboard was updated")

        # 4. DUPLICATE dashboard
        duplicate_name = f"Duplicate Dashboard {unique_id}"
        duplicated_dashboard = chronicle.duplicate_dashboard(
            dashboard_id=dashboard_id,
            display_name=duplicate_name,
            access_type="PRIVATE",
        )
        assert duplicated_dashboard is not None
        assert duplicated_dashboard.get("displayName") == duplicate_name
        duplicated_id = duplicated_dashboard["name"].split("/")[-1]
        cleanup_dashboard_ids.append(duplicated_id)
        print(f"Dashboard duplicated successfully: {duplicated_id}")

        # Verify duplicate exists
        duplicate_details = chronicle.get_dashboard(dashboard_id=duplicated_id)
        assert duplicate_details.get("displayName") == duplicate_name
        print("Verified duplicate dashboard exists")

        # 5. DELETE both dashboards
        # Delete original dashboard
        chronicle.delete_dashboard(dashboard_id=dashboard_id)
        print(f"Original dashboard deleted successfully: {dashboard_id}")

        # Verify deletion of original
        try:
            chronicle.get_dashboard(dashboard_id=dashboard_id)
            assert False, "Original dashboard should have been deleted"
        except APIError:
            print("Verified original dashboard was deleted")
            cleanup_dashboard_ids.remove(dashboard_id)

        # Delete duplicate dashboard
        chronicle.delete_dashboard(dashboard_id=duplicated_id)
        print(f"Duplicate dashboard deleted successfully: {duplicated_id}")

        # Verify deletion of duplicate
        try:
            chronicle.get_dashboard(dashboard_id=duplicated_id)
            assert False, "Duplicate dashboard should have been deleted"
        except APIError:
            print("Verified duplicate dashboard was deleted")
            cleanup_dashboard_ids.remove(duplicated_id)

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.fail(f"Dashboard lifecycle test failed: {str(e)}")

    finally:
        # Clean up if test fails partway through
        if cleanup_dashboard_ids:
            for dashboard_id in cleanup_dashboard_ids:
                chronicle.delete_dashboard(dashboard_id=dashboard_id)
                print(f"Cleaned up dashboard id: {dashboard_id}")


@pytest.mark.integration
def test_dashboard_chart_lifecycle():
    """Test full dashboard chart lifecycle: add, get, edit and remove."""

    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique dashboard name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Chart Test Dashboard {unique_id}"
    chart_name = f"Test Chart {unique_id}"

    created_dashboard = None
    try:
        # Create the dashboard
        created_dashboard = chronicle.create_dashboard(
            display_name=display_name, access_type="PRIVATE"
        )
        dashboard_id = created_dashboard["name"].split("/")[-1]
        print(f"Dashboard created for chart test: {dashboard_id}")

        # Add Chart to created dashboard
        query = """
            metadata.event_type = "NETWORK_DNS"
            match:
            principal.hostname
            outcome:
            $dns_query_count = count(metadata.id)
            order:
            principal.hostname asc
        """
        chart_layout = {"startX": 0, "spanX": 12, "startY": 0, "spanY": 8}
        chart_datasource = {"dataSources": ["UDM"]}
        interval = {"relativeTime": {"timeUnit": "DAY", "startTimeVal": "1"}}

        chart_result = chronicle.add_chart(
            dashboard_id=dashboard_id,
            display_name=chart_name,
            query=query,
            chart_layout=chart_layout,
            chart_datasource=chart_datasource,
            interval=interval,
        )

        assert chart_result is not None
        assert "dashboardChart" in chart_result
        assert "name" in chart_result["dashboardChart"]
        print(f"Chart added successfully to dashboard")

        # Get chart details
        chart_id = chart_result["dashboardChart"]["name"].split("/")[-1]
        chart_details = chronicle.get_chart(chart_id=chart_id)

        assert chart_details is not None
        assert "name" in chart_details
        assert chart_id in chart_details["name"]
        assert "etag" in chart_details
        print("Chart details fetched successfully")

        # Edit chart detail
        updated_dashboard_chart = {
            "name": chart_id,
            "displayName": "Updated Chart name",
            "etag": chart_details["etag"],
        }
        updated_chart = chronicle.edit_chart(
            dashboard_id=dashboard_id, dashboard_chart=updated_dashboard_chart
        )

        assert updated_chart is not None
        assert "dashboardChart" in updated_chart
        assert "displayName" in updated_chart["dashboardChart"]
        assert (
            updated_chart["dashboardChart"]["displayName"]
            == "Updated Chart name"
        )
        print("Chart updated successfully")

        # Remove chart from dashboard
        chronicle.remove_chart(dashboard_id=dashboard_id, chart_id=chart_id)
        print("Chart removed successfully")

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.fail(f"Dashboard chart test failed: {str(e)}")

    finally:
        # Clean up
        if created_dashboard:
            try:
                dashboard_id = created_dashboard["name"].split("/")[-1]
                chronicle.delete_dashboard(dashboard_id=dashboard_id)
                print(f"Cleaned up test dashboard: {dashboard_id}")
            except Exception as e:
                print(f"Clean up failed: {str(e)}")


@pytest.mark.integration
def test_dashboard_import():
    """Test importing a dashboard."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    imported_dashboard_id = None

    try:
        # dashboard import payload
        import_payload = {
            "dashboard": {
                "name": "50221a9e-afd7-4f7b-8043-35a925454995",
                "displayName": "Source Dashboard 8f736a58",
                "description": "Source dashboard for import test",
                "definition": {
                    "filters": [
                        {
                            "id": "GlobalTimeFilter",
                            "dataSource": "GLOBAL",
                            "filterOperatorAndFieldValues": [
                                {
                                    "filterOperator": "PAST",
                                    "fieldValues": ["1", "DAY"],
                                }
                            ],
                            "displayName": "Global Time Filter",
                            "isStandardTimeRangeFilter": True,
                            "isStandardTimeRangeFilterEnabled": True,
                        }
                    ]
                },
                "type": "CUSTOM",
                "etag": "9bcb466d09e461d19aa890d0f5eb38a5496fa085dc2605954e4457b408acd916",
                "access": "DASHBOARD_PRIVATE",
            }
        }

        # 1. Import dashboard
        imported_dashboard = chronicle.import_dashboard(import_payload)

        assert imported_dashboard is not None
        assert "results" in imported_dashboard
        assert len(imported_dashboard["results"]) > 0
        assert "dashboard" in imported_dashboard["results"][0]

        # Extract the imported dashboard ID
        imported_dashboard_path = imported_dashboard["results"][0]["dashboard"]
        imported_dashboard_id = imported_dashboard_path.split("/")[-1]
        print(f"Imported dashboard with ID: {imported_dashboard_id}")

        # 2. Verify the imported dashboard exists
        imported_details = chronicle.get_dashboard(
            dashboard_id=imported_dashboard_id
        )
        assert imported_details is not None

        # Verify key properties match the original import payload
        assert (
            imported_details.get("displayName")
            == import_payload["dashboard"]["displayName"]
        )
        assert (
            imported_details.get("description")
            == import_payload["dashboard"]["description"]
        )
        assert (
            imported_details.get("access")
            == import_payload["dashboard"]["access"]
        )
        assert (
            imported_details.get("type") == import_payload["dashboard"]["type"]
        )

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.fail(f"Dashboard import test failed: {str(e)}")

    finally:
        # Clean up the imported dashboard
        if imported_dashboard_id:
            try:
                chronicle.delete_dashboard(dashboard_id=imported_dashboard_id)
                print(
                    f"Cleaned up imported dashboard with ID: {imported_dashboard_id}"
                )
            except Exception as e:
                print(f"Clean up failed for imported dashboard: {str(e)}")
