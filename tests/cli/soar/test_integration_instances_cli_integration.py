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
"""Integration tests for the SecOps CLI integration instances commands."""

import json
import subprocess
import time
import uuid

import pytest


@pytest.mark.integration
def test_cli_integration_instances_workflow(cli_env, common_args):
    """Test the integration instance create, get, update, list, test, get-affected-items and delete commands.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    auth_errors = [
        "401",
        "Unauthorized",
        "AuthenticationError",
        "Failed to get credentials",
        "DefaultCredentialsError",
    ]

    # Step 1: Find an integration
    print("\n1. Finding a target integration")
    list_integrations_cmd = (
        ["secops"]
        + common_args
        + ["integration", "integrations", "list", "--page-size", "1"]
    )

    list_integrations_result = subprocess.run(
        list_integrations_cmd, env=cli_env, capture_output=True, text=True
    )

    if list_integrations_result.returncode != 0:
        error_output = (
            list_integrations_result.stderr + list_integrations_result.stdout
        )
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.skip(f"Could not fetch integrations: {error_output[:200]}")

    try:
        integrations_data = json.loads(list_integrations_result.stdout)
        integrations = integrations_data.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available to test instance creation.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")
    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse integrations response")

    # Step 2: Create integration instance
    print("\n2. Creating integration instance")
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Test Instance {unique_id}"
    environment = "Default Environment"

    create_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "instances",
            "create",
            "--integration-name",
            integration_name,
            "--environment",
            environment,
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
        pytest.fail(f"Failed to create integration instance: {error_output}")

    try:
        create_data = json.loads(create_result.stdout)
        assert "name" in create_data
        instance_id = create_data["name"].split("/")[-1]
        print(f"Created instance with ID: {instance_id}")
    except (json.JSONDecodeError, KeyError):
        pytest.fail("Could not parse create response")

    time.sleep(2)

    try:
        # Step 3: Get instance details
        print("\n3. Getting instance details")
        get_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "instances",
                "get",
                "--integration-name",
                integration_name,
                "--instance-id",
                instance_id,
            ]
        )

        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )
        assert get_result.returncode == 0
        get_data = json.loads(get_result.stdout)
        assert get_data.get("displayName") == display_name
        print(f"Successfully retrieved instance: {display_name}")

        # Step 4: Update instance
        print("\n4. Updating instance")
        updated_name = f"Updated CLI Test Instance {unique_id}"
        update_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "instances",
                "update",
                "--integration-name",
                integration_name,
                "--instance-id",
                instance_id,
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
        update_data = json.loads(update_result.stdout)
        assert update_data.get("displayName") == updated_name
        print(f"Successfully updated instance: {updated_name}")

        # Step 5: Test the instance connectivity
        print("\n5. Executing integration instance test")
        test_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "instances",
                "test",
                "--integration-name",
                integration_name,
                "--instance-id",
                instance_id,
            ]
        )
        test_result = subprocess.run(
            test_cmd, env=cli_env, capture_output=True, text=True
        )
        # We don't assert return code here because the connectivity test itself might fail for a dummy setup
        if test_result.returncode == 0:
            try:
                test_data = json.loads(test_result.stdout)
                print(
                    f"Test executed. Successful: {test_data.get('successful')}"
                )
            except json.JSONDecodeError:
                pass
        else:
            print(
                f"Test execution returned error (expected for some configs): {test_result.stderr}"
            )

        # Step 6: List instances
        print("\n6. Listing integration instances")
        list_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "instances",
                "list",
                "--integration-name",
                integration_name,
                "--page-size",
                "10",
            ]
        )

        list_result = subprocess.run(
            list_cmd, env=cli_env, capture_output=True, text=True
        )
        assert list_result.returncode == 0
        list_data = json.loads(list_result.stdout)
        instances = list_data.get("integrationInstances", [])
        found = any(i.get("name", "").endswith(instance_id) for i in instances)
        assert found, f"Created instance {instance_id} not found in list."
        print("Successfully found instance in list results")

        # Step 7: Get affected items
        print("\n7. Getting affected items")
        affected_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "instances",
                "get-affected-items",
                "--integration-name",
                integration_name,
                "--instance-id",
                instance_id,
            ]
        )

        affected_result = subprocess.run(
            affected_cmd, env=cli_env, capture_output=True, text=True
        )
        assert affected_result.returncode == 0
        print("Successfully retrieved affected items")

    finally:
        # Step 8: Delete instance (Cleanup)
        print(f"\n8. Cleaning up: Deleting instance {instance_id}")
        delete_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "instances",
                "delete",
                "--integration-name",
                integration_name,
                "--instance-id",
                instance_id,
            ]
        )

        delete_result = subprocess.run(
            delete_cmd, env=cli_env, capture_output=True, text=True
        )
        if delete_result.returncode == 0:
            print(f"Successfully deleted instance: {instance_id}")
        else:
            print(
                f"Warning: Failed to delete test instance: {delete_result.stderr}"
            )


@pytest.mark.integration
def test_cli_get_default_integration_instance(cli_env, common_args):
    """Test getting default integration instance via CLI.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    auth_errors = [
        "401",
        "Unauthorized",
        "AuthenticationError",
        "Failed to get credentials",
        "DefaultCredentialsError",
    ]

    print("\n1. Finding a target integration")
    list_integrations_cmd = (
        ["secops"]
        + common_args
        + ["integration", "integrations", "list", "--page-size", "1"]
    )

    list_integrations_result = subprocess.run(
        list_integrations_cmd, env=cli_env, capture_output=True, text=True
    )

    if list_integrations_result.returncode != 0:
        error_output = (
            list_integrations_result.stderr + list_integrations_result.stdout
        )
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.skip(f"Could not fetch integrations: {error_output[:200]}")

    try:
        integrations_data = json.loads(list_integrations_result.stdout)
        integrations = integrations_data.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")
    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse integrations response")

    print("\n2. Getting default instance")
    get_default_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "instances",
            "get-default",
            "--integration-name",
            integration_name,
        ]
    )

    get_default_result = subprocess.run(
        get_default_cmd, env=cli_env, capture_output=True, text=True
    )

    if get_default_result.returncode != 0:
        error_output = get_default_result.stderr + get_default_result.stdout
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        if "400" in error_output or "404" in error_output:
            pytest.skip(
                f"Skipping due to HTTP Error (integration may not have a default instance): {error_output[:200]}"
            )
        pytest.fail(f"Failed to get default instance: {error_output}")

    try:
        default_data = json.loads(get_default_result.stdout)
        assert "name" in default_data.get("instance")
        print(
            "Successfully retrieved default instance: "
            f"{default_data.get('instance').get('name')}"
        )
    except json.JSONDecodeError:
        pytest.fail("Could not parse get-default response")
