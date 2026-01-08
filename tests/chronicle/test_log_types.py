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
"""Tests for Chronicle log types functionality."""

from unittest.mock import Mock

import pytest

from secops.chronicle import log_types
from secops.chronicle.log_types import (
    classify_logs,
    get_all_log_types,
    get_log_type_description,
    is_valid_log_type,
    load_log_types,
    search_log_types,
)
from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def mock_chronicle_client():
    """Create a mock Chronicle client."""
    client = Mock()
    client.base_url = "https://us-chronicle.googleapis.com/v1alpha"
    client.instance_id = "projects/123/locations/us/instances/456"
    client.session = Mock()
    return client


@pytest.fixture
def mock_api_response():
    """Create a mock API response with log types."""
    return {
        "logTypes": [
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/OKTA"
                ),
                "displayName": "Okta Identity Management",
            },
            {
                "name": (
                    "projects/123/locations/us/instances/456/"
                    "logTypes/AWS_CLOUDTRAIL"
                ),
                "displayName": "AWS Cloudtrail",
            },
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/WINDOWS"
                ),
                "displayName": "Windows Event Logs",
            },
        ]
    }


@pytest.fixture
def mock_api_response_paginated_page1():
    """Create a mock API response for first page."""
    return {
        "logTypes": [
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/OKTA"
                ),
                "displayName": "Okta",
            },
            {
                "name": (
                    "projects/123/locations/us/instances/456/"
                    "logTypes/AWS_CLOUDTRAIL"
                ),
                "displayName": "AWS Cloudtrail",
            },
        ],
        "nextPageToken": "page2_token",
    }


@pytest.fixture
def mock_api_response_paginated_page2():
    """Create a mock API response for second page."""
    return {
        "logTypes": [
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/WINDOWS"
                ),
                "displayName": "Windows Event Logs",
            },
        ]
    }


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache before each test."""
    # pylint: disable=protected-access
    log_types._LOG_TYPES_CACHE = None
    yield
    # Clean up after test
    log_types._LOG_TYPES_CACHE = None


def test_load_log_types_from_api(mock_chronicle_client, mock_api_response):
    """Test loading log types from API."""
    # Mock the API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_chronicle_client.session.get.return_value = mock_response

    result = load_log_types(client=mock_chronicle_client)

    assert any("OKTA" in log_type["name"] for log_type in result)
    assert any("AWS_CLOUDTRAIL" in log_type["name"] for log_type in result)
    assert any("WINDOWS" in log_type["name"] for log_type in result)
    # Verify we get raw dict responses
    assert isinstance(result[0], dict)
    assert any(
        log_type["displayName"] == "Okta Identity Management"
        for log_type in result
    )
    # Verify pagination params: pageSize=1000 for fetching all
    call_args = mock_chronicle_client.session.get.call_args
    assert call_args[1]["params"]["pageSize"] == 1000


def test_load_log_types_api_pagination(
    mock_chronicle_client,
    mock_api_response_paginated_page1,
    mock_api_response_paginated_page2,
):
    """Test loading log types from API with pagination (all pages)."""
    # Mock the API responses for pagination
    mock_response_page1 = Mock()
    mock_response_page1.status_code = 200
    mock_response_page1.json.return_value = mock_api_response_paginated_page1

    mock_response_page2 = Mock()
    mock_response_page2.status_code = 200
    mock_response_page2.json.return_value = mock_api_response_paginated_page2

    mock_chronicle_client.session.get.side_effect = [
        mock_response_page1,
        mock_response_page2,
    ]

    result = load_log_types(client=mock_chronicle_client)

    # Verify pagination worked - should fetch all pages
    assert len(result) == 3
    assert any("OKTA" in log_type.get("name") for log_type in result)
    assert any("AWS_CLOUDTRAIL" in log_type.get("name") for log_type in result)
    assert any("WINDOWS" in log_type.get("name") for log_type in result)
    # Verify get was called twice (once per page)
    assert mock_chronicle_client.session.get.call_count == 2


def test_fetch_log_types_single_page(
    mock_chronicle_client, mock_api_response_paginated_page1
):
    """Test fetching single page when page_size is specified."""
    from secops.chronicle.log_types import _fetch_log_types_from_api

    # Mock API response with nextPageToken (more data available)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response_paginated_page1
    mock_chronicle_client.session.get.return_value = mock_response

    # Fetch with explicit page_size - should fetch only one page
    result = _fetch_log_types_from_api(
        client=mock_chronicle_client, page_size=2
    )

    # Should return only first page results, not continue pagination
    assert len(result) == 2
    assert any("OKTA" in log_type.get("name") for log_type in result)
    assert any("AWS_CLOUDTRAIL" in log_type.get("name") for log_type in result)
    # Verify get was called only once
    assert mock_chronicle_client.session.get.call_count == 1
    # Verify correct page_size was used
    call_args = mock_chronicle_client.session.get.call_args
    assert call_args[1]["params"]["pageSize"] == 2


def test_fetch_log_types_with_page_token(
    mock_chronicle_client, mock_api_response_paginated_page2
):
    """Test fetching with page_token parameter."""
    from secops.chronicle.log_types import _fetch_log_types_from_api

    # Mock API response for second page
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response_paginated_page2
    mock_chronicle_client.session.get.return_value = mock_response

    # Fetch with page_token
    result = _fetch_log_types_from_api(
        client=mock_chronicle_client,
        page_size=10,
        page_token="page2_token",
    )

    # Should have results from second page
    assert any(
        "WINDOWS" in log_type.get("name")
        for log_type in result
        if log_type.get("name")
    )

    # Verify page_token was passed
    call_args = mock_chronicle_client.session.get.call_args
    assert call_args[1]["params"]["pageToken"] == "page2_token"
    assert call_args[1]["params"]["pageSize"] == 10


def test_load_log_types_cache(mock_chronicle_client, mock_api_response):
    """Test that log types are cached."""
    # Mock the API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_chronicle_client.session.get.return_value = mock_response

    # First call - should make API request
    result1 = load_log_types(client=mock_chronicle_client)
    assert mock_chronicle_client.session.get.call_count == 1

    # Second call - should return cached data
    result2 = load_log_types(client=mock_chronicle_client)

    # Should be the same object (cached)
    assert result1 is result2
    # Should not make another API call
    assert mock_chronicle_client.session.get.call_count == 1


def test_get_all_log_types_from_api(mock_chronicle_client, mock_api_response):
    """Test getting all log types from API."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_chronicle_client.session.get.return_value = mock_response

    result = get_all_log_types(client=mock_chronicle_client)

    assert isinstance(result, list)
    assert len(result) == 3
    # Should return raw dicts
    assert all(isinstance(item, dict) for item in result)


def test_is_valid_log_type_from_api(mock_chronicle_client, mock_api_response):
    """Test validating log type from API."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_chronicle_client.session.get.return_value = mock_response

    assert is_valid_log_type(client=mock_chronicle_client, log_type_id="OKTA")
    # Second call uses cached data
    assert is_valid_log_type(
        client=mock_chronicle_client, log_type_id="AWS_CLOUDTRAIL"
    )
    # Invalid type
    assert not is_valid_log_type(
        client=mock_chronicle_client, log_type_id="INVALID_TYPE"
    )


def test_get_log_type_description_from_api(
    mock_chronicle_client, mock_api_response
):
    """Test getting log type description from API."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_chronicle_client.session.get.return_value = mock_response

    desc = get_log_type_description("OKTA", client=mock_chronicle_client)
    assert desc == "Okta Identity Management"

    # Non-existent log type
    assert (
        get_log_type_description("INVALID_TYPE", client=mock_chronicle_client)
        is None
    )


def test_search_log_types_from_api(mock_chronicle_client, mock_api_response):
    """Test searching log types from API."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response
    mock_chronicle_client.session.get.return_value = mock_response

    results = search_log_types("OKTA", client=mock_chronicle_client)
    assert len(results) >= 1
    # Should return raw dicts
    assert isinstance(results[0], dict)
    # Verify it's the right one
    assert "OKTA" in results[0]["name"]


def test_search_log_types_case_sensitive(mock_chronicle_client):
    """Test case-sensitive search."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "logTypes": [
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/OKTA"
                ),
                "displayName": "Okta",
            }
        ]
    }
    mock_chronicle_client.session.get.return_value = mock_response

    # Case sensitive - should find
    results = search_log_types(
        "OKTA", case_sensitive=True, client=mock_chronicle_client
    )
    assert len(results) >= 1

    # Clear cache between searches to ensure fresh data
    # pylint: disable=protected-access
    log_types._LOG_TYPES_CACHE = None

    # Case sensitive - should not find
    results = search_log_types(
        "okta", case_sensitive=True, client=mock_chronicle_client
    )
    assert len(results) == 0


def test_search_log_types_id_only(mock_chronicle_client):
    """Test searching only in log type IDs."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "logTypes": [
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/OKTA"
                ),
                "displayName": "Okta Identity Management",
            }
        ]
    }
    mock_chronicle_client.session.get.return_value = mock_response

    # Search in ID only
    results = search_log_types(
        "OKTA",
        search_in_description=False,
        client=mock_chronicle_client,
    )
    assert len(results) >= 1

    # Clear cache between searches to ensure fresh data
    # pylint: disable=protected-access
    log_types._LOG_TYPES_CACHE = None

    # Search for description term (should not find)
    results = search_log_types(
        "Identity",
        search_in_description=False,
        client=mock_chronicle_client,
    )
    assert len(results) == 0


def test_api_response_missing_fields(mock_chronicle_client):
    """Test handling API response with missing fields."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "logTypes": [
            {
                # Missing name field
                "displayName": "Test Log Type",
            },
            {
                "name": (
                    "projects/123/locations/us/instances/456/logTypes/OKTA"
                ),
                # Missing displayName - should still work
            },
        ]
    }
    mock_chronicle_client.session.get.return_value = mock_response

    result = load_log_types(client=mock_chronicle_client)

    # Should handle gracefully - OKTA should be present
    assert any(
        "OKTA" in log_type.get("name")
        for log_type in result
        if log_type.get("name")
    )


def test_classify_logs_success(mock_chronicle_client):
    """Test successful log classification."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [
            {"logType": "OKTA", "score": 0.95},
            {"logType": "ONELOGIN", "score": 0.03},
        ]
    }
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = '{"eventType": "user.session.start"}'
    result = classify_logs(client=mock_chronicle_client, log_data=log_data)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["logType"] == "OKTA"
    assert result[0]["score"] == 0.95
    assert result[1]["logType"] == "ONELOGIN"
    assert result[1]["score"] == 0.03

    mock_chronicle_client.session.post.assert_called_once()
    call_args = mock_chronicle_client.session.post.call_args
    assert "logs:classify" in call_args[0][0]
    assert "logData" in call_args[1]["json"]


def test_classify_logs_empty_predictions(mock_chronicle_client):
    """Test classification with empty predictions."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"predictions": []}
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = "unknown log format"
    result = classify_logs(client=mock_chronicle_client, log_data=log_data)

    assert isinstance(result, list)
    assert len(result) == 0


def test_classify_logs_missing_predictions_key(mock_chronicle_client):
    """Test classification when API response missing predictions key."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = "test log"
    result = classify_logs(client=mock_chronicle_client, log_data=log_data)

    assert isinstance(result, list)
    assert len(result) == 0


def test_classify_logs_empty_log_data(mock_chronicle_client):
    """Test classification with empty log data."""
    with pytest.raises(SecOpsError, match="log data cannot be empty"):
        classify_logs(client=mock_chronicle_client, log_data="")

    mock_chronicle_client.session.post.assert_not_called()


def test_classify_logs_none_log_data(mock_chronicle_client):
    """Test classification with None log data."""
    with pytest.raises(SecOpsError, match="log data cannot be empty"):
        classify_logs(client=mock_chronicle_client, log_data=None)

    mock_chronicle_client.session.post.assert_not_called()


def test_classify_logs_non_string_log_data(mock_chronicle_client):
    """Test classification with non-string log data."""
    with pytest.raises(SecOpsError, match="log data must be a string"):
        classify_logs(client=mock_chronicle_client, log_data=123)

    mock_chronicle_client.session.post.assert_not_called()

    with pytest.raises(SecOpsError, match="log data must be a string"):
        classify_logs(client=mock_chronicle_client, log_data=["log"])

    with pytest.raises(SecOpsError, match="log data must be a string"):
        classify_logs(client=mock_chronicle_client, log_data={"log": "data"})


def test_classify_logs_api_error(mock_chronicle_client):
    """Test classification with API error response."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid request"
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = "test log"
    with pytest.raises(APIError, match="Failed to classify log"):
        classify_logs(client=mock_chronicle_client, log_data=log_data)


def test_classify_logs_special_characters(mock_chronicle_client):
    """Test classification with special characters in log data."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [{"logType": "WINDOWS", "score": 0.88}]
    }
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = "<Event>\n  <System>\n    <EventID>4624</EventID>\n  </System>\n</Event>"
    result = classify_logs(client=mock_chronicle_client, log_data=log_data)

    assert len(result) == 1
    assert result[0]["logType"] == "WINDOWS"


def test_classify_logs_unicode_characters(mock_chronicle_client):
    """Test classification with unicode characters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [{"logType": "CUSTOM", "score": 0.75}]
    }
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = '{"user": "测试用户", "message": "Événement système"}'
    result = classify_logs(client=mock_chronicle_client, log_data=log_data)

    assert len(result) == 1
    assert result[0]["logType"] == "CUSTOM"
    mock_chronicle_client.session.post.assert_called_once()


def test_classify_logs_large_log(mock_chronicle_client):
    """Test classification with large log data."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "predictions": [{"logType": "AWS_CLOUDTRAIL", "score": 0.92}]
    }
    mock_chronicle_client.session.post.return_value = mock_response

    log_data = '{"eventName": "GetObject"}' * 1000
    result = classify_logs(client=mock_chronicle_client, log_data=log_data)

    assert len(result) == 1
    assert result[0]["logType"] == "AWS_CLOUDTRAIL"
