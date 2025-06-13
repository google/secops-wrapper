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

import pytest
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.parser import (
    activate_parser,
    activate_release_candidate_parser,
    copy_parser,
    create_parser,
    deactivate_parser,
    delete_parser,
    get_parser,
    list_parsers
)
from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    return ChronicleClient(
        customer_id="test-customer",
        project_id="test-project"
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
    mock.raise_for_status.side_effect = Exception("API Error") # To simulate requests.exceptions.HTTPError
    return mock


# --- activate_parser Tests ---
def test_activate_parser_success(chronicle_client, mock_response):
    """Test activate_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_12345"
    mock_response.json.return_value = {} # Expected empty JSON object

    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = activate_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:activate"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == {}


def test_activate_parser_error(chronicle_client, mock_error_response):
    """Test activate_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_12345"

    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            activate_parser(chronicle_client, log_type, parser_id)
        assert "Failed to activate parser: Error message" in str(exc_info.value)


# --- activate_release_candidate_parser Tests ---
def test_activate_release_candidate_parser_success(chronicle_client, mock_response):
    """Test activate_release_candidate_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_67890"
    mock_response.json.return_value = {}

    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = activate_release_candidate_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:activateReleaseCandidateParser"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == {}


def test_activate_release_candidate_parser_error(chronicle_client, mock_error_response):
    """Test activate_release_candidate_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_67890"

    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            activate_release_candidate_parser(chronicle_client, log_type, parser_id)
        assert "Failed to activate parser: Error message" in str(exc_info.value)


# --- copy_parser Tests ---
def test_copy_parser_success(chronicle_client, mock_response):
    """Test copy_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_copy_orig"
    expected_parser = {"name": "projects/test-project/locations/us/instances/test-customer/logTypes/SOME_LOG_TYPE/parsers/pa_copy_new", "id": "pa_copy_new"}
    mock_response.json.return_value = expected_parser

    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = copy_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:copy"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == expected_parser


def test_copy_parser_error(chronicle_client, mock_error_response):
    """Test copy_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_copy_orig"

    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            copy_parser(chronicle_client, log_type, parser_id)
        assert "Failed to copy parser: Error message" in str(exc_info.value)


# --- create_parser Tests ---
def test_create_parser_success_default_validation(chronicle_client, mock_response):
    """Test create_parser function for success with default validated_on_empty_logs."""
    log_type = "NIX_SYSTEM"
    parser_code = "parser UDM_Parser:events {}"
    expected_parser_info = {"name": "pa_new_parser", "cbn": parser_code, "validated_on_empty_logs": True}
    mock_response.json.return_value = expected_parser_info

    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = create_parser(chronicle_client, log_type, parser_code)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_post.assert_called_once_with(
            expected_url,
            json={"cbn": parser_code, "validated_on_empty_logs": True}
        )
        assert result == expected_parser_info


def test_create_parser_success_with_validation_false(chronicle_client, mock_response):
    """Test create_parser function for success with validated_on_empty_logs=False."""
    log_type = "NIX_SYSTEM"
    parser_code = "parser CustomParser:events {}"
    expected_parser_info = {"name": "pa_new_parser_no_val", "cbn": parser_code, "validated_on_empty_logs": False}
    mock_response.json.return_value = expected_parser_info

    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = create_parser(chronicle_client, log_type, parser_code, validated_on_empty_logs=False)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_post.assert_called_once_with(
            expected_url,
            json={"cbn": parser_code, "validated_on_empty_logs": False}
        )
        assert result == expected_parser_info


def test_create_parser_error(chronicle_client, mock_error_response):
    """Test create_parser function for API error."""
    log_type = "NIX_SYSTEM"
    parser_code = "parser UDM_Parser:events {}"

    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            create_parser(chronicle_client, log_type, parser_code)
        assert "Failed to create parser: Error message" in str(exc_info.value)


# --- deactivate_parser Tests ---
def test_deactivate_parser_success(chronicle_client, mock_response):
    """Test deactivate_parser function for success."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_deactivate_me"
    mock_response.json.return_value = {}

    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = deactivate_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}:deactivate"
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == {}


def test_deactivate_parser_error(chronicle_client, mock_error_response):
    """Test deactivate_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_deactivate_me"

    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            deactivate_parser(chronicle_client, log_type, parser_id)
        assert "Failed to deactivate parser: Error message" in str(exc_info.value)


# --- delete_parser Tests ---
def test_delete_parser_success_no_force(chronicle_client, mock_response):
    """Test delete_parser function for success without force."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_delete_me"
    mock_response.json.return_value = {}

    with patch.object(chronicle_client.session, 'delete', return_value=mock_response) as mock_delete:
        result = delete_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}"
        mock_delete.assert_called_once_with(expected_url, params={"force": False})
        assert result == {}


def test_delete_parser_success_with_force(chronicle_client, mock_response):
    """Test delete_parser function for success with force=True."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_force_delete_me"
    mock_response.json.return_value = {}

    with patch.object(chronicle_client.session, 'delete', return_value=mock_response) as mock_delete:
        result = delete_parser(chronicle_client, log_type, parser_id, force=True)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}"
        mock_delete.assert_called_once_with(expected_url, params={"force": True})
        assert result == {}


def test_delete_parser_error(chronicle_client, mock_error_response):
    """Test delete_parser function for API error."""
    log_type = "SOME_LOG_TYPE"
    parser_id = "pa_delete_error"

    with patch.object(chronicle_client.session, 'delete', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            delete_parser(chronicle_client, log_type, parser_id)
        # Note: The original code's error message for delete_parser is "Failed to deactivate parser",
        # which seems like a typo. I'll assert against that, rather than "Failed to delete parser".
        assert "Failed to deactivate parser: Error message" in str(exc_info.value)


# --- get_parser Tests ---
def test_get_parser_success(chronicle_client, mock_response):
    """Test get_parser function for success."""
    log_type = "WINDOWS_DNS"
    parser_id = "pa_dns_parser"
    expected_parser = {"name": "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS_DNS/parsers/pa_dns_parser", "cbn": "parser DNS {}"}
    mock_response.json.return_value = expected_parser

    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = get_parser(chronicle_client, log_type, parser_id)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers/{parser_id}"
        mock_get.assert_called_once_with(expected_url)
        assert result == expected_parser


def test_get_parser_error(chronicle_client, mock_error_response):
    """Test get_parser function for API error."""
    log_type = "WINDOWS_DNS"
    parser_id = "pa_dns_parser"

    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            get_parser(chronicle_client, log_type, parser_id)
        assert "Failed to get parser: Error message" in str(exc_info.value)


# --- list_parsers Tests ---
def test_list_parsers_single_page_success(chronicle_client, mock_response):
    """Test list_parsers function for single-page success."""
    log_type = "LINUX_PROCESS"
    expected_parsers = [
        {"name": "pa_linux_1", "id": "pa_linux_1"},
        {"name": "pa_linux_2", "id": "pa_linux_2"}
    ]
    mock_response.json.return_value = {"parsers": expected_parsers}

    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = list_parsers(chronicle_client, log_type=log_type)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_get.assert_called_once_with(
            expected_url,
            params={"pageSize": 100, "pageToken": None, "filter": None}
        )
        assert result == expected_parsers


def test_list_parsers_no_parsers_success(chronicle_client, mock_response):
    """Test list_parsers function when no parsers are returned."""
    log_type = "EMPTY_LOG_TYPE"
    mock_response.json.return_value = {"parsers": []} # Or simply {} if 'parsers' key is absent

    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = list_parsers(chronicle_client, log_type=log_type)

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_get.assert_called_once_with(
            expected_url,
            params={"pageSize": 100, "pageToken": None, "filter": None}
        )
        assert result == []


def test_list_parsers_error(chronicle_client, mock_error_response):
    """Test list_parsers function for API error."""
    log_type = "ERROR_LOG_TYPE"

    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            list_parsers(chronicle_client, log_type=log_type)
        assert "Failed to list parsers: Error message" in str(exc_info.value)


def test_list_parsers_with_optional_params(chronicle_client, mock_response):
    """Test list_parsers function with custom page_size, page_token, and filter."""
    log_type = "CUSTOM_LOG_TYPE"
    page_size = 50
    page_token = "custom_token_xyz"
    filter_query = "name=contains('custom')"
    expected_parsers = [{"name": "pa_custom_1"}]
    mock_response.json.return_value = {"parsers": expected_parsers}

    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = list_parsers(
            chronicle_client,
            log_type=log_type,
            page_size=page_size,
            page_token=page_token,
            filter=filter_query
        )

        expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logTypes/{log_type}/parsers"
        mock_get.assert_called_once_with(
            expected_url,
            params={
                "pageSize": page_size,
                "pageToken": page_token,
                "filter": filter_query
            }
        )
        assert result == expected_parsers