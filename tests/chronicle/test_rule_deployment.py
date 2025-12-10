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
"""Unit tests for rule deployment updates."""

import pytest
from unittest.mock import Mock, patch

from secops.chronicle.rule import (
    update_rule_deployment,
    enable_rule,
    set_rule_alerting,
)
from secops.chronicle.models import APIVersion
from secops.chronicle.client import ChronicleClient
from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def chronicle_client():
    """Create a mock Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(customer_id="test-customer", project_id="test-project")


@pytest.fixture
def response_mock():
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"ok": True}
    return mock


def _deployment_url(client: ChronicleClient, rule_id: str) -> str:
    return f"{client.base_url(APIVersion.V1)}/{client.instance_id}/rules/{rule_id}/deployment"


def test_update_rule_deployment_enabled(chronicle_client, response_mock):
    """Update only enabled flag."""
    chronicle_client.session.patch.return_value = response_mock

    rule_id = "ru_123"
    res = update_rule_deployment(chronicle_client, rule_id, enabled=True)

    chronicle_client.session.patch.assert_called_once_with(
        _deployment_url(chronicle_client, rule_id),
        params={"update_mask": "enabled"},
        json={"enabled": True},
    )
    assert res == {"ok": True}


def test_update_rule_deployment_multiple_fields(chronicle_client, response_mock):
    """Update enabled, alerting and runFrequency in one PATCH."""
    chronicle_client.session.patch.return_value = response_mock

    rule_id = "ru_abc"
    res = update_rule_deployment(
        chronicle_client,
        rule_id,
        enabled=True,
        alerting=False,
        run_frequency="LIVE",
    )

    chronicle_client.session.patch.assert_called_once_with(
        _deployment_url(chronicle_client, rule_id),
        params={"update_mask": "enabled,alerting,runFrequency"},
        json={"enabled": True, "alerting": False, "runFrequency": "LIVE"},
    )
    assert res == {"ok": True}


def test_update_rule_deployment_archived_only(chronicle_client, response_mock):
    """Update only archived flag."""
    chronicle_client.session.patch.return_value = response_mock

    rule_id = "ru_arch"
    res = update_rule_deployment(chronicle_client, rule_id, archived=True)

    chronicle_client.session.patch.assert_called_once_with(
        _deployment_url(chronicle_client, rule_id),
        params={"update_mask": "archived"},
        json={"archived": True},
    )
    assert res == {"ok": True}


def test_update_rule_deployment_no_fields_error(chronicle_client, response_mock):
    """No fields provided should raise APIError."""
    with pytest.raises(SecOpsError, match="No deployment fields provided"):
        update_rule_deployment(chronicle_client, "ru_none")


def test_update_rule_deployment_api_error(chronicle_client, response_mock):
    """Non-200 response should raise APIError."""
    response_mock.status_code = 400
    response_mock.text = "Bad Request"
    chronicle_client.session.patch.return_value = response_mock

    with pytest.raises(APIError, match="Failed to update rule deployment"):
        update_rule_deployment(chronicle_client, "ru_err", enabled=True)


def test_enable_rule_wrapper(chronicle_client, response_mock):
    """enable_rule delegates to update_rule_deployment."""
    chronicle_client.session.patch.return_value = response_mock
    rule_id = "ru_wrap"

    res = enable_rule(chronicle_client, rule_id, enabled=False)

    chronicle_client.session.patch.assert_called_once_with(
        _deployment_url(chronicle_client, rule_id),
        params={"update_mask": "enabled"},
        json={"enabled": False},
    )
    assert res == {"ok": True}


def test_set_rule_alerting_wrapper(chronicle_client, response_mock):
    """set_rule_alerting delegates to update_rule_deployment."""
    chronicle_client.session.patch.return_value = response_mock
    rule_id = "ru_alert"

    res = set_rule_alerting(chronicle_client, rule_id, alerting_enabled=True)

    chronicle_client.session.patch.assert_called_once_with(
        _deployment_url(chronicle_client, rule_id),
        params={"update_mask": "alerting"},
        json={"alerting": True},
    )
    assert res == {"ok": True} 