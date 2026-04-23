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
"""Integration tests for the SecOps CLI integration actions commands."""

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

_ACTION_SCRIPT = (
    "from SiemplifyAction import SiemplifyAction\n"
    "siemplify = SiemplifyAction()\n"
    "siemplify.end('Test action', True)\n"
)


@pytest.mark.integration
def test_cli_actions_workflow(cli_env, common_args):
    """Test action template, create, get, list, update, and delete via CLI.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    integration_name = None
    action_id = None

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
            pytest.skip("No integrations available to test action workflow.")
        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")
    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse integrations response")

    # Step 2: Get action template
    print("\n2. Getting action template")
    template_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "actions",
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
    ), f"Failed to get action template: {template_result.stderr}"
    print("Retrieved action template successfully")

    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Test Action {unique_id}"

    try:
        # Step 3: Create an action
        print("\n3. Creating an action")
        create_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "actions",
                "create",
                "--integration-name",
                integration_name,
                "--display-name",
                display_name,
                "--code",
                _ACTION_SCRIPT,
                "--description",
                "Temporary action created by CLI integration test",
                "--timeout-seconds",
                "60",
                "--script-result-name",
                "result",
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
            pytest.fail(f"Failed to create action: {error_output}")

        create_data = json.loads(create_result.stdout)
        assert "name" in create_data
        action_id = create_data["name"].split("/")[-1]
        print(f"Created action with ID: {action_id}")

        time.sleep(2)

        # Step 4: Get action details
        print("\n4. Getting action details")
        get_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "actions",
                "get",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
            ]
        )

        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            get_result.returncode == 0
        ), f"Failed to get action: {get_result.stderr}"
        get_data = json.loads(get_result.stdout)
        assert get_data.get("displayName") == display_name
        print(f"Retrieved action: {get_data.get('displayName')}")

        # Step 5: List actions and verify created action appears
        print("\n5. Listing actions")
        list_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "actions",
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
        ), f"Failed to list actions: {list_result.stderr}"
        list_data = json.loads(list_result.stdout)
        actions = list_data.get("actions", [])
        found = any(a.get("name", "").endswith(action_id) for a in actions)
        assert found, f"Created action {action_id} not found in list."
        print(f"Found action in list ({len(actions)} total)")

        # Step 6: Update the action
        print("\n6. Updating the action")
        updated_description = f"Updated by CLI integration test {unique_id}"
        update_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "actions",
                "update",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
                "--description",
                updated_description,
            ]
        )

        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            update_result.returncode == 0
        ), f"Failed to update action: {update_result.stderr}"
        update_data = json.loads(update_result.stdout)
        assert "name" in update_data
        print("Updated action description successfully")

        # Step 7: Delete the action
        print("\n7. Deleting the action")
        delete_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "actions",
                "delete",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
            ]
        )

        delete_result = subprocess.run(
            delete_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            delete_result.returncode == 0
        ), f"Failed to delete action: {delete_result.stderr}"
        action_id = None
        print("Action deleted successfully")

    finally:
        # Cleanup: delete action if not already deleted
        print("\n8. Cleaning up")
        if action_id:
            delete_cmd = (
                ["secops"]
                + common_args
                + [
                    "integration",
                    "actions",
                    "delete",
                    "--integration-name",
                    integration_name,
                    "--action-id",
                    action_id,
                ]
            )
            delete_result = subprocess.run(
                delete_cmd, env=cli_env, capture_output=True, text=True
            )
            if delete_result.returncode == 0:
                print(f"Cleaned up action: {action_id}")
            else:
                print(
                    f"Warning: Failed to delete test action:"
                    f" {delete_result.stderr}"
                )
