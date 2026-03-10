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
"""Tests for Chronicle marketplace integration job instances functions."""

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import (
    APIVersion,
    IntegrationJobInstanceParameter,
    AdvancedConfig,
    ScheduleType,
    DailyScheduleDetails,
    Date,
    TimeOfDay,
)
from secops.chronicle.integration.job_instances import (
    list_integration_job_instances,
    get_integration_job_instance,
    delete_integration_job_instance,
    create_integration_job_instance,
    update_integration_job_instance,
    run_integration_job_instance_on_demand,
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


# -- list_integration_job_instances tests --


def test_list_integration_job_instances_success(chronicle_client):
    """Test list_integration_job_instances delegates to chronicle_paginated_request."""
    expected = {
        "jobInstances": [{"name": "ji1"}, {"name": "ji2"}],
        "nextPageToken": "t",
    }

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated, patch(
        "secops.chronicle.integration.job_instances.format_resource_id",
        return_value="My Integration",
    ):
        result = list_integration_job_instances(
            chronicle_client,
            integration_name="My Integration",
            job_id="j1",
            page_size=10,
            page_token="next-token",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert "jobs/j1/jobInstances" in kwargs["path"]
        assert kwargs["items_key"] == "jobInstances"
        assert kwargs["page_size"] == 10
        assert kwargs["page_token"] == "next-token"


def test_list_integration_job_instances_default_args(chronicle_client):
    """Test list_integration_job_instances with default args."""
    expected = {"jobInstances": []}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_instances(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
        )

        assert result == expected


def test_list_integration_job_instances_with_filters(chronicle_client):
    """Test list_integration_job_instances with filter and order_by."""
    expected = {"jobInstances": [{"name": "ji1"}]}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_instances(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            filter_string="enabled = true",
            order_by="displayName",
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["extra_params"] == {
            "filter": "enabled = true",
            "orderBy": "displayName",
        }


def test_list_integration_job_instances_as_list(chronicle_client):
    """Test list_integration_job_instances returns list when as_list=True."""
    expected = [{"name": "ji1"}, {"name": "ji2"}]

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_instances(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            as_list=True,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["as_list"] is True


def test_list_integration_job_instances_error(chronicle_client):
    """Test list_integration_job_instances raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_paginated_request",
        side_effect=APIError("Failed to list job instances"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_integration_job_instances(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
            )
        assert "Failed to list job instances" in str(exc_info.value)


# -- get_integration_job_instance tests --


def test_get_integration_job_instance_success(chronicle_client):
    """Test get_integration_job_instance issues GET request."""
    expected = {
        "name": "jobInstances/ji1",
        "displayName": "My Job Instance",
        "intervalSeconds": 300,
        "enabled": True,
    }

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert "jobs/j1/jobInstances/ji1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_get_integration_job_instance_error(chronicle_client):
    """Test get_integration_job_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        side_effect=APIError("Failed to get job instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            get_integration_job_instance(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                job_instance_id="ji1",
            )
        assert "Failed to get job instance" in str(exc_info.value)


# -- delete_integration_job_instance tests --


def test_delete_integration_job_instance_success(chronicle_client):
    """Test delete_integration_job_instance issues DELETE request."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=None,
    ) as mock_request:
        delete_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
        )

        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert "jobs/j1/jobInstances/ji1" in kwargs["endpoint_path"]
        assert kwargs["api_version"] == APIVersion.V1BETA


def test_delete_integration_job_instance_error(chronicle_client):
    """Test delete_integration_job_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        side_effect=APIError("Failed to delete job instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            delete_integration_job_instance(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                job_instance_id="ji1",
            )
        assert "Failed to delete job instance" in str(exc_info.value)


# -- create_integration_job_instance tests --


def test_create_integration_job_instance_required_fields_only(chronicle_client):
    """Test create_integration_job_instance sends only required fields."""
    expected = {"name": "jobInstances/new", "displayName": "My Job Instance"}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            display_name="My Job Instance",
            interval_seconds=300,
            enabled=True,
            advanced=False,
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path="integrations/test-integration/jobs/j1/jobInstances",
            api_version=APIVersion.V1BETA,
            json={
                "displayName": "My Job Instance",
                "intervalSeconds": 300,
                "enabled": True,
                "advanced": False,
            },
        )


def test_create_integration_job_instance_with_optional_fields(chronicle_client):
    """Test create_integration_job_instance includes optional fields when provided."""
    expected = {"name": "jobInstances/new"}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            display_name="My Job Instance",
            interval_seconds=300,
            enabled=True,
            advanced=False,
            description="Test job instance",
            parameters=[{"id": 1, "value": "test"}],
            agent="agent-123",
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["description"] == "Test job instance"
        assert kwargs["json"]["parameters"] == [{"id": 1, "value": "test"}]
        assert kwargs["json"]["agent"] == "agent-123"


def test_create_integration_job_instance_with_dataclass_params(chronicle_client):
    """Test create_integration_job_instance converts dataclass parameters."""
    expected = {"name": "jobInstances/new"}

    param = IntegrationJobInstanceParameter(value="test-value")

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            display_name="My Job Instance",
            interval_seconds=300,
            enabled=True,
            advanced=False,
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["value"] == "test-value"


def test_create_integration_job_instance_with_advanced_config(chronicle_client):
    """Test create_integration_job_instance with AdvancedConfig dataclass."""
    expected = {"name": "jobInstances/new"}

    advanced_config = AdvancedConfig(
        time_zone="America/New_York",
        schedule_type=ScheduleType.DAILY,
        daily_schedule=DailyScheduleDetails(
            start_date=Date(year=2026, month=3, day=8),
            time=TimeOfDay(hours=2, minutes=0),
            interval=1
        )
    )

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = create_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            display_name="My Job Instance",
            interval_seconds=300,
            enabled=True,
            advanced=True,
            advanced_config=advanced_config,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        config_sent = kwargs["json"]["advancedConfig"]
        assert config_sent["timeZone"] == "America/New_York"
        assert config_sent["scheduleType"] == "DAILY"
        assert "dailySchedule" in config_sent


def test_create_integration_job_instance_error(chronicle_client):
    """Test create_integration_job_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        side_effect=APIError("Failed to create job instance"),
    ):
        with pytest.raises(APIError) as exc_info:
            create_integration_job_instance(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                display_name="My Job Instance",
                interval_seconds=300,
                enabled=True,
                advanced=False,
            )
        assert "Failed to create job instance" in str(exc_info.value)


# -- update_integration_job_instance tests --


def test_update_integration_job_instance_single_field(chronicle_client):
    """Test update_integration_job_instance updates a single field."""
    expected = {"name": "jobInstances/ji1", "displayName": "Updated Instance"}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.job_instances.build_patch_body",
        return_value=(
            {"displayName": "Updated Instance"},
            {"updateMask": "displayName"},
        ),
    ) as mock_build_patch:
        result = update_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            display_name="Updated Instance",
        )

        assert result == expected

        mock_build_patch.assert_called_once()
        mock_request.assert_called_once_with(
            chronicle_client,
            method="PATCH",
            endpoint_path=(
                "integrations/test-integration/jobs/j1/jobInstances/ji1"
            ),
            api_version=APIVersion.V1BETA,
            json={"displayName": "Updated Instance"},
            params={"updateMask": "displayName"},
        )


def test_update_integration_job_instance_multiple_fields(chronicle_client):
    """Test update_integration_job_instance updates multiple fields."""
    expected = {"name": "jobInstances/ji1"}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.job_instances.build_patch_body",
        return_value=(
            {
                "displayName": "Updated",
                "intervalSeconds": 600,
                "enabled": False,
            },
            {"updateMask": "displayName,intervalSeconds,enabled"},
        ),
    ):
        result = update_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            display_name="Updated",
            interval_seconds=600,
            enabled=False,
        )

        assert result == expected


def test_update_integration_job_instance_with_dataclass_params(chronicle_client):
    """Test update_integration_job_instance converts dataclass parameters."""
    expected = {"name": "jobInstances/ji1"}

    param = IntegrationJobInstanceParameter(value="updated-value")

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.job_instances.build_patch_body",
        return_value=(
            {"parameters": [{"value": "updated-value"}]},
            {"updateMask": "parameters"},
        ),
    ):
        result = update_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            parameters=[param],
        )

        assert result == expected


def test_update_integration_job_instance_with_advanced_config(chronicle_client):
    """Test update_integration_job_instance with AdvancedConfig dataclass."""
    expected = {"name": "jobInstances/ji1"}

    advanced_config = AdvancedConfig(
        time_zone="UTC",
        schedule_type=ScheduleType.DAILY,
        daily_schedule=DailyScheduleDetails(
            start_date=Date(year=2026, month=3, day=8),
            time=TimeOfDay(hours=0, minutes=0),
            interval=1
        )
    )

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.job_instances.build_patch_body",
        return_value=(
            {
                "advancedConfig": {
                    "timeZone": "UTC",
                    "scheduleType": "DAILY",
                    "dailySchedule": {
                        "startDate": {"year": 2026, "month": 3, "day": 8},
                        "time": {"hours": 0, "minutes": 0},
                        "interval": 1
                    }
                }
            },
            {"updateMask": "advancedConfig"},
        ),
    ):
        result = update_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            advanced_config=advanced_config,
        )

        assert result == expected


def test_update_integration_job_instance_with_update_mask(chronicle_client):
    """Test update_integration_job_instance respects explicit update_mask."""
    expected = {"name": "jobInstances/ji1"}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request, patch(
        "secops.chronicle.integration.job_instances.build_patch_body",
        return_value=(
            {"displayName": "Updated"},
            {"updateMask": "displayName"},
        ),
    ):
        result = update_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            display_name="Updated",
            update_mask="displayName",
        )

        assert result == expected


def test_update_integration_job_instance_error(chronicle_client):
    """Test update_integration_job_instance raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        side_effect=APIError("Failed to update job instance"),
    ), patch(
        "secops.chronicle.integration.job_instances.build_patch_body",
        return_value=({"enabled": False}, {"updateMask": "enabled"}),
    ):
        with pytest.raises(APIError) as exc_info:
            update_integration_job_instance(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                job_instance_id="ji1",
                enabled=False,
            )
        assert "Failed to update job instance" in str(exc_info.value)


# -- run_integration_job_instance_on_demand tests --


def test_run_integration_job_instance_on_demand_success(chronicle_client):
    """Test run_integration_job_instance_on_demand issues POST request."""
    expected = {"success": True}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = run_integration_job_instance_on_demand(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
        )

        assert result == expected

        mock_request.assert_called_once_with(
            chronicle_client,
            method="POST",
            endpoint_path=(
                "integrations/test-integration/jobs/j1/jobInstances/ji1:runOnDemand"
            ),
            api_version=APIVersion.V1BETA,
            json={},
        )


def test_run_integration_job_instance_on_demand_with_params(chronicle_client):
    """Test run_integration_job_instance_on_demand with parameters."""
    expected = {"success": True}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = run_integration_job_instance_on_demand(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            parameters=[{"id": 1, "value": "override"}],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["json"]["parameters"] == [{"id": 1, "value": "override"}]


def test_run_integration_job_instance_on_demand_with_dataclass(chronicle_client):
    """Test run_integration_job_instance_on_demand converts dataclass parameters."""
    expected = {"success": True}

    param = IntegrationJobInstanceParameter(value="test")

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = run_integration_job_instance_on_demand(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            parameters=[param],
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        params_sent = kwargs["json"]["parameters"]
        assert len(params_sent) == 1
        assert params_sent[0]["value"] == "test"


def test_run_integration_job_instance_on_demand_error(chronicle_client):
    """Test run_integration_job_instance_on_demand raises APIError on failure."""
    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        side_effect=APIError("Failed to run job instance on demand"),
    ):
        with pytest.raises(APIError) as exc_info:
            run_integration_job_instance_on_demand(
                chronicle_client,
                integration_name="test-integration",
                job_id="j1",
                job_instance_id="ji1",
            )
        assert "Failed to run job instance on demand" in str(exc_info.value)


# -- API version tests --


def test_list_integration_job_instances_custom_api_version(chronicle_client):
    """Test list_integration_job_instances with custom API version."""
    expected = {"jobInstances": []}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_integration_job_instances(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_paginated.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA


def test_get_integration_job_instance_custom_api_version(chronicle_client):
    """Test get_integration_job_instance with custom API version."""
    expected = {"name": "jobInstances/ji1"}

    with patch(
        "secops.chronicle.integration.job_instances.chronicle_request",
        return_value=expected,
    ) as mock_request:
        result = get_integration_job_instance(
            chronicle_client,
            integration_name="test-integration",
            job_id="j1",
            job_instance_id="ji1",
            api_version=APIVersion.V1ALPHA,
        )

        assert result == expected

        _, kwargs = mock_request.call_args
        assert kwargs["api_version"] == APIVersion.V1ALPHA

