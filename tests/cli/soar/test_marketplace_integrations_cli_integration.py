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
"""Integration tests for the SecOps CLI marketplace integrations commands."""

import json
import subprocess
import time

import pytest


@pytest.mark.integration
def test_cli_marketplace_integrations_workflow(cli_env, common_args):
    """Test the marketplace integration list, get, diff, install, and uninstall commands.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    auth_errors = [
        "401",
        "Unauthorized",
        "AuthenticationError",
        "Failed to get credentials",
        "DefaultCredentialsError",
    ]

    print("\n1. Listing marketplace integrations")
    list_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "marketplace",
            "list",
            "--page-size",
            "10",
        ]
    )

    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )

    if list_result.returncode != 0:
        error_output = list_result.stderr + list_result.stdout
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.fail(f"Failed to list marketplace integrations: {error_output}")

    try:
        list_data = json.loads(list_result.stdout)
        integrations = list_data.get("marketplaceIntegrations", [])
        if not integrations:
            pytest.skip("No marketplace integrations available to test.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using marketplace integration: {integration_name}")
    except (json.JSONDecodeError, KeyError):
        pytest.fail("Could not parse list response")

    # Step 2: Get marketplace integration details
    print("\n2. Getting marketplace integration details")
    get_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "marketplace",
            "get",
            "--integration-name",
            integration_name,
        ]
    )

    get_result = subprocess.run(
        get_cmd, env=cli_env, capture_output=True, text=True
    )
    if get_result.returncode != 0:
        error_output = get_result.stderr + get_result.stdout
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
        pytest.fail(f"Failed to get marketplace integration: {error_output}")

    get_data = json.loads(get_result.stdout)
    assert get_data.get("name", "").endswith(integration_name)
    print(f"Successfully retrieved marketplace integration: {integration_name}")

    # Step 3: Get marketplace integration diff
    print("\n3. Getting marketplace integration diff")
    diff_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "marketplace",
            "diff",
            "--integration-name",
            integration_name,
        ]
    )

    diff_result = subprocess.run(
        diff_cmd, env=cli_env, capture_output=True, text=True
    )
    if diff_result.returncode == 0:
        print("Successfully retrieved marketplace integration diff")
    else:
        print(
            f"Warning: Failed to retrieve diff (may not be supported for this integration): {diff_result.stderr}"
        )

    # Step 4 & 5: Install & Uninstall
    print("\n4. Installing marketplace integration")
    install_cmd = (
        ["secops"]
        + common_args
        + [
            "integration",
            "marketplace",
            "install",
            "--integration-name",
            integration_name,
        ]
    )

    install_result = subprocess.run(
        install_cmd, env=cli_env, capture_output=True, text=True
    )

    if install_result.returncode == 0:
        print(f"Successfully installed integration: {integration_name}")
        time.sleep(2)

        print("\n5. Uninstalling marketplace integration")
        uninstall_cmd = (
            ["secops"]
            + common_args
            + [
                "integration",
                "marketplace",
                "uninstall",
                "--integration-name",
                integration_name,
            ]
        )

        uninstall_result = subprocess.run(
            uninstall_cmd, env=cli_env, capture_output=True, text=True
        )
        if uninstall_result.returncode == 0:
            print(f"Successfully uninstalled integration: {integration_name}")
        else:
            print(
                f"Warning: Failed to uninstall integration: {uninstall_result.stderr}"
            )
    else:
        error_output = install_result.stderr + install_result.stdout
        print(
            f"Install failed or skipped (may already be installed): {error_output[:200]}"
        )
        if any(err in error_output for err in auth_errors):
            pytest.skip(
                f"Skipping due to SOAR IAM/auth issue: {error_output[:200]}"
            )
