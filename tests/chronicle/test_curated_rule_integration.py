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
"""Integration tests for curated rule set functionality in Chronicle API.

These tests require valid credentials and API access.
"""
import pytest

from secops import SecOpsClient

from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.fixture(scope="module")
def chronicle():
    """Fixture to create a Chronicle client for testing."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    return client.chronicle(**CHRONICLE_CONFIG)


@pytest.mark.integration
def test_curated_rule_sets(chronicle):
    """Test listing and retrieving curated rule sets."""
    # Test basic listing
    rule_sets = chronicle.list_curated_rule_sets()
    assert isinstance(rule_sets, list)
    assert len(rule_sets) > 0, "Expected at least one curated rule set to exist"

    # Test with pagination parameters
    page_size = 5
    rule_sets_paged = chronicle.list_curated_rule_sets(page_size=page_size)
    assert isinstance(rule_sets_paged, dict)
    assert len(rule_sets_paged.get("curatedRuleSets")) <= page_size

    # Keep first rule set for get test and later use in other tests
    first_rule_set = rule_sets[0]
    assert "name" in first_rule_set
    assert "displayName" in first_rule_set

    # Extract rule set ID from the name field
    rule_set_id = first_rule_set["name"].split("/")[-1]
    assert rule_set_id, "Failed to extract rule set ID from name"

    # Test get operation
    print(f"\nTesting get_curated_rule_set with ID: {rule_set_id}")
    rule_set = chronicle.get_curated_rule_set(rule_set_id)
    assert rule_set["name"] == first_rule_set["name"]
    assert rule_set["displayName"] == first_rule_set["displayName"]

    return first_rule_set


@pytest.mark.integration
def test_curated_rule_set_categories(chronicle):
    """Test listing and retrieving curated rule set categories."""
    # Test basic listing
    categories = chronicle.list_curated_rule_set_categories()
    assert isinstance(categories, list)
    assert len(categories) > 0, "Expected at least one category to exist"

    # Test with pagination parameters
    page_size = 5
    categories_paged = chronicle.list_curated_rule_set_categories(
        page_size=page_size
    )
    assert isinstance(categories_paged, dict)
    assert len(categories_paged.get("curatedRuleSetCategories")) <= page_size

    # Keep first category for get test and later use in other tests
    first_category = categories[0]
    assert "name" in first_category
    assert "displayName" in first_category

    # Extract category ID from the name field
    category_id = first_category["name"].split("/")[-1]
    assert category_id, "Failed to extract category ID from name"

    # Test get operation
    print(f"\nTesting get_curated_rule_set_category with ID: {category_id}")
    category = chronicle.get_curated_rule_set_category(category_id)
    assert category["name"] == first_category["name"]
    assert category["displayName"] == first_category["displayName"]

    return first_category


@pytest.mark.integration
def test_curated_rules(chronicle):
    """Test listing and retrieving curated rules."""
    # Test basic listing
    rules = chronicle.list_curated_rules()
    assert isinstance(rules, list)
    assert len(rules) > 0, "Expected at least one curated rule to exist"

    # Test with pagination parameters
    page_size = 5
    rules_paged = chronicle.list_curated_rules(page_size=page_size)
    assert isinstance(rules_paged, dict)
    assert len(rules_paged.get("curatedRules")) <= page_size

    # Keep first rule for get tests and later use in other tests
    first_rule = rules[0]
    assert "name" in first_rule
    assert "displayName" in first_rule

    # Extract rule ID from the name field
    rule_id = first_rule["name"].split("/")[-1]
    assert rule_id, "Failed to extract rule ID from name"

    # Test get operation by ID
    print(f"\nTesting get_curated_rule with ID: {rule_id}")
    rule = chronicle.get_curated_rule(rule_id)
    assert rule["name"] == first_rule["name"]
    assert rule["displayName"] == first_rule["displayName"]

    # Test get operation by display name
    display_name = first_rule["displayName"]
    print(f"\nTesting get_curated_rule_by_name with name: {display_name}")
    rule_by_name = chronicle.get_curated_rule_by_name(display_name)
    assert rule_by_name["name"] == first_rule["name"]
    assert rule_by_name["displayName"].lower() == display_name.lower()

    return first_rule


@pytest.mark.integration
def test_curated_rule_set_deployments(chronicle):
    """Test listing and retrieving curated rule set deployments."""
    # Part 1: Test listing deployments
    print("\nTesting list_curated_rule_set_deployments")
    deployments = chronicle.list_curated_rule_set_deployments()
    assert isinstance(deployments, list)

    if not deployments:
        pytest.skip("No rule set deployments found to test with")

    # Test with filters
    enabled_deployments = chronicle.list_curated_rule_set_deployments(
        only_enabled=True
    )
    assert isinstance(enabled_deployments, list)
    for deployment in enabled_deployments:
        assert deployment.get("enabled") is True

    alerting_deployments = chronicle.list_curated_rule_set_deployments(
        only_alerting=True
    )
    assert isinstance(alerting_deployments, list)
    for deployment in alerting_deployments:
        assert deployment.get("alerting") is True

    # Test with pagination parameters
    page_size = 5
    deployments_paged = chronicle.list_curated_rule_set_deployments(
        page_size=page_size
    )
    assert isinstance(deployments_paged, dict)
    assert len(deployments_paged.get("curatedRuleSetDeployments")) <= page_size

    # Keep first deployment for reference
    first_deployment = deployments[0]
    assert "name" in first_deployment
    assert "displayName" in first_deployment

    # Part 2: Test getting deployment by rule set ID and precision
    print("\nTesting get_curated_rule_set_deployment")
    rule_sets = chronicle.list_curated_rule_sets()
    assert rule_sets, "No rule sets found to test with"

    # Get the first rule set's ID
    first_rule_set = rule_sets[0]
    rule_set_id = first_rule_set["name"].split("/")[-1]

    # Try to get deployment for both precision levels
    deployment_found = False
    for precision in ["precise", "broad"]:
        try:
            deployment = chronicle.get_curated_rule_set_deployment(
                rule_set_id, precision
            )
            print(f"Found {precision} deployment for rule set {rule_set_id}")
            assert "name" in deployment
            assert "displayName" in deployment
            # Ensure the precision in the response matches what we requested
            assert deployment.get("precision", "").upper() == precision.upper()
            deployment_found = True
            break  # If we succeed with either precision, continue to next test
        except Exception as e:
            # Some rule sets might not have deployments for both precision levels
            print(f"No {precision} deployment for rule set {rule_set_id}: {e}")

    if not deployment_found:
        pytest.skip("No deployments found for any rule sets")

    # Part 3: Test getting deployment by display name and precision
    print("\nTesting get_curated_rule_set_deployment_by_name")
    display_name = first_rule_set["displayName"]

    # Try to get deployment by display name for both precision levels
    found_by_name = False
    for precision in ["precise", "broad"]:
        try:
            deployment_by_name = (
                chronicle.get_curated_rule_set_deployment_by_name(
                    display_name, precision
                )
            )
            print(f"Found {precision} deployment for rule set '{display_name}'")
            assert "name" in deployment_by_name
            assert (
                deployment_by_name.get("displayName").lower()
                == display_name.lower()
            )
            # Ensure the precision in the response matches what we requested
            assert (
                deployment_by_name.get("precision", "").upper()
                == precision.upper()
            )
            found_by_name = True
            break  # If we succeed with either precision, that's enough
        except Exception as e:
            print(
                f"No {precision} deployment for rule set '{display_name}': {e}"
            )

    if not found_by_name:
        pytest.skip(f"No deployments found for rule set '{display_name}'")

    return first_deployment


@pytest.mark.integration
def test_update_curated_rule_set_deployment(chronicle):
    """Test updating and restoring a curated rule set deployment."""
    print("\nTesting update_curated_rule_set_deployment lifecycle")

    # 1. Find valid rule set and category IDs
    rule_sets = chronicle.list_curated_rule_sets()
    assert rule_sets, "No rule sets found to test with"

    # Get a rule set ID
    first_rule_set = rule_sets[0]
    rule_set_name = first_rule_set["name"]
    rule_set_id = rule_set_name.split("/")[-1]

    # Extract category ID from rule set name
    # Format: projects/PROJECT/locations/LOCATION/curatedRuleSetCategories/CATEGORY_ID/curatedRuleSets/RULE_SET_ID
    name_parts = rule_set_name.split("/")
    category_index = name_parts.index("curatedRuleSetCategories")
    category_id = name_parts[category_index + 1]

    print(
        f"Using rule set: {first_rule_set['displayName']} (ID: {rule_set_id})"
    )
    print(f"Category ID: {category_id}")

    # Try both precision levels to find one that works
    deployment_found = False
    precision = None
    current = None

    for prec in ["precise", "broad"]:
        try:
            current = chronicle.get_curated_rule_set_deployment(
                rule_set_id, prec
            )
            deployment_found = True
            precision = prec
            print(f"Found {prec} deployment for rule set {rule_set_id}")
            break
        except Exception as e:
            print(f"No {prec} deployment available: {e}")

    if not deployment_found:
        pytest.skip(f"No deployments found for rule set {rule_set_id}")

    # Save original state for restoration
    original_enabled = current.get("enabled")
    original_alerting = current.get("alerting")

    if original_enabled is None or original_alerting is None:
        pytest.skip("Original state not found")

    print(
        f"Original state - enabled: {original_enabled}, alerting: {original_alerting}"
    )

    try:
        # Define the deployment configuration with opposite values
        deployment_config = {
            "category_id": category_id,
            "rule_set_id": rule_set_id,
            "precision": precision,
            "enabled": not original_enabled,
            "alerting": not original_alerting,
        }

        print(
            f"Updating to - enabled: {not original_enabled}, alerting: {not original_alerting}"
        )

        # Update the deployment
        updated = chronicle.update_curated_rule_set_deployment(
            deployment_config
        )
        print("Update successful")

        # Verify the update
        assert updated is not None

        # Double-check by getting the deployment again
        updated_get = chronicle.get_curated_rule_set_deployment(
            rule_set_id, precision
        )
        if "enabled" in updated_get:
            assert updated_get.get("enabled") == (not original_enabled)

        if "alerting" in updated_get:
            assert updated_get.get("alerting") == (not original_alerting)

    finally:
        # Always restore the original state
        try:
            print(
                f"Restoring to original state - enabled: {original_enabled}, alerting: {original_alerting}"
            )
            restore_config = {
                "category_id": category_id,
                "rule_set_id": rule_set_id,
                "precision": precision,
                "enabled": original_enabled,
                "alerting": original_alerting,
            }

            chronicle.update_curated_rule_set_deployment(restore_config)
            print(f"Successfully restored deployment to original state")
        except Exception as cleanup_error:
            print(f"Warning: Failed to restore original state: {cleanup_error}")


@pytest.mark.integration
def test_search_curated_detections(chronicle):
    """Test searching for detections generated by curated rules.
    """
    from datetime import datetime, timedelta, timezone
    from secops.chronicle.models import AlertState, ListBasis

    print("\nTesting search_curated_detections")

    # Get a valid rule ID first
    rules = chronicle.list_curated_rules()
    assert rules, "No curated rules found to test with"

    first_rule = rules[0]
    rule_id = first_rule["name"].split("/")[-1]
    rule_name = first_rule["displayName"]
    print(f"Testing with rule: {rule_name} (ID: {rule_id})")

    # Define time range (last 30 days)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=30)

    # Test 1: Basic search with DETECTION_TIME
    print("\n1. Searching detections with DETECTION_TIME basis")
    result = chronicle.search_curated_detections(
        rule_id=rule_id,
        start_time=start_time,
        end_time=end_time,
        list_basis=ListBasis.DETECTION_TIME,
    )

    assert isinstance(result, dict), "Expected dict response"
    assert "curatedDetections" in result, "Missing curatedDetections key"
    detections = result["curatedDetections"]
    assert isinstance(detections, list), "Expected list of detections"
    print(f"Found {len(detections)} detections with DETECTION_TIME")

    # Test 2: Search with CREATED_TIME basis
    print("\n2. Searching detections with CREATED_TIME basis")
    result_created = chronicle.search_curated_detections(
        rule_id=rule_id,
        start_time=start_time,
        end_time=end_time,
        list_basis=ListBasis.CREATED_TIME,
    )

    assert isinstance(result_created, dict), "Expected dict response"
    assert "curatedDetections" in result_created
    print(f"Found {len(result_created['curatedDetections'])} detections")

    # Test 3: Search with alert_state filter (ALERTING)
    print("\n3. Searching detections with ALERTING filter")
    result_alerting = chronicle.search_curated_detections(
        rule_id=rule_id,
        start_time=start_time,
        end_time=end_time,
        list_basis=ListBasis.DETECTION_TIME,
        alert_state=AlertState.ALERTING,
    )

    assert isinstance(result_alerting, dict)
    assert "curatedDetections" in result_alerting
    print(
        f"Found {len(result_alerting['curatedDetections'])} "
        f"ALERTING detections"
    )

    # Test 4: Search with manual pagination
    print("\n4. Testing manual pagination with page_size")
    result_paged = chronicle.search_curated_detections(
        rule_id=rule_id,
        start_time=start_time,
        end_time=end_time,
        list_basis=ListBasis.DETECTION_TIME,
        page_size=10,
    )

    assert isinstance(result_paged, dict)
    assert "curatedDetections" in result_paged
    detections_paged = result_paged["curatedDetections"]
    assert len(detections_paged) <= 10, "Page size exceeded"
    print(f"Retrieved {len(detections_paged)} detections (page_size=10)")

    # Check if pagination token exists when results might span pages
    if len(detections_paged) == 10:
        print(f"NextPageToken present: " f"{'nextPageToken' in result_paged}")

    # Test 5: Search with minimal parameters (no time range)
    print("\n5. Searching with minimal parameters")
    result_minimal = chronicle.search_curated_detections(
        rule_id=rule_id, list_basis=ListBasis.DETECTION_TIME
    )

    assert isinstance(result_minimal, dict)
    assert "curatedDetections" in result_minimal
    print(
        f"Found {len(result_minimal['curatedDetections'])} "
        f"detections without time filter"
    )

    # Verify structure of detections if any exist
    if len(detections) > 0:
        print("\n6. Verifying detection structure")
        detection = detections[0]
        assert "id" in detection, "Missing detection ID"
        print(f"Sample detection ID: {detection.get('id', 'N/A')[:50]}...")

    print("\nTest search_curated_detections completed successfully")


if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-v", __file__, "-m", "integration"])
