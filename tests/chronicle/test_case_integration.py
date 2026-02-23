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
"""Integration tests for Chronicle case management.

These tests require valid credentials and API access.
They interact with real Chronicle API endpoints.
"""

import pytest
from secops import SecOpsClient
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON
from secops.exceptions import APIError


@pytest.mark.integration
def test_list_and_get_cases_workflow():
    """Test listing and getting cases workflow."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Test basic list
    result = chronicle.list_cases(page_size=5)
    assert isinstance(result, dict)
    assert "cases" in result
    assert isinstance(result["cases"], list)
    assert "totalSize" in result

    # Test with as_list=False (default)
    result_dict = chronicle.list_cases(page_size=3, as_list=False)
    assert isinstance(result_dict, dict)
    assert "cases" in result_dict
    assert "nextPageToken" in result_dict or "totalSize" in result_dict

    # Test with as_list=True
    result_list = chronicle.list_cases(page_size=3, as_list=True)
    assert isinstance(result_list, list)
    if result_list:
        assert "name" in result_list[0]

    # Test list with filter
    filtered = chronicle.list_cases(
        page_size=5, filter_query='status = "OPENED"'
    )
    assert isinstance(filtered, dict)
    assert "cases" in filtered

    # Test get case by ID
    if result.get("cases"):
        case_data = result["cases"][0]
        case_id = case_data.get("name", "").split("/")[-1]

        if case_id:
            case = chronicle.get_case(case_id)
            assert case is not None
            assert hasattr(case, "id")
            assert hasattr(case, "display_name")
            assert hasattr(case, "priority")
            assert hasattr(case, "status")
    else:
        pytest.skip("No cases available for testing")


@pytest.mark.integration
def test_case_update_workflow():
    """Test case update (patch) workflow.

    Tests patching a case's priority and verifying the change.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Use dedicated test case ID
    case_id = "7418669"

    # Get original case state
    original_case = chronicle.get_case(case_id)
    original_priority = original_case.priority

    # Determine new priority (toggle between HIGH and MEDIUM)
    new_priority = (
        "PRIORITY_MEDIUM"
        if original_priority == "PRIORITY_HIGH"
        else "PRIORITY_HIGH"
    )

    try:
        # Update the case
        updated_case = chronicle.patch_case(
            case_id, {"priority": new_priority}, update_mask="priority"
        )

        assert updated_case is not None
        assert updated_case.priority == new_priority

        # Verify by fetching again
        verified_case = chronicle.get_case(case_id)
        assert verified_case.priority == new_priority

    finally:
        # Cleanup: Restore original priority
        try:
            chronicle.patch_case(
                case_id,
                {"priority": original_priority},
                update_mask="priority",
            )
        except Exception as e:
            print(f"Cleanup warning: Failed to restore priority - {e}")


@pytest.mark.integration
def test_bulk_operations_workflow():
    """Test bulk operations workflow including tag, priority, stage."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Use dedicated test case ID
    case_ids = [7418669]

    print(f"\nTesting bulk operations on cases: {case_ids}")

    # Test bulk add tag

    result = chronicle.execute_bulk_add_tag(case_ids, ["integration-test-tag"])
    assert isinstance(result, dict)
    print("Bulk add tag: SUCCESS")

    # Test bulk change priority
    result = chronicle.execute_bulk_change_priority(case_ids, "PRIORITY_MEDIUM")
    assert isinstance(result, dict)
    print("Bulk change priority: SUCCESS")

    # Test bulk change stage
    result = chronicle.execute_bulk_change_stage(case_ids, "Triage")
    assert isinstance(result, dict)
    print("Bulk change stage: SUCCESS")


@pytest.mark.integration
def test_bulk_assign():
    """Test bulk assign operation."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Use dedicated test case ID
    case_ids = [7418669]

    try:
        result = chronicle.execute_bulk_assign(case_ids, "@Administrator")
        assert isinstance(result, dict)
        print("Bulk assign: SUCCESS")
    except APIError as e:
        error_msg = str(e)
        # Skip if API returns INTERNAL/500 error
        if "INTERNAL" in error_msg or "500" in error_msg:
            pytest.skip(f"Bulk assign API returned INTERNAL error: {e}")
        # Re-raise other errors
        raise


@pytest.mark.integration
def test_bulk_close_reopen_workflow():
    """Test bulk close and reopen workflow.

    This test closes cases and then reopens them.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Use dedicated test case ID
    case_ids = [7418669]

    print(f"\nTesting close/reopen workflow on cases: {case_ids}")

    try:
        # Close the cases
        close_result = chronicle.execute_bulk_close(
            case_ids=case_ids,
            close_reason="MAINTENANCE",
            root_cause="Integration test - closing for testing",
        )
        assert isinstance(close_result, dict)
        print("Bulk close: SUCCESS")

        # Verify cases are closed by fetching one
        if case_ids:
            case = chronicle.get_case(str(case_ids[0]))
            assert case.status == "CLOSED"
            print(f"Verified case {case_ids[0]} is CLOSED")

    finally:
        # Cleanup: Reopen the cases
        try:
            reopen_result = chronicle.execute_bulk_reopen(
                case_ids, "Integration test - reopening after test"
            )
            assert isinstance(reopen_result, dict)
            print("Bulk reopen (cleanup): SUCCESS")

            # Verify case is reopened
            if case_ids:
                case = chronicle.get_case(str(case_ids[0]))
                assert case.status == "OPENED"
                print(f"Verified case {case_ids[0]} is OPENED")

        except Exception as e:
            print(f"Cleanup warning: Failed to reopen cases - {e}")
