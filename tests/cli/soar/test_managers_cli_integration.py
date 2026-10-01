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
"""Integration tests for the SecOps CLI integration managers commands."""

import json
import subprocess
import time
import uuid

import pytest


AUTH_ERRORS = [
    "401",
    "Unauthorized",
    "AuthenticationError",
    "Failed to get credentials",
    "DefaultCredentialsError",
]

_MANAGER_SCRIPT = (
    "def helper_function():\n"
    "    return 'Integration test manager helper'\n"
)


@pytest.mark.integration
def test_cli_managers_workflow(cli_env, common_args):
    """Test manager template, create, get, list, update, and delete via CLI.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    integration_name = None
    manager_id = None

    # Step 1: Find a target integration
    print("\n1. Finding a target integration")
    list_integrations_cmd = (
        ["secops"]
        + common_args
        + ["integration", "integrations", "list", "--page-size", "5"]
    )

    list_integrations_result = subprocess.run(
        list_integrations_cmd, env=cli_env, capture_output=True, text=True
    )

    if list_integrations_result.returncode != 0:
        error_output = (
            list_integrations_result.stderr + list_integrations_result.stdout
        )
        if any(err in error_output for err in AUTH_ERRORS):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.skip(f"Could not fetch integrations: {error_output[:200]}")

    try:
        integrations_data = json.loads(list_integrations_result.stdout)
        integrations = integrations_data.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available to test manager workflow.")
        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")
    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse integrations response")

    # Step 2: Get manager template
    print("\n2. Getting manager template")
    template_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "managers",
            "template",
            "--integration-name",
            integration_name,
        ]
    )

    template_result = subprocess.run(
        template_cmd, env=cli_env, capture_output=True, text=True
    )
    assert (
        template_result.returncode == 0
    ), f"Failed to get manager template: {template_result.stderr}"
    print("Retrieved manager template successfully")

    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Test Manager {unique_id}"

    try:
        # Step 3: Create a manager
        print("\n3. Creating a manager")
        create_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "managers",
                "create",
                "--integration-name",
                integration_name,
                "--display-name",
                display_name,
                "--code",
                _MANAGER_SCRIPT,
                "--description",
                "Temporary manager created by CLI integration test",
            ]
        )

        create_result = subprocess.run(
            create_cmd, env=cli_env, capture_output=True, text=True
        )

        if create_result.returncode != 0:
            error_output = create_result.stderr + create_result.stdout
            if any(err in error_output for err in AUTH_ERRORS):
                pytest.skip(
                    f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
                )
            pytest.fail(f"Failed to create manager: {error_output}")

        create_data = json.loads(create_result.stdout)
        assert "name" in create_data
        manager_id = create_data["name"].split("/")[-1]
        print(f"Created manager with ID: {manager_id}")

        time.sleep(2)

        # Step 4: Get manager details
        print("\n4. Getting manager details")
        get_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "managers",
                "get",
                "--integration-name",
                integration_name,
                "--manager-id",
                manager_id,
            ]
        )

        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            get_result.returncode == 0
        ), f"Failed to get manager: {get_result.stderr}"
        get_data = json.loads(get_result.stdout)
        assert get_data.get("displayName") == display_name
        print(f"Retrieved manager: {get_data.get('displayName')}")

        # Step 5: List managers and verify created manager appears
        print("\n5. Listing managers")
        list_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "managers",
                "list",
                "--integration-name",
                integration_name,
            ]
        )

        list_result = subprocess.run(
            list_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            list_result.returncode == 0
        ), f"Failed to list managers: {list_result.stderr}"
        list_data = json.loads(list_result.stdout)
        managers = list_data.get("managers", [])
        found = any(m.get("name", "").endswith(manager_id) for m in managers)
        assert found, f"Created manager {manager_id} not found in list."
        print(f"Found manager in list ({len(managers)} total)")

        # Step 6: Update the manager
        print("\n6. Updating the manager")
        updated_description = f"Updated by CLI integration test {unique_id}"
        update_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "managers",
                "update",
                "--integration-name",
                integration_name,
                "--manager-id",
                manager_id,
                "--description",
                updated_description,
            ]
        )

        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            update_result.returncode == 0
        ), f"Failed to update manager: {update_result.stderr}"
        update_data = json.loads(update_result.stdout)
        assert "name" in update_data
        print("Updated manager description successfully")

        # Step 7: Delete the manager
        print("\n7. Deleting the manager")
        delete_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "managers",
                "delete",
                "--integration-name",
                integration_name,
                "--manager-id",
                manager_id,
            ]
        )

        delete_result = subprocess.run(
            delete_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            delete_result.returncode == 0
        ), f"Failed to delete manager: {delete_result.stderr}"
        manager_id = None
        print("Manager deleted successfully")

    finally:
        # Cleanup: delete manager if not already deleted
        print("\n8. Cleaning up")
        if manager_id:
            delete_cmd = (
                ["secops"]
                + common_args
                + [
                    "integration",
                    "managers",
                    "delete",
                    "--integration-name",
                    integration_name,
                    "--manager-id",
                    manager_id,
                ]
            )
            delete_result = subprocess.run(
                delete_cmd, env=cli_env, capture_output=True, text=True
            )
            if delete_result.returncode == 0:
                print(f"Cleaned up manager: {manager_id}")
            else:
                print(
                    f"Warning: Failed to delete test manager:"
                    f" {delete_result.stderr}"
                )
