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
"""Tests for the Rule Exclusion module."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from secops.chronicle import rule_exclusion
from secops.chronicle.client import ChronicleClient
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a mock Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer", project_id="test-project"
        )


@pytest.fixture
def response_mock():
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"testKey": "testValue"}
    return mock


# --- list_rule_exclusions Tests ---


def test_list_rule_exclusions(chronicle_client, response_mock):
    """Test list_rule_exclusions function."""
    chronicle_client.session.get.return_value = response_mock

    result = rule_exclusion.list_rule_exclusions(
        chronicle_client, page_size=50, page_token="test-token"
    )

    chronicle_client.session.get.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements",
        params={"pageSize": 50, "pageToken": "test-token"},
    )

    assert result == {"testKey": "testValue"}


def test_list_rule_exclusions_error(chronicle_client, response_mock):
    """Test list_rule_exclusions function with error response."""
    response_mock.status_code = 400
    response_mock.text = "Bad Request"
    chronicle_client.session.get.return_value = response_mock

    with pytest.raises(APIError, match="Failed to list rule exclusions"):
        rule_exclusion.list_rule_exclusions(chronicle_client)


# --- get_rule_exclusion Tests ---


def test_get_rule_exclusion_with_id(chronicle_client, response_mock):
    """Test get_rule_exclusion function with ID only."""
    chronicle_client.session.get.return_value = response_mock

    result = rule_exclusion.get_rule_exclusion(chronicle_client, "exclusion-id")

    chronicle_client.session.get.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id"
    )

    assert result == {"testKey": "testValue"}


def test_get_rule_exclusion_with_full_resource_name(
    chronicle_client, response_mock
):
    """Test get_rule_exclusion function with full resource name."""
    chronicle_client.session.get.return_value = response_mock

    full_name = (
        f"{chronicle_client.instance_id}/findingsRefinements/exclusion-id"
    )
    result = rule_exclusion.get_rule_exclusion(chronicle_client, full_name)

    chronicle_client.session.get.assert_called_once_with(
        f"{chronicle_client.base_url}/{full_name}"
    )

    assert result == {"testKey": "testValue"}


def test_get_rule_exclusion_error(chronicle_client, response_mock):
    """Test get_rule_exclusion function with error response."""
    response_mock.status_code = 404
    response_mock.text = "Not Found"
    chronicle_client.session.get.return_value = response_mock

    with pytest.raises(APIError, match="Failed to get rule exclusion"):
        rule_exclusion.get_rule_exclusion(chronicle_client, "exclusion-id")


# --- create_rule_exclusion Tests ---


def test_create_rule_exclusion(chronicle_client, response_mock):
    """Test create_rule_exclusion function with all parameters."""
    chronicle_client.session.post.return_value = response_mock

    result = rule_exclusion.create_rule_exclusion(
        client=chronicle_client,
        display_name="Test rule exclusion",
        refinement_type=rule_exclusion.RuleExclusionType.DETECTION_EXCLUSION,
        query="rule_id = 'rule-123'",
    )

    expected_body = {
        "display_name": "Test rule exclusion",
        "type": "DETECTION_EXCLUSION",
        "query": "rule_id = 'rule-123'",
    }

    chronicle_client.session.post.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements",
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_create_rule_exclusion_minimal(chronicle_client, response_mock):
    """Test create_rule_exclusion function with missing parameters."""
    chronicle_client.session.post.return_value = response_mock

    # The actual implementation requires display_name, refinement_type, and query
    # This test should verify a TypeError is raised when parameters are missing
    with pytest.raises(TypeError):
        # Missing required parameters
        rule_exclusion.create_rule_exclusion(chronicle_client)


def test_create_rule_exclusion_with_display_name(
    chronicle_client, response_mock
):
    """Test create_rule_exclusion function with display name and minimal parameters."""
    chronicle_client.session.post.return_value = response_mock

    result = rule_exclusion.create_rule_exclusion(
        client=chronicle_client,
        display_name="Test display name",
        refinement_type=rule_exclusion.RuleExclusionType.DETECTION_EXCLUSION,
        query="simple query",
    )

    expected_body = {
        "display_name": "Test display name",
        "type": "DETECTION_EXCLUSION",
        "query": "simple query",
    }

    chronicle_client.session.post.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements",
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_create_rule_exclusion_with_complex_query(
    chronicle_client, response_mock
):
    """Test create_rule_exclusion with complex query condition."""
    chronicle_client.session.post.return_value = response_mock

    # Test with complex query
    complex_query = (
        "rule_id = 'rule-456' AND rule_version = '1.0' AND "
        "rule_name = 'Test Rule' AND rule_type = 'RULE_TYPE_MULTI_EVENT'"
    )

    result = rule_exclusion.create_rule_exclusion(
        client=chronicle_client,
        display_name="Complex query exclusion",
        refinement_type=rule_exclusion.RuleExclusionType.DETECTION_EXCLUSION,
        query=complex_query,
    )

    expected_body = {
        "display_name": "Complex query exclusion",
        "type": "DETECTION_EXCLUSION",
        "query": complex_query,
    }

    chronicle_client.session.post.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements",
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_create_rule_exclusion_error(chronicle_client, response_mock):
    """Test create_rule_exclusion function with error response."""
    response_mock.status_code = 400
    response_mock.text = "Bad Request"
    chronicle_client.session.post.return_value = response_mock

    with pytest.raises(APIError, match="Failed to create rule exclusion"):
        rule_exclusion.create_rule_exclusion(
            client=chronicle_client,
            display_name="Test rule exclusion",
            refinement_type=rule_exclusion.RuleExclusionType.DETECTION_EXCLUSION,
            query="rule_id = 'rule-123'",
        )


# --- patch_rule_exclusion Tests ---


def test_patch_rule_exclusion(chronicle_client, response_mock):
    """Test patch_rule_exclusion function."""
    chronicle_client.session.patch.return_value = response_mock

    # Test with all parameters
    result = rule_exclusion.patch_rule_exclusion(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        display_name="Updated display name",
        refinement_type=rule_exclusion.RuleExclusionType.DETECTION_EXCLUSION,
        query="updated_rule_id = 'rule-456'",
        update_mask="display_name,type,query",
    )

    expected_body = {
        "display_name": "Updated display name",
        "type": "DETECTION_EXCLUSION",
        "query": "updated_rule_id = 'rule-456'",
    }

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id",
        params={"updateMask": "display_name,type,query"},
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_patch_rule_exclusion_with_partial_update(
    chronicle_client, response_mock
):
    """Test patch_rule_exclusion function with partial update."""
    chronicle_client.session.patch.return_value = response_mock

    # Test with only display_name update
    result = rule_exclusion.patch_rule_exclusion(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        display_name="Only display name updated",
        update_mask="display_name",
    )

    expected_body = {"display_name": "Only display name updated"}

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id",
        params={"updateMask": "display_name"},
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_patch_rule_exclusion_with_full_resource_name(
    chronicle_client, response_mock
):
    """Test patch_rule_exclusion with full resource name."""
    chronicle_client.session.patch.return_value = response_mock

    # Test with full resource name
    full_name = (
        f"{chronicle_client.instance_id}/findingsRefinements/exclusion-id"
    )
    result = rule_exclusion.patch_rule_exclusion(
        client=chronicle_client,
        exclusion_id=full_name,  # Using exclusion_id instead of name
        query="Updated query with full resource name",
        update_mask="query",
    )

    expected_body = {"query": "Updated query with full resource name"}

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{full_name}",
        params={"updateMask": "query"},
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_patch_rule_exclusion_with_no_update_mask(
    chronicle_client, response_mock
):
    """Test patch_rule_exclusion with no update mask."""
    chronicle_client.session.patch.return_value = response_mock

    # Test with no update mask (should default to all fields)
    result = rule_exclusion.patch_rule_exclusion(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        refinement_type=rule_exclusion.RuleExclusionType.FINDINGS_REFINEMENT_TYPE_UNSPECIFIED,
    )

    expected_body = {"type": "FINDINGS_REFINEMENT_TYPE_UNSPECIFIED"}

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id",
        params={},  # No update_mask specified
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_patch_rule_exclusion_error(chronicle_client, response_mock):
    """Test patch_rule_exclusion function with error response."""
    response_mock.status_code = 404
    response_mock.text = "Not Found"
    chronicle_client.session.patch.return_value = response_mock

    with pytest.raises(APIError, match="Failed to update rule exclusion"):
        rule_exclusion.patch_rule_exclusion(
            client=chronicle_client,
            exclusion_id="nonexistent-id",
            display_name="This update will fail",
        )


# --- compute_rule_exclusion_activity Tests ---


def test_compute_rule_exclusion_activity_specific(
    chronicle_client, response_mock
):
    """Test compute_rule_exclusion_activity function with specific exclusion."""
    chronicle_client.session.post.return_value = response_mock
    start_time = datetime(2025, 1, 1)
    end_time = datetime(2025, 1, 2)

    # Test with specific exclusion
    result = rule_exclusion.compute_rule_exclusion_activity(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        start_time=start_time,
        end_time=end_time,
    )

    expected_body = {
        "interval": {
            "start_time": "2025-01-01T00:00:00.000000Z",
            "end_time": "2025-01-02T00:00:00.000000Z",
        }
    }

    chronicle_client.session.post.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id"
        ":computeFindingsRefinementActivity",
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


# --- get_rule_exclusion_deployment Tests ---


def test_get_rule_exclusion_deployment(chronicle_client, response_mock):
    """Test get_rule_exclusion_deployment function."""
    chronicle_client.session.get.return_value = response_mock

    result = rule_exclusion.get_rule_exclusion_deployment(
        chronicle_client, "exclusion-id"
    )

    chronicle_client.session.get.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
        "findingsRefinements/exclusion-id/deployment"
    )

    assert result == {"testKey": "testValue"}


# --- update_rule_exclusion_deployment Tests ---


def test_update_rule_exclusion_deployment(chronicle_client, response_mock):
    """Test update_rule_exclusion_deployment function."""
    chronicle_client.session.patch.return_value = response_mock

    # Create deployment details with all parameters
    deployment_details = rule_exclusion.UpdateRuleDeployment(
        enabled=True,
        archived=False,
        detection_exclusion_application={"scope": "global"},
    )

    # Test with deployment details
    result = rule_exclusion.update_rule_exclusion_deployment(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        deployment_details=deployment_details,
        update_mask="enabled,archived,detection_exclusion_application",
    )

    expected_body = {
        "enabled": True,
        "archived": False,
        "detection_exclusion_application": {"scope": "global"},
    }

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id/deployment",
        params={
            "updateMask": "enabled,archived,detection_exclusion_application"
        },
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_update_rule_exclusion_deployment_disable(
    chronicle_client, response_mock
):
    """Test update_rule_exclusion_deployment to disable a rule exclusion."""
    chronicle_client.session.patch.return_value = response_mock

    # Create deployment details with disabled flag
    deployment_details = rule_exclusion.UpdateRuleDeployment(enabled=False)

    # Test disabling a rule exclusion
    result = rule_exclusion.update_rule_exclusion_deployment(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        deployment_details=deployment_details,
    )

    expected_body = {
        "enabled": False,
        "archived": None,
        "detection_exclusion_application": None,
    }

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id/deployment",
        params={"updateMask": "enabled"},
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_update_rule_exclusion_deployment_with_archived(
    chronicle_client, response_mock
):
    """Test update_rule_exclusion_deployment with archived flag."""
    chronicle_client.session.patch.return_value = response_mock

    # Create deployment details with archived flag
    deployment_details = rule_exclusion.UpdateRuleDeployment(archived=True)

    result = rule_exclusion.update_rule_exclusion_deployment(
        client=chronicle_client,
        exclusion_id="exclusion-id",
        deployment_details=deployment_details,
    )

    expected_body = {
        "enabled": None,
        "archived": True,
        "detection_exclusion_application": None,
    }

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}/findingsRefinements/exclusion-id/deployment",
        params={"updateMask": "archived"},
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_update_rule_exclusion_deployment_with_full_resource_name(
    chronicle_client, response_mock
):
    """Test update_rule_exclusion_deployment with full resource name."""
    chronicle_client.session.patch.return_value = response_mock

    # Test with full resource name
    full_name = (
        f"{chronicle_client.instance_id}/findingsRefinements/exclusion-id"
    )

    # Create deployment details
    deployment_details = rule_exclusion.UpdateRuleDeployment(
        enabled=True,
    )

    result = rule_exclusion.update_rule_exclusion_deployment(
        client=chronicle_client,
        exclusion_id=full_name,
        deployment_details=deployment_details,
    )

    expected_body = {
        "enabled": True,
        "archived": None,
        "detection_exclusion_application": None,
    }

    chronicle_client.session.patch.assert_called_once_with(
        f"{chronicle_client.base_url}/{full_name}/deployment",
        params={"updateMask": "enabled"},
        json=expected_body,
    )

    assert result == {"testKey": "testValue"}


def test_update_rule_exclusion_deployment_error(
    chronicle_client, response_mock
):
    """Test update_rule_exclusion_deployment with error response."""
    response_mock.status_code = 404
    response_mock.text = "Not Found"
    chronicle_client.session.patch.return_value = response_mock

    # Create deployment details
    deployment_details = rule_exclusion.UpdateRuleDeployment(
        enabled=True,
    )

    with pytest.raises(
        APIError, match="Failed to update rule exclusion deployment"
    ):
        rule_exclusion.update_rule_exclusion_deployment(
            client=chronicle_client,
            exclusion_id="nonexistent-id",
            deployment_details=deployment_details,
        )
