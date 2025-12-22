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
"""CLI Integration tests for curated rule set functionality in Chronicle.

These tests require valid credentials and API access.
"""
import json
import subprocess
from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.integration
def test_cli_curated_rule_sets(cli_env, common_args):
    """Test CLI commands for listing and getting curated rule sets.

    Args:
        cli_env: Environment variables for CLI execution.
        common_args: Common CLI arguments.
    """
    print("\nTesting rule-set list and get commands")

    # Test list command
    print("1. Listing curated rule sets")
    list_cmd = (
        [
            "secops",
        ]
        + common_args
        + ["curated-rule", "rule-set", "list"]
    )

    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert list_result.returncode == 0, f"Command failed: {list_result.stderr}"

    # Parse the output
    rule_sets = json.loads(list_result.stdout)
    assert isinstance(rule_sets, list), "Expected a list of rule sets"
    assert len(rule_sets) > 0, "Expected at least one rule set"

    # Check structure of first rule set
    first_rule_set = rule_sets[0]
    assert "name" in first_rule_set, "Missing name in rule set"
    assert "displayName" in first_rule_set, "Missing displayName in rule set"

    # Extract rule set ID from first result
    rule_set_id = first_rule_set["name"].split("/")[-1]
    print(
        f"Found rule set: {first_rule_set['displayName']} (ID: {rule_set_id})"
    )

    # Test get command with the extracted ID
    print("\n2. Getting specific rule set by ID")
    get_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "curated-rule",
            "rule-set",
            "get",
            "--id",  # parameter is --id, not --rule-set-id
            rule_set_id,
        ]
    )

    get_result = subprocess.run(
        get_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert get_result.returncode == 0, f"Command failed: {get_result.stderr}"

    # Parse and verify the output
    rule_set_data = json.loads(get_result.stdout)
    assert (
        rule_set_data["name"] == first_rule_set["name"]
    ), "Rule set name doesn't match"
    assert (
        rule_set_data["displayName"] == first_rule_set["displayName"]
    ), "Rule set display name doesn't match"

    return rule_set_id, first_rule_set["displayName"]


@pytest.mark.integration
def test_cli_curated_rule_set_categories(cli_env, common_args):
    """Test CLI commands for listing and getting curated rule set categories.

    Args:
        cli_env: Environment variables for CLI execution.
        common_args: Common CLI arguments.
    """
    print("\nTesting rule-set categories commands")

    # Test list categories command
    print("1. Listing curated rule set categories")
    list_cmd = (
        [
            "secops",
        ]
        + common_args
        + ["curated-rule", "rule-set-category", "list"]
    )

    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert list_result.returncode == 0, f"Command failed: {list_result.stderr}"

    # Parse the output
    categories = json.loads(list_result.stdout)
    assert isinstance(categories, list), "Expected a list of categories"
    assert len(categories) > 0, "Expected at least one category"

    # Check structure of first category
    first_category = categories[0]
    assert "name" in first_category, "Missing name in category"
    assert "displayName" in first_category, "Missing displayName in category"

    # Extract category ID from first result
    category_id = first_category["name"].split("/")[-1]
    print(
        f"Found category: {first_category['displayName']} (ID: {category_id})"
    )

    # Test get category command
    print("\n2. Getting specific category by ID")
    get_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "curated-rule",
            "rule-set-category",
            "get",
            "--id",  # parameter is --id, not --category-id
            category_id,
        ]
    )

    get_result = subprocess.run(
        get_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert get_result.returncode == 0, f"Command failed: {get_result.stderr}"

    # Parse and verify the output
    category_data = json.loads(get_result.stdout)
    assert (
        category_data["name"] == first_category["name"]
    ), "Category name doesn't match"
    assert (
        category_data["displayName"] == first_category["displayName"]
    ), "Category display name doesn't match"

    return category_id, first_category["displayName"]


@pytest.mark.integration
def test_cli_curated_rules(cli_env, common_args):
    """Test CLI commands for listing and getting curated rules.

    Args:
        cli_env: Environment variables for CLI execution.
        common_args: Common CLI arguments.
    """
    print("\nTesting curated rules commands")

    # List curated rules
    print("1. Listing curated rules")
    list_cmd = (
        [
            "secops",
        ]
        + common_args
        + ["curated-rule", "rule", "list"]
    )

    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert list_result.returncode == 0, f"Command failed: {list_result.stderr}"

    # Parse the output
    rules = json.loads(list_result.stdout)
    assert isinstance(rules, list), "Expected a list of rules"
    assert len(rules) > 0, "Expected at least one rule"

    # Check structure of first rule
    first_rule = rules[0]
    assert "name" in first_rule, "Missing name in rule"
    assert "displayName" in first_rule, "Missing displayName in rule"

    # Extract rule ID and display name
    rule_id = first_rule["name"].split("/")[-1]
    display_name = first_rule["displayName"]
    print(f"Found rule: {display_name} (ID: {rule_id})")

    # Get rule by ID
    print("\n2. Getting specific rule by ID")
    get_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "curated-rule",
            "rule",
            "get",
            "--id",  # parameter is --id, not --rule-id
            rule_id,
        ]
    )

    get_result = subprocess.run(
        get_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert get_result.returncode == 0, f"Command failed: {get_result.stderr}"

    # Parse and verify the output
    rule_data = json.loads(get_result.stdout)
    assert rule_data["name"] == first_rule["name"], "Rule name doesn't match"
    assert (
        rule_data["displayName"] == first_rule["displayName"]
    ), "Rule display name doesn't match"

    # Get rule by display name
    print(f"\n3. Getting rule by display name: {display_name}")
    # Need to quote the display name to handle spaces and special characters
    name_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "curated-rule",
            "rule",
            "get",
            "--name",  # Use --name instead of ID
            f"{display_name}",
        ]
    )

    name_result = subprocess.run(
        name_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert name_result.returncode == 0, f"Command failed: {name_result.stderr}"

    # Parse and verify the output
    rule_by_name_data = json.loads(name_result.stdout)
    assert (
        rule_by_name_data["name"] == first_rule["name"]
    ), "Rule name doesn't match"
    assert (
        rule_by_name_data["displayName"].lower() == display_name.lower()
    ), "Rule display name doesn't match"

    return rule_id, display_name


@pytest.mark.integration
def test_cli_curated_rule_set_deployments(cli_env, common_args):
    """Test CLI commands for listing, getting, and updating curated rule set deployments.

    Args:
        cli_env: Environment variables for CLI execution.
        common_args: Common CLI arguments.
    """
    print("\nTesting rule-set deployment commands")

    # Part 1: List deployments
    print("1. Listing curated rule set deployments")
    list_cmd = (
        [
            "secops",
        ]
        + common_args
        + ["curated-rule", "rule-set-deployment", "list"]
    )

    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert list_result.returncode == 0, f"Command failed: {list_result.stderr}"

    # Parse the output
    deployments = json.loads(list_result.stdout)
    assert isinstance(deployments, list), "Expected a list of deployments"

    # Part 2: Get rule set for testing
    print("\n2. First list rule sets to get a valid ID")
    list_rs_cmd = (
        [
            "secops",
        ]
        + common_args
        + ["curated-rule", "rule-set", "list"]
    )

    list_rs_result = subprocess.run(
        list_rs_cmd, env=cli_env, capture_output=True, text=True
    )

    # Check that the command executed successfully
    assert (
        list_rs_result.returncode == 0
    ), f"Command failed: {list_rs_result.stderr}"

    # Parse the output
    rule_sets = json.loads(list_rs_result.stdout)
    assert len(rule_sets) > 0, "No rule sets found for testing"

    # Get first rule set metadata
    first_rule_set = rule_sets[0]
    rule_set_name = first_rule_set["name"]
    rule_set_id = rule_set_name.split("/")[-1]
    display_name = first_rule_set["displayName"]
    print(f"Using rule set: {display_name} (ID: {rule_set_id})")

    # Extract category ID from the rule set name
    try:
        # Format: projects/PROJECT/locations/LOCATION/curatedRuleSetCategories/CATEGORY_ID/curatedRuleSets/RULE_SET_ID
        name_parts = rule_set_name.split("/")
        category_index = name_parts.index("curatedRuleSetCategories")
        category_id = name_parts[category_index + 1]
        print(f"Category ID: {category_id}")
    except (ValueError, IndexError) as e:
        pytest.skip(f"Cannot extract category ID from rule set name: {e}")

    # Part 3: Try to get a deployment
    print("\n3. Finding a valid deployment")
    deployment_found = False
    working_precision = None

    for precision in ["precise", "broad"]:
        print(f"Trying {precision} precision...")
        get_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "curated-rule",
                "rule-set-deployment",
                "get",
                "--id",  # parameter is --id, not --rule-set-id
                rule_set_id,
                "--precision",
                precision,
            ]
        )

        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )

        if get_result.returncode == 0:
            deployment_data = json.loads(get_result.stdout)
            assert "name" in deployment_data, "Missing name in deployment"
            assert (
                deployment_data.get("precision", "").upper()
                == precision.upper()
            )

            # We found a working deployment
            deployment_found = True
            working_precision = precision
            print(f"Found {precision} deployment for rule set {rule_set_id}")

            # Get original state for restoration
            original_enabled = deployment_data.get("enabled")
            original_alerting = deployment_data.get("alerting")

            if original_enabled is None or original_alerting is None:
                print(
                    "Warning: Couldn't determine original state, skipping update test"
                )
                pytest.skip("Original state not available")

            print(
                f"Original state - enabled: {original_enabled}, alerting: {original_alerting}"
            )
            break
        else:
            print(f"No {precision} deployment available: {get_result.stderr}")

    if not deployment_found:
        pytest.skip(f"No deployments found for rule set {rule_set_id}")

    # Part 4: Test update
    print("\n4. Testing update-deployment command")
    print(
        f"Updating to - enabled: {not original_enabled}, alerting: {not original_alerting}"
    )

    update_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "curated-rule",
            "rule-set-deployment",
            "update",
            "--category-id",
            category_id,
            "--rule-set-id",
            rule_set_id,
            "--precision",
            working_precision,
            "--enabled",
            str(not original_enabled).lower(),
            "--alerting",
            str(not original_alerting).lower(),
        ]
    )

    try:
        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert (
            update_result.returncode == 0
        ), f"Update failed: {update_result.stderr}"
        print("Update command successful")

        # Verify the update worked by getting the deployment again
        print("\n5. Verifying the update")
        verify_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "curated-rule",
                "rule-set-deployment",
                "get",
                "--id",
                rule_set_id,
                "--precision",
                working_precision,
            ]
        )

        verify_result = subprocess.run(
            verify_cmd, env=cli_env, capture_output=True, text=True
        )

        # Check that the command executed successfully
        assert (
            verify_result.returncode == 0
        ), f"Verification failed: {verify_result.stderr}"

        # Parse and verify
        verify_data = json.loads(verify_result.stdout)

        # Check only if fields exist, they might not always be updated
        if "enabled" in verify_data:
            assert verify_data.get("enabled") == (
                not original_enabled
            ), "Enabled state not updated"

        if "alerting" in verify_data:
            assert verify_data.get("alerting") == (
                not original_alerting
            ), "Alerting state not updated"

        print("Update verified successfully")

    finally:
        # Part 6: Restore the original state
        print("\n6. Restoring original state")
        restore_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "curated-rule",
                "rule-set-deployment",
                "update",
                "--category-id",
                category_id,
                "--rule-set-id",
                rule_set_id,
                "--precision",
                working_precision,
                "--enabled",
                str(original_enabled).lower(),
                "--alerting",
                str(original_alerting).lower(),
            ]
        )

        try:
            restore_result = subprocess.run(
                restore_cmd, env=cli_env, capture_output=True, text=True
            )

            # Check that the command executed successfully
            assert (
                restore_result.returncode == 0
            ), f"Restore failed: {restore_result.stderr}"
            print(f"Successfully restored deployment to original state")
        except Exception as cleanup_error:
            print(f"Warning: Failed to restore original state: {cleanup_error}")


@pytest.mark.integration
def test_cli_search_curated_detections(cli_env, common_args):
    """Test CLI command for searching curated detections.
    """

    print("\nTesting curated-rule rule search-detections command")

    # Step 1: Get a valid rule ID first
    print("1. Getting a valid rule ID for testing")
    list_rules_cmd = ["secops"] + common_args + ["curated-rule", "rule", "list"]

    list_result = subprocess.run(
        list_rules_cmd, env=cli_env, capture_output=True, text=True
    )

    assert list_result.returncode == 0, f"Failed: {list_result.stderr}"

    rules = json.loads(list_result.stdout)
    assert len(rules) > 0, "No curated rules found for testing"

    first_rule = rules[0]
    rule_id = first_rule["name"].split("/")[-1]
    rule_name = first_rule["displayName"]
    print(f"Using rule: {rule_name} (ID: {rule_id})")

    # Calculate time range for search (last 30 days)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=30)
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Step 2: Test basic search with time range and DETECTION_TIME
    print("\n2. Searching detections with DETECTION_TIME basis")
    search_cmd = (
        ["secops"]
        + common_args
        + [
            "curated-rule",
            "search-detections",
            "--rule-id",
            rule_id,
            "--start-time",
            start_time_str,
            "--end-time",
            end_time_str,
            "--list-basis",
            "DETECTION_TIME",
        ]
    )

    search_result = subprocess.run(
        search_cmd, env=cli_env, capture_output=True, text=True
    )

    assert (
        search_result.returncode == 0
    ), f"Search failed: {search_result.stderr}"

    result_data = json.loads(search_result.stdout)
    assert isinstance(result_data, dict), "Expected dict response"
    assert "curatedDetections" in result_data, "Missing curatedDetections"
    detections = result_data["curatedDetections"]
    assert isinstance(detections, list), "Expected list of detections"
    print(f"Found {len(detections)} detections with DETECTION_TIME")

    # Step 3: Test search with ALERTING filter
    print("\n3. Searching detections with ALERTING filter")
    search_alerting_cmd = (
        ["secops"]
        + common_args
        + [
            "curated-rule",
            "search-detections",
            "--rule-id",
            rule_id,
            "--start-time",
            start_time_str,
            "--end-time",
            end_time_str,
            "--list-basis",
            "DETECTION_TIME",
            "--alert-state",
            "ALERTING",
        ]
    )

    alerting_result = subprocess.run(
        search_alerting_cmd, env=cli_env, capture_output=True, text=True
    )

    assert (
        alerting_result.returncode == 0
    ), f"Alerting search failed: {alerting_result.stderr}"

    alerting_data = json.loads(alerting_result.stdout)
    assert "curatedDetections" in alerting_data
    print(
        f"Found {len(alerting_data['curatedDetections'])} "
        f"ALERTING detections"
    )

    # Step 4: Test search with CREATED_TIME basis
    print("\n4. Searching detections with CREATED_TIME basis")
    search_created_cmd = (
        ["secops"]
        + common_args
        + [
            "curated-rule",
            "search-detections",
            "--rule-id",
            rule_id,
            "--start-time",
            start_time_str,
            "--end-time",
            end_time_str,
            "--list-basis",
            "CREATED_TIME",
        ]
    )

    created_result = subprocess.run(
        search_created_cmd, env=cli_env, capture_output=True, text=True
    )

    assert (
        created_result.returncode == 0
    ), f"Created time search failed: {created_result.stderr}"

    created_data = json.loads(created_result.stdout)
    assert "curatedDetections" in created_data
    print(f"Found {len(created_data['curatedDetections'])} detections")

    # Step 5: Test search with pagination
    print("\n5. Testing manual pagination with page_size")
    search_paged_cmd = (
        ["secops"]
        + common_args
        + [
            "curated-rule",
            "search-detections",
            "--rule-id",
            rule_id,
            "--start-time",
            start_time_str,
            "--end-time",
            end_time_str,
            "--list-basis",
            "DETECTION_TIME",
            "--page-size",
            "10",
        ]
    )

    paged_result = subprocess.run(
        search_paged_cmd, env=cli_env, capture_output=True, text=True
    )

    assert (
        paged_result.returncode == 0
    ), f"Paged search failed: {paged_result.stderr}"

    paged_data = json.loads(paged_result.stdout)
    assert "curatedDetections" in paged_data
    detections_paged = paged_data["curatedDetections"]
    assert len(detections_paged) <= 10, "Page size limit exceeded"
    print(f"Retrieved {len(detections_paged)} detections (page_size=10)")

    # Check pagination token if results might span pages
    if len(detections_paged) == 10:
        has_token = "nextPageToken" in paged_data
        print(f"NextPageToken present: {has_token}")

    # Step 6: Verify detection structure if any detections exist
    if len(detections) > 0:
        print("\n6. Verifying detection structure")
        detection = detections[0]
        assert "id" in detection, "Missing detection ID"
        print(f"Sample detection ID: {detection.get('id', 'N/A')[:50]}...")

    print("\nTest CLI search-detections completed successfully")


if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-v", __file__, "-m", "integration"])
