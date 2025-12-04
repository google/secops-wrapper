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
"""Tests for Chronicle parser functions."""

import base64
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.parser import (
    MAX_LOG_SIZE,
    MAX_LOGS,
    MAX_TOTAL_SIZE,
    activate_parser,
    activate_release_candidate_parser,
    copy_parser,
    create_parser,
    deactivate_parser,
    delete_parser,
    get_parser,
    list_parsers,
    run_parser,
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
            customer_id="test-customer", project_id="test-project"
        )


@pytest.fixture
def mock_response():
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    # Default return value, can be overridden in specific tests
    mock.json.return_value = {}
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response object."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception(
        "API Error"
    )  # To simulate requests.exceptions.HTTPError
    return mock


# --- activate_parser Tests ---
def test_activate_parser_success(chronicle_client, mock_response):
    """Test activate_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_12345"
    mock_response.json.return_value = {}  # Expected empty JSON object

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = activate_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:activate"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == {}


def test_activate_parser_error(chronicle_client, mock_error_response):
    """Test activate_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_12345"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            activate_parser(chronicle_client, log_type, parser_id)
        assert "Failed to activate parser: Error message" in str(exc_info.value)


# --- activate_release_candidate_parser Tests ---
def test_activate_release_candidate_parser_success(
    chronicle_client, mock_response
):
    """Test activate_release_candidate_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_67890"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = activate_release_candidate_parser(
            chronicle_client, log_type, parser_id
        )

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:activateReleaseCandidateParser"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == {}


def test_activate_release_candidate_parser_error(
    chronicle_client, mock_error_response
):
    """Test activate_release_candidate_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_67890"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            activate_release_candidate_parser(
                chronicle_client, log_type, parser_id
            )
        assert "Failed to activate parser: Error message" in str(exc_info.value)


# --- copy_parser Tests ---
def test_copy_parser_success(chronicle_client, mock_response):
    """Test copy_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_copy_orig"
    expected_parser = {
        "name": "projects/test-project/locations/us/instances/test-customer/logTypes/SOME_LOG_TYPE/parsers/pa_copy_new",
        "id": "pa_copy_new",
    }
    mock_response.json.return_value = expected_parser

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = copy_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:copy"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == expected_parser


def test_copy_parser_error(chronicle_client, mock_error_response):
    """Test copy_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_copy_orig"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            copy_parser(chronicle_client, log_type, parser_id)
        assert "Failed to copy parser: Error message" in str(exc_info.value)


# --- create_parser Tests ---
def test_create_parser_success_default_validation(
    chronicle_client, mock_response
):
    """Test create_parser function for success with default validated_on_empty_logs."""
    log_type = "NIX_SYSTEM"
    parser_code = "filter {}"
    expected_parser_info = {
        "name": "pa_new_parser",
        "cbn": parser_code,
        "validated_on_empty_logs": True,
    }
    mock_response.json.return_value = expected_parser_info

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = create_parser(chronicle_client, log_type, parser_code)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_post.assert_called_once_with(
            expected_url,
            json={
                "cbn": base64.b64encode(parser_code.encode("utf-8")).decode(
                    "utf-8"
                ),
                "validated_on_empty_logs": True,
            },
        )
        assert result == expected_parser_info


def test_create_parser_success_with_validation_false(
    chronicle_client, mock_response
):
    """Test create_parser function for success with validated_on_empty_logs=False."""
    log_type = "NIX_SYSTEM"
    parser_code = "filter {}"
    expected_parser_info = {
        "name": "pa_new_parser_no_val",
        "cbn": parser_code,
        "validated_on_empty_logs": False,
    }
    mock_response.json.return_value = expected_parser_info

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = create_parser(
            chronicle_client,
            log_type,
            parser_code,
            validated_on_empty_logs=False,
        )

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_post.assert_called_once_with(
            expected_url,
            json={
                "cbn": base64.b64encode(parser_code.encode("utf-8")).decode(
                    "utf-8"
                ),
                "validated_on_empty_logs": False,
            },
        )
        assert result == expected_parser_info


def test_create_parser_error(chronicle_client, mock_error_response):
    """Test create_parser function for API error."""
    log_type = "NIX_SYSTEM"
    parser_code = "parser UDM_Parser:events {}"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            create_parser(chronicle_client, log_type, parser_code)
        assert "Failed to create parser: Error message" in str(exc_info.value)


# --- deactivate_parser Tests ---
def test_deactivate_parser_success(chronicle_client, mock_response):
    """Test deactivate_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_deactivate_me"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = deactivate_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:deactivate"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == {}


def test_deactivate_parser_error(chronicle_client, mock_error_response):
    """Test deactivate_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_deactivate_me"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            deactivate_parser(chronicle_client, log_type, parser_id)
        assert "Failed to deactivate parser: Error message" in str(
            exc_info.value
        )


# --- delete_parser Tests ---
def test_delete_parser_success_no_force(chronicle_client, mock_response):
    """Test delete_parser function for success without force."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_delete_me"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_response
    ) as mock_delete:
        result = delete_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}"
        mock_delete.assert_called_once_with(
            expected_url, params={"force": False}
        )
        assert result == {}


def test_delete_parser_success_with_force(chronicle_client, mock_response):
    """Test delete_parser function for success with force=True."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_force_delete_me"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_response
    ) as mock_delete:
        result = delete_parser(
            chronicle_client, log_type, parser_id, force=True
        )

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}"
        mock_delete.assert_called_once_with(
            expected_url, params={"force": True}
        )
        assert result == {}


def test_delete_parser_error(chronicle_client, mock_error_response):
    """Test delete_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_delete_error"

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            delete_parser(chronicle_client, log_type, parser_id)
        assert "Failed to delete parser: Error message" in str(exc_info.value)


# --- get_parser Tests ---
def test_get_parser_success(chronicle_client, mock_response):
    """Test get_parser function for success."""
    log_type = "WINDOWS_DNS"
    parser_id = "pa_dns_parser"
    expected_parser = {
        "name": "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS_DNS/parsers/pa_dns_parser",
        "cbn": "parser DNS {}",
    }
    mock_response.json.return_value = expected_parser

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = get_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}"
        mock_get.assert_called_once_with(expected_url)
        assert result == expected_parser


def test_get_parser_error(chronicle_client, mock_error_response):
    """Test get_parser function for API error."""
    log_type = "WINDOWS_DNS"
    parser_id = "pa_dns_parser"

    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            get_parser(chronicle_client, log_type, parser_id)
        assert "Failed to get parser: Error message" in str(exc_info.value)


# --- list_parsers Tests ---
def test_list_parsers_single_page_success(chronicle_client, mock_response):
    """Test list_parsers function for single-page success."""
    log_type = "LINUX_PROCESS"
    expected_parsers = [
        {"name": "pa_linux_1", "id": "pa_linux_1"},
        {"name": "pa_linux_2", "id": "pa_linux_2"},
    ]
    mock_response.json.return_value = {"parsers": expected_parsers}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_parsers(chronicle_client, log_type=log_type)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_get.assert_called_once_with(
            expected_url,
            params={},
        )
        assert result == expected_parsers


def test_list_parsers_no_parsers_success(chronicle_client, mock_response):
    """Test list_parsers function when no parsers are returned."""
    log_type = "EMPTY_LOG_TYPE"
    mock_response.json.return_value = {
        "parsers": []
    }  # Or simply {} if 'parsers' key is absent

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_parsers(chronicle_client, log_type=log_type)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_get.assert_called_once_with(
            expected_url,
            params={},
        )
        assert result == []


def test_list_parsers_error(chronicle_client, mock_error_response):
    """Test list_parsers function for API error."""
    log_type = "ERROR_LOG_TYPE"

    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            list_parsers(chronicle_client, log_type=log_type)
        assert "Failed to list parsers: Error message" in str(exc_info.value)


def test_list_parsers_with_page_size_returns_raw_response(
    chronicle_client, mock_response
):
    """Test list_parsers returns raw API response when page_size is provided."""
    log_type = "CUSTOM_LOG_TYPE"
    page_size = 50
    page_token = "custom_token_xyz"
    filter_query = "name=contains('custom')"
    expected_parsers = [{"name": "pa_custom_1"}]
    expected_response = {
        "parsers": expected_parsers,
        "nextPageToken": "next_token_abc",
    }
    mock_response.json.return_value = expected_response

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_parsers(
            chronicle_client,
            log_type=log_type,
            page_size=page_size,
            page_token=page_token,
            filter=filter_query,
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}"
            f"/logTypes/{log_type}/parsers"
        )
        mock_get.assert_called_once_with(
            expected_url,
            params={
                "pageSize": page_size,
                "pageToken": page_token,
                "filter": filter_query,
            },
        )
        # With page_size provided, returns raw response dict
        assert result == expected_response
        assert "nextPageToken" in result


def test_list_parsers_auto_pagination(chronicle_client):
    """Test list_parsers auto-paginates when page_size is None (default).

    This test validates that the pagination correctly handles the
    'nextPageToken' field returned by the API and fetches all pages.
    """
    log_type = "WINDOWS"

    # First page of parsers with nextPageToken
    first_page_parsers = [
        {"name": "pa_windows_1", "id": "pa_windows_1"},
        {"name": "pa_windows_2", "id": "pa_windows_2"},
    ]

    # Second page of parsers without nextPageToken (last page)
    second_page_parsers = [
        {"name": "pa_windows_3", "id": "pa_windows_3"},
    ]

    # Mock responses for each page
    first_response = Mock()
    first_response.status_code = 200
    first_response.json.return_value = {
        "parsers": first_page_parsers,
        "nextPageToken": "page2_token",
    }

    second_response = Mock()
    second_response.status_code = 200
    second_response.json.return_value = {
        "parsers": second_page_parsers,
        # No nextPageToken - this is the last page
    }

    with patch.object(
        chronicle_client.session,
        "get",
        side_effect=[first_response, second_response],
    ) as mock_get:
        # No page_size means auto-pagination
        result = list_parsers(chronicle_client, log_type=log_type)

        # Verify we made two API calls (one per page)
        assert mock_get.call_count == 2

        # Verify first call uses default page size of 100
        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}"
            f"/logTypes/{log_type}/parsers"
        )
        first_call = mock_get.call_args_list[0]
        assert first_call[0][0] == expected_url

        # Verify second call uses the nextPageToken from first response
        second_call = mock_get.call_args_list[1]
        assert second_call[0][0] == expected_url
        assert second_call[1]["params"]["pageToken"] == "page2_token"

        # Verify all parsers from both pages are returned as a list
        expected_all_parsers = first_page_parsers + second_page_parsers
        assert result == expected_all_parsers
        assert len(result) == 3


def test_list_parsers_manual_pagination_single_page(
    chronicle_client, mock_response
):
    """Test list_parsers returns raw response for manual pagination."""
    log_type = "MANUAL_LOG_TYPE"
    page_size = 10
    expected_parsers = [{"name": "pa_manual_1"}]
    expected_response = {
        "parsers": expected_parsers,
        "nextPageToken": "next_page_token",
    }
    mock_response.json.return_value = expected_response

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_parsers(
            chronicle_client, log_type=log_type, page_size=page_size
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}"
            f"/logTypes/{log_type}/parsers"
        )
        mock_get.assert_called_once_with(
            expected_url,
            params={"pageSize": page_size},
        )
        # Returns raw response dict, not just the parsers list
        assert result == expected_response
        assert "parsers" in result
        assert "nextPageToken" in result


# --- run_parser Tests ---
def test_run_parser_success(chronicle_client, mock_response):
    """Test run_parser function for success."""
    log_type = "WINDOWS_AD"
    parser_code = "filter { mutate { add_field => { 'test' => 'value' } } }"
    parser_extension_code = "snippet { add_field => { 'ext' => 'value' } }"
    logs = ["log line 1", "log line 2"]

    expected_result = {
        "runParserResults": [
            {"parsedEvents": [{"event": {"test": "value", "ext": "value"}}]}
        ]
    }
    mock_response.json.return_value = expected_result

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = run_parser(
            chronicle_client,
            log_type=log_type,
            parser_code=parser_code,
            parser_extension_code=parser_extension_code,
            logs=logs,
            statedump_allowed=True,
        )

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}:runParser"

        # Verify the request body
        called_args = mock_post.call_args
        assert called_args[0][0] == expected_url

        request_body = called_args[1]["json"]
        assert "parser" in request_body
        assert "parser_extension" in request_body
        assert "log" in request_body
        assert request_body["statedump_allowed"] is True

        # Verify base64 encoding
        assert request_body["parser"]["cbn"] == base64.b64encode(
            parser_code.encode("utf8")
        ).decode("utf-8")
        assert request_body["parser_extension"][
            "cbn_snippet"
        ] == base64.b64encode(parser_extension_code.encode("utf8")).decode(
            "utf-8"
        )
        assert len(request_body["log"]) == 2
        assert request_body["log"][0] == base64.b64encode(
            logs[0].encode("utf8")
        ).decode("utf-8")
        assert request_body["log"][1] == base64.b64encode(
            logs[1].encode("utf8")
        ).decode("utf-8")

        assert result == expected_result


def test_run_parser_without_extension(chronicle_client, mock_response):
    """Test run_parser function without parser extension."""
    log_type = "OKTA"
    parser_code = "filter { mutate { add_field => { 'test' => 'value' } } }"
    logs = ["log line 1"]

    expected_result = {"runParserResults": [{"parsedEvents": []}]}
    mock_response.json.return_value = expected_result

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = run_parser(
            chronicle_client,
            log_type=log_type,
            parser_code=parser_code,
            parser_extension_code="",  # Empty extension
            logs=logs,
            statedump_allowed=False,
        )

        called_args = mock_post.call_args
        request_body = called_args[1]["json"]

        # Verify parser_extension is None when empty
        assert request_body["parser_extension"] is None
        assert request_body["statedump_allowed"] is False

        assert result == expected_result


def test_run_parser_empty_logs(chronicle_client):
    """Test run_parser function with empty logs list."""
    # Empty logs should now raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="WINDOWS",
            parser_code="filter {}",
            parser_extension_code="",
            logs=[],
        )
    assert "At least one log must be provided" in str(exc_info.value)


def test_run_parser_unicode_logs(chronicle_client, mock_response):
    """Test run_parser function with unicode characters in logs."""
    log_type = "CUSTOM"
    parser_code = "filter {}"
    logs = ["日本語ログ", "Ñoño log with émojis 🎉"]

    expected_result = {"runParserResults": [{"parsedEvents": []}]}
    mock_response.json.return_value = expected_result

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = run_parser(
            chronicle_client,
            log_type=log_type,
            parser_code=parser_code,
            parser_extension_code="",
            logs=logs,
        )

        called_args = mock_post.call_args
        request_body = called_args[1]["json"]

        # Verify unicode is properly encoded
        assert request_body["log"][0] == base64.b64encode(
            logs[0].encode("utf8")
        ).decode("utf-8")
        assert request_body["log"][1] == base64.b64encode(
            logs[1].encode("utf8")
        ).decode("utf-8")

        assert result == expected_result


def test_run_parser_error(chronicle_client, mock_error_response):
    """Test run_parser function for API error."""
    log_type = "WINDOWS"
    parser_code = "invalid parser"
    logs = ["test log"]

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            run_parser(
                chronicle_client,
                log_type=log_type,
                parser_code=parser_code,
                parser_extension_code="",
                logs=logs,
            )
        # Check for the new detailed error message format
        assert "Failed to evaluate parser for log type 'WINDOWS'" in str(
            exc_info.value
        )
        assert "Bad request" in str(exc_info.value)


def test_run_parser_large_logs(chronicle_client, mock_response):
    """Test run_parser function with large log entries."""
    log_type = "BIG_DATA"
    parser_code = "filter {}"
    # Create a large log entry (1MB)
    large_log = "x" * (1024 * 1024)
    logs = [large_log]

    expected_result = {"runParserResults": [{"parsedEvents": []}]}
    mock_response.json.return_value = expected_result

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = run_parser(
            chronicle_client,
            log_type=log_type,
            parser_code=parser_code,
            parser_extension_code="",
            logs=logs,
        )

        called_args = mock_post.call_args
        request_body = called_args[1]["json"]

        # Verify large log is properly encoded
        assert len(request_body["log"]) == 1
        # Base64 encoding increases size by ~33%
        assert len(request_body["log"][0]) > 1024 * 1024

        assert result == expected_result


def test_run_parser_validation_empty_log_type(chronicle_client):
    """Test run_parser validation for empty log_type."""
    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="",
            parser_code="filter {}",
            parser_extension_code="",
            logs=["test log"],
        )
    assert "log_type cannot be empty" in str(exc_info.value)


def test_run_parser_validation_empty_parser_code(chronicle_client):
    """Test run_parser validation for empty parser_code."""
    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="",
            parser_extension_code="",
            logs=["test log"],
        )
    assert "parser_code cannot be empty" in str(exc_info.value)


def test_run_parser_validation_logs_not_list(chronicle_client):
    """Test run_parser validation when logs is not a list."""
    with pytest.raises(TypeError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code="",
            logs="not a list",  # type: ignore
        )
    assert "logs must be a list" in str(exc_info.value)


def test_run_parser_validation_log_too_large(chronicle_client):
    """Test run_parser validation when a log exceeds size limit."""
    large_log = "x" * (MAX_LOG_SIZE + 1)
    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code="",
            logs=[large_log],
        )
    assert "exceeds maximum size" in str(exc_info.value)
    assert str(MAX_LOG_SIZE) in str(exc_info.value)


def test_run_parser_validation_too_many_logs(chronicle_client):
    """Test run_parser validation when too many logs are provided."""
    logs = ["log"] * (MAX_LOGS + 1)
    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code="",
            logs=logs,
        )
    assert f"exceeds maximum of {MAX_LOGS}" in str(exc_info.value)


def test_run_parser_validation_total_size_exceeded(chronicle_client):
    """Test run_parser validation when total size exceeds limit."""
    # Create logs that individually are OK but together exceed total limit
    log_size = 1024 * 1024  # 1MB each
    num_logs = (MAX_TOTAL_SIZE // log_size) + 2
    logs = ["x" * log_size for _ in range(num_logs)]

    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code="",
            logs=logs,
        )
    assert "Total size of all logs" in str(exc_info.value)
    assert str(MAX_TOTAL_SIZE) in str(exc_info.value)


def test_run_parser_validation_invalid_extension_type(chronicle_client):
    """Test run_parser validation when parser_extension_code is wrong type."""
    with pytest.raises(TypeError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code=123,  # type: ignore
            logs=["test log"],
        )
    assert "parser_extension_code must be a string or None" in str(
        exc_info.value
    )


def test_run_parser_detailed_error_400(chronicle_client, mock_response):
    """Test run_parser with detailed error message for 400 status."""
    mock_response.status_code = 400
    mock_response.text = "Invalid log type: INVALID_TYPE"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError) as exc_info:
            run_parser(
                chronicle_client,
                log_type="INVALID_TYPE",
                parser_code="filter {}",
                parser_extension_code="",
                logs=["test log"],
            )
        error_msg = str(exc_info.value)
        assert (
            "Failed to evaluate parser for log type 'INVALID_TYPE'" in error_msg
        )
        assert "Bad request" in error_msg
        assert "Log type 'INVALID_TYPE' may not be valid" in error_msg


def test_run_parser_detailed_error_404(chronicle_client, mock_response):
    """Test run_parser with detailed error message for 404 status."""
    mock_response.status_code = 404
    mock_response.text = "Not found"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError) as exc_info:
            run_parser(
                chronicle_client,
                log_type="MISSING_TYPE",
                parser_code="filter {}",
                parser_extension_code="",
                logs=["test log"],
            )
        error_msg = str(exc_info.value)
        assert "Log type 'MISSING_TYPE' not found" in error_msg


def test_run_parser_detailed_error_413(chronicle_client, mock_response):
    """Test run_parser with detailed error message for 413 status."""
    mock_response.status_code = 413
    mock_response.text = "Request entity too large"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError) as exc_info:
            run_parser(
                chronicle_client,
                log_type="OKTA",
                parser_code="filter {}",
                parser_extension_code="",
                logs=["test log"],
            )
        error_msg = str(exc_info.value)
        assert "Request too large" in error_msg
        assert "Try reducing the number or size of logs" in error_msg


def test_run_parser_validation_empty_logs_list(chronicle_client):
    """Test run_parser validation for empty logs list."""
    with pytest.raises(ValueError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code="",
            logs=[],
        )
    assert "At least one log must be provided" in str(exc_info.value)


def test_run_parser_validation_non_string_log(chronicle_client):
    """Test run_parser validation when a log is not a string."""
    with pytest.raises(TypeError) as exc_info:
        run_parser(
            chronicle_client,
            log_type="OKTA",
            parser_code="filter {}",
            parser_extension_code="",
            logs=["valid log", 123, "another log"],  # type: ignore
        )
    assert "All logs must be strings" in str(exc_info.value)
    assert "index 1" in str(exc_info.value)
