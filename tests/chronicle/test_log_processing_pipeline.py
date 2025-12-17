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
"""Tests for Chronicle log processing pipeline functions."""

import pytest
from unittest.mock import Mock, patch

from secops.chronicle.client import ChronicleClient
from secops.chronicle.log_processing_pipelines import (
    list_log_processing_pipelines,
    get_log_processing_pipeline,
    create_log_processing_pipeline,
    update_log_processing_pipeline,
    delete_log_processing_pipeline,
    associate_streams,
    dissociate_streams,
    fetch_associated_pipeline,
    fetch_sample_logs_by_streams,
    test_pipeline as pipeline_test_function,
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
    """Create a mock API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/logProcessingPipelines/pipeline_12345",
        "displayName": "Test Pipeline",
        "description": "Test pipeline description",
        "processors": [{"filterProcessor": {"include": {}}}],
    }
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    return mock


def test_list_log_processing_pipelines(chronicle_client, mock_response):
    """Test list_log_processing_pipelines function."""
    mock_response.json.return_value = {
        "logProcessingPipelines": [
            {"name": "pipeline1"},
            {"name": "pipeline2"},
        ]
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_log_processing_pipelines(chronicle_client)

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines",
            params={},
        )
        assert result == mock_response.json.return_value


def test_list_log_processing_pipelines_with_params(
    chronicle_client, mock_response
):
    """Test list_log_processing_pipelines with pagination and filter."""
    mock_response.json.return_value = {
        "logProcessingPipelines": [{"name": "pipeline1"}],
        "nextPageToken": "token123",
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_log_processing_pipelines(
            chronicle_client,
            page_size=50,
            page_token="prev_token",
            filter_expr='displayName="Test"',
        )

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines",
            params={
                "pageSize": 50,
                "pageToken": "prev_token",
                "filter": 'displayName="Test"',
            },
        )
        assert result == mock_response.json.return_value


def test_list_log_processing_pipelines_error(
    chronicle_client, mock_error_response
):
    """Test list_log_processing_pipelines with error response."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            list_log_processing_pipelines(chronicle_client)

        assert "Failed to list log processing pipelines" in str(exc_info.value)


def test_get_log_processing_pipeline(chronicle_client, mock_response):
    """Test get_log_processing_pipeline function."""
    pipeline_id = "pipeline_12345"

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = get_log_processing_pipeline(chronicle_client, pipeline_id)

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}"
        )
        assert result == mock_response.json.return_value


def test_get_log_processing_pipeline_error(
    chronicle_client, mock_error_response
):
    """Test get_log_processing_pipeline with error response."""
    pipeline_id = "pipeline_12345"

    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            get_log_processing_pipeline(chronicle_client, pipeline_id)

        assert "Failed to get log processing pipeline" in str(exc_info.value)


def test_create_log_processing_pipeline(chronicle_client, mock_response):
    """Test create_log_processing_pipeline function."""
    pipeline_config = {
        "displayName": "Test Pipeline",
        "description": "Test description",
        "processors": [{"filterProcessor": {"include": {}}}],
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = create_log_processing_pipeline(
            chronicle_client, pipeline_config
        )

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines",
            json=pipeline_config,
            params={},
        )
        assert result == mock_response.json.return_value


def test_create_log_processing_pipeline_with_id(
    chronicle_client, mock_response
):
    """Test create_log_processing_pipeline with custom pipeline ID."""
    pipeline_config = {
        "displayName": "Test Pipeline",
        "processors": [{"filterProcessor": {"include": {}}}],
    }
    pipeline_id = "custom_pipeline_id"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = create_log_processing_pipeline(
            chronicle_client, pipeline_config, pipeline_id=pipeline_id
        )

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines",
            json=pipeline_config,
            params={"logProcessingPipelineId": pipeline_id},
        )
        assert result == mock_response.json.return_value


def test_create_log_processing_pipeline_error(
    chronicle_client, mock_error_response
):
    """Test create_log_processing_pipeline with error response."""
    pipeline_config = {"displayName": "Test Pipeline"}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            create_log_processing_pipeline(chronicle_client, pipeline_config)

        assert "Failed to create log processing pipeline" in str(exc_info.value)


def test_update_log_processing_pipeline(chronicle_client, mock_response):
    """Test update_log_processing_pipeline function."""
    pipeline_id = "pipeline_12345"
    pipeline_config = {
        "name": "projects/test-project/locations/us/instances/test-customer/logProcessingPipelines/pipeline_12345",
        "displayName": "Updated Pipeline",
        "processors": [{"filterProcessor": {"include": {}}}],
    }

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = update_log_processing_pipeline(
            chronicle_client, pipeline_id, pipeline_config
        )

        mock_patch.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}",
            json=pipeline_config,
            params={},
        )
        assert result == mock_response.json.return_value


def test_update_log_processing_pipeline_with_update_mask(
    chronicle_client, mock_response
):
    """Test update_log_processing_pipeline with update mask."""
    pipeline_id = "pipeline_12345"
    pipeline_config = {
        "name": "projects/test-project/locations/us/instances/test-customer/logProcessingPipelines/pipeline_12345",
        "displayName": "Updated Pipeline",
    }
    update_mask = "displayName,description"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = update_log_processing_pipeline(
            chronicle_client,
            pipeline_id,
            pipeline_config,
            update_mask=update_mask,
        )

        mock_patch.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}",
            json=pipeline_config,
            params={"updateMask": update_mask},
        )
        assert result == mock_response.json.return_value


def test_update_log_processing_pipeline_with_full_name(
    chronicle_client, mock_response
):
    """Test update_log_processing_pipeline with full resource name."""
    full_name = "projects/test-project/locations/us/instances/test-customer/logProcessingPipelines/pipeline_12345"
    pipeline_config = {
        "name": full_name,
        "displayName": "Updated Pipeline",
    }

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = update_log_processing_pipeline(
            chronicle_client, full_name, pipeline_config
        )

        mock_patch.assert_called_once_with(
            f"{chronicle_client.base_url}/{full_name}",
            json=pipeline_config,
            params={},
        )
        assert result == mock_response.json.return_value


def test_update_log_processing_pipeline_error(
    chronicle_client, mock_error_response
):
    """Test update_log_processing_pipeline with error response."""
    pipeline_id = "pipeline_12345"
    pipeline_config = {"displayName": "Updated Pipeline"}

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            update_log_processing_pipeline(
                chronicle_client, pipeline_id, pipeline_config
            )

        assert "Failed to patch log processing pipeline" in str(exc_info.value)


def test_delete_log_processing_pipeline(chronicle_client, mock_response):
    """Test delete_log_processing_pipeline function."""
    pipeline_id = "pipeline_12345"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_response
    ) as mock_delete:
        result = delete_log_processing_pipeline(chronicle_client, pipeline_id)

        mock_delete.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}",
            params={},
        )
        assert result == {}


def test_delete_log_processing_pipeline_with_etag(
    chronicle_client, mock_response
):
    """Test delete_log_processing_pipeline with etag."""
    pipeline_id = "pipeline_12345"
    etag = "etag_value_123"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_response
    ) as mock_delete:
        result = delete_log_processing_pipeline(
            chronicle_client, pipeline_id, etag=etag
        )

        mock_delete.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}",
            params={"etag": etag},
        )
        assert result == {}


def test_delete_log_processing_pipeline_error(
    chronicle_client, mock_error_response
):
    """Test delete_log_processing_pipeline with error response."""
    pipeline_id = "pipeline_12345"

    with patch.object(
        chronicle_client.session, "delete", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            delete_log_processing_pipeline(chronicle_client, pipeline_id)

        assert "Failed to delete log processing pipeline" in str(exc_info.value)


def test_associate_streams(chronicle_client, mock_response):
    """Test associate_streams function."""
    pipeline_id = "pipeline_12345"
    streams = [{"logType": "WINEVTLOG"}, {"feedId": "feed_123"}]
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = associate_streams(chronicle_client, pipeline_id, streams)

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}:associateStreams",
            json={"streams": streams},
        )
        assert result == {}


def test_associate_streams_error(chronicle_client, mock_error_response):
    """Test associate_streams with error response."""
    pipeline_id = "pipeline_12345"
    streams = [{"logType": "WINEVTLOG"}]

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            associate_streams(chronicle_client, pipeline_id, streams)

        assert "Failed to associate streams" in str(exc_info.value)


def test_associate_streams_empty_list(chronicle_client, mock_response):
    """Test associate_streams with empty streams list."""
    pipeline_id = "pipeline_12345"
    streams = []
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = associate_streams(chronicle_client, pipeline_id, streams)

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}:associateStreams",
            json={"streams": []},
        )
        assert result == {}


def test_dissociate_streams(chronicle_client, mock_response):
    """Test dissociate_streams function."""
    pipeline_id = "pipeline_12345"
    streams = [{"logType": "WINEVTLOG"}, {"feedId": "feed_123"}]
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = dissociate_streams(chronicle_client, pipeline_id, streams)

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines/{pipeline_id}:dissociateStreams",
            json={"streams": streams},
        )
        assert result == {}


def test_dissociate_streams_error(chronicle_client, mock_error_response):
    """Test dissociate_streams with error response."""
    pipeline_id = "pipeline_12345"
    streams = [{"logType": "WINEVTLOG"}]

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            dissociate_streams(chronicle_client, pipeline_id, streams)

        assert "Failed to dissociate streams" in str(exc_info.value)


def test_fetch_associated_pipeline_with_log_type(
    chronicle_client, mock_response
):
    """Test fetch_associated_pipeline with logType."""
    stream = {"logType": "WINEVTLOG"}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = fetch_associated_pipeline(chronicle_client, stream)

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:fetchAssociatedPipeline",
            params={"stream.logType": "WINEVTLOG"},
        )
        assert result == mock_response.json.return_value


def test_fetch_associated_pipeline_with_feed_id(
    chronicle_client, mock_response
):
    """Test fetch_associated_pipeline with feedId."""
    stream = {"feedId": "feed_123"}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = fetch_associated_pipeline(chronicle_client, stream)

        mock_get.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:fetchAssociatedPipeline",
            params={"stream.feedId": "feed_123"},
        )
        assert result == mock_response.json.return_value


def test_fetch_associated_pipeline_with_multiple_fields(
    chronicle_client, mock_response
):
    """Test fetch_associated_pipeline with multiple stream fields."""
    stream = {"logType": "WINEVTLOG", "namespace": "test"}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = fetch_associated_pipeline(chronicle_client, stream)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "stream.logType" in call_args[1]["params"]
        assert "stream.namespace" in call_args[1]["params"]
        assert result == mock_response.json.return_value


def test_fetch_associated_pipeline_error(chronicle_client, mock_error_response):
    """Test fetch_associated_pipeline with error response."""
    stream = {"logType": "WINEVTLOG"}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            fetch_associated_pipeline(chronicle_client, stream)

        assert "Failed to fetch associated pipeline" in str(exc_info.value)


def test_fetch_sample_logs_by_streams(chronicle_client, mock_response):
    """Test fetch_sample_logs_by_streams function."""
    streams = [{"logType": "WINEVTLOG"}, {"feedId": "feed_123"}]
    mock_response.json.return_value = {
        "logs": [{"data": "log1"}, {"data": "log2"}]
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = fetch_sample_logs_by_streams(chronicle_client, streams)

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:fetchSampleLogsByStreams",
            json={"streams": streams},
        )
        assert result == mock_response.json.return_value


def test_fetch_sample_logs_by_streams_with_count(
    chronicle_client, mock_response
):
    """Test fetch_sample_logs_by_streams with sample count."""
    streams = [{"logType": "WINEVTLOG"}]
    sample_logs_count = 50
    mock_response.json.return_value = {"logs": []}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = fetch_sample_logs_by_streams(
            chronicle_client, streams, sample_logs_count=sample_logs_count
        )

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:fetchSampleLogsByStreams",
            json={"streams": streams, "sampleLogsCount": sample_logs_count},
        )
        assert result == mock_response.json.return_value


def test_fetch_sample_logs_by_streams_error(
    chronicle_client, mock_error_response
):
    """Test fetch_sample_logs_by_streams with error response."""
    streams = [{"logType": "WINEVTLOG"}]

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            fetch_sample_logs_by_streams(chronicle_client, streams)

        assert "Failed to fetch sample logs by streams" in str(exc_info.value)


def test_fetch_sample_logs_by_streams_empty_streams(
    chronicle_client, mock_response
):
    """Test fetch_sample_logs_by_streams with empty streams list."""
    streams = []
    mock_response.json.return_value = {"logs": []}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = fetch_sample_logs_by_streams(chronicle_client, streams)

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:fetchSampleLogsByStreams",
            json={"streams": []},
        )
        assert result == mock_response.json.return_value


def test_test_pipeline(chronicle_client, mock_response):
    """Test test_pipeline function."""
    pipeline_config = {
        "displayName": "Test Pipeline",
        "processors": [{"filterProcessor": {"include": {}}}],
    }
    input_logs = [
        {"data": "bG9nMQ==", "logEntryTime": "2024-01-01T00:00:00Z"},
        {"data": "bG9nMg==", "logEntryTime": "2024-01-01T00:00:01Z"},
    ]
    mock_response.json.return_value = {"logs": input_logs}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = pipeline_test_function(
            chronicle_client, pipeline_config, input_logs
        )

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:testPipeline",
            json={
                "logProcessingPipeline": pipeline_config,
                "inputLogs": input_logs,
            },
        )
        assert result == mock_response.json.return_value


def test_test_pipeline_error(chronicle_client, mock_error_response):
    """Test test_pipeline with error response."""
    pipeline_config = {"displayName": "Test Pipeline"}
    input_logs = [{"data": "bG9nMQ=="}]

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            pipeline_test_function(
                chronicle_client, pipeline_config, input_logs
            )

        assert "Failed to test pipeline" in str(exc_info.value)


def test_test_pipeline_empty_logs(chronicle_client, mock_response):
    """Test test_pipeline with empty input logs."""
    pipeline_config = {
        "displayName": "Test Pipeline",
        "processors": [{"filterProcessor": {"include": {}}}],
    }
    input_logs = []
    mock_response.json.return_value = {"logs": []}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = pipeline_test_function(
            chronicle_client, pipeline_config, input_logs
        )

        mock_post.assert_called_once_with(
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/logProcessingPipelines:testPipeline",
            json={
                "logProcessingPipeline": pipeline_config,
                "inputLogs": [],
            },
        )
        assert result == mock_response.json.return_value


def test_test_pipeline_with_complex_processors(chronicle_client, mock_response):
    """Test test_pipeline with complex processor configuration."""
    pipeline_config = {
        "displayName": "Complex Pipeline",
        "processors": [
            {
                "filterProcessor": {
                    "include": {
                        "logMatchType": "REGEXP",
                        "logBodies": [".*error.*"],
                    }
                }
            },
            {
                "transformProcessor": {
                    "fields": [{"field": "message", "transformation": "upper"}]
                }
            },
        ],
    }
    input_logs = [{"data": "bG9nMQ==", "logEntryTime": "2024-01-01T00:00:00Z"}]
    mock_response.json.return_value = {"logs": input_logs}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = pipeline_test_function(
            chronicle_client, pipeline_config, input_logs
        )

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["logProcessingPipeline"] == pipeline_config
        assert result == mock_response.json.return_value
