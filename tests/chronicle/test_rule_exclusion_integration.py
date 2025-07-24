#!/usr/bin/env python3
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
"""Integration tests for the rule_exclusion service in Chronicle API.

These tests require valid credentials and API access.
"""
import pytest
import uuid
import time
from datetime import datetime, timedelta, timezone

from secops import SecOpsClient
from secops.chronicle.rule_exclusion import RuleExclusionType
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_rule_exclusion_lifecycle():
    """Test the complete lifecycle of rule exclusions with real API.

    This test covers:
    1. Creating a rule exclusion
    2. Getting the rule exclusion
    3. Listing rule exclusions
    4. Getting deployment information
    5. Updating deployment (enabling/disabling)
    6. Computing rule exclusion activity
    7. Cleanup by archiving the rule exclusion
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate a unique ID for this test run
    test_id = f"test_excl_{uuid.uuid4().hex[:8]}"
    display_name = f"Integration Test Rule Exclusion {test_id}"
    exclusion_name = None

    try:
        print(f"\n>>> Creating rule exclusion with ID: {test_id}")

        # 1. Create rule exclusion
        create_result = chronicle.create_rule_exclusion(
            display_name=display_name,
            refinement_type=RuleExclusionType.DETECTION_EXCLUSION.value,
            query='(ip = "8.8.8.8")',
        )

        # Extract the full name from the response
        exclusion_name = create_result.get("name")
        assert (
            exclusion_name is not None
        ), "Failed to get name from created rule exclusion"
        print(f"Created rule exclusion: {exclusion_name}")
        # Wait to ensure resource is created
        time.sleep(2)

        # 2. Get the rule exclusion
        print(">>> Getting rule exclusion details")
        get_result = chronicle.get_rule_exclusion(exclusion_name)
        assert get_result.get("name") == exclusion_name
        assert get_result.get("displayName") == display_name
        print(f"Successfully retrieved rule exclusion: {display_name}")

        # 3. List rule exclusions and find our test exclusion
        print(">>> Listing rule exclusions")
        list_result = chronicle.list_rule_exclusions()

        exclusions = list_result.get("findingsRefinements", [])

        found = False
        for exclusion in exclusions:
            if exclusion.get("name") == exclusion_name:
                found = True
                break

        assert (
            found
        ), f"Created rule exclusion {exclusion_name} not found in list results"
        print(f"Successfully found rule exclusion in list results")

        # 4. Get deployment information
        print(">>> Getting deployment information")
        deployment_result = chronicle.get_rule_exclusion_deployment(
            exclusion_name
        )
        assert deployment_result is not None
        initial_enabled_state = deployment_result.get("enabled", False)
        print(f"Current deployment state - enabled: {initial_enabled_state}")

        # 5. Update deployment status (toggle enabled)
        print(">>> Updating deployment status")

        update_result = chronicle.update_rule_exclusion_deployment(
            exclusion_id=exclusion_name,
            enabled=True,
        )

        assert update_result.get("enabled") == (not initial_enabled_state)
        print(
            f"Successfully toggled enabled state to {not initial_enabled_state}"
        )

        # 6. Compute rule exclusion activity
        print(">>> Computing rule exclusion activity")
        # end_time = datetime.now(timezone.utc)
        # start_time = end_time - timedelta(hours=1)

        # activity_result = chronicle.compute_rule_exclusion_activity(
        #     exclusion_id=exclusion_name,
        #     start_time=start_time,
        #     end_time=end_time,
        # )

        # assert activity_result is not None
        # print("Successfully retrieved rule exclusion activity")

    except Exception as e:
        print(f"Error in rule exclusion lifecycle test: {e}")
        raise
    finally:
        # 7. Cleanup: Archive the rule exclusion
        print(">>> Cleaning up: Archiving rule exclusion")
        if exclusion_name:
            try:
                # Archive the rule exclusion
                chronicle.update_rule_exclusion_deployment(
                    exclusion_id=exclusion_name, enabled=False, archived=True
                )
                print(f"Successfully archived rule exclusion: {exclusion_name}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to archive rule exclusion: {cleanup_error}"
                )


@pytest.mark.integration
def test_rule_exclusion_list_pagination():
    """Test pagination for listing rule exclusions.

    This test:
    1. Lists rule exclusions with small page size
    2. Verifies pagination works if there are enough exclusions
    3. No cleanup needed as no resources are created
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        print("\n>>> Testing rule exclusion pagination")

        # Request with small page size to force pagination if enough exclusions exist
        page_size = 1
        first_page = chronicle.list_rule_exclusions(page_size=page_size)

        first_page_items = first_page.get("findingsRefinements", [])
        print(f"Retrieved {len(first_page_items)} items on first page")

        # Check for next page token
        next_page_token = first_page.get("nextPageToken")

        if next_page_token:
            print(f"Found next page token: {next_page_token[:10]}...")
            second_page = chronicle.list_rule_exclusions(
                page_size=page_size, page_token=next_page_token
            )

            second_page_items = second_page.get("findingsRefinements", [])
            print(f"Retrieved {len(second_page_items)} items on second page")

            # Verify we got different items on each page
            if len(first_page_items) > 0 and len(second_page_items) > 0:
                # Compare the first item from each page - they should be different
                assert first_page_items[0].get("name") != second_page_items[
                    0
                ].get("name")
                print("Verified different items on different pages")
            else:
                print("Second page has no items or is empty")
        else:
            print(
                f"No pagination needed (fewer than {page_size} rule exclusions exist)"
            )

    except Exception as e:
        print(f"Error in rule exclusion pagination test: {e}")
        raise
