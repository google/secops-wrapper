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
"""Tests for Chronicle rule detection functions."""

import pytest
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.rule_detection import (
    list_detections,
    get_detection,
    search_curated_detections,
    count_all_curated_rule_set_detections,
    count_curated_rule_set_detections,
    search_detection_events,
    search_detection_count_buckets,
    search_rule_results,
    list_errors
)
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    return ChronicleClient(
        customer_id="test-customer",
        project_id="test-project",
        region="us" # Assuming 'us' region for base_url construction
    )


@pytest.fixture
def mock_response():
    """Create a mock API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"detections": [{"id": "de_123"}]} # Example response
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock

# --- Tests for list_detections ---

def test_list_detections(chronicle_client, mock_response):
    """Test list_detections function."""
    rule_id = "ru_123"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = list_detections(chronicle_client, rule_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchDetections",
            params={"rule_id": rule_id}
        )
        assert result == mock_response.json.return_value

def test_list_detections_with_params(chronicle_client, mock_response):
    """Test list_detections function with optional parameters."""
    rule_id = "ru_123"
    alert_state = "ALERTING"
    page_size = 50
    page_token = "token123"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = list_detections(chronicle_client, rule_id, alert_state=alert_state, page_size=page_size, page_token=page_token)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchDetections",
            params={"rule_id": rule_id, "alertState": alert_state, "pageSize": page_size, "pageToken": page_token}
        )
        assert result == mock_response.json.return_value

def test_list_detections_invalid_alert_state(chronicle_client):
    """Test list_detections with invalid alert_state."""
    with pytest.raises(ValueError) as exc_info:
        list_detections(chronicle_client, "ru_123", alert_state="INVALID_STATE")
    assert "alert_state must be one of" in str(exc_info.value)

def test_list_detections_error(chronicle_client, mock_error_response):
    """Test list_detections function with error response."""
    rule_id = "ru_123"
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            list_detections(chronicle_client, rule_id)
        assert "Failed to list detections" in str(exc_info.value)

# --- Tests for get_detection ---

def test_get_detection(chronicle_client, mock_response):
    """Test get_detection function."""
    detection_id = "de_456"
    mock_response.json.return_value = {"id": detection_id, "details": "..."}
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = get_detection(chronicle_client, detection_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacyGetDetection",
            params={"detection_id": detection_id}
        )
        assert result == mock_response.json.return_value

def test_get_detection_error(chronicle_client, mock_error_response):
    """Test get_detection function with error response."""
    detection_id = "de_456"
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            get_detection(chronicle_client, detection_id)
        assert f"Failed to get detection {detection_id}" in str(exc_info.value)

# --- Tests for search_curated_detections ---

def test_search_curated_detections(chronicle_client, mock_response):
    """Test search_curated_detections function."""
    rule_id = "cr_789"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_curated_detections(chronicle_client, rule_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchCuratedDetections",
            params={"rule_id": rule_id}
        )
        assert result == mock_response.json.return_value

def test_search_curated_detections_with_params(chronicle_client, mock_response):
    """Test search_curated_detections with optional parameters."""
    rule_id = "cr_789"
    start_time = "2023-01-01T00:00:00Z"
    end_time = "2023-01-02T00:00:00Z"
    page_size = 10
    page_token = "token456"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_curated_detections(chronicle_client, rule_id, start_time=start_time, end_time=end_time, page_size=page_size, page_token=page_token)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchCuratedDetections",
            params={"rule_id": rule_id, "start_time": start_time, "end_time": end_time, "page_size": page_size, "page_token": page_token}
        )
        assert result == mock_response.json.return_value

def test_search_curated_detections_error(chronicle_client, mock_error_response):
    """Test search_curated_detections function with error response."""
    rule_id = "cr_789"
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            search_curated_detections(chronicle_client, rule_id)
        assert f"Failed to search curated detections for rule {rule_id}" in str(exc_info.value)

# --- Tests for count_all_curated_rule_set_detections ---

def test_count_all_curated_rule_set_detections(chronicle_client, mock_response):
    """Test count_all_curated_rule_set_detections function."""
    mock_response.json.return_value = {"totalCount": 150}
    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = count_all_curated_rule_set_detections(chronicle_client)
        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}:countAllCuratedRuleSetDetections",
            json={}
        )
        assert result == mock_response.json.return_value

def test_count_all_curated_rule_set_detections_with_params(chronicle_client, mock_response):
    """Test count_all_curated_rule_set_detections with optional parameters."""
    start_time = "2023-01-01T00:00:00Z"
    end_time = "2023-01-02T00:00:00Z"
    filter_str = "rule_set = 'rs_123'"
    mock_response.json.return_value = {"totalCount": 50}
    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = count_all_curated_rule_set_detections(chronicle_client, start_time=start_time, end_time=end_time, filter_str=filter_str)
        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}:countAllCuratedRuleSetDetections",
            json={"startTime": start_time, "endTime": end_time, "filter": filter_str}
        )
        assert result == mock_response.json.return_value

def test_count_all_curated_rule_set_detections_error(chronicle_client, mock_error_response):
    """Test count_all_curated_rule_set_detections function with error response."""
    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            count_all_curated_rule_set_detections(chronicle_client)
        assert "Failed to count all curated rule set detections" in str(exc_info.value)

# --- Tests for count_curated_rule_set_detections ---

def test_count_curated_rule_set_detections(chronicle_client, mock_response):
    """Test count_curated_rule_set_detections function."""
    category_id = "cat_abc"
    rule_set_id = "rs_xyz"
    mock_response.json.return_value = {"totalCount": 25}
    expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/curatedRuleSetCategories/{category_id}/curatedRuleSets/{rule_set_id}:countCuratedRuleSetDetections"
    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = count_curated_rule_set_detections(chronicle_client, category_id, rule_set_id)
        mock_post.assert_called_once_with(expected_url, json={})
        assert result == mock_response.json.return_value

def test_count_curated_rule_set_detections_with_params(chronicle_client, mock_response):
    """Test count_curated_rule_set_detections with optional parameters."""
    category_id = "cat_abc"
    rule_set_id = "rs_xyz"
    start_time = "2023-01-01T00:00:00Z"
    end_time = "2023-01-02T00:00:00Z"
    filter_str = "severity = HIGH"
    mock_response.json.return_value = {"totalCount": 10}
    expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/curatedRuleSetCategories/{category_id}/curatedRuleSets/{rule_set_id}:countCuratedRuleSetDetections"
    with patch.object(chronicle_client.session, 'post', return_value=mock_response) as mock_post:
        result = count_curated_rule_set_detections(chronicle_client, category_id, rule_set_id, start_time=start_time, end_time=end_time, filter_str=filter_str)
        mock_post.assert_called_once_with(
            expected_url,
            json={"startTime": start_time, "endTime": end_time, "filter": filter_str}
        )
        assert result == mock_response.json.return_value

def test_count_curated_rule_set_detections_error(chronicle_client, mock_error_response):
    """Test count_curated_rule_set_detections function with error response."""
    category_id = "cat_abc"
    rule_set_id = "rs_xyz"
    expected_url = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/curatedRuleSetCategories/{category_id}/curatedRuleSets/{rule_set_id}:countCuratedRuleSetDetections"
    with patch.object(chronicle_client.session, 'post', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            count_curated_rule_set_detections(chronicle_client, category_id, rule_set_id)
        assert f"Failed to count detections for curated rule set {rule_set_id}" in str(exc_info.value)

# --- Tests for search_detection_events ---

def test_search_detection_events(chronicle_client, mock_response):
    """Test search_detection_events function."""
    detection_id = "de_987"
    mock_response.json.return_value = {"events": [{"udm": {}}]}
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_detection_events(chronicle_client, detection_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchRuleDetectionEvents",
            params={"detection_id": detection_id}
        )
        assert result == mock_response.json.return_value

def test_search_detection_events_with_params(chronicle_client, mock_response):
    """Test search_detection_events with optional parameters."""
    detection_id = "de_987"
    page_size = 20
    page_token = "token789"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_detection_events(chronicle_client, detection_id, page_size=page_size, page_token=page_token)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchRuleDetectionEvents",
            params={"detection_id": detection_id, "page_size": page_size, "page_token": page_token}
        )
        assert result == mock_response.json.return_value

def test_search_detection_events_error(chronicle_client, mock_error_response):
    """Test search_detection_events function with error response."""
    detection_id = "de_987"
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            search_detection_events(chronicle_client, detection_id)
        assert f"Failed to search detection events for {detection_id}" in str(exc_info.value)

# --- Tests for search_detection_count_buckets ---

def test_search_detection_count_buckets(chronicle_client, mock_response):
    """Test search_detection_count_buckets function."""
    rule_id = "ru_abc"
    mock_response.json.return_value = {"buckets": [{"startTime": "...", "count": 5}]}
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_detection_count_buckets(chronicle_client, rule_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchRuleDetectionCountBuckets",
            params={"rule_id": rule_id}
        )
        assert result == mock_response.json.return_value

def test_search_detection_count_buckets_with_params(chronicle_client, mock_response):
    """Test search_detection_count_buckets with optional parameters."""
    rule_id = "ru_abc"
    start_time = "2023-01-01T00:00:00Z"
    end_time = "2023-01-02T00:00:00Z"
    bucket_duration = "3600s"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_detection_count_buckets(chronicle_client, rule_id, start_time=start_time, end_time=end_time, bucket_duration=bucket_duration)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchRuleDetectionCountBuckets",
            params={"rule_id": rule_id, "start_time": start_time, "end_time": end_time, "bucket_duration": bucket_duration}
        )
        assert result == mock_response.json.return_value

def test_search_detection_count_buckets_error(chronicle_client, mock_error_response):
    """Test search_detection_count_buckets function with error response."""
    rule_id = "ru_abc"
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            search_detection_count_buckets(chronicle_client, rule_id)
        assert f"Failed to search detection count buckets for rule {rule_id}" in str(exc_info.value)

# --- Tests for search_rule_results ---

def test_search_rule_results(chronicle_client, mock_response):
    """Test search_rule_results function."""
    rule_id = "ru_def"
    mock_response.json.return_value = {"results": [{"timestamp": "...", "count": 10}]}
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_rule_results(chronicle_client, rule_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchRuleResults",
            params={"rule_id": rule_id}
        )
        assert result == mock_response.json.return_value

def test_search_rule_results_with_params(chronicle_client, mock_response):
    """Test search_rule_results with optional parameters."""
    rule_id = "ru_def"
    start_time = "2023-01-01T00:00:00Z"
    end_time = "2023-01-02T00:00:00Z"
    page_size = 100
    page_token = "tokenabc"
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = search_rule_results(chronicle_client, rule_id, start_time=start_time, end_time=end_time, page_size=page_size, page_token=page_token)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/legacy:legacySearchRuleResults",
            params={"rule_id": rule_id, "start_time": start_time, "end_time": end_time, "page_size": page_size, "page_token": page_token}
        )
        assert result == mock_response.json.return_value

def test_search_rule_results_error(chronicle_client, mock_error_response):
    """Test search_rule_results function with error response."""
    rule_id = "ru_def"
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            search_rule_results(chronicle_client, rule_id)
        assert f"Failed to search rule results for rule {rule_id}" in str(exc_info.value)

# --- Tests for list_errors ---

def test_list_errors(chronicle_client, mock_response):
    """Test list_errors function."""
    rule_id = "ru_xyz"
    mock_response.json.return_value = {"errors": [{"message": "Syntax error"}]}
    expected_filter = f'rule = "{chronicle_client.instance_id}/rules/{rule_id}"'
    with patch.object(chronicle_client.session, 'get', return_value=mock_response) as mock_get:
        result = list_errors(chronicle_client, rule_id)
        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/ruleExecutionErrors",
            params={"filter": expected_filter}
        )
        assert result == mock_response.json.return_value

def test_list_errors_error(chronicle_client, mock_error_response):
    """Test list_errors function with error response."""
    rule_id = "ru_xyz"
    expected_filter = f'rule = "{chronicle_client.instance_id}/rules/{rule_id}"'
    with patch.object(chronicle_client.session, 'get', return_value=mock_error_response):
        with pytest.raises(APIError) as exc_info:
            list_errors(chronicle_client, rule_id)
        assert "Failed to list rule errors" in str(exc_info.value)
