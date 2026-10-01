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
"""Integration tests for the SecOps CLI integration action revisions commands."""

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
def test_cli_action_revisions_workflow(cli_env, common_args):
    """Test action revision create, list, rollback, and delete via CLI.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    integration_name = None
    action_id = None
    revision_id = None

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
            pytest.skip("No integrations available to test action revisions.")
        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")
    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse integrations response")

    # Step 2: Create a temporary custom action
    print("\n2. Creating a temporary custom action")
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Test Action {unique_id}"

    create_action_cmd = (
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

    create_action_result = subprocess.run(
        create_action_cmd, env=cli_env, capture_output=True, text=True
    )

    if create_action_result.returncode != 0:
        error_output = create_action_result.stderr + create_action_result.stdout
        if any(err in error_output for err in AUTH_ERRORS):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.fail(f"Failed to create action: {error_output}")

    try:
        create_action_data = json.loads(create_action_result.stdout)
        assert "name" in create_action_data
        action_id = create_action_data["name"].split("/")[-1]
        print(f"Created action with ID: {action_id}")
    except (json.JSONDecodeError, KeyError):
        pytest.fail("Could not parse create action response")

    time.sleep(2)

    try:
        # Step 3: Create a revision of the action
        print("\n3. Creating a revision of the action")
        revision_comment = f"CLI test revision {unique_id}"

        create_rev_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "action-revisions",
                "create",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
                "--comment",
                revision_comment,
            ]
        )

        create_rev_result = subprocess.run(
            create_rev_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            create_rev_result.returncode == 0
        ), f"Failed to create revision: {create_rev_result.stderr}"

        create_rev_data = json.loads(create_rev_result.stdout)
        assert "name" in create_rev_data
        revision_id = create_rev_data["name"].split("/")[-1]
        print(f"Created revision with ID: {revision_id}")

        time.sleep(1)

        # Step 4: List revisions and verify the new revision appears
        print("\n4. Listing revisions")
        list_rev_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "action-revisions",
                "list",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
            ]
        )

        list_rev_result = subprocess.run(
            list_rev_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            list_rev_result.returncode == 0
        ), f"Failed to list revisions: {list_rev_result.stderr}"

        list_rev_data = json.loads(list_rev_result.stdout)
        revisions = list_rev_data.get("revisions", [])
        found = any(r.get("name", "").endswith(revision_id) for r in revisions)
        assert found, f"Created revision {revision_id} not found in list."
        print(f"Found revision in list ({len(revisions)} total)")

        # Step 5: Rollback to the created revision
        print("\n5. Rolling back to the created revision")
        rollback_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "action-revisions",
                "rollback",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
                "--revision-id",
                revision_id,
            ]
        )

        rollback_result = subprocess.run(
            rollback_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            rollback_result.returncode == 0
        ), f"Failed to rollback revision: {rollback_result.stderr}"
        rollback_data = json.loads(rollback_result.stdout)
        assert "name" in rollback_data
        print(f"Rollback successful: {rollback_data.get('name')}")

        time.sleep(1)

        # Step 6: Delete the revision
        print("\n6. Deleting the revision")
        delete_rev_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "action-revisions",
                "delete",
                "--integration-name",
                integration_name,
                "--action-id",
                action_id,
                "--revision-id",
                revision_id,
            ]
        )

        delete_rev_result = subprocess.run(
            delete_rev_cmd, env=cli_env, capture_output=True, text=True
        )
        assert (
            delete_rev_result.returncode == 0
        ), f"Failed to delete revision: {delete_rev_result.stderr}"
        revision_id = None
        print("Revision deleted successfully")

    finally:
        # Step 7: Cleanup — delete revision if not already deleted, then action
        print("\n7. Cleaning up")
        if revision_id:
            delete_rev_cmd = (
                ["secops"]
                + common_args
                + [
                    "integration",
                    "action-revisions",
                    "delete",
                    "--integration-name",
                    integration_name,
                    "--action-id",
                    action_id,
                    "--revision-id",
                    revision_id,
                ]
            )
            delete_rev_result = subprocess.run(
                delete_rev_cmd, env=cli_env, capture_output=True, text=True
            )
            if delete_rev_result.returncode == 0:
                print(f"Cleaned up revision: {revision_id}")
            else:
                print(
                    f"Warning: Failed to delete test revision:"
                    f" {delete_rev_result.stderr}"
                )

        if action_id:
            delete_action_cmd = (
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
            delete_action_result = subprocess.run(
                delete_action_cmd,
                env=cli_env,
                capture_output=True,
                text=True,
            )
            if delete_action_result.returncode == 0:
                print(f"Cleaned up action: {action_id}")
            else:
                print(
                    f"Warning: Failed to delete test action:"
                    f" {delete_action_result.stderr}"
                )
