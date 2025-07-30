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
"""Tests for the UDM Key/Value Mapping module."""

import base64
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.udm_mapping import (
    RowLogFormat,
    generate_udm_key_value_mappings,
)
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


def test_row_log_format_enum() -> None:
    """Test RowLogFormat enum values and string representation."""
    assert str(RowLogFormat.JSON) == "JSON"
    assert str(RowLogFormat.CSV) == "CSV"
    assert str(RowLogFormat.XML) == "XML"
    assert str(RowLogFormat.LOG_FORMAT_UNSPECIFIED) == "LOG_FORMAT_UNSPECIFIED"


def test_generate_udm_key_value_mappings_success(
    chronicle_client, response_mock
):
    """Test generate_udm_key_value_mappings with success response."""

    response_mock.json.return_value = {
        "fieldMappings": {
            "event.id": "123",
            "event.user": "test_user",
            "event.action": "allowed",
        }
    }
    chronicle_client.session.post.return_value = response_mock

    # Test input
    test_log = '{"event":{"id":"123","user":"test_user","action":"allowed"}}'

    result = generate_udm_key_value_mappings(
        chronicle_client,
        RowLogFormat.JSON,
        test_log,
        use_array_bracket_notation=True,
        compress_array_fields=False,
    )

    # Verify API call
    expected_url = (
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}"
        ":generateUdmKeyValueMappings"
    )
    chronicle_client.session.post.assert_called_once()
    args, kwargs = chronicle_client.session.post.call_args

    # Check URL and payload structure
    assert args[0] == expected_url
    # Verify result
    assert result == {
        "event.id": "123",
        "event.user": "test_user",
        "event.action": "allowed",
    }


def test_generate_udm_key_value_mappings_already_encoded(
    chronicle_client, response_mock
):
    """Test UDM mapping with already base64 encoded log."""
    response_mock.json.return_value = {
        "fieldMappings": {"test.field": "test_value"}
    }
    chronicle_client.session.post.return_value = response_mock

    # Create a base64 encoded log
    raw_log = '{"test":{"field":"test_value"}}'
    encoded_log = base64.b64encode(raw_log.encode("utf-8")).decode("utf-8")

    result = generate_udm_key_value_mappings(
        chronicle_client, RowLogFormat.JSON, encoded_log
    )

    # Assert log wasn't double-encoded
    _, kwargs = chronicle_client.session.post.call_args
    assert kwargs["json"]["log"] == encoded_log
    assert result == {"test.field": "test_value"}


def test_generate_udm_key_value_mappings_error(chronicle_client, response_mock):
    """Test generate_udm_key_value_mappings function with error response."""
    response_mock.status_code = 400
    response_mock.text = "Bad Request"
    chronicle_client.session.post.return_value = response_mock

    with pytest.raises(APIError, match="Failed to generate key/value mapping"):
        generate_udm_key_value_mappings(
            chronicle_client, RowLogFormat.JSON, "test"
        )
