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
"""Unit tests for parser extension management functionality."""

import base64
import json
import pytest
from unittest.mock import Mock, patch
from requests import Session

from secops.chronicle.client import ChronicleClient
from secops.chronicle.parser_extension import (
    ParserExtensionConfig,
    create_parser_extension,
    get_parser_extension,
    list_parser_extensions,
    activate_parser_extension,
    delete_parser_extension,
)
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_auth.return_value.client_cert = None
        mock_auth.return_value.client_cert_pass = None
        mock_auth.return_value.session = Mock(spec=Session)
        mock_auth.return_value.base_url = "https://test.com"
        mock_auth.return_value.instance_id = "test-instance"
        client = ChronicleClient(
            "test-project",
            "test-customer",
            region="us",
            auth=mock_auth.return_value,
        )
        return client


@pytest.fixture
def mock_response():
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.ok = True
    # Default return value, can be overridden in specific tests
    mock.json.return_value = {}
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response object."""
    mock = Mock()
    mock.status_code = 400
    mock.ok = False
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock


class TestParserExtensionConfig:
    """Tests for ParserExtensionConfig class."""

    def test_encode_base64_with_plain_text(self):
        """Test base64 encoding with plain text input."""
        text = "test log message"
        result = ParserExtensionConfig.encode_base64(text)
        assert base64.b64decode(result).decode("utf-8") == text

    def test_encode_base64_with_empty_string(self):
        """Test base64 encoding with empty string."""
        with pytest.raises(
            ValueError, match="Value cannot be empty for encoding"
        ):
            ParserExtensionConfig.encode_base64("")

    def test_encode_base64_with_already_encoded(self):
        """Test base64 encoding with already encoded input."""
        encoded = base64.b64encode("test".encode("utf-8")).decode("utf-8")
        result = ParserExtensionConfig.encode_base64(encoded)
        assert result == encoded

    def test_init_with_log(self):
        """Test initialization with log field."""
        config = ParserExtensionConfig(log="test log")
        assert config.log == "test log"
        assert config.encoded_log == base64.b64encode(
            "test log".encode("utf-8")
        ).decode("utf-8")

    def test_init_with_parser_config(self):
        """Test initialization with parser config."""
        config = ParserExtensionConfig(parser_config="parser code")
        assert config.parser_config == "parser code"
        assert config.encoded_cbn_snippet == base64.b64encode(
            "parser code".encode("utf-8")
        ).decode("utf-8")

    def test_init_with_field_extractors_dict(self):
        """Test initialization with field extractors dictionary."""
        extractors = {"field1": "value1"}
        config = ParserExtensionConfig(field_extractors=extractors)
        assert config.field_extractors == extractors

    def test_init_with_field_extractors_json(self):
        """Test initialization with field extractors JSON string."""
        extractors = '{"field1": "value1"}'
        config = ParserExtensionConfig(field_extractors=extractors)
        assert config.field_extractors == json.loads(extractors)

    def test_init_with_invalid_field_extractors_json(self):
        """Test initialization with invalid field extractors JSON string."""
        with pytest.raises(
            ValueError, match="Invalid JSON for field_extractors"
        ):
            ParserExtensionConfig(field_extractors="{invalid json}")

    def test_init_with_dynamic_parsing_dict(self):
        """Test initialization with dynamic parsing dictionary."""
        parsing = {"opted_fields": [{"field": "value"}]}
        config = ParserExtensionConfig(dynamic_parsing=parsing)
        assert config.dynamic_parsing == parsing

    def test_init_with_dynamic_parsing_json(self):
        """Test initialization with dynamic parsing JSON string."""
        parsing = '{"opted_fields": [{"field": "value"}]}'
        config = ParserExtensionConfig(dynamic_parsing=parsing)
        assert config.dynamic_parsing == json.loads(parsing)

    def test_init_with_invalid_dynamic_parsing_json(self):
        """Test initialization with invalid dynamic parsing JSON string."""
        with pytest.raises(
            ValueError, match="Invalid JSON for dynamic_parsing"
        ):
            ParserExtensionConfig(dynamic_parsing="{invalid json}")

    def test_validate_with_no_config(self):
        """Test validation with no configuration."""
        config = ParserExtensionConfig()
        with pytest.raises(ValueError, match="Exactly one of parser_config"):
            config.validate()

    def test_validate_with_multiple_configs(self):
        """Test validation with multiple configurations."""
        config = ParserExtensionConfig(
            parser_config="code", field_extractors={"field": "value"}
        )
        with pytest.raises(ValueError, match="Exactly one of parser_config"):
            config.validate()

    def test_to_dict_with_log_and_cbn(self):
        """Test to_dict with log and CBN snippet."""
        config = ParserExtensionConfig(
            log="test log", parser_config="test code"
        )
        result = config.to_dict()
        assert "log" in result
        assert "cbn_snippet" in result
        assert result["log"] == config.encoded_log
        assert result["cbn_snippet"] == config.encoded_cbn_snippet

    def test_to_dict_with_field_extractors(self):
        """Test to_dict with field extractors."""
        extractors = {"field1": "value1"}
        config = ParserExtensionConfig(field_extractors=extractors)
        result = config.to_dict()
        assert "field_extractors" in result
        assert result["field_extractors"] == extractors

    def test_to_dict_with_dynamic_parsing(self):
        """Test to_dict with dynamic parsing."""
        parsing = {"opted_fields": [{"field": "value"}]}
        config = ParserExtensionConfig(dynamic_parsing=parsing)
        result = config.to_dict()
        assert "dynamic_parsing" in result
        assert result["dynamic_parsing"] == parsing


# --- create_parser_extension Tests ---
def test_create_parser_extension_success(chronicle_client, mock_response):
    """Test successful creation of parser extension."""
    mock_response.json.return_value = {"id": "test-id"}
    chronicle_client.session.request.return_value = mock_response

    config = ParserExtensionConfig(parser_config="test code")
    result = create_parser_extension(chronicle_client, "test-type", config)

    assert result == {"id": "test-id"}
    chronicle_client.session.request.assert_called_once()


def test_create_parser_extension_failure(chronicle_client, mock_error_response):
    """Test failed creation of parser extension."""
    chronicle_client.session.request.return_value = mock_error_response

    config = ParserExtensionConfig(parser_config="test code")
    with pytest.raises(APIError, match="Failed to create parser extension"):
        create_parser_extension(chronicle_client, "test-type", config)


# --- get_parser_extension Tests ---
def test_get_parser_extension_success(chronicle_client, mock_response):
    """Test successful retrieval of parser extension."""
    mock_response.json.return_value = {"id": "test-id"}
    chronicle_client.session.request.return_value = mock_response

    result = get_parser_extension(chronicle_client, "test-type", "test-id")

    assert result == {"id": "test-id"}
    chronicle_client.session.request.assert_called_once()


def test_get_parser_extension_failure(chronicle_client, mock_error_response):
    """Test failed retrieval of parser extension."""
    chronicle_client.session.request.return_value = mock_error_response

    with pytest.raises(APIError, match="Failed to get parser extension"):
        get_parser_extension(chronicle_client, "test-type", "test-id")


# --- list_parser_extensions Tests ---
def test_list_parser_extensions_success(chronicle_client, mock_response):
    """Test successful listing of parser extensions."""
    mock_response.json.return_value = {"parserExtensions": [{"id": "test-id"}]}
    chronicle_client.session.request.return_value = mock_response

    result = list_parser_extensions(
        client=chronicle_client, 
        log_type="test-type", 
        as_list=False
    )

    assert result == {"parserExtensions": [{"id": "test-id"}]}
    chronicle_client.session.request.assert_called_once()


def test_list_parser_extensions_with_pagination(
    chronicle_client, mock_response
):
    """Test listing parser extensions with pagination parameters."""
    mock_response.json.return_value = {"parserExtensions": []}
    chronicle_client.session.request.return_value = mock_response

    list_parser_extensions(
        chronicle_client, "test-type", page_size=10, page_token="next-page"
    )

    chronicle_client.session.request.assert_called_once()
    assert (
        "pageSize"
        in chronicle_client.session.request.call_args.kwargs["params"]
    )
    assert (
        "pageToken"
        in chronicle_client.session.request.call_args.kwargs["params"]
    )


# --- activate_parser_extension Tests ---
def test_activate_parser_extension_success(chronicle_client, mock_response):
    """Test successful activation of parser extension."""
    chronicle_client.session.request.return_value = mock_response

    activate_parser_extension(chronicle_client, "test-type", "test-id")

    chronicle_client.session.request.assert_called_once()
    assert (
        ":activate" in chronicle_client.session.request.call_args.kwargs["url"]
    )


def test_activate_parser_extension_failure(
    chronicle_client, mock_error_response
):
    """Test failed activation of parser extension."""
    chronicle_client.session.request.return_value = mock_error_response

    with pytest.raises(APIError, match="Failed to activate parser extension"):
        activate_parser_extension(chronicle_client, "test-type", "test-id")


# --- delete_parser_extension Tests ---
def test_delete_parser_extension_success(chronicle_client, mock_response):
    """Test successful deletion of parser extension."""
    chronicle_client.session.request.return_value = mock_response

    delete_parser_extension(chronicle_client, "test-type", "test-id")

    chronicle_client.session.request.assert_called_once()


def test_delete_parser_extension_failure(chronicle_client, mock_error_response):
    """Test failed deletion of parser extension."""
    chronicle_client.session.request.return_value = mock_error_response

    with pytest.raises(APIError, match="Failed to delete parser extension"):
        delete_parser_extension(chronicle_client, "test-type", "test-id")
