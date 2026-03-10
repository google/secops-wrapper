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
"""Tests for Chronicle marketplace integration jobs functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion, JobParameter, ParamType
from secops.chronicle.integration.jobs import (
    list_integration_jobs,
    get_integration_job,
    delete_integration_job,
    create_integration_job,
    update_integration_job,
    execute_integration_job_test,
    get_integration_job_template,
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


# -- list_integration_jobs tests --


def test_list_integration_jobs_success(chronicle_client):
    """Test list_integration_jobs delegates to chronicle_paginated_request."""
    expected = {"jobs": [{"name": "j1"}, {"name": "j2"}], "nextPageToken": "t"}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.jobs.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_jobs(
            chronicle_client,
            integration_name="My Integration",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            api_version=APIVersion.V1BETA,
            path="integrations/My Integration/jobs",
            items_key="jobs",
            page_size=10,
            page_token="next-token",
            extra_params={},
            as_list=False,
        )


def test_list_integration_jobs_default_args(chronicle_client):
    """Test list_integration_jobs with default args."""
    expected = {"jobs": []}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_jobs(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected


def test_list_integration_jobs_with_filters(chronicle_client):
    """Test list_integration_jobs with filter and order_by."""
    expected = {"jobs": [{"name": "j1"}]}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_jobs(
            chronicle_client,
            integration_name="test-integration",
            filter_string="custom=true",
            order_by="displayName",
            exclude_staging=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": "custom=true",
            "orderBy": "displayName",
            "excludeStaging": True,
        }


def test_list_integration_jobs_as_list(chronicle_client):
    """Test list_integration_jobs returns list when as_list=True."""
    expected = [{"name": "j1"}, {"name": "j2"}]

    with patch(
        "secops.chronicle.integration.jobs.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_jobs(
            chronicle_client,
            integration_name="test-integration",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_integration_jobs_error(chronicle_client):
    """Test list_integration_jobs raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_paginated_request",
        side_effect=APIError("Failed to list integration jobs"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_jobs(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to list integration jobs" in str(exc_info.value)


# -- get_integration_job tests --


def test_get_integration_job_success(chronicle_client):
    """Test get_integration_job issues GET request."""
    expected = {
        "name": "jobs/j1",
        "displayName": "My Job",
        "script": "print('hello')",
    }

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_job(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/jobs/j1",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_job_error(chronicle_client):
    """Test get_integration_job raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        side_effect=APIError("Failed to get integration job"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_job(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
            )
        assert "Failed to get integration job" in str(exc_info.value)


# -- delete_integration_job tests --


def test_delete_integration_job_success(chronicle_client):
    """Test delete_integration_job issues DELETE request."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_job(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
        )

        mock_request.assert_called_once_with(
            chronicle_client,
            method="DELETE",
            endpoint_path="integrations/test-integration/jobs/j1",
            api_version=APIVersion.V1BETA,
        )


def test_delete_integration_job_error(chronicle_client):
    """Test delete_integration_job raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        side_effect=APIError("Failed to delete integration job"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_job(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
            )
        assert "Failed to delete integration job" in str(exc_info.value)


# -- create_integration_job tests --


def test_create_integration_job_required_fields_only(chronicle_client):
    """Test create_integration_job sends only required fields when optionals omitted."""
    expected = {"name": "jobs/new", "displayName": "My Job"}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Job",
            script="print('hi')",
            version=1,
            enabled=True,
            custom=True,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/jobs",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Job",
                "script": "print('hi')",
                "version": 1,
                "enabled": True,
                "custom": True,
            },
        )


def test_create_integration_job_with_optional_fields(chronicle_client):
    """Test create_integration_job includes optional fields when provided."""
    expected = {"name": "jobs/new"}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Job",
            script="print('hi')",
            version=1,
            enabled=True,
            custom=True,
            description="Test job",
            parameters=[{"id": 1, "displayName": "p1", "type": "STRING"}],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["description"] == "Test job"
        assert kwargs["json"]["parameters"] == [
            {"id": 1, "displayName": "p1", "type": "STRING"}
        ]


def test_create_integration_job_with_dataclass_parameters(chronicle_client):
    """Test create_integration_job converts JobParameter dataclasses."""
    expected = {"name": "jobs/new"}

    param = JobParameter(
        id=1,
        display_name="API Key",
        description="API key for authentication",
        type=ParamType.STRING,
        mandatory=True,
    )

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job(
            chronicle_client,
            integration_name="test-integration",
            display_name="My Job",
            script="print('hi')",
            version=1,
            enabled=True,
            custom=True,
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["id"] == 1
        assert params_sent[0]["displayName"] == "API Key"
        assert params_sent[0]["type"] == "STRING"


def test_create_integration_job_error(chronicle_client):
    """Test create_integration_job raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        side_effect=APIError("Failed to create integration job"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_job(
                chronicle_client,
                integration_name="test-integration",
                display_name="My Job",
                script="print('hi')",
                version=1,
                enabled=True,
                custom=True,
            )
        assert "Failed to create integration job" in str(exc_info.value)


# -- update_integration_job tests --


def test_update_integration_job_with_explicit_update_mask(chronicle_client):
    """Test update_integration_job passes through explicit update_mask."""
    expected = {"name": "jobs/j1", "displayName": "New Name"}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_job(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            display_name="New Name",
            update_mask="displayName",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path="integrations/test-integration/jobs/j1",
            api_version=APIVersion.V1BETA,
            json={"displayName": "New Name"},
            params={"updateMask": "displayName"},
        )


def test_update_integration_job_auto_update_mask(chronicle_client):
    """Test update_integration_job auto-generates updateMask based on fields."""
    expected = {"name": "jobs/j1"}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_job(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            enabled=False,
            version=2,
        )

        assert result == expected

        assert mock_request.call_count == 1
        _, kwargs = mock_request.call_args

        assert kwargs["method"] == "PATCH"
        assert kwargs["endpoint_path"] == "integrations/test-integration/jobs/j1"
        assert kwargs["api_version"] == APIVersion.V1BETA

        assert kwargs["json"] == {"enabled": False, "version": 2}

        update_mask = kwargs["params"]["updateMask"]
        assert set(update_mask.split(",")) == {"enabled", "version"}


def test_update_integration_job_with_parameters(chronicle_client):
    """Test update_integration_job with parameters field."""
    expected = {"name": "jobs/j1"}

    param = JobParameter(
        id=2,
        display_name="Auth Token",
        description="Authentication token",
        type=ParamType.PASSWORD,
        mandatory=True,
    )

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = update_integration_job(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["id"] == 2
        assert params_sent[0]["displayName"] == "Auth Token"


def test_update_integration_job_error(chronicle_client):
    """Test update_integration_job raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        side_effect=APIError("Failed to update integration job"),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration_job(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                display_name="New Name",
            )
        assert "Failed to update integration job" in str(exc_info.value)


# -- execute_integration_job_test tests --


def test_execute_integration_job_test_success(chronicle_client):
    """Test execute_integration_job_test sends POST request with job."""
    expected = {
        "output": "Success",
        "debugOutput": "Debug info",
        "resultObjectJson": {"status": "ok"},
    }

    job = {
        "displayName": "Test Job",
        "script": "print('test')",
        "enabled": True,
    }

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = execute_integration_job_test(
            chronicle_client,
            integration_name="test-integration",
            job=job,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/jobs:executeTest",
            api_version=APIVersion.V1BETA,
            json={"job": job},
        )


def test_execute_integration_job_test_with_agent_identifier(chronicle_client):
    """Test execute_integration_job_test includes agent_identifier when provided."""
    expected = {"output": "Success"}

    job = {"displayName": "Test", "script": "print('test')"}

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = execute_integration_job_test(
            chronicle_client,
            integration_name="test-integration",
            job=job,
            agent_identifier="agent-123",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["agentIdentifier"] == "agent-123"


def test_execute_integration_job_test_error(chronicle_client):
    """Test execute_integration_job_test raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        side_effect=APIError("Failed to execute job test"),
    ):
        with pytest.raises(APIError) as exc_info:
            execute_integration_job_test(
                chronicle_client,
                integration_name="test-integration",
                job={"displayName": "Test"},
            )
        assert "Failed to execute job test" in str(exc_info.value)


# -- get_integration_job_template tests --


def test_get_integration_job_template_success(chronicle_client):
    """Test get_integration_job_template issues GET request."""
    expected = {
        "script": "# Template script\nprint('hello')",
        "displayName": "Template Job",
    }

    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_job_template(
            chronicle_client,
            integration_name="test-integration",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="GET",
            endpoint_path="integrations/test-integration/jobs:fetchTemplate",
            api_version=APIVersion.V1BETA,
        )


def test_get_integration_job_template_error(chronicle_client):
    """Test get_integration_job_template raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.jobs.chronicle_request",
        side_effect=APIError("Failed to get job template"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_job_template(
                chronicle_client,
                integration_name="test-integration",
            )
        assert "Failed to get job template" in str(exc_info.value)

