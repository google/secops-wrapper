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
"""Integration tests for Chronicle Investigations API.

These tests require valid credentials and API access.
Note: Investigations cannot be deleted via API, so cleanup is limited.
"""
import pytest
from datetime import datetime, timedelta

from secops import SecOpsClient
from secops.chronicle import DetectionType
from secops.exceptions import APIError

from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_list_and_get_investigation():
    """Test listing and getting investigations workflow."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        # Step 1: List investigations
        list_result = chronicle.list_investigations()
        assert isinstance(list_result, dict)
        assert "investigations" in list_result
        assert isinstance(list_result["investigations"], list)
        print(f"Found {len(list_result['investigations'])} investigations")

        if not list_result["investigations"]:
            pytest.skip("No investigations available to test get operation")

        # Step 2: Get a specific investigation
        inv = list_result["investigations"][0]
        investigation_id = inv["name"].split("/")[-1]
        print(f"Testing get for investigation: {investigation_id}")

        get_result = chronicle.get_investigation(investigation_id)
        assert isinstance(get_result, dict)
        assert "name" in get_result
        assert investigation_id in get_result["name"]
        print(f"Successfully retrieved investigation: {get_result['name']}")

        if "verdict" in get_result:
            print(f"Investigation verdict: {get_result['verdict']}")
        if "status" in get_result:
            print(f"Investigation status: {get_result['status']}")

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.skip(f"List/get investigation test skipped: {str(e)}")


@pytest.mark.integration
def test_list_investigations_with_pagination():
    """Test listing investigations with pagination parameters."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        result = chronicle.list_investigations(page_size=5)
        assert isinstance(result, dict)
        assert "investigations" in result
        assert len(result["investigations"]) <= 5
        print(
            f"Retrieved {len(result['investigations'])} "
            f"investigations with page_size=5"
        )

        if "nextPageToken" in result:
            next_result = chronicle.list_investigations(
                page_size=5, page_token=result["nextPageToken"]
            )
            assert isinstance(next_result, dict)
            assert "investigations" in next_result
            print(
                f"Retrieved next page with "
                f"{len(next_result['investigations'])} investigations"
            )

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.skip(f"List investigations pagination test skipped: {str(e)}")


@pytest.mark.integration
def test_trigger_and_fetch_associated_workflow():
    """Test triggering investigation and fetching associated ones."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    alert_id = None

    try:
        # Step 1: Get an alert ID to trigger investigation
        print("Fetching alerts to get an alert ID...")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        alerts_result = chronicle.get_alerts(
            start_time=start_time, end_time=end_time, max_alerts=1
        )
        if not alerts_result.get("alerts"):
            pytest.skip("No alerts available to test trigger operation")
        alert_id = alerts_result["alerts"]["alerts"][0]["id"]
        print(f"Using alert ID: {alert_id}")

        # Step 2: Trigger investigation for the alert
        print(f"Triggering investigation for alert: {alert_id}")
        trigger_result = chronicle.trigger_investigation(alert_id)
        assert isinstance(trigger_result, dict)
        assert "name" in trigger_result
        print(
            f"Investigation triggered successfully: "
            f"{trigger_result['name']}"
        )

        if "status" in trigger_result:
            print(f"Investigation status: {trigger_result['status']}")

        # Step 3: Fetch associated investigations for the alert
        print(f"Fetching investigations associated with alert: {alert_id}")
        fetch_result = chronicle.fetch_associated_investigations(
            detection_type=DetectionType.ALERT,
            alert_ids=[alert_id],
            association_limit_per_detection=5,
        )
        assert isinstance(fetch_result, dict)
        print(f"Fetch associated result: {fetch_result.keys()}")

        if "associationsList" in fetch_result:
            associations = fetch_result["associationsList"]
            print(f"Found associations for {len(associations)} detections")

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.skip(f"Trigger/fetch workflow test skipped: {str(e)}")


@pytest.mark.integration
def test_fetch_associated_investigations_with_cases():
    """Test fetching investigations associated with cases."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        # Try to get a case ID
        print("Fetching cases to get a case ID...")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        cases_result = chronicle.get_cases(
            start_time=start_time, end_time=end_time
        )
        if not cases_result.get("cases"):
            pytest.skip("No cases available to test fetch operation")

        case_id = cases_result["cases"][0]["name"].split("/")[-1]
        print(f"Using case ID: {case_id}")

        # Fetch associated investigations for the case
        print(f"Fetching investigations associated with case: {case_id}")
        result = chronicle.fetch_associated_investigations(
            detection_type=DetectionType.CASE,
            case_ids=[case_id],
            association_limit_per_detection=3,
        )
        assert isinstance(result, dict)
        print(f"Fetch associated with cases result: {result.keys()}")

        if "associationsList" in result:
            print(
                f"Found associations for "
                f"{len(result['associationsList'])} detections"
            )

    except APIError as e:
        print(f"API Error: {str(e)}")
        pytest.skip(f"Fetch associated with cases test skipped: {str(e)}")
