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
"""Tests for Chronicle log ingestion functionality."""
import base64
import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from secops.chronicle.client import ChronicleClient
from secops.chronicle.log_ingest import (
    ingest_log,
    get_or_create_forwarder,
    list_forwarders,
    create_forwarder,
    extract_forwarder_id,
    ingest_udm,
)
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    return ChronicleClient(
        customer_id="test-customer", project_id="test-project", region="us"
    )


@pytest.fixture
def mock_forwarder_response():
    """Create a mock forwarder API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/forwarders/test-forwarder-id",
        "displayName": "Wrapper-SDK-Forwarder",
        "createTime": "2025-01-01T00:00:00.000Z",
        "updateTime": "2025-01-01T00:00:00.000Z",
        "config": {"uploadCompression": False, "metadata": {}},
    }
    return mock


@pytest.fixture
def mock_forwarders_list_response():
    """Create a mock forwarders list API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "forwarders": [
            {
                "name": "projects/test-project/locations/us/instances/test-customer/forwarders/test-forwarder-id",
                "displayName": "Wrapper-SDK-Forwarder",
                "createTime": "2025-01-01T00:00:00.000Z",
                "updateTime": "2025-01-01T00:00:00.000Z",
                "config": {"uploadCompression": False, "metadata": {}},
            }
        ]
    }
    return mock


@pytest.fixture
def mock_ingest_response():
    """Create a mock log ingestion API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "operation": "projects/test-project/locations/us/operations/operation-id"
    }
    return mock


@pytest.fixture
def mock_udm_event():
    """Create a sample UDM event for testing."""
    return {
        "metadata": {
            "event_type": "NETWORK_CONNECTION",
            "product_name": "Test Product",
            "id": "test-event-id",
        },
        "principal": {"ip": "192.168.1.100"},
        "target": {"ip": "10.0.0.1"},
    }


@pytest.fixture
def mock_udm_response():
    """Create a mock UDM ingestion API response."""
    mock = Mock()
    mock.status_code = 200
    mock.text = "{}"  # Empty response according to the API docs
    mock.json.return_value = {}
    return mock


def test_extract_forwarder_id():
    """Test extracting forwarder ID from full resource name."""
    # Test with full resource name
    resource_name = "projects/test-project/locations/us/instances/test-customer/forwarders/test-forwarder-id"
    assert extract_forwarder_id(resource_name) == "test-forwarder-id"

    # Test with just ID
    assert extract_forwarder_id("test-forwarder-id") == "test-forwarder-id"

    # Test with empty string
    with pytest.raises(ValueError):
        extract_forwarder_id("")

    # Test with invalid format
    with pytest.raises(ValueError):
        extract_forwarder_id("/")


def test_create_forwarder(chronicle_client, mock_forwarder_response):
    """Test creating a forwarder."""
    with patch.object(
        chronicle_client.session, "post", return_value=mock_forwarder_response
    ):
        result = create_forwarder(
            client=chronicle_client, display_name="Wrapper-SDK-Forwarder"
        )

        assert (
            result["name"]
            == "projects/test-project/locations/us/instances/test-customer/forwarders/test-forwarder-id"
        )
        assert result["displayName"] == "Wrapper-SDK-Forwarder"


def test_create_forwarder_error(chronicle_client):
    """Test error handling when creating a forwarder."""
    error_response = Mock()
    error_response.status_code = 400
    error_response.text = "Invalid request"

    with patch.object(chronicle_client.session, "post", return_value=error_response):
        with pytest.raises(APIError, match="Failed to create forwarder"):
            create_forwarder(
                client=chronicle_client, display_name="Wrapper-SDK-Forwarder"
            )


def test_list_forwarders(chronicle_client, mock_forwarders_list_response):
    """Test listing forwarders."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ):
        result = list_forwarders(client=chronicle_client)

        assert len(result["forwarders"]) == 1
        assert result["forwarders"][0]["displayName"] == "Wrapper-SDK-Forwarder"


def test_list_forwarders_error(chronicle_client):
    """Test error handling when listing forwarders."""
    error_response = Mock()
    error_response.status_code = 400
    error_response.text = "Invalid request"

    with patch.object(chronicle_client.session, "get", return_value=error_response):
        with pytest.raises(APIError, match="Failed to list forwarders"):
            list_forwarders(client=chronicle_client)


def test_get_or_create_forwarder_existing(
    chronicle_client, mock_forwarders_list_response
):
    """Test getting an existing forwarder."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ):
        result = get_or_create_forwarder(
            client=chronicle_client, display_name="Wrapper-SDK-Forwarder"
        )

        assert result["displayName"] == "Wrapper-SDK-Forwarder"


def test_get_or_create_forwarder_new(
    chronicle_client, mock_forwarders_list_response, mock_forwarder_response
):
    """Test creating a new forwarder when one doesn't exist."""
    # Empty list of forwarders
    empty_response = Mock()
    empty_response.status_code = 200
    empty_response.json.return_value = {"forwarders": []}

    with patch.object(
        chronicle_client.session, "get", return_value=empty_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_forwarder_response
    ):
        result = get_or_create_forwarder(
            client=chronicle_client, display_name="Wrapper-SDK-Forwarder"
        )

        assert result["displayName"] == "Wrapper-SDK-Forwarder"


def test_ingest_log_basic(
    chronicle_client, mock_forwarders_list_response, mock_ingest_response
):
    """Test basic log ingestion functionality."""
    test_log = {"test": "log", "message": "Test message"}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch(
        "secops.chronicle.log_ingest.is_valid_log_type", return_value=True
    ):
        result = ingest_log(
            client=chronicle_client, log_type="OKTA", log_message=json.dumps(test_log)
        )

        assert "operation" in result
        assert (
            result["operation"]
            == "projects/test-project/locations/us/operations/operation-id"
        )


def test_ingest_log_with_timestamps(
    chronicle_client, mock_forwarders_list_response, mock_ingest_response
):
    """Test log ingestion with custom timestamps."""
    test_log = {"test": "log", "message": "Test message"}
    log_entry_time = datetime.now(timezone.utc) - timedelta(hours=1)
    collection_time = datetime.now(timezone.utc)

    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch(
        "secops.chronicle.log_ingest.is_valid_log_type", return_value=True
    ):
        result = ingest_log(
            client=chronicle_client,
            log_type="OKTA",
            log_message=json.dumps(test_log),
            log_entry_time=log_entry_time,
            collection_time=collection_time,
        )

        assert "operation" in result


def test_ingest_log_invalid_timestamps(chronicle_client):
    """Test log ingestion with invalid timestamps (collection before entry)."""
    test_log = {"test": "log", "message": "Test message"}
    log_entry_time = datetime.now(timezone.utc)
    collection_time = datetime.now(timezone.utc) - timedelta(
        hours=1
    )  # Earlier than entry time

    with pytest.raises(
        ValueError, match="Collection time must be same or after log entry time"
    ):
        ingest_log(
            client=chronicle_client,
            log_type="OKTA",
            log_message=json.dumps(test_log),
            log_entry_time=log_entry_time,
            collection_time=collection_time,
        )


def test_ingest_log_invalid_log_type(chronicle_client):
    """Test log ingestion with invalid log type."""
    test_log = {"test": "log", "message": "Test message"}

    with patch("secops.chronicle.log_ingest.is_valid_log_type", return_value=False):
        with pytest.raises(ValueError, match="Invalid log type"):
            ingest_log(
                client=chronicle_client,
                log_type="INVALID_LOG_TYPE",
                log_message=json.dumps(test_log),
            )


def test_ingest_log_force_log_type(
    chronicle_client, mock_forwarders_list_response, mock_ingest_response
):
    """Test log ingestion with forced log type."""
    test_log = {"test": "log", "message": "Test message"}

    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch(
        "secops.chronicle.log_ingest.is_valid_log_type", return_value=False
    ):
        result = ingest_log(
            client=chronicle_client,
            log_type="CUSTOM_LOG_TYPE",
            log_message=json.dumps(test_log),
            force_log_type=True,
        )

        assert "operation" in result


def test_ingest_log_with_custom_forwarder(chronicle_client, mock_ingest_response):
    """Test log ingestion with a custom forwarder ID."""
    test_log = {"test": "log", "message": "Test message"}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch("secops.chronicle.log_ingest.is_valid_log_type", return_value=True):
        result = ingest_log(
            client=chronicle_client,
            log_type="OKTA",
            log_message=json.dumps(test_log),
            forwarder_id="custom-forwarder-id",
        )

        assert "operation" in result


def test_ingest_xml_log(
    chronicle_client, mock_forwarders_list_response, mock_ingest_response
):
    """Test ingesting an XML log."""
    xml_log = """<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
    <System>
        <Provider Name='Microsoft-Windows-Security-Auditing' Guid='{54849625-5478-4994-A5BA-3E3B0328C30D}'/>
        <EventID>4624</EventID>
        <TimeCreated SystemTime='2025-03-23T14:47:00.647937Z'/>
        <Computer>WINSERVER.example.com</Computer>
    </System>
    <EventData>
        <Data Name='TargetUserName'>TestUser</Data>
        <Data Name='LogonType'>3</Data>
    </EventData>
</Event>"""

    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch(
        "secops.chronicle.log_ingest.is_valid_log_type", return_value=True
    ):
        result = ingest_log(
            client=chronicle_client, log_type="WINEVTLOG_XML", log_message=xml_log
        )

        assert "operation" in result
        assert (
            result["operation"]
            == "projects/test-project/locations/us/operations/operation-id"
        )


def test_ingest_udm_single_event(chronicle_client, mock_udm_event, mock_udm_response):
    """Test ingesting a single UDM event."""
    with patch.object(chronicle_client.session, "post", return_value=mock_udm_response):
        result = ingest_udm(client=chronicle_client, udm_events=mock_udm_event)

        # Check that the request was made correctly
        call_args = chronicle_client.session.post.call_args
        assert call_args is not None

        # Verify URL format
        url = call_args[0][0]
        assert (
            "projects/test-project/locations/us/instances/test-customer/events:import"
            in url
        )

        # Verify request payload
        payload = call_args[1]["json"]
        assert "inline_source" in payload
        assert "events" in payload["inline_source"]
        assert len(payload["inline_source"]["events"]) == 1
        assert (
            payload["inline_source"]["events"][0]["udm"]["metadata"]["id"]
            == "test-event-id"
        )

        # Verify the result
        assert isinstance(result, dict)


def test_ingest_udm_multiple_events(
    chronicle_client, mock_udm_event, mock_udm_response
):
    """Test ingesting multiple UDM events."""
    # Create multiple events
    event1 = mock_udm_event

    event2 = {
        "metadata": {
            "event_type": "PROCESS_LAUNCH",
            "product_name": "Test Product",
            "id": "test-event-id-2",
        },
        "principal": {"hostname": "host1", "process": {"command_line": "./test.exe"}},
    }

    events = [event1, event2]

    with patch.object(chronicle_client.session, "post", return_value=mock_udm_response):
        result = ingest_udm(client=chronicle_client, udm_events=events)

        # Check that the request was made correctly
        call_args = chronicle_client.session.post.call_args
        assert call_args is not None

        # Verify request payload
        payload = call_args[1]["json"]
        assert len(payload["inline_source"]["events"]) == 2
        event_ids = [
            e["udm"]["metadata"]["id"] for e in payload["inline_source"]["events"]
        ]
        assert "test-event-id" in event_ids
        assert "test-event-id-2" in event_ids


def test_ingest_udm_adds_missing_id(chronicle_client, mock_udm_response):
    """Test that UDM ingestion adds missing IDs."""
    event = {
        "metadata": {
            "event_type": "NETWORK_CONNECTION",
            "product_name": "Test Product",
            # No ID provided
        },
        "principal": {"ip": "192.168.1.100"},
    }

    with patch.object(chronicle_client.session, "post", return_value=mock_udm_response):
        ingest_udm(client=chronicle_client, udm_events=event)

        # Verify ID was added
        call_args = chronicle_client.session.post.call_args
        payload = call_args[1]["json"]
        event_metadata = payload["inline_source"]["events"][0]["udm"]["metadata"]
        assert "id" in event_metadata
        assert event_metadata["id"]  # ID is not empty


def test_ingest_udm_adds_missing_timestamp(chronicle_client, mock_udm_response):
    """Test that UDM ingestion adds missing timestamps."""
    event = {
        "metadata": {
            "event_type": "NETWORK_CONNECTION",
            "product_name": "Test Product",
            "id": "test-id",
            # No timestamp provided
        },
        "principal": {"ip": "192.168.1.100"},
    }

    with patch.object(chronicle_client.session, "post", return_value=mock_udm_response):
        ingest_udm(client=chronicle_client, udm_events=event)

        # Verify timestamp was added
        call_args = chronicle_client.session.post.call_args
        payload = call_args[1]["json"]
        event_metadata = payload["inline_source"]["events"][0]["udm"]["metadata"]
        assert "event_timestamp" in event_metadata
        assert event_metadata["event_timestamp"]  # Timestamp is not empty


def test_ingest_udm_validation_error_no_metadata(chronicle_client):
    """Test validation error when event has no metadata."""
    event = {
        # No metadata section
        "principal": {"ip": "192.168.1.100"}
    }

    with pytest.raises(
        ValueError, match="UDM event missing required 'metadata' section"
    ):
        ingest_udm(client=chronicle_client, udm_events=event)


def test_ingest_udm_validation_error_invalid_event_type(chronicle_client):
    """Test validation error when event is not a dictionary."""
    with pytest.raises(ValueError, match="Invalid UDM event type"):
        ingest_udm(client=chronicle_client, udm_events=["not a dictionary"])


def test_ingest_udm_validation_error_empty_events(chronicle_client):
    """Test validation error when no events are provided."""
    with pytest.raises(ValueError, match="No UDM events provided"):
        ingest_udm(client=chronicle_client, udm_events=[])


def test_ingest_udm_api_error(chronicle_client):
    """Test error handling when the API request fails."""
    event = {
        "metadata": {"event_type": "NETWORK_CONNECTION", "product_name": "Test Product"}
    }

    error_response = Mock()
    error_response.status_code = 400
    error_response.text = "Invalid request"

    with patch.object(chronicle_client.session, "post", return_value=error_response):
        with pytest.raises(APIError, match="Failed to ingest UDM events"):
            ingest_udm(client=chronicle_client, udm_events=event)


def test_ingest_log_batch(
    chronicle_client, mock_forwarders_list_response, mock_ingest_response
):
    """Test batch log ingestion functionality."""
    test_logs = [
        json.dumps({"test": "log1", "message": "Test message 1"}),
        json.dumps({"test": "log2", "message": "Test message 2"}),
        json.dumps({"test": "log3", "message": "Test message 3"}),
    ]

    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch(
        "secops.chronicle.log_ingest.is_valid_log_type", return_value=True
    ):
        result = ingest_log(
            client=chronicle_client, log_type="OKTA", log_message=test_logs
        )

        # Check result
        assert "operation" in result
        assert (
            result["operation"]
            == "projects/test-project/locations/us/operations/operation-id"
        )

        # Verify request payload
        call_args = chronicle_client.session.post.call_args
        assert call_args is not None
        payload = call_args[1]["json"]
        assert "inline_source" in payload
        assert "logs" in payload["inline_source"]
        assert len(payload["inline_source"]["logs"]) == 3


def test_ingest_log_backward_compatibility(
    chronicle_client, mock_forwarders_list_response, mock_ingest_response
):
    """Test backward compatibility of log ingestion."""
    # Original way of calling with a single log
    test_log = json.dumps({"test": "log", "message": "Test message"})

    with patch.object(
        chronicle_client.session, "get", return_value=mock_forwarders_list_response
    ), patch.object(
        chronicle_client.session, "post", return_value=mock_ingest_response
    ), patch(
        "secops.chronicle.log_ingest.is_valid_log_type", return_value=True
    ):
        result = ingest_log(
            client=chronicle_client, log_type="OKTA", log_message=test_log
        )

        # Check result
        assert "operation" in result

        # Verify request payload still has the expected format
        call_args = chronicle_client.session.post.call_args
        assert call_args is not None
        payload = call_args[1]["json"]
        assert "inline_source" in payload
        assert "logs" in payload["inline_source"]
        assert len(payload["inline_source"]["logs"]) == 1

        # Verify the log content is properly encoded
        log_entry = payload["inline_source"]["logs"][0]
        assert "data" in log_entry
        decoded_data = base64.b64decode(log_entry["data"]).decode("utf-8")
        assert json.loads(decoded_data) == {"test": "log", "message": "Test message"}
