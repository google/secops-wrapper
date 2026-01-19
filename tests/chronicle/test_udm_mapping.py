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

from __future__ import annotations

import base64
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.models import APIVersion
from secops.chronicle.udm_mapping import RowLogFormat, generate_udm_key_value_mappings
from secops.exceptions import APIError


@pytest.fixture
def client() -> Mock:
    # This module only passes client through to chronicle_request
    return Mock()


def test_row_log_format_enum() -> None:
    assert str(RowLogFormat.JSON) == "JSON"
    assert str(RowLogFormat.CSV) == "CSV"
    assert str(RowLogFormat.XML) == "XML"
    assert str(RowLogFormat.LOG_FORMAT_UNSPECIFIED) == "LOG_FORMAT_UNSPECIFIED"


def test_generate_udm_key_value_mappings_success(client: Mock) -> None:
    expected = {
        "fieldMappings": {
            "event.id": "123",
            "event.user": "test_user",
            "event.action": "allowed",
        }
    }

    test_log = '{"event":{"id":"123","user":"test_user","action":"allowed"}}'

    with patch("secops.chronicle.udm_mapping.chronicle_request", return_value=expected) as req:
        result = generate_udm_key_value_mappings(
            client,
            RowLogFormat.JSON,
            test_log,
            use_array_bracket_notation=True,
            compress_array_fields=False,
        )

    # Your function returns the full chronicle_request output (dict)
    assert result == expected

    # Verify helper invocation (module behaviour)
    req.assert_called_once()
    args, kwargs = req.call_args

    assert args[0] is client
    assert args[1] == "POST"
    assert kwargs["endpoint_path"] == ":generateUdmKeyValueMappings"
    assert kwargs["api_version"] == APIVersion.V1ALPHA

    payload = kwargs["json"]
    assert payload["log_format"] == RowLogFormat.JSON
    assert payload["use_array_bracket_notation"] is True
    assert payload["compress_array_fields"] is False

    # Ensure the log was base64 encoded
    decoded = base64.b64decode(payload["log"]).decode("utf-8")
    assert decoded == test_log


def test_generate_udm_key_value_mappings_already_encoded(client: Mock) -> None:
    expected = {"fieldMappings": {"test.field": "test_value"}}

    raw_log = '{"test":{"field":"test_value"}}'
    encoded_log = base64.b64encode(raw_log.encode("utf-8")).decode("utf-8")

    with patch("secops.chronicle.udm_mapping.chronicle_request", return_value=expected) as req:
        result = generate_udm_key_value_mappings(client, RowLogFormat.JSON, encoded_log)

    assert result == expected

    payload = req.call_args.kwargs["json"]
    # Should not double-encode
    assert payload["log"] == encoded_log
    assert payload["log_format"] == RowLogFormat.JSON


def test_generate_udm_key_value_mappings_propagates_api_error(client: Mock) -> None:
    with patch(
        "secops.chronicle.udm_mapping.chronicle_request",
        side_effect=APIError("boom"),
    ):
        with pytest.raises(APIError, match="boom"):
            generate_udm_key_value_mappings(client, RowLogFormat.JSON, "test")
