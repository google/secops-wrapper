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
"""CLI Integration tests for watchlist functionality in Chronicle.

These tests require valid credentials and API access.
"""

import json
import subprocess
from datetime import datetime, timezone

import pytest


@pytest.mark.integration
def test_cli_watchlist_list_and_get(cli_env, common_args):
    """Test CLI commands for listing and getting watchlists.

    Args:
        cli_env: Environment variables for CLI execution.
        common_args: Common CLI arguments.
    """
    print("\nTesting watchlist list and get commands")

    # 1. List watchlists
    print("1. Listing watchlists")
    list_cmd = ["secops"] + common_args + ["watchlist", "list"]

    list_result = subprocess.run(
        list_cmd,
        env=cli_env,
        capture_output=True,
        text=True,
    )

    # Ensure command succeeded
    assert list_result.returncode == 0, f"Command failed: {list_result.stderr}"

    # Parse output
    data = json.loads(list_result.stdout)
    assert isinstance(data, dict), "Expected dict response from watchlist list"
    assert "watchlists" in data, "Missing 'watchlists' key in response"

    watchlists = data["watchlists"]
    assert isinstance(watchlists, list), "Expected 'watchlists' to be a list"
    assert len(watchlists) > 0, "Expected at least one watchlist"

    first_watchlist = watchlists[0]
    assert "name" in first_watchlist, "Missing 'name' in watchlist"
    assert (
        "displayName" in first_watchlist
    ), "Missing 'displayName' in watchlist"

    # Extract watchlist ID (name is a resource path, ID is last component)
    watchlist_name = first_watchlist["name"]
    watchlist_id = watchlist_name.split("/")[-1]
    display_name = first_watchlist["displayName"]

    print(f"Found watchlist: {display_name} (ID: {watchlist_id})")

    # 2. Get specific watchlist by ID
    print("\n2. Getting specific watchlist by ID")
    get_cmd = (
        ["secops"]
        + common_args
        + [
            "watchlist",
            "get",
            "--watchlist-id",
            watchlist_id,
        ]
    )

    get_result = subprocess.run(
        get_cmd,
        env=cli_env,
        capture_output=True,
        text=True,
    )

    assert get_result.returncode == 0, f"Command failed: {get_result.stderr}"

    watchlist_data = json.loads(get_result.stdout)
    assert isinstance(
        watchlist_data, dict
    ), "Expected dict response from watchlist get"
    assert (
        watchlist_data.get("name") == watchlist_name
    ), "Watchlist name doesn't match"
    assert (
        watchlist_data.get("displayName") == display_name
    ), "Watchlist display name doesn't match"


@pytest.mark.integration
def test_cli_watchlist_create_update_delete(cli_env, common_args):
    """Test CLI commands for creating, updating, and deleting a watchlist.

    Args:
        cli_env: Environment variables for CLI execution.
        common_args: Common CLI arguments.
    """
    print("\nTesting watchlist create, update, and delete commands")

    # Use a timestamped name to avoid collisions
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    watchlist_name = f"secops-test-watchlist-{ts}"
    display_name = f"SecOps Test Watchlist {ts}"
    multiplying_factor = 1.5
    description = "Integration test watchlist"

    # 1. Create watchlist
    print("1. Creating watchlist")
    create_cmd = (
        ["secops"]
        + common_args
        + [
            "watchlist",
            "create",
            "--name",
            watchlist_name,
            "--display-name",
            display_name,
            "--multiplying-factor",
            str(multiplying_factor),
            "--description",
            description,
        ]
    )

    create_result = subprocess.run(
        create_cmd,
        env=cli_env,
        capture_output=True,
        text=True,
    )

    assert (
        create_result.returncode == 0
    ), f"Create failed: {create_result.stderr}"

    created_data = json.loads(create_result.stdout)
    assert isinstance(created_data, dict), "Expected dict response"
    assert created_data.get("name"), "Missing 'name' in created watchlist"
    assert (
        created_data.get("displayName") == display_name
    ), "Created watchlist display name mismatch"

    created_name = created_data["name"]
    created_id = created_name.split("/")[-1]
    print(f"Created watchlist: {display_name} (ID: {created_id})")

    # 2. Update watchlist
    print("\n2. Updating watchlist")
    updated_display_name = f"Updated Watchlist {ts}"
    updated_multiplying_factor = 2.5
    updated_description = "Updated integration test watchlist"

    update_cmd = (
        ["secops"]
        + common_args
        + [
            "watchlist",
            "update",
            "--watchlist-id",
            created_id,
            "--display-name",
            updated_display_name,
            "--multiplying-factor",
            str(updated_multiplying_factor),
            "--description",
            updated_description,
            "--pinned",
            "true",
        ]
    )

    update_result = subprocess.run(
        update_cmd,
        env=cli_env,
        capture_output=True,
        text=True,
    )

    assert (
        update_result.returncode == 0
    ), f"Update failed: {update_result.stderr}"

    update_data = json.loads(update_result.stdout)
    assert isinstance(update_data, dict), "Expected dict response"
    assert (
        update_data.get("displayName") == updated_display_name
    ), "Updated display name mismatch"
    assert (
        update_data.get("multiplyingFactor") == updated_multiplying_factor
    ), "Updated multiplying factor mismatch"
    user_prefs = update_data.get("watchlistUserPreferences", {})
    assert user_prefs.get("pinned") is True, "Watchlist should be pinned"
    print(f"Updated watchlist: {updated_display_name}")

    # 3. Verify updates via get command
    print("\n3. Verifying updates via get command")
    get_cmd = (
        ["secops"]
        + common_args
        + [
            "watchlist",
            "get",
            "--watchlist-id",
            created_id,
        ]
    )

    get_result = subprocess.run(
        get_cmd,
        env=cli_env,
        capture_output=True,
        text=True,
    )

    assert get_result.returncode == 0, f"Get failed: {get_result.stderr}"

    get_data = json.loads(get_result.stdout)
    assert get_data.get("name") == created_name, "Get watchlist name mismatch"
    assert (
        get_data.get("displayName") == updated_display_name
    ), "Get watchlist display name mismatch"
    print("Verified updates successfully")

    # 4. Delete created watchlist (cleanup)
    print("\n4. Deleting created watchlist")
    delete_cmd = (
        ["secops"]
        + common_args
        + [
            "watchlist",
            "delete",
            "--watchlist-id",
            created_id,
        ]
    )

    delete_result = subprocess.run(
        delete_cmd,
        env=cli_env,
        capture_output=True,
        text=True,
    )

    assert (
        delete_result.returncode == 0
    ), f"Delete failed: {delete_result.stderr}"

    if delete_result.stdout.strip():
        delete_data = json.loads(delete_result.stdout)
        assert isinstance(
            delete_data, dict
        ), "Expected dict or empty response from delete"

    print(f"Successfully deleted watchlist {created_id}")


if __name__ == "__main__":
    # Allow running directly
    pytest.main(["-v", __file__, "-m", "integration"])
