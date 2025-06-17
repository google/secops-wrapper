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
"""Tests for Chronicle Data Export API functionality."""
from datetime import datetime, timezone
import pytest
from unittest.mock import Mock, patch

from secops.chronicle.client import ChronicleClient
from secops.chronicle.data_export import AvailableLogType
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    return ChronicleClient(customer_id="test-customer", project_id="test-project")


def test_get_data_export(chronicle_client):
    """Test retrieving a data export."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "start_time": "2024-01-01T00:00:00.000Z",
        "end_time": "2024-01-02T00:00:00.000Z",
        "gcs_bucket": "projects/test-project/buckets/my-bucket",
        "data_export_status": {"stage": "FINISHED_SUCCESS", "progress_percentage": 100},
    }

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        result = chronicle_client.get_data_export("export123")

        assert result["name"].endswith("/dataExports/export123")
        assert result["data_export_status"]["stage"] == "FINISHED_SUCCESS"
        assert result["data_export_status"]["progress_percentage"] == 100


def test_get_data_export_error(chronicle_client):
    """Test error handling when retrieving a data export."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Data export not found"

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        with pytest.raises(APIError, match="Failed to get data export"):
            chronicle_client.get_data_export("nonexistent-export")


def test_create_data_export(chronicle_client):
    """Test creating a data export."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "start_time": "2024-01-01T00:00:00.000Z",
        "end_time": "2024-01-02T00:00:00.000Z",
        "gcs_bucket": "projects/test-project/buckets/my-bucket",
        "log_type": "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS",
        "data_export_status": {"stage": "IN_QUEUE"},
    }

    with patch.object(chronicle_client.session, "post", return_value=mock_response):
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        result = chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS",
        )

        assert result["name"].endswith("/dataExports/export123")
        assert result["log_type"].endswith("/logTypes/WINDOWS")
        assert result["data_export_status"]["stage"] == "IN_QUEUE"


def test_create_data_export_validation(chronicle_client):
    """Test validation when creating a data export."""
    start_time = datetime(2024, 1, 2, tzinfo=timezone.utc)
    end_time = datetime(2024, 1, 1, tzinfo=timezone.utc)  # End time before start time

    with pytest.raises(ValueError, match="End time must be after start time"):
        chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS",
        )

    # Test missing log type and export_all_logs
    start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

    with pytest.raises(
        ValueError,
        match="Either log_type must be specified or export_all_logs must be True",
    ):
        chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
        )

    # Test both log_type and export_all_logs specified
    with pytest.raises(
        ValueError, match="Cannot specify both log_type and export_all_logs=True"
    ):
        chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS",
            export_all_logs=True,
        )

    # Test invalid GCS bucket format
    with pytest.raises(ValueError, match="GCS bucket must be in format"):
        chronicle_client.create_data_export(
            gcs_bucket="my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS",
        )


def test_create_data_export_with_all_logs(chronicle_client):
    """Test creating a data export with all logs."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "start_time": "2024-01-01T00:00:00.000Z",
        "end_time": "2024-01-02T00:00:00.000Z",
        "gcs_bucket": "projects/test-project/buckets/my-bucket",
        "export_all_logs": True,
        "data_export_status": {"stage": "IN_QUEUE"},
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        result = chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            export_all_logs=True,
        )

        assert result["export_all_logs"] is True

        # Check that the request payload included export_all_logs
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["export_all_logs"] is True
        assert "log_type" not in kwargs["json"]


def test_cancel_data_export(chronicle_client):
    """Test cancelling a data export."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "data_export_status": {"stage": "CANCELLED"},
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = chronicle_client.cancel_data_export("export123")

        assert result["data_export_status"]["stage"] == "CANCELLED"

        # Check that the request was sent to the correct URL
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0].endswith("/dataExports/export123:cancel")


def test_cancel_data_export_error(chronicle_client):
    """Test error handling when cancelling a data export."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Data export not found"

    with patch.object(chronicle_client.session, "post", return_value=mock_response):
        with pytest.raises(APIError, match="Failed to cancel data export"):
            chronicle_client.cancel_data_export("nonexistent-export")


def test_fetch_available_log_types(chronicle_client):
    """Test fetching available log types for export."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "available_log_types": [
            {
                "log_type": "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS",
                "display_name": "Windows Event Logs",
                "start_time": "2024-01-01T00:00:00.000Z",
                "end_time": "2024-01-02T00:00:00.000Z",
            },
            {
                "log_type": "projects/test-project/locations/us/instances/test-customer/logTypes/AZURE_AD",
                "display_name": "Azure Active Directory",
                "start_time": "2024-01-01T00:00:00.000Z",
                "end_time": "2024-01-02T00:00:00.000Z",
            },
        ],
        "next_page_token": "token123",
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        result = chronicle_client.fetch_available_log_types(
            start_time=start_time, end_time=end_time, page_size=100
        )

        assert len(result["available_log_types"]) == 2
        assert isinstance(result["available_log_types"][0], AvailableLogType)
        assert result["available_log_types"][0].log_type.endswith("/logTypes/WINDOWS")
        assert result["available_log_types"][0].display_name == "Windows Event Logs"
        assert result["available_log_types"][0].start_time.day == 1
        assert result["available_log_types"][0].end_time.day == 2
        assert result["next_page_token"] == "token123"

        # Check that the request payload included page_size
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["page_size"] == 100


def test_fetch_available_log_types_validation(chronicle_client):
    """Test validation when fetching available log types."""
    start_time = datetime(2024, 1, 2, tzinfo=timezone.utc)
    end_time = datetime(2024, 1, 1, tzinfo=timezone.utc)  # End time before start time

    with pytest.raises(ValueError, match="End time must be after start time"):
        chronicle_client.fetch_available_log_types(
            start_time=start_time, end_time=end_time
        )


def test_fetch_available_log_types_error(chronicle_client):
    """Test error handling when fetching available log types."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid time range"

    with patch.object(chronicle_client.session, "post", return_value=mock_response):
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        with pytest.raises(APIError, match="Failed to fetch available log types"):
            chronicle_client.fetch_available_log_types(
                start_time=start_time, end_time=end_time
            )
