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
"""Tests for format helper functions."""
from __future__ import annotations

import pytest

from secops.chronicle.utils.format_utils import (
    format_resource_id,
    parse_json_list,
)
from secops.exceptions import APIError


def test_format_resource_id_returns_bare_id_unchanged() -> None:
    # A plain ID with no path prefix should pass through as-is
    assert format_resource_id("123-ID-abc") == "123-ID-abc"


def test_format_resource_id_extracts_id_from_full_resource_name() -> None:
    # Full resource name should have the ID extracted correctly
    full_name = "projects/12345/locations/eu/instances/my-instance/nativeDashboards/123-ID-abc"
    assert format_resource_id(full_name) == "123-ID-abc"


def test_format_resource_id_handles_minimal_projects_prefix() -> None:
    # Minimal case: just "projects/<id>"
    assert format_resource_id("projects/my-project") == "my-project"


def test_format_resource_id_does_not_alter_non_projects_paths() -> None:
    # Paths that don't start with "projects/" should be returned as-is
    assert (
        format_resource_id("instances/my-instance/dashboards/abc")
        == "instances/my-instance/dashboards/abc"
    )


def test_format_resource_id_empty_string_returns_empty_string() -> None:
    assert format_resource_id("") == ""


def test_parse_json_list_returns_list_unchanged() -> None:
    # A pre-built list should be returned as-is without any parsing
    value = [{"key": "value"}, {"key2": "value2"}]
    assert parse_json_list(value, "filters") is value


def test_parse_json_list_parses_valid_json_array_string() -> None:
    json_str = '[{"key": "value"}, {"key2": "value2"}]'
    result = parse_json_list(json_str, "filters")
    assert result == [{"key": "value"}, {"key2": "value2"}]


def test_parse_json_list_wraps_single_json_object_in_list() -> None:
    # A JSON string containing a single object (not an array) should be wrapped
    json_str = '{"key": "value"}'
    result = parse_json_list(json_str, "filters")
    assert result == [{"key": "value"}]


def test_parse_json_list_raises_api_error_on_invalid_json() -> None:
    with pytest.raises(APIError, match="Invalid filters JSON"):
        parse_json_list("not valid json {", "filters")


def test_parse_json_list_error_message_includes_field_name() -> None:
    # The field name should appear in the error to aid debugging
    with pytest.raises(APIError, match="Invalid charts JSON"):
        parse_json_list("{bad json", "charts")


def test_parse_json_list_raises_api_error_chained_from_value_error() -> None:
    # The APIError should chain from the underlying ValueError
    with pytest.raises(APIError) as exc_info:
        parse_json_list("bad json", "filters")
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_parse_json_list_handles_empty_json_array() -> None:
    result = parse_json_list("[]", "filters")
    assert result == []


def test_parse_json_list_handles_empty_list_input() -> None:
    result = parse_json_list([], "filters")
    assert result == []
