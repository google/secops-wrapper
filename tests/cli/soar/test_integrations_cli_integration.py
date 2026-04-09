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
"""Integration tests for the SecOps CLI integrations commands."""

import json
import subprocess
import time
import uuid

import pytest


@pytest.mark.integration
def test_cli_integrations_workflow(cli_env, common_args):
    """Test the integration create, get, update-custom, list, affected-items and delete commands.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    auth_errors = [
        "401",
        "Unauthorized",
        "AuthenticationError",
        "Failed to get credentials",
        "DefaultCredentialsError",
    ]

    # Step 1: Create custom integration
    print("\n1. Creating custom integration")
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Test Integration {unique_id}"

    create_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "integrations",
            "create",
            "--display-name",
            display_name,
            "--description",
            "Created by CLI integration test",
        ]
    )

    create_result = subprocess.run(
        create_cmd, env=cli_env, capture_output=True, text=True
    )

    if create_result.returncode != 0:
        error_output = create_result.stderr + create_result.stdout
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.fail(f"Failed to create integration: {error_output}")

    try:
        create_data = json.loads(create_result.stdout)
        assert "name" in create_data
        integration_id = create_data["name"].split("/")[-1]
        print(f"Created integration with ID: {integration_id}")
    except (json.JSONDecodeError, KeyError):
        pytest.fail("Could not parse create response")

    time.sleep(2)

    try:
        # Step 2: Get integration details
        print("\n2. Getting integration details")
        get_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "integrations",
                "get",
                "--integration-id",
                integration_id,
            ]
        )

        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )
        assert get_result.returncode == 0
        get_data = json.loads(get_result.stdout)
        assert get_data.get("displayName") == display_name
        print(f"Successfully retrieved integration: {display_name}")

        # Step 3: Update integration
        print("\n3. Updating custom integration")
        updated_name = f"Updated CLI Test Integration {unique_id}"
        update_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "integrations",
                "update-custom",
                "--integration-id",
                integration_id,
                "--display-name",
                updated_name,
                "--description",
                "Updated description",
                "--update-mask",
                "displayName,description",
            ]
        )

        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )
        assert update_result.returncode == 0
        print(f"Update Result STDOUT: {update_result.stdout}")
        update_data = json.loads(update_result.stdout)
        assert (
            update_data.get("integration", {}).get("description")
            == "Updated description"
        )
        print(f"Successfully updated integration: {updated_name}")

        # Step 4: List integrations
        print("\n4. Listing integrations")
        list_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "integrations",
                "list",
                "--page-size",
                "50",
            ]
        )

        list_result = subprocess.run(
            list_cmd, env=cli_env, capture_output=True, text=True
        )
        assert list_result.returncode == 0
        list_data = json.loads(list_result.stdout)
        integrations = list_data.get("integrations", [])
        found = any(
            i.get("name", "").endswith(
                update_data.get("integration", {}).get("name").split("/")[-1]
            )
            for i in integrations
        )
        assert found, f"Created integration {integration_id} not found in list."
        print("Successfully found integration in list results")

        # Step 5: Get affected items
        print("\n5. Getting affected items")
        affected_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "integrations",
                "affected-items",
                "--integration-id",
                integration_id,
            ]
        )

        affected_result = subprocess.run(
            affected_cmd, env=cli_env, capture_output=True, text=True
        )
        assert affected_result.returncode == 0
        print("Successfully retrieved affected items")

    finally:
        # Step 6: Delete integration (Cleanup)
        print(f"\n6. Cleaning up: Deleting integration {integration_id}")
        delete_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "integrations",
                "delete",
                "--integration-id",
                integration_id,
            ]
        )

        delete_result = subprocess.run(
            delete_cmd, env=cli_env, capture_output=True, text=True
        )
        if delete_result.returncode == 0:
            print(f"Successfully deleted integration: {integration_id}")
        else:
            print(
                f"Warning: Failed to delete test integration: {delete_result.stderr}"
            )
