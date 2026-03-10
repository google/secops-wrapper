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
"""Tests for Chronicle integration logical operator revisions functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.logical_operator_revisions import (
    list_integration_logical_operator_revisions,
    delete_integration_logical_operator_revision,
    create_integration_logical_operator_revision,
    rollback_integration_logical_operator_revision,
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
            default_api_version=APIVersion.V1ALPHA,
        )


# -- list_integration_logical_operator_revisions tests --


def test_list_integration_logical_operator_revisions_success(chronicle_client):
    """Test list_integration_logical_operator_revisions delegates to paginated request."""
    expected = {
        "revisions": [{"name": "r1"}, {"name": "r2"}],
        "nextPageToken": "token",
    }

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.logical_operator_revisions.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_logical_operator_revisions(
            chronicle_client,
            integration_name="My Integration",
            logical_operator_id="lo1",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/My Integration/logicalOperators/lo1/revisions",
            items_key="revisions",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_logical_operator_revisions_default_args(chronicle_client):
    """Test list_integration_logical_operator_revisions with default args."""
    expected = {"revisions": []}

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_logical_operator_revisions(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/logicalOperators/lo1/revisions",
            items_key="revisions",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=False,
        )


def test_list_integration_logical_operator_revisions_with_filter_order(
    chronicle_client,
):
    """Test list passes filter/orderBy in extra_params."""
    expected = {"revisions": [{"name": "r1"}]}

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_logical_operator_revisions(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            filter_string='version = "1.0"',
            order_by="createTime desc",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/logicalOperators/lo1/revisions",
            items_key="revisions",
            page_size=None,
            page_token=None,
            extra_params={
                "filter": 'version = "1.0"',
                "orderBy": "createTime desc",
            },
            as_list=False,
        )


def test_list_integration_logical_operator_revisions_as_list(chronicle_client):
    """Test list_integration_logical_operator_revisions with as_list=True."""
    expected = [{"name": "r1"}, {"name": "r2"}]

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_logical_operator_revisions(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            as_list=True,
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1ALPHA,
            path="integrations/test-integration/logicalOperators/lo1/revisions",
            items_key="revisions",
            page_size=None,
            page_token=None,
            extra_params={},
            as_list=True,
        )


# -- delete_integration_logical_operator_revision tests --


def test_delete_integration_logical_operator_revision_success(chronicle_client):
    """Test delete_integration_logical_operator_revision delegates to chronicle_request."""
    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        return_value=None,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operator_revisions.format_resource_id",
        return_value="test-integration",
    ):
        delete_integration_logical_operator_revision(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            revision_id="rev1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path=(
                "integrations/test-integration/logicalOperators/lo1/revisions/rev1"
            ),
            api_version=APIVersion.V1ALPHA,
        )


# -- create_integration_logical_operator_revision tests --


def test_create_integration_logical_operator_revision_minimal(chronicle_client):
    """Test create_integration_logical_operator_revision with minimal fields."""
    logical_operator = {
        "displayName": "Test Operator",
        "script": "def evaluate(a, b): return a == b",
    }
    expected = {"name": "rev1", "comment": ""}

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operator_revisions.format_resource_id",
        return_value="test-integration",
    ):
        result = create_integration_logical_operator_revision(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            logical_operator=logical_operator,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path=(
                "integrations/test-integration/logicalOperators/lo1/revisions"
            ),
            api_version=APIVersion.V1ALPHA,
            json={"logicalOperator": logical_operator},
        )


def test_create_integration_logical_operator_revision_with_comment(chronicle_client):
    """Test create_integration_logical_operator_revision with comment."""
    logical_operator = {
        "displayName": "Test Operator",
        "script": "def evaluate(a, b): return a == b",
    }
    expected = {"name": "rev1", "comment": "Version 2.0"}

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_logical_operator_revision(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            logical_operator=logical_operator,
            comment="Version 2.0",
        )

        assert result == expected

        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["json"]["logicalOperator"] == logical_operator
        assert call_kwargs["json"]["comment"] == "Version 2.0"


# -- rollback_integration_logical_operator_revision tests --


def test_rollback_integration_logical_operator_revision_success(chronicle_client):
    """Test rollback_integration_logical_operator_revision delegates to chronicle_request."""
    expected = {"name": "rev1", "comment": "Rolled back"}

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.logical_operator_revisions.format_resource_id",
        return_value="test-integration",
    ):
        result = rollback_integration_logical_operator_revision(
            chronicle_client,
            integration_name="test-integration",
            logical_operator_id="lo1",
            revision_id="rev1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path=(
                "integrations/test-integration/logicalOperators/lo1/"
                "revisions/rev1:rollback"
            ),
            api_version=APIVersion.V1ALPHA,
        )


# -- Error handling tests --


def test_list_integration_logical_operator_revisions_api_error(chronicle_client):
    """Test list_integration_logical_operator_revisions handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_paginated_request",
        side_effect=APIError("API Error"),
    ):
        with pytest.raises(APIError, match="API Error"):
            list_integration_logical_operator_revisions(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="lo1",
            )


def test_delete_integration_logical_operator_revision_api_error(chronicle_client):
    """Test delete_integration_logical_operator_revision handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        side_effect=APIError("Delete failed"),
    ):
        with pytest.raises(APIError, match="Delete failed"):
            delete_integration_logical_operator_revision(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="lo1",
                revision_id="rev1",
            )


def test_create_integration_logical_operator_revision_api_error(chronicle_client):
    """Test create_integration_logical_operator_revision handles API errors."""
    logical_operator = {"displayName": "Test"}

    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        side_effect=APIError("Creation failed"),
    ):
        with pytest.raises(APIError, match="Creation failed"):
            create_integration_logical_operator_revision(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="lo1",
                logical_operator=logical_operator,
            )


def test_rollback_integration_logical_operator_revision_api_error(chronicle_client):
    """Test rollback_integration_logical_operator_revision handles API errors."""
    with patch(
        "secops.chronicle.integration.logical_operator_revisions.chronicle_request",
        side_effect=APIError("Rollback failed"),
    ):
        with pytest.raises(APIError, match="Rollback failed"):
            rollback_integration_logical_operator_revision(
                chronicle_client,
                integration_name="test-integration",
                logical_operator_id="lo1",
                revision_id="rev1",
            )

