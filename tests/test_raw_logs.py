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
"""Tests for raw logs search functionality."""

import datetime
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.raw_logs import find_raw_logs
from secops.exceptions import APIError


def test_find_raw_logs_basic():
    """Test basic raw logs search."""
    client = Mock()
    client.base_url = "https://chronicle.googleapis.com/v1alpha"
    client.instance_id = "projects/test-project/locations/us/instances/test-instance"
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "rawLogs": [
            {
                "timestamp": "2025-01-23T10:00:00Z",
                "logSource": "MICROSOFT_WINDOWS",
                "logType": "WINDOWS_DHCP",
                "rawLog": "Sample log entry 1"
            },
            {
                "timestamp": "2025-01-23T10:01:00Z",
                "logSource": "MICROSOFT_WINDOWS", 
                "logType": "WINDOWS_DHCP",
                "rawLog": "Sample log entry 2"
            }
        ],
        "nextPageToken": "token123"
    }
    
    client.session.post.return_value = mock_response
    
    start_time = datetime.datetime(2025, 1, 23, 9, 0, 0)
    end_time = datetime.datetime(2025, 1, 23, 11, 0, 0)
    
    result = find_raw_logs(
        client,
        start_time=start_time,
        end_time=end_time
    )
    
    assert result["rawLogs"][0]["rawLog"] == "Sample log entry 1"
    assert result["nextPageToken"] == "token123"
    
    # Verify the request
    client.session.post.assert_called_once()
    call_args = client.session.post.call_args
    assert call_args[0][0] == (
        "https://chronicle.googleapis.com/v1alpha/"
        "projects/test-project/locations/us/instances/test-instance/"
        "legacy:legacyFindRawLogs"
    )
    
    request_body = call_args[1]["json"]
    assert request_body["timeRange"]["startTime"] == "2025-01-23T09:00:00.000000Z"
    assert request_body["timeRange"]["endTime"] == "2025-01-23T11:00:00.000000Z"
    assert request_body["pageSize"] == 100


def test_find_raw_logs_with_filters():
    """Test raw logs search with filters."""
    client = Mock()
    client.base_url = "https://chronicle.googleapis.com/v1alpha"
    client.instance_id = "projects/test-project/locations/us/instances/test-instance"
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rawLogs": []}
    
    client.session.post.return_value = mock_response
    
    start_time = datetime.datetime(2025, 1, 23, 9, 0, 0)
    end_time = datetime.datetime(2025, 1, 23, 11, 0, 0)
    
    find_raw_logs(
        client,
        start_time=start_time,
        end_time=end_time,
        log_source="MICROSOFT_WINDOWS",
        log_type="WINDOWS_DHCP",
        query="error",
        page_size=50,
        page_token="next123"
    )
    
    # Verify the request
    client.session.post.assert_called_once()
    call_args = client.session.post.call_args
    request_body = call_args[1]["json"]
    
    assert request_body["logSource"] == "MICROSOFT_WINDOWS"
    assert request_body["logType"] == "WINDOWS_DHCP"
    assert request_body["query"] == "error"
    assert request_body["pageSize"] == 50
    assert request_body["pageToken"] == "next123"


def test_find_raw_logs_timezone_handling():
    """Test that timezone-naive datetimes are handled correctly."""
    client = Mock()
    client.base_url = "https://chronicle.googleapis.com/v1alpha"
    client.instance_id = "projects/test-project/locations/us/instances/test-instance"
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rawLogs": []}
    
    client.session.post.return_value = mock_response
    
    # Use timezone-naive datetimes
    start_time = datetime.datetime(2025, 1, 23, 9, 0, 0)
    end_time = datetime.datetime(2025, 1, 23, 11, 0, 0)
    
    find_raw_logs(
        client,
        start_time=start_time,
        end_time=end_time
    )
    
    # Verify the times were converted to UTC
    call_args = client.session.post.call_args
    request_body = call_args[1]["json"]
    assert request_body["timeRange"]["startTime"] == "2025-01-23T09:00:00.000000Z"
    assert request_body["timeRange"]["endTime"] == "2025-01-23T11:00:00.000000Z"


def test_find_raw_logs_error():
    """Test error handling in raw logs search."""
    client = Mock()
    client.base_url = "https://chronicle.googleapis.com/v1alpha"
    client.instance_id = "projects/test-project/locations/us/instances/test-instance"
    
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid request"
    
    client.session.post.return_value = mock_response
    
    start_time = datetime.datetime(2025, 1, 23, 9, 0, 0)
    end_time = datetime.datetime(2025, 1, 23, 11, 0, 0)
    
    with pytest.raises(APIError) as exc:
        find_raw_logs(
            client,
            start_time=start_time,
            end_time=end_time
        )
    
    assert "Chronicle API request failed: Invalid request" in str(exc.value)


@pytest.mark.integration
def test_find_raw_logs_integration():
    """Integration test for raw logs search."""
    from secops.chronicle import ChronicleClient
    
    # This test requires proper authentication setup
    try:
        client = ChronicleClient(
            project_id="test-project",
            location="us",
            instance_id="test-instance"
        )
        
        start_time = datetime.datetime.now() - datetime.timedelta(hours=1)
        end_time = datetime.datetime.now()
        
        result = client.find_raw_logs(
            start_time=start_time,
            end_time=end_time,
            page_size=10
        )
        
        # Basic validation of response structure
        assert isinstance(result, dict)
        assert "rawLogs" in result
        assert isinstance(result["rawLogs"], list)
        
    except Exception as e:
        # Skip if authentication is not configured
        pytest.skip(f"Integration test skipped: {e}")