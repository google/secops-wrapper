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
from secops.chronicle.data_export import (
    AvailableLogType,
    update_data_export,
    list_data_export
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

    with patch.object(chronicle_client.session, "request", return_value=mock_response):
        result = chronicle_client.get_data_export("export123")

        assert result["name"].endswith("/dataExports/export123")
        assert result["data_export_status"]["stage"] == "FINISHED_SUCCESS"
        assert result["data_export_status"]["progress_percentage"] == 100


def test_get_data_export_error(chronicle_client):
    """Test error handling when retrieving a data export."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Data export not found"

    with patch.object(chronicle_client.session, "request", return_value=mock_response):
        with pytest.raises(APIError, match="Failed to get data export"):
            chronicle_client.get_data_export("nonexistent-export")


def test_create_data_export_with_log_type(chronicle_client):
    """Test creating a data export with a single log type (string parameter)."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "startTime": "2024-01-01T00:00:00.000Z",
        "endTime": "2024-01-02T00:00:00.000Z",
        "gcsBucket": "projects/test-project/buckets/my-bucket",
        "includeLogTypes": [
            "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS"
        ],
        "dataExportStatus": {"stage": "IN_QUEUE"},
    }

    with patch.object(chronicle_client.session, "request", return_value=mock_response) as mock_post:
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        # Test with legacy log_type parameter
        result = chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS",
        )

        assert result["name"].endswith("/dataExports/export123")
        assert len(result["includeLogTypes"]) == 1
        assert result["includeLogTypes"][0].endswith("/logTypes/WINDOWS")
        assert result["dataExportStatus"]["stage"] == "IN_QUEUE"
        
        # Check that the API was called correctly
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert "includeLogTypes" in kwargs["json"]
        assert len(kwargs["json"]["includeLogTypes"]) == 1


def test_create_data_export_with_log_types(chronicle_client):
    """Test creating a data export with multiple log types (list parameter)."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "startTime": "2024-01-01T00:00:00.000Z",
        "endTime": "2024-01-02T00:00:00.000Z",
        "gcsBucket": "projects/test-project/buckets/my-bucket",
        "includeLogTypes": [
            "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS",
            "projects/test-project/locations/us/instances/test-customer/logTypes/LINUX"
        ],
        "dataExportStatus": {"stage": "IN_QUEUE"},
    }

    with patch.object(chronicle_client.session, "request", return_value=mock_response) as mock_post:
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        # Test with new log_types parameter
        result = chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_types=["WINDOWS", "LINUX"],
        )

        assert result["name"].endswith("/dataExports/export123")
        assert len(result["includeLogTypes"]) == 2
        assert result["dataExportStatus"]["stage"] == "IN_QUEUE"
        
        # Check that the API was called correctly
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert "includeLogTypes" in kwargs["json"]
        assert len(kwargs["json"]["includeLogTypes"]) == 2


def test_create_data_export_validation(chronicle_client):
    """Test validation when creating a data export."""
    start_time = datetime(2024, 1, 2, tzinfo=timezone.utc)
    end_time = datetime(2024, 1, 1, tzinfo=timezone.utc)  # End time before start time

    with pytest.raises(ValueError, match="End time must be after start time"):
        chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_types=["WINDOWS"],
        )

    # Test missing log types and export_all_logs
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

    # Test both log_types and export_all_logs specified
    with pytest.raises(
        ValueError, match="Cannot specify both log_type and export_all_logs=True"
    ):
        chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_types=["WINDOWS"],
            export_all_logs=True,
        )
        
    # Test both legacy log_type and new log_types specified together
    with pytest.raises(
        ValueError, match="Use either log_type or log_types, not both"
    ):
        chronicle_client.create_data_export(
            gcs_bucket="projects/test-project/buckets/my-bucket",
            start_time=start_time,
            end_time=end_time,
            log_type="WINDOWS",
            log_types=["LINUX"],
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
        chronicle_client.session, "request", return_value=mock_response
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
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["includeLogTypes"] == []


def test_cancel_data_export(chronicle_client):
    """Test cancelling a data export."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "data_export_status": {"stage": "CANCELLED"},
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_post:
        result = chronicle_client.cancel_data_export("export123")

        assert result["data_export_status"]["stage"] == "CANCELLED"

        # Check that the request was sent to the correct URL
        mock_post.assert_called_once()
        assert mock_post.call_args[1]["url"].endswith("/dataExports/export123:cancel")


def test_cancel_data_export_error(chronicle_client):
    """Test error handling when cancelling a data export."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Data export not found"

    with patch.object(chronicle_client.session, "request", return_value=mock_response):
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
        chronicle_client.session, "request", return_value=mock_response
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
        assert kwargs["json"]["pageSize"] == 100


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

    with patch.object(chronicle_client.session, "request", return_value=mock_response):
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        with pytest.raises(APIError, match="Failed to fetch available log types"):
            chronicle_client.fetch_available_log_types(
                start_time=start_time, end_time=end_time
            )


def test_update_data_export_success(chronicle_client):
    """Test successful update of a data export."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "startTime": "2024-01-02T00:00:00.000Z",
        "endTime": "2024-01-03T00:00:00.000Z",
        "gcsBucket": "projects/test-project/buckets/updated-bucket",
        "includeLogTypes": [
            "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS",
            "projects/test-project/locations/us/instances/test-customer/logTypes/LINUX"
        ],
        "dataExportStatus": {"stage": "IN_QUEUE"},
    }

    # Act
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_patch:
        start_time = datetime(2024, 1, 2, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 3, tzinfo=timezone.utc)
        new_log_types = [
            "projects/test-project/locations/us/instances/test-customer/logTypes/WINDOWS",
            "projects/test-project/locations/us/instances/test-customer/logTypes/LINUX"
        ]

        result = update_data_export(
            client=chronicle_client,
            data_export_id="export123",
            start_time=start_time,
            end_time=end_time,
            gcs_bucket="projects/test-project/buckets/updated-bucket",
            log_types=new_log_types
        )

    # Assert
    assert result["name"].endswith("/dataExports/export123")
    assert result["startTime"] == "2024-01-02T00:00:00.000Z"
    assert result["endTime"] == "2024-01-03T00:00:00.000Z"
    assert result["gcsBucket"] == "projects/test-project/buckets/updated-bucket"
    assert len(result["includeLogTypes"]) == 2
    
    # Check request payload and parameters
    mock_patch.assert_called_once()
    _, kwargs = mock_patch.call_args
    assert "update_mask" in kwargs["params"]
    assert "startTime" in kwargs["params"]["update_mask"]
    assert "endTime" in kwargs["params"]["update_mask"]
    assert "gcsBucket" in kwargs["params"]["update_mask"]
    assert "includeLogTypes" in kwargs["params"]["update_mask"]


def test_update_data_export_partial_update(chronicle_client):
    """Test updating only some fields of a data export."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export123",
        "gcsBucket": "projects/test-project/buckets/updated-bucket",
        "dataExportStatus": {"stage": "IN_QUEUE"},
    }

    # Act
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_patch:
        result = update_data_export(
            client=chronicle_client,
            data_export_id="export123",
            gcs_bucket="projects/test-project/buckets/updated-bucket"
        )

    # Assert
    assert result["name"].endswith("/dataExports/export123")
    assert result["gcsBucket"] == "projects/test-project/buckets/updated-bucket"
    
    # Check request payload and parameters
    mock_patch.assert_called_once()
    _, kwargs = mock_patch.call_args
    assert "update_mask" in kwargs["params"]
    assert kwargs["params"]["update_mask"] == "gcsBucket"
    assert "gcsBucket" in kwargs["json"]
    assert "startTime" not in kwargs["json"]
    assert "endTime" not in kwargs["json"]
    assert "includeLogTypes" not in kwargs["json"]


def test_update_data_export_validation_error(chronicle_client):
    """Test validation error when updating a data export with invalid GCS bucket."""
    # Arrange
    with pytest.raises(ValueError, match="GCS bucket must be in format"):
        update_data_export(
            client=chronicle_client,
            data_export_id="export123",
            gcs_bucket="invalid-bucket-format"
        )


def test_update_data_export_no_fields_error(chronicle_client):
    """Test error when no fields are provided for update."""
    # Arrange
    with pytest.raises(ValueError, match="At least one field to update must be provided"):
        update_data_export(
            client=chronicle_client,
            data_export_id="export123"
        )


def test_update_data_export_api_error(chronicle_client):
    """Test API error when updating a data export."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid data export ID"

    # Act
    with patch.object(chronicle_client.session, "request", return_value=mock_response):
        # Assert
        with pytest.raises(APIError, match="Failed to update data export"):
            update_data_export(
                client=chronicle_client,
                data_export_id="invalid-id",
                gcs_bucket="projects/test-project/buckets/my-bucket"
            )


def test_list_data_export_success(chronicle_client):
    """Test successful listing of data exports."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "dataExports": [
            {
                "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export1",
                "dataExportStatus": {"stage": "FINISHED_SUCCESS"},
            },
            {
                "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export2",
                "dataExportStatus": {"stage": "IN_QUEUE"},
            }
        ],
        "nextPageToken": "next-page"
    }

    # Act
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_get:
        result = list_data_export(
            client=chronicle_client,
            filters="status=IN_QUEUE",
            page_size=10,
            page_token="current-page"
        )

    # Assert
    assert len(result["dataExports"]) == 2
    assert result["nextPageToken"] == "next-page"
    
    # Check request parameters
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["filter"] == "status=IN_QUEUE"
    assert kwargs["params"]["pageSize"] == 10
    assert kwargs["params"]["pageToken"] == "current-page"


def test_list_data_export_default_params(chronicle_client):
    """Test listing data exports with default parameters."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "dataExports": [
            {
                "name": "projects/test-project/locations/us/instances/test-customer/dataExports/export1",
                "dataExportStatus": {"stage": "FINISHED_SUCCESS"},
            }
        ]
    }

    # Act
    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_get:
        result = list_data_export(client=chronicle_client)

    # Assert
    assert len(result["dataExports"]) == 1
    
    # Check default parameters
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["pageSize"] == 1000 # 1000 page size for auto pagination
    assert "pageToken" not in kwargs["params"]
    assert "filter" not in kwargs["params"]


def test_list_data_export_error(chronicle_client):
    """Test error when listing data exports."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid filter"

    # Act
    with patch.object(chronicle_client.session, "request", return_value=mock_response):
        # Assert
        with pytest.raises(APIError, match="API request failed:"):
            list_data_export(
                client=chronicle_client,
                filters="invalid-filter"
            )
