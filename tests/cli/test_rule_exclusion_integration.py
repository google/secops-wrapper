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
"""Integration tests for the SecOps CLI rule exclusion commands."""

import json
import os
import subprocess
import time
import uuid

# from datetime import datetime, timedelta

import pytest


@pytest.mark.integration
def test_cli_rule_exclusion_lifecycle(cli_env, common_args):
    """Test the rule exclusion create, get, update, and deployment commands."""
    # Generate unique rule exclusion name and ID
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Integration test rule exclusion {unique_id}"
    query = f'(ip = "8.8.8.8")'

    exclusion_id = None

    try:
        # 1. Create rule exclusion
        create_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "rule-exclusion",
                "create",
                "--display-name",
                display_name,
                "--type",
                "DETECTION_EXCLUSION",
                "--query",
                query,
            ]
        )

        print(f"\nCreating rule exclusion: {display_name}")
        create_result = subprocess.run(
            create_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert create_result.returncode == 0

        # Parse the output to get the rule exclusion ID
        exclusion_data = json.loads(create_result.stdout)
        assert "name" in exclusion_data
        exclusion_id = exclusion_data["name"].split("/")[-1]
        print(f"Created rule exclusion with ID: {exclusion_id}")

        # Wait briefly for the rule exclusion to be fully created
        time.sleep(2)

        # 2. Get the rule exclusion
        get_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "rule-exclusion",
                "get",
                "--id",
                exclusion_id,
            ]
        )

        print(f"\nGetting rule exclusion details: {exclusion_id}")
        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert get_result.returncode == 0

        # Verify the result contains expected data
        get_data = json.loads(get_result.stdout)
        assert "name" in get_data
        assert "displayName" in get_data
        assert get_data["displayName"] == display_name
        assert "query" in get_data
        assert get_data["query"] == query

        # 3. Update the rule exclusion
        updated_display_name = f"Updated {display_name}"
        update_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "rule-exclusion",
                "update",
                "--id",
                exclusion_id,
                "--display-name",
                updated_display_name,
                "--update-mask",
                "display_name",
            ]
        )

        print(f"\nUpdating rule exclusion: {exclusion_id}")
        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert update_result.returncode == 0

        # Verify the update was applied
        update_data = json.loads(update_result.stdout)
        assert "displayName" in update_data
        assert update_data["displayName"] == updated_display_name

        # 4. Get deployment status
        get_deployment_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "rule-exclusion",
                "get-deployment",
                "--id",
                exclusion_id,
            ]
        )

        print(f"\nGetting deployment status: {exclusion_id}")
        get_deployment_result = subprocess.run(
            get_deployment_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert get_deployment_result.returncode == 0

        # Verify the result contains enabled field
        deployment_data = json.loads(get_deployment_result.stdout)
        assert exclusion_data["name"] in deployment_data.get("name")
        initial_enabled_state = deployment_data.get("enabled", False)

        # 5. Update deployment status (toggle enabled)
        toggle_enabled = "true" if not initial_enabled_state else "false"
        update_deployment_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "rule-exclusion",
                "update-deployment",
                "--id",
                exclusion_id,
                "--enabled",
                toggle_enabled,
            ]
        )

        print(f"\nToggling enabled state to: {toggle_enabled}")
        update_deployment_result = subprocess.run(
            update_deployment_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert update_deployment_result.returncode == 0

        # Verify the update was applied
        updated_deployment_data = json.loads(update_deployment_result.stdout)
        assert "enabled" in updated_deployment_data
        expected_enabled = toggle_enabled == "true"
        assert updated_deployment_data["enabled"] == expected_enabled

        # 6. Compute activity (might not have activity if newly created)
        # today = datetime.now()
        # yesterday = today - timedelta(days=1)

        # activity_cmd = (
        #     [
        #         "secops",
        #     ]
        #     + common_args
        #     + [
        #         "rule-exclusion",
        #         "compute-activity",
        #         "--id",
        #         exclusion_id,
        #         "--start-time",
        #         yesterday.strftime("%Y-%m-%dT00:00:00Z"),
        #         "--end-time",
        #         today.strftime("%Y-%m-%dT23:59:59Z"),
        #     ]
        # )

        # print(f"\nComputing activity for: {exclusion_id}")
        # activity_result = subprocess.run(
        #     activity_cmd, env=cli_env, capture_output=True, text=True
        # )

        # # We don't assert success here since new exclusions might not have activity data
        # # Just verify we can run the command without errors
        # print(f"Activity command exit code: {activity_result.returncode}")
        # if activity_result.returncode != 0:
        #     print(
        #         f"Activity command error (expected for new exclusions): {activity_result.stderr}"
        #     )

    finally:
        # Clean up: Archive the rule exclusion
        if exclusion_id:
            archive_cmd = (
                [
                    "secops",
                ]
                + common_args
                + [
                    "rule-exclusion",
                    "update-deployment",
                    "--id",
                    exclusion_id,
                    "--archived",
                    "true",
                ]
            )

            print(f"\nCleaning up: Archiving rule exclusion: {exclusion_id}")
            archive_result = subprocess.run(
                archive_cmd, env=cli_env, capture_output=True, text=True
            )

            # Check that the command executed successfully
            if archive_result.returncode == 0:
                print(f"Successfully archived rule exclusion: {exclusion_id}")
            else:
                print(
                    f"Failed to archive rule exclusion: {archive_result.stderr}"
                )


@pytest.mark.integration
def test_cli_rule_exclusion_pagination(cli_env, common_args):
    """Test rule exclusion list pagination."""
    # First request with small page size
    first_page_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "rule-exclusion",
            "list",
            "--page-size",
            "1",  # Very small to force pagination
        ]
    )

    print("\nFetching first page of rule exclusions")
    first_page_result = subprocess.run(
        first_page_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert first_page_result.returncode == 0

    # Parse the output
    first_page_data = json.loads(first_page_result.stdout)

    # Check if we have a next page token and at least one exclusion
    if "nextPageToken" in first_page_data and first_page_data.get(
        "findingsRefinements"
    ):
        next_page_token = first_page_data["nextPageToken"]
        first_page_item = first_page_data["findingsRefinements"][0]

        # Request second page using the token
        second_page_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "rule-exclusion",
                "list",
                "--page-size",
                "1",
                "--page-token",
                next_page_token,
            ]
        )

        print("\nFetching second page with token")
        second_page_result = subprocess.run(
            second_page_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert second_page_result.returncode == 0

        # Parse the output
        second_page_data = json.loads(second_page_result.stdout)

        # Verify we got a second page with different data
        if second_page_data.get("findingsRefinements"):
            second_page_item = second_page_data["findingsRefinements"][0]
            assert (
                first_page_item["name"] != second_page_item["name"]
            ), "Expected different items on second page"
            print(
                "Pagination successful - received different items on second page"
            )
        else:
            print(
                "Second page empty - pagination works but not enough items to show"
            )
    else:
        print(
            "No pagination token returned - not enough rule exclusions for pagination test"
        )
