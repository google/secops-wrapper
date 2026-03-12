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
"""Tests for Chronicle integration functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import (
    APIVersion,
    DiffType,
    TargetMode,
    PythonVersion,
)
from secops.chronicle.integration.integrations import (
    list_integrations,
    get_integration,
    delete_integration,
    create_integration,
    download_integration,
    download_integration_dependency,
    export_integration_items,
    get_integration_affected_items,
    get_agent_integrations,
    get_integration_dependencies,
    get_integration_restricted_agents,
    get_integration_diff,
    transition_integration,
    update_integration,
    update_custom_integration,
)
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer",
            project_id="test-project",
            default_api_version=APIVersion.V1BETA,
        )


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {}
    return mock


@pytest.fixture
def mock_error_response() -> Mock:
    """Create a mock error API response object."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock


# -- list_integrations tests --


def test_list_integrations_success(chronicle_client):
    """Test list_integrations delegates to chronicle_paginated_request."""
    expected = {"integrations": [{"name": "i1"}, {"name": "i2"}]}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integrations(
            chronicle_client,
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations",
            items_key="integrations",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integrations_with_filter_and_order_by(chronicle_client):
    """Test list_integrations passes filter_string and order_by in extra_params."""
    expected = {"integrations": []}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integrations(
            chronicle_client,
            filter_string='displayName = "My Integration"',
            order_by="displayName",
            as_list=True,
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations",
            items_key="integrations",
            page_size=None,
            page_token=None,
            extra_params={
                "filter": 'displayName = "My Integration"',
                "orderBy": "displayName",
            },
            as_list=True,
        )


def test_list_integrations_error(chronicle_client):
    """Test list_integrations propagates APIError from helper."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_paginated_request",
        side_effect=APIError("Failed to list integrations"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integrations(chronicle_client)

        assert "Failed to list integrations" in str(exc_info.value)


# -- get_integration tests --


def test_get_integration_success(chronicle_client):
    """Test get_integration returns expected result."""
    expected = {"name": "integrations/test-integration", "displayName": "Test"}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration(chronicle_client, "test-integration")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_error(chronicle_client):
    """Test get_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to get integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration(chronicle_client, "test-integration")

        assert "Failed to get integration" in str(exc_info.value)


# -- delete_integration tests --


def test_delete_integration_success(chronicle_client):
    """Test delete_integration delegates to chronicle_request."""
    with patch("secops.chronicle.integration.integrations.chronicle_request") as mock_request:
        delete_integration(chronicle_client, "test-integration")

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration",
            api_version=APIVersion.V1BETA,
        )


def test_delete_integration_error(chronicle_client):
    """Test delete_integration propagates APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to delete integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration(chronicle_client, "test-integration")

        assert "Failed to delete integration" in str(exc_info.value)


# -- create_integration tests --


def test_create_integration_required_fields_only(chronicle_client):
    """Test create_integration with required fields only."""
    expected = {"name": "integrations/test", "displayName": "Test"}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration(
            chronicle_client,
            display_name="Test",
            staging=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations",
            json={"displayName": "Test", "staging": True},
            api_version=APIVersion.V1BETA,
        )


def test_create_integration_all_optional_fields(chronicle_client):
    """Test create_integration with all optional fields."""
    expected = {"name": "integrations/test"}

    python_version = list(PythonVersion)[0]
    integration_type = Mock(name="integration_type")

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration(
            chronicle_client,
            display_name="Test",
            staging=False,
            description="desc",
            image_base64="b64",
            svg_icon="<svg/>",
            python_version=python_version,
            parameters=[{"id": "p1"}],
            categories=["cat"],
            integration_type=integration_type,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations",
            json={
                "displayName": "Test",
                "staging": False,
                "description": "desc",
                "imageBase64": "b64",
                "svgIcon": "<svg/>",
                "pythonVersion": python_version,
                "parameters": [{"id": "p1"}],
                "categories": ["cat"],
                "type": integration_type,
            },
            api_version=APIVersion.V1BETA,
        )


def test_create_integration_none_fields_excluded(chronicle_client):
    """Test that None optional fields are excluded from create_integration body."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value={"name": "integrations/test"},
    ) as mock_request:
        create_integration(
            chronicle_client,
            display_name="Test",
            staging=True,
            description=None,
            image_base64=None,
            svg_icon=None,
            python_version=None,
            parameters=None,
            categories=None,
            integration_type=None,
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations",
            json={"displayName": "Test", "staging": True},
            api_version=APIVersion.V1BETA,
        )


def test_create_integration_error(chronicle_client):
    """Test create_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to create integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration(chronicle_client, display_name="Test", staging=True)

        assert "Failed to create integration" in str(exc_info.value)


# -- download_integration tests --


def test_download_integration_success(chronicle_client):
    """Test download_integration uses chronicle_request_bytes with alt=media and zip accept."""
    expected = b"ZIPBYTES"

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request_bytes",
        return_value=expected,
    ) as mock_bytes:
        result = download_integration(chronicle_client, "test-integration")

        assert result == expected

        mock_bytes.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:export",
            api_version=APIVersion.V1BETA,
            params={"alt": "media"},
            headers={"Accept": "application/zip"},
        )


def test_download_integration_error(chronicle_client):
    """Test download_integration propagates APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request_bytes",
        side_effect=APIError("Failed to download integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            download_integration(chronicle_client, "test-integration")

        assert "Failed to download integration" in str(exc_info.value)


# -- download_integration_dependency tests --


def test_download_integration_dependency_success(chronicle_client):
    """Test download_integration_dependency posts dependency name."""
    expected = {"dependency": "requests"}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = download_integration_dependency(
            chronicle_client,
            integration_name="test-integration",
            dependency_name="requests==2.32.0",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration:downloadDependency",
            json={"dependency": "requests==2.32.0"},
            api_version=APIVersion.V1BETA,
        )


def test_download_integration_dependency_error(chronicle_client):
    """Test download_integration_dependency raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to download dependency"),
    ):
        with pytest.raises(APIError) as exc_info:
            download_integration_dependency(
                chronicle_client,
                integration_name="test-integration",
                dependency_name="requests",
            )

        assert "Failed to download dependency" in str(exc_info.value)


# -- export_integration_items tests --


def test_export_integration_items_success_some_fields(chronicle_client):
    """Test export_integration_items builds params correctly and uses chronicle_request_bytes."""
    expected = b"ZIPBYTES"

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request_bytes",
        return_value=expected,
    ) as mock_bytes:
        result = export_integration_items(
            chronicle_client,
            integration_name="test-integration",
            actions=["1", "2"],
            connectors=["10"],
            logical_operators=["7"],
        )

        assert result == expected

        mock_bytes.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:exportItems",
            params={
                "actions": "1,2",
                "connectors": ["10"],
                "logicalOperators": ["7"],
                "alt": "media",
            },
            api_version=APIVersion.V1BETA,
            headers={"Accept": "application/zip"},
        )


def test_export_integration_items_no_fields(chronicle_client):
    """Test export_integration_items always includes alt=media."""
    expected = b"ZIPBYTES"

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request_bytes",
        return_value=expected,
    ) as mock_bytes:
        result = export_integration_items(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_bytes.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:exportItems",
            params={"alt": "media"},
            api_version=APIVersion.V1BETA,
            headers={"Accept": "application/zip"},
        )


def test_export_integration_items_error(chronicle_client):
    """Test export_integration_items propagates APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request_bytes",
        side_effect=APIError("Failed to export integration items"),
    ):
        with pytest.raises(APIError) as exc_info:
            export_integration_items(chronicle_client, "test-integration")

        assert "Failed to export integration items" in str(exc_info.value)


# -- get_integration_affected_items tests --


def test_get_integration_affected_items_success(chronicle_client):
    """Test get_integration_affected_items delegates to chronicle_request."""
    expected = {"affectedItems": []}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_affected_items(chronicle_client, "test-integration")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:fetchAffectedItems",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_affected_items_error(chronicle_client):
    """Test get_integration_affected_items raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to fetch affected items"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_affected_items(chronicle_client, "test-integration")

        assert "Failed to fetch affected items" in str(exc_info.value)


# -- get_agent_integrations tests --


def test_get_agent_integrations_success(chronicle_client):
    """Test get_agent_integrations passes agentId parameter."""
    expected = {"integrations": []}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_agent_integrations(chronicle_client, agent_id="agent-123")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations:fetchAgentIntegrations",
            params={"agentId": "agent-123"},
            api_version=APIVersion.V1BETA,
        )


def test_get_agent_integrations_error(chronicle_client):
    """Test get_agent_integrations raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to fetch agent integrations"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_agent_integrations(chronicle_client, agent_id="agent-123")

        assert "Failed to fetch agent integrations" in str(exc_info.value)


# -- get_integration_dependencies tests --


def test_get_integration_dependencies_success(chronicle_client):
    """Test get_integration_dependencies delegates to chronicle_request."""
    expected = {"dependencies": []}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_dependencies(chronicle_client, "test-integration")

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:fetchDependencies",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_dependencies_error(chronicle_client):
    """Test get_integration_dependencies raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to fetch dependencies"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_dependencies(chronicle_client, "test-integration")

        assert "Failed to fetch dependencies" in str(exc_info.value)


# -- get_integration_restricted_agents tests --


def test_get_integration_restricted_agents_success(chronicle_client):
    """Test get_integration_restricted_agents passes required python version and pushRequest."""
    expected = {"restrictedAgents": []}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_restricted_agents(
            chronicle_client,
            integration_name="test-integration",
            required_python_version=PythonVersion.PYTHON_3_11,
            push_request=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:fetchRestrictedAgents",
            params={
                "requiredPythonVersion": PythonVersion.PYTHON_3_11.value,
                "pushRequest": True,
            },
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_restricted_agents_default_push_request(chronicle_client):
    """Test get_integration_restricted_agents default push_request=False is sent."""
    expected = {"restrictedAgents": []}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        get_integration_restricted_agents(
            chronicle_client,
            integration_name="test-integration",
            required_python_version=PythonVersion.PYTHON_3_11,
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:fetchRestrictedAgents",
            params={
                "requiredPythonVersion": PythonVersion.PYTHON_3_11.value,
                "pushRequest": False,
            },
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_restricted_agents_error(chronicle_client):
    """Test get_integration_restricted_agents raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to fetch restricted agents"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_restricted_agents(
                chronicle_client,
                integration_name="test-integration",
                required_python_version=PythonVersion.PYTHON_3_11,
            )

        assert "Failed to fetch restricted agents" in str(exc_info.value)


# -- get_integration_diff tests --


def test_get_integration_diff_success(chronicle_client):
    """Test get_integration_diff builds endpoint with diff type."""
    expected = {"diff": {}}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_diff(
            chronicle_client,
            integration_name="test-integration",
            diff_type=DiffType.PRODUCTION,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration:fetchProductionDiff",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_diff_error(chronicle_client):
    """Test get_integration_diff raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to fetch diff"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_diff(chronicle_client, "test-integration")

        assert "Failed to fetch diff" in str(exc_info.value)


# -- transition_integration tests --


def test_transition_integration_success(chronicle_client):
    """Test transition_integration posts to pushTo{TargetMode}."""
    expected = {"name": "integrations/test"}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = transition_integration(
            chronicle_client,
            integration_name="test-integration",
            target_mode=TargetMode.PRODUCTION,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration:pushToProduction",
            api_version=APIVersion.V1BETA,
        )


def test_transition_integration_error(chronicle_client):
    """Test transition_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to transition integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            transition_integration(
                chronicle_client,
                integration_name="test-integration",
                target_mode=TargetMode.STAGING,
            )

        assert "Failed to transition integration" in str(exc_info.value)


# -- update_integration tests --


def test_update_integration_uses_build_patch_body_and_passes_dependencies_to_remove(
    chronicle_client,
):
    """Test update_integration uses build_patch_body and adds dependenciesToRemove."""
    body = {"displayName": "New"}
    params = {"updateMask": "displayName"}

    with patch(
        "secops.chronicle.integration.integrations.build_patch_body",
        return_value=(body, params),
    ) as mock_build_patch, patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value={"name": "integrations/test"},
    ) as mock_request:
        result = update_integration(
            chronicle_client,
            integration_name="test-integration",
            display_name="New",
            dependencies_to_remove=["dep1", "dep2"],
            update_mask="displayName",
        )

        assert result == {"name": "integrations/test"}

        mock_build_patch.assert_called_once()
        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="integrations/test-integration",
            json=body,
            params={"updateMask": "displayName", "dependenciesToRemove": "dep1,dep2"},
            api_version=APIVersion.V1BETA,
        )


def test_update_integration_when_build_patch_body_returns_no_params(chronicle_client):
    """Test update_integration handles params=None from build_patch_body."""
    body = {"description": "New"}

    with patch(
        "secops.chronicle.integration.integrations.build_patch_body",
        return_value=(body, None),
    ), patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value={"name": "integrations/test"},
    ) as mock_request:
        update_integration(
            chronicle_client,
            integration_name="test-integration",
            description="New",
            dependencies_to_remove=["dep1"],
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="integrations/test-integration",
            json=body,
            params={"dependenciesToRemove": "dep1"},
            api_version=APIVersion.V1BETA,
        )


def test_update_integration_error(chronicle_client):
    """Test update_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.build_patch_body",
        return_value=({}, None),
    ), patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to update integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration(chronicle_client, "test-integration")

        assert "Failed to update integration" in str(exc_info.value)


# -- update_custom_integration tests --


def test_update_custom_integration_builds_body_and_params(chronicle_client):
    """Test update_custom_integration builds nested integration body and updateMask param."""
    expected = {"successful": True, "integration": {"name": "integrations/test"}}

    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_custom_integration(
            chronicle_client,
            integration_name="test-integration",
            display_name="New",
            staging=False,
            dependencies_to_remove=["dep1"],
            update_mask="displayName,staging",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration:updateCustomIntegration",
            json={
                "integration": {
                    "name": "test-integration",
                    "displayName": "New",
                    "staging": False,
                },
                "dependenciesToRemove": ["dep1"],
            },
            params={"updateMask": "displayName,staging"},
            api_version=APIVersion.V1BETA,
        )


def test_update_custom_integration_excludes_none_fields(chronicle_client):
    """Test update_custom_integration excludes None fields from integration object."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        return_value={"successful": True},
    ) as mock_request:
        update_custom_integration(
            chronicle_client,
            integration_name="test-integration",
            display_name=None,
            description=None,
            image_base64=None,
            svg_icon=None,
            python_version=None,
            parameters=None,
            categories=None,
            integration_type=None,
            staging=None,
            dependencies_to_remove=None,
            update_mask=None,
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration:updateCustomIntegration",
            json={"integration": {"name": "test-integration"}},
            params=None,
            api_version=APIVersion.V1BETA,
        )


def test_update_custom_integration_error(chronicle_client):
    """Test update_custom_integration raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.integrations.chronicle_request",
        side_effect=APIError("Failed to update custom integration"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_custom_integration(chronicle_client, "test-integration")

        assert "Failed to update custom integration" in str(exc_info.value)
