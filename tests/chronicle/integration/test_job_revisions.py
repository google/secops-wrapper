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
"""Tests for Chronicle marketplace integration job revisions functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion
from secops.chronicle.integration.job_revisions import (
    list_integration_job_revisions,
    delete_integration_job_revision,
    create_integration_job_revision,
    rollback_integration_job_revision,
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


# -- list_integration_job_revisions tests --


def test_list_integration_job_revisions_success(chronicle_client):
    """Test list_integration_job_revisions delegates to chronicle_paginated_request."""
    expected = {
        "revisions": [{"name": "r1"}, {"name": "r2"}],
        "nextPageToken": "t",
    }

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.job_revisions.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_job_revisions(
            chronicle_client,
            integration_name="My Integration",
            job_id="j1",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert "jobs/j1/revisions" in kwargs["path"]
        assert kwargs["items_key"] == "revisions"
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "next-token"


def test_list_integration_job_revisions_default_args(chronicle_client):
    """Test list_integration_job_revisions with default args."""
    expected = {"revisions": []}

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_revisions(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
        )

        assert result == expected


def test_list_integration_job_revisions_with_filters(chronicle_client):
    """Test list_integration_job_revisions with filter and order_by."""
    expected = {"revisions": [{"name": "r1"}]}

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_revisions(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            filter_string='version = "1.0"',
            order_by="createTime",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": 'version = "1.0"',
            "orderBy": "createTime",
        }


def test_list_integration_job_revisions_as_list(chronicle_client):
    """Test list_integration_job_revisions returns list when as_list=True."""
    expected = [{"name": "r1"}, {"name": "r2"}]

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_revisions(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_integration_job_revisions_error(chronicle_client):
    """Test list_integration_job_revisions raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_paginated_request",
        side_effect=APIError("Failed to list job revisions"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_job_revisions(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
            )
        assert "Failed to list job revisions" in str(exc_info.value)


# -- delete_integration_job_revision tests --


def test_delete_integration_job_revision_success(chronicle_client):
    """Test delete_integration_job_revision issues DELETE request."""
    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_job_revision(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            revision_id="r1",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert "jobs/j1/revisions/r1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_delete_integration_job_revision_error(chronicle_client):
    """Test delete_integration_job_revision raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        side_effect=APIError("Failed to delete job revision"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_job_revision(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                revision_id="r1",
            )
        assert "Failed to delete job revision" in str(exc_info.value)


# -- create_integration_job_revision tests --


def test_create_integration_job_revision_required_fields_only(
    chronicle_client,
):
    """Test create_integration_job_revision with required fields only."""
    expected = {"name": "revisions/new", "job": {"displayName": "My Job"}}
    job_dict = {
        "displayName": "My Job",
        "script": "print('hello')",
        "version": 1,
        "enabled": True,
        "custom": True,
    }

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job_revision(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job=job_dict,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path=(
                "integrations/test-integration/jobs/j1/revisions"
            ),
            api_version=APIVersion.V1BETA,
            json={"job": job_dict},
        )


def test_create_integration_job_revision_with_comment(chronicle_client):
    """Test create_integration_job_revision includes comment when provided."""
    expected = {"name": "revisions/new"}
    job_dict = {
        "displayName": "My Job",
        "script": "print('hello')",
        "version": 1,
        "enabled": True,
        "custom": True,
    }

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job_revision(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job=job_dict,
            comment="Backup before major update",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["comment"] == "Backup before major update"
        assert kwargs["json"]["job"] == job_dict


def test_create_integration_job_revision_error(chronicle_client):
    """Test create_integration_job_revision raises APIError on failure."""
    job_dict = {
        "displayName": "My Job",
        "script": "print('hello')",
        "version": 1,
        "enabled": True,
        "custom": True,
    }

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        side_effect=APIError("Failed to create job revision"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_job_revision(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                job=job_dict,
            )
        assert "Failed to create job revision" in str(exc_info.value)


# -- rollback_integration_job_revision tests --


def test_rollback_integration_job_revision_success(chronicle_client):
    """Test rollback_integration_job_revision issues POST request."""
    expected = {
        "name": "revisions/r1",
        "job": {
            "displayName": "My Job",
            "script": "print('hello')",
        },
    }

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = rollback_integration_job_revision(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            revision_id="r1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert "jobs/j1/revisions/r1:rollback" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_rollback_integration_job_revision_error(chronicle_client):
    """Test rollback_integration_job_revision raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        side_effect=APIError("Failed to rollback job revision"),
    ):
        with pytest.raises(APIError) as exc_info:
            rollback_integration_job_revision(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                revision_id="r1",
            )
        assert "Failed to rollback job revision" in str(exc_info.value)


# -- API version tests --


def test_list_integration_job_revisions_custom_api_version(chronicle_client):
    """Test list_integration_job_revisions with custom API version."""
    expected = {"revisions": []}

    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_revisions(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_delete_integration_job_revision_custom_api_version(chronicle_client):
    """Test delete_integration_job_revision with custom API version."""
    with patch(
        "secops.chronicle.integration.job_revisions.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_job_revision(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            revision_id="r1",
            api_version=APIVersion.V1ALPHA,
        )

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA

