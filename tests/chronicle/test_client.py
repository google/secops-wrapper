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
"""Tests for Chronicle API client."""
from datetime import datetime, timezone, timedelta
import pytest
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import CaseList
from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        client = ChronicleClient(
            project_id="test-project", customer_id="test-customer", region="us"
        )
        return client


@pytest.fixture
def mock_response():
    """Create a mock API response."""
    mock = Mock()
    mock.status_code = 200
    # Mock the text attribute to return a CSV string
    mock.text = "timestamp,user,hostname,process_name\n2024-01-15T00:00:00Z,user1,host1,process1\n"
    return mock


def test_chronicle_client_initialization():
    """Test Chronicle client initialization."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        client = ChronicleClient(
            project_id="test-project", customer_id="test-customer", region="us"
        )
        assert client.project_id == "test-project"
        assert client.customer_id == "test-customer"
        assert client.region == "us"
        assert client.base_url == "https://us-chronicle.googleapis.com/v1alpha"


def test_chronicle_client_custom_user_agent():
    """Test that Chronicle client sets custom user agent."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session

        client = ChronicleClient(
            project_id="test-project", customer_id="test-customer", region="us"
        )

        # Verify that the user agent was set
        assert client.session.headers.get("User-Agent") == "secops-wrapper-sdk"


def test_chronicle_client_custom_session_user_agent():
    """Test that Chronicle client sets custom user agent even with custom session."""
    mock_session = Mock()
    mock_session.headers = {}

    client = ChronicleClient(
        project_id="test-project",
        customer_id="test-customer",
        region="us",
        session=mock_session,
    )

    # Verify that the user agent was set
    assert client.session.headers.get("User-Agent") == "secops-wrapper-sdk"


def test_fetch_udm_search_csv(chronicle_client, mock_response):
    """Test fetching UDM search results."""
    with patch.object(chronicle_client.session, "post", return_value=mock_response):
        result = chronicle_client.fetch_udm_search_csv(
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc),
            fields=["timestamp", "user", "hostname", "process name"],
        )

        assert "timestamp,user,hostname,process_name" in result
        assert "2024-01-15T00:00:00Z,user1,host1,process1" in result


def test_fetch_udm_search_csv_error(chronicle_client):
    """Test handling of API errors."""
    error_response = Mock()
    error_response.status_code = 400
    error_response.text = "Invalid request"

    with patch(
        "google.auth.transport.requests.AuthorizedSession.post",
        return_value=error_response,
    ):
        with pytest.raises(APIError) as exc_info:
            chronicle_client.fetch_udm_search_csv(
                query="invalid query",
                start_time=datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc),
                end_time=datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc),
                fields=["timestamp"],
            )

        assert "Chronicle API request failed" in str(exc_info.value)


def test_fetch_udm_search_csv_parsing_error(chronicle_client):
    """Test handling of parsing errors in CSV response."""
    error_response = Mock()
    error_response.status_code = 200
    # Set text to start with { to trigger JSON parsing attempt
    error_response.text = '{"invalid": json}'
    error_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(chronicle_client.session, "post", return_value=error_response):
        with pytest.raises(APIError) as exc_info:
            chronicle_client.fetch_udm_search_csv(
                query='metadata.event_type = "NETWORK_CONNECTION"',
                start_time=datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc),
                end_time=datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc),
                fields=["timestamp"],
            )

        assert "Failed to parse CSV response" in str(exc_info.value)


def test_fetch_udm_search_view(chronicle_client, mock_response):
    mock_response.json.return_value = [{"progress": 1, "complete": True, "validBaselineQuery": True, "baselineEventsCount": 50, "validSnapshotQuery": True, "filteredEventsCount": 50}]
    """Test fetching UDM search view results."""
    with patch.object(chronicle_client.session, "post", return_value=mock_response):
        result = chronicle_client.fetch_udm_search_view(
            query='metadata.event_type = "PROCESS_LAUNCH" and target.process.file.full_path = /powershell.exe/ nocase',
            start_time=datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc),
                end_time=datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc),
                max_events=1
        )

    assert result[0]["complete"] is True


def test_fetch_udm_search_view_syntax_error(chronicle_client):
    """Test handling of API errors"""
    error_response = Mock()
    error_response.status_code = 200
    error_response.json.return_value =  [{"error": {"code": 400, "message": "something went wrong, please try again later", "status": "INVALID_ARGUMENT"}}]

    with patch.object(chronicle_client.session, "post", return_value=error_response):
        with pytest.raises(APIError) as exc_info:
            chronicle_client.fetch_udm_search_view(
                query='metadata.event_types = "PROCESS_LAUNCH"',
                start_time=datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc),
                end_time=datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc),
                max_events=1
            )

        assert "Chronicle API request failed" in str(exc_info.value)


def test_fetch_udm_search_view_parsing_error(chronicle_client):
    """Test handling of API errors"""
    error_response = Mock()
    error_response.status_code = 200
    error_response.json.text = '[{invalid: json}]'
    error_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(chronicle_client.session, "post", return_value=error_response):
        with pytest.raises(APIError) as exc_info:
            chronicle_client.fetch_udm_search_view(
                query='metadata.event_type = "PROCESS_LAUNCH"',
                start_time=datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc),
                end_time=datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc),
                max_events=1
            )

        assert "Failed to parse UDM search response" in str(exc_info.value)


def test_validate_query(chronicle_client):
    """Test query validation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "queryType": "QUERY_TYPE_UDM_QUERY",
        "isValid": True,
    }

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        result = chronicle_client.validate_query(
            'metadata.event_type = "NETWORK_CONNECTION"'
        )

        assert result.get("isValid") is True
        assert result.get("queryType") == "QUERY_TYPE_UDM_QUERY"


def test_get_stats(chronicle_client):
    """Test stats search functionality."""
    # Mock the search request
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "stats": {
            "results": [
                {"column": "count", "values": [{"value": {"int64Val": "42"}}]},
                {
                    "column": "hostname",
                    "values": [{"value": {"stringVal": "test-host"}}],
                },
            ]
        }
    }

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        result = chronicle_client.get_stats(
            query="""target.ip != ""
match:
  target.ip, principal.hostname
outcome:
  $count = count(metadata.id)
order:
  principal.hostname asc""",
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
            max_events=10,
            max_values=10,
        )

        assert result["total_rows"] == 1
        assert result["columns"] == ["count", "hostname"]
        assert result["rows"][0]["count"] == 42
        assert result["rows"][0]["hostname"] == "test-host"


def test_search_udm(chronicle_client):
    """Test UDM search functionality."""
    # Mock the search request
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "events": [
            {
                "name": "projects/test-project/locations/us/instances/test-instance/events/event1",
                "udm": {
                    "metadata": {
                        "eventTimestamp": "2024-01-01T00:00:00Z",
                        "eventType": "NETWORK_CONNECTION",
                    },
                    "target": {"ip": "192.168.1.1", "hostname": "test-host"},
                },
            }
        ],
        "moreDataAvailable": False,
    }

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        result = chronicle_client.search_udm(
            query='target.ip != ""',
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
            max_events=10,
        )

        assert "events" in result
        assert "total_events" in result
        assert result["total_events"] == 1
        assert result["events"][0]["udm"]["target"]["ip"] == "192.168.1.1"


@patch("secops.chronicle.entity._detect_value_type_for_query")
@patch("secops.chronicle.entity._summarize_entity_by_id")
def test_summarize_entity_ip(mock_summarize_by_id, mock_detect, chronicle_client):
    """Test summarize_entity for an IP address."""
    mock_detect.return_value = ('ip = "8.8.8.8"', "ASSET")

    # Mock response for summarizeEntitiesFromQuery
    mock_query_response = Mock()
    mock_query_response.status_code = 200
    mock_query_response.json.return_value = {
        "entitySummaries": [
            {
                "entity": [
                    {
                        "name": "projects/p/locations/l/instances/i/entities/ip-entity-id",
                        "metadata": {"entityType": "IP_ADDRESS"},
                        "metric": {
                            "firstSeen": "2024-01-01T00:00:00Z",
                            "lastSeen": "2024-01-02T00:00:00Z",
                        },
                        "entity": {"artifact": {"ip": "8.8.8.8"}},
                    }
                ]
            },
            {
                "entity": [
                    {
                        "name": "projects/p/locations/l/instances/i/entities/asset-entity-id",
                        "metadata": {"entityType": "ASSET"},
                        "metric": {
                            "firstSeen": "2024-01-01T01:00:00Z",
                            "lastSeen": "2024-01-02T01:00:00Z",
                        },
                        "entity": {"asset": {"ip": ["8.8.8.8"]}},
                    }
                ]
            },
        ]
    }

    # Mock responses for _summarize_entity_by_id (for asset-entity-id)
    # Call 1: Get details + alerts + timeline
    mock_details_response = {
        "entities": [
            {
                "name": "projects/p/locations/l/instances/i/entities/asset-entity-id",
                "metadata": {"entityType": "ASSET"},
                "metric": {
                    "firstSeen": "2024-01-01T01:00:00Z",
                    "lastSeen": "2024-01-02T01:00:00Z",
                },
                "entity": {"asset": {"ip": ["8.8.8.8"]}},
            }
        ],
        "alertCounts": [{"rule": "Test IP Alert", "count": "5"}],
        "timeline": {"buckets": [{}, {}], "bucketSize": "3600s"},
    }
    # Call 2: Get prevalence
    mock_prevalence_response = {
        "prevalenceResult": [{"prevalenceTime": "2024-01-01T00:00:00Z", "count": 10}]
    }
    mock_summarize_by_id.side_effect = [mock_details_response, mock_prevalence_response]

    with patch.object(
        chronicle_client.session, "get", return_value=mock_query_response
    ) as mock_session_get:
        result = chronicle_client.summarize_entity(
            value="8.8.8.8",
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
        )

    # Assertions
    mock_detect.assert_called_once_with("8.8.8.8")
    # Check the query call was made
    mock_session_get.assert_called_once()
    query_call_args = mock_session_get.call_args
    assert "summarizeEntitiesFromQuery" in query_call_args[0][0]
    assert query_call_args[1]["params"]["query"] == 'ip = "8.8.8.8"'

    # Check the _summarize_entity_by_id calls
    assert mock_summarize_by_id.call_count == 2
    details_call = mock_summarize_by_id.call_args_list[0]
    prevalence_call = mock_summarize_by_id.call_args_list[1]

    assert details_call[0][1] == "asset-entity-id"  # Check entity ID
    assert details_call[1]["return_alerts"] is True  # Check keyword arg
    assert details_call[1]["return_prevalence"] is False  # Check keyword arg

    assert prevalence_call[0][1] == "ip-entity-id"  # Check entity ID
    assert prevalence_call[1]["return_alerts"] is False  # Check keyword arg
    assert prevalence_call[1]["return_prevalence"] is True  # Check keyword arg

    # Check final EntitySummary structure
    assert result.primary_entity is not None
    assert result.primary_entity.metadata.entity_type == "ASSET"
    assert result.primary_entity.entity["asset"]["ip"] == ["8.8.8.8"]
    assert len(result.related_entities) == 1
    assert result.related_entities[0].metadata.entity_type == "IP_ADDRESS"
    assert result.alert_counts is not None
    assert len(result.alert_counts) == 1
    assert result.alert_counts[0].rule == "Test IP Alert"
    assert result.alert_counts[0].count == 5
    assert result.timeline is not None
    assert len(result.timeline.buckets) == 2
    assert result.prevalence is not None
    assert len(result.prevalence) == 1
    assert result.prevalence[0].count == 10
    assert result.file_metadata_and_properties is None  # Not expected for IP


@patch(
    "secops.chronicle.entity._detect_value_type_for_query", return_value=(None, None)
)
def test_summarize_entity_detect_error(mock_detect, chronicle_client):
    """Test summarize_entity raises ValueError on detection failure."""
    with pytest.raises(
        ValueError, match="Could not determine how to query"
    ):  # Check specific error message if possible
        chronicle_client.summarize_entity(
            value="???",
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
        )


def test_list_iocs(chronicle_client):
    """Test listing IoCs."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "matches": [
            {
                "ioc": {"value": "malicious.com", "type": "DOMAIN_NAME"},
                "sources": ["Mandiant"],
                "firstSeenTimestamp": "2024-01-01T00:00:00.000Z",
                "lastSeenTimestamp": "2024-01-02T00:00:00.000Z",
                "filterProperties": {
                    "stringProperties": {
                        "category": {"values": [{"rawValue": "malware"}]}
                    }
                },
                "associationIdentifier": [
                    {
                        "name": "test-campaign",
                        "associationType": "CAMPAIGN",
                        "regionCode": "US",
                    },
                    {
                        "name": "test-campaign",
                        "associationType": "CAMPAIGN",
                        "regionCode": "EU",
                    },
                ],
            }
        ]
    }

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        result = chronicle_client.list_iocs(
            start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
        )

        # Check that the response has matches
        assert "matches" in result
        assert len(result["matches"]) == 1
        match = result["matches"][0]

        # Check IoC value
        assert match["ioc"]["value"] == "malicious.com"

        # Check timestamps are processed (Z removed)
        assert match["firstSeenTimestamp"] == "2024-01-01T00:00:00.000"
        assert match["lastSeenTimestamp"] == "2024-01-02T00:00:00.000"

        # Check properties are extracted
        assert "properties" in match
        assert match["properties"]["category"] == ["malware"]

        # Check associations are deduplicated
        assert len(match["associationIdentifier"]) == 1


def test_list_iocs_error(chronicle_client):
    """Test error handling when listing IoCs."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid request"

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        with pytest.raises(APIError, match="Failed to list IoCs"):
            chronicle_client.list_iocs(
                start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
            )


def test_get_cases(chronicle_client):
    """Test getting case details."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cases": [
            {
                "id": "case-123",
                "displayName": "Test Case",
                "stage": "Investigation",
                "priority": "PRIORITY_HIGH",
                "status": "OPEN",
                "soarPlatformInfo": {
                    "caseId": "soar-123",
                    "responsePlatformType": "RESPONSE_PLATFORM_TYPE_SIEMPLIFY",
                },
            }
        ]
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = chronicle_client.get_cases(["case-123"])

        # Verify the correct endpoint was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "legacy:legacyBatchGetCases" in call_args[0][0]

        # Verify the correct parameter name was used
        assert call_args[1]["params"] == {"names": ["case-123"]}

        assert isinstance(result, CaseList)
        case = result.get_case("case-123")
        assert case.display_name == "Test Case"
        assert case.priority == "PRIORITY_HIGH"
        assert case.soar_platform_info.case_id == "soar-123"


def test_get_cases_filtering(chronicle_client):
    """Test CaseList filtering methods."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cases": [
            {
                "id": "case-1",
                "priority": "PRIORITY_HIGH",
                "status": "OPEN",
                "stage": "Investigation",
            },
            {
                "id": "case-2",
                "priority": "PRIORITY_MEDIUM",
                "status": "CLOSED",
                "stage": "Triage",
            },
        ]
    }

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        result = chronicle_client.get_cases(["case-1", "case-2"])

        high_priority = result.filter_by_priority("PRIORITY_HIGH")
        assert len(high_priority) == 1
        assert high_priority[0].id == "case-1"

        open_cases = result.filter_by_status("OPEN")
        assert len(open_cases) == 1
        assert open_cases[0].id == "case-1"


def test_get_cases_error(chronicle_client):
    """Test error handling when getting cases."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid request"

    with patch.object(chronicle_client.session, "get", return_value=mock_response):
        with pytest.raises(APIError, match="Failed to get cases"):
            chronicle_client.get_cases(["invalid-id"])


def test_get_cases_limit(chronicle_client):
    """Test limiting the number of cases returned."""
    with pytest.raises(
        ValueError, match="Maximum of 1000 cases can be retrieved in a batch"
    ):
        chronicle_client.get_cases(["case-id"] * 1001)


def test_get_alerts(chronicle_client):
    """Test getting alerts."""
    # First response with in-progress status
    initial_response = Mock()
    initial_response.status_code = 200
    initial_response.iter_lines.return_value = [
        b'{"progress": 0.057142861187458038, "validBaselineQuery": true, "validSnapshotQuery": true}'
    ]

    # Second response with completed results
    complete_response = Mock()
    complete_response.status_code = 200
    complete_response.iter_lines.return_value = [
        b'{"progress": 1, "complete": true, "validBaselineQuery": true, "baselineAlertsCount": 1, "validSnapshotQuery": true, "filteredAlertsCount": 1,',
        b'"alerts": {"alerts": [{"type": "RULE_DETECTION", "detection": [{"ruleName": "TEST_RULE", "description": "Test Rule", "ruleId": "rule-123"}],',
        b'"createdTime": "2025-03-09T15:26:10.248291Z", "id": "alert-123", "caseName": "case-123",',
        b'"feedbackSummary": {"status": "OPEN", "priority": "PRIORITY_MEDIUM", "severityDisplay": "Medium"}}]},',
        b'"fieldAggregations": {"fields": [{"fieldName": "detection.rule_name", "baselineAlertCount": 1, "alertCount": 1, "valueCount": 1,',
        b'"allValues": [{"value": {"stringValue": "TEST_RULE"}, "baselineAlertCount": 1, "alertCount": 1}]}]}}',
    ]

    # Mock the sleep function to prevent actual waiting
    with patch("time.sleep"), patch.object(
        chronicle_client.session,
        "get",
        side_effect=[initial_response, complete_response],
    ):
        result = chronicle_client.get_alerts(
            start_time=datetime(2025, 3, 8, tzinfo=timezone.utc),
            end_time=datetime(2025, 3, 9, tzinfo=timezone.utc),
            snapshot_query='feedback_summary.status != "CLOSED"',
            max_alerts=10,
            poll_interval=0.001,  # Use a very small interval for testing
        )

        # Check the key parts of the response
        assert result.get("complete") is True
        assert result.get("validBaselineQuery") is True
        assert result.get("filteredAlertsCount") == 1

        # Check alert details
        alerts = result.get("alerts", {}).get("alerts", [])
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.get("id") == "alert-123"
        assert alert.get("caseName") == "case-123"
        assert alert.get("feedbackSummary", {}).get("status") == "OPEN"
        assert alert.get("detection")[0].get("ruleName") == "TEST_RULE"

        # Check field aggregations
        field_aggregations = result.get("fieldAggregations", {}).get("fields", [])
        assert len(field_aggregations) > 0
        rule_name_field = next(
            (
                f
                for f in field_aggregations
                if f.get("fieldName") == "detection.rule_name"
            ),
            None,
        )
        assert rule_name_field is not None
        assert rule_name_field.get("alertCount") == 1


def test_get_alerts_error(chronicle_client):
    """Test error handling for get_alerts."""
    error_response = Mock()
    error_response.status_code = 400
    error_response.text = "Invalid query syntax"

    with patch.object(chronicle_client.session, "get", return_value=error_response):
        with pytest.raises(
            APIError, match="Failed to get alerts: Invalid query syntax"
        ):
            chronicle_client.get_alerts(
                start_time=datetime(2025, 3, 8, tzinfo=timezone.utc),
                end_time=datetime(2025, 3, 9, tzinfo=timezone.utc),
            )


def test_get_alerts_json_parsing(chronicle_client):
    """Test handling of streaming response and JSON parsing."""
    response = Mock()
    response.status_code = 200
    # Simulate response line with a trailing comma
    response.iter_lines.return_value = [
        b'{"progress": 1, "complete": true,"alerts": {"alerts": [{"id": "alert-1"},{"id": "alert-2"},]},"fieldAggregations": {"fields": []}}'
    ]

    # Mock the sleep function to prevent actual waiting
    with patch("time.sleep"), patch.object(
        chronicle_client.session, "get", return_value=response
    ):
        result = chronicle_client.get_alerts(
            start_time=datetime(2025, 3, 8, tzinfo=timezone.utc),
            end_time=datetime(2025, 3, 9, tzinfo=timezone.utc),
            max_attempts=1,  # Only make one request
        )

        # Verify the response was properly parsed despite formatting issues
        assert result.get("complete") is True
        alerts = result.get("alerts", {}).get("alerts", [])
        assert len(alerts) == 2
        assert alerts[0].get("id") == "alert-1"
        assert alerts[1].get("id") == "alert-2"


def test_get_alerts_parameters(chronicle_client):
    """Test that parameters are correctly set in the request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [b'{"progress": 1, "complete": true}']

    with patch("time.sleep"), patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        # Test with a non-UTC timezone (Eastern Time)
        eastern = timezone(timedelta(hours=-5))
        start_time = datetime(2025, 3, 8, 10, 30, 45, tzinfo=eastern)  # 10:30:45 ET
        end_time = datetime(2025, 3, 9, 15, 45, 30, tzinfo=eastern)  # 15:45:30 ET

        # Expected UTC timestamps after conversion
        expected_start = "2025-03-08T15:30:45Z"  # 10:30:45 ET = 15:30:45 UTC
        expected_end = "2025-03-09T20:45:30Z"  # 15:45:30 ET = 20:45:30 UTC

        snapshot_query = 'feedback_summary.status = "OPEN"'
        baseline_query = 'detection.rule_id = "rule-123"'
        max_alerts = 50
        enable_cache = False

        chronicle_client.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query=snapshot_query,
            baseline_query=baseline_query,
            max_alerts=max_alerts,
            enable_cache=enable_cache,
            max_attempts=1,  # Only make one request
        )

        # Verify that the correct parameters were sent
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args

        # Check URL and parameters using explicit string comparison
        params = kwargs.get("params", {})
        assert params.get("timeRange.startTime") == expected_start
        assert params.get("timeRange.endTime") == expected_end
        assert params.get("snapshotQuery") == snapshot_query
        assert params.get("baselineQuery") == baseline_query
        assert params.get("alertListOptions.maxReturnedAlerts") == max_alerts
        assert params.get("enableCache") == "ALERTS_FEATURE_PREFERENCE_DISABLED"

        # Reset mock to test another timezone scenario
        mock_get.reset_mock()

        # Test with another timezone (Pacific Time)
        pacific = timezone(timedelta(hours=-8))
        start_time = datetime(2025, 3, 8, 7, 15, 30, tzinfo=pacific)  # 7:15:30 PT
        end_time = datetime(2025, 3, 9, 19, 45, 0, tzinfo=pacific)  # 19:45:00 PT

        # Expected UTC timestamps after conversion
        expected_start = "2025-03-08T15:15:30Z"  # 7:15:30 PT = 15:15:30 UTC
        expected_end = "2025-03-10T03:45:00Z"  # 19:45:00 PT = 03:45:00 UTC (next day)

        chronicle_client.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query=snapshot_query,
            baseline_query=baseline_query,
            max_alerts=max_alerts,
            enable_cache=enable_cache,
            max_attempts=1,
        )

        # Verify again with the second timezone
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        assert params.get("timeRange.startTime") == expected_start
        assert params.get("timeRange.endTime") == expected_end

        # Reset mock for one more test with microseconds
        mock_get.reset_mock()

        # Test with microseconds that should be stripped
        indian = timezone(
            timedelta(hours=5, minutes=30)
        )  # Indian Standard Time UTC+5:30
        start_time = datetime(
            2025, 3, 8, 12, 30, 45, 123456, tzinfo=indian
        )  # With microseconds
        end_time = datetime(
            2025, 3, 9, 18, 15, 30, 987654, tzinfo=indian
        )  # With microseconds

        # Expected UTC timestamps after conversion (microseconds removed)
        expected_start = (
            "2025-03-08T07:00:45Z"  # 12:30:45 IST = 07:00:45 UTC (no microseconds)
        )
        expected_end = (
            "2025-03-09T12:45:30Z"  # 18:15:30 IST = 12:45:30 UTC (no microseconds)
        )

        chronicle_client.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query=snapshot_query,
            baseline_query=baseline_query,
            max_alerts=max_alerts,
            enable_cache=enable_cache,
            max_attempts=1,
        )

        # Verify microseconds handling
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        assert params.get("timeRange.startTime") == expected_start
        assert params.get("timeRange.endTime") == expected_end

        # Reset mock for one more test with naive datetime objects (no timezone)
        mock_get.reset_mock()

        # Test with naive datetime objects (no timezone) which should be interpreted as UTC
        naive_start_time = datetime(2025, 3, 8, 9, 30, 45)  # No timezone info
        naive_end_time = datetime(2025, 3, 9, 14, 15, 30)  # No timezone info

        # Expected UTC timestamps
        expected_start = "2025-03-08T09:30:45Z"  # Should be treated as UTC
        expected_end = "2025-03-09T14:15:30Z"  # Should be treated as UTC

        chronicle_client.get_alerts(
            start_time=naive_start_time,
            end_time=naive_end_time,
            snapshot_query=snapshot_query,
            baseline_query=baseline_query,
            max_alerts=max_alerts,
            enable_cache=enable_cache,
            max_attempts=1,
        )

        # Verify handling of naive datetime objects
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        assert params.get("timeRange.startTime") == expected_start
        assert params.get("timeRange.endTime") == expected_end


def test_get_alerts_json_processing(chronicle_client):
    """Test processing of streaming JSON response with complex structure."""
    response = Mock()
    response.status_code = 200
    # Simulate a complex JSON response with nested structures matching the real API
    response.iter_lines.return_value = [
        b'{"progress": 1, "complete": true, "validBaselineQuery": true, "baselineAlertsCount": 2, "validSnapshotQuery": true, "filteredAlertsCount": 2, '
        b'"alerts": {"alerts": ['
        b'{"type": "RULE_DETECTION", "detection": [{"ruleName": "RULE1", "ruleId": "rule-1", "alertState": "ALERTING", "detectionFields": [{"key": "hostname", "value": "host1"}]}], "id": "alert-1", "createdTime": "2025-03-01T00:00:00Z"},'
        b'{"type": "RULE_DETECTION", "detection": [{"ruleName": "RULE2", "ruleId": "rule-2", "alertState": "ALERTING", "detectionFields": [{"key": "hostname", "value": "host2"}]}], "id": "alert-2", "createdTime": "2025-03-02T00:00:00Z"}'
        b"]},"
        b'"fieldAggregations": {"fields": [{"fieldName": "detection.rule_name", "baselineAlertCount": 2, "alertCount": 2, "valueCount": 2, '
        b'"allValues": ['
        b'{"value": {"stringValue": "RULE1"}, "baselineAlertCount": 1, "alertCount": 1},'
        b'{"value": {"stringValue": "RULE2"}, "baselineAlertCount": 1, "alertCount": 1}'
        b"]}]}}"
    ]

    with patch("time.sleep"), patch.object(
        chronicle_client.session, "get", return_value=response
    ):
        result = chronicle_client.get_alerts(
            start_time=datetime(2025, 3, 1, tzinfo=timezone.utc),
            end_time=datetime(2025, 3, 3, tzinfo=timezone.utc),
            max_attempts=1,  # Only make one request
        )

        # Verify that complex nested structures are correctly processed
        assert result.get("complete") is True
        assert result.get("baselineAlertsCount") == 2
        assert result.get("filteredAlertsCount") == 2

        # Check alerts list
        alerts = result.get("alerts", {}).get("alerts", [])
        assert len(alerts) == 2

        # First alert
        assert alerts[0].get("id") == "alert-1"
        assert alerts[0].get("detection")[0].get("ruleName") == "RULE1"
        assert (
            alerts[0].get("detection")[0].get("detectionFields")[0].get("value")
            == "host1"
        )

        # Second alert
        assert alerts[1].get("id") == "alert-2"
        assert alerts[1].get("detection")[0].get("ruleName") == "RULE2"
        assert (
            alerts[1].get("detection")[0].get("detectionFields")[0].get("value")
            == "host2"
        )

        # Field aggregations
        field_aggs = result.get("fieldAggregations", {}).get("fields", [])
        assert len(field_aggs) == 1
        rule_name_field = field_aggs[0]
        assert rule_name_field.get("fieldName") == "detection.rule_name"
        assert rule_name_field.get("valueCount") == 2
        assert len(rule_name_field.get("allValues", [])) == 2
        rule_values = [
            v.get("value", {}).get("stringValue")
            for v in rule_name_field.get("allValues", [])
        ]
        assert "RULE1" in rule_values
        assert "RULE2" in rule_values


def test_fix_json_formatting(chronicle_client):
    """Test JSON formatting fix helper method."""
    # Test trailing commas in arrays
    json_with_array_trailing_comma = '{"items": [1, 2, 3,]}'
    fixed = chronicle_client._fix_json_formatting(json_with_array_trailing_comma)
    assert fixed == '{"items": [1, 2, 3]}'

    # Test trailing commas in objects
    json_with_object_trailing_comma = '{"a": 1, "b": 2,}'
    fixed = chronicle_client._fix_json_formatting(json_with_object_trailing_comma)
    assert fixed == '{"a": 1, "b": 2}'

    # Test multiple trailing commas
    json_with_multiple_trailing_commas = '{"a": [1, 2,], "b": {"c": 3, "d": 4,},}'
    fixed = chronicle_client._fix_json_formatting(json_with_multiple_trailing_commas)
    assert fixed == '{"a": [1, 2], "b": {"c": 3, "d": 4}}'

    # Test no trailing commas
    json_without_trailing_commas = '{"a": [1, 2], "b": {"c": 3, "d": 4}}'
    fixed = chronicle_client._fix_json_formatting(json_without_trailing_commas)
    assert fixed == json_without_trailing_commas


def test_find_udm_field_values_basic(chronicle_client):
    """Test basic UDM field values search functionality."""
    # Mock the response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "valueMatches": [
            {"value": "elevated", "count": 15},
            {"value": "elevation", "count": 8}
        ],
        "fieldMatches": [
            {"field": "principal.process.file.full_path", "count": 12},
            {"field": "principal.user.attribute.roles", "count": 11}
        ],
        "fieldMatchRegex": ".*elev.*"
    }

    # Configure the mock session
    chronicle_client.session.get.return_value = mock_response

    # Call the method
    result = chronicle_client.find_udm_field_values(query="elev")

    # Verify the request was made correctly
    chronicle_client.session.get.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}:findUdmFieldValues",
        params={"query": "elev"}
    )

    # Verify the response was processed correctly
    assert len(result["valueMatches"]) == 2
    assert result["valueMatches"][0]["value"] == "elevated"
    assert result["valueMatches"][0]["count"] == 15
    assert result["valueMatches"][1]["value"] == "elevation"
    assert len(result["fieldMatches"]) == 2
    assert result["fieldMatchRegex"] == ".*elev.*"


def test_find_udm_field_values_with_page_size(chronicle_client):
    """Test UDM field values search with page size parameter."""
    # Mock the response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "valueMatches": [
            {"value": "elevated", "count": 15}
        ],
        "fieldMatches": [
            {"field": "principal.process.file.full_path", "count": 12}
        ]
    }

    # Configure the mock session
    chronicle_client.session.get.return_value = mock_response

    # Call the method with page_size
    result = chronicle_client.find_udm_field_values(query="elev", page_size=1)

    # Verify the request was made with correct parameters
    chronicle_client.session.get.assert_called_once_with(
        f"{chronicle_client.base_url}/{chronicle_client.instance_id}:findUdmFieldValues",
        params={"query": "elev", "pageSize": 1}
    )

    # Verify the response
    assert len(result["valueMatches"]) == 1
    assert len(result["fieldMatches"]) == 1


def test_find_udm_field_values_error_response(chronicle_client):
    """Test error handling for UDM field values search."""
    # Mock an error response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request: Invalid query parameter"

    # Configure the mock session
    chronicle_client.session.get.return_value = mock_response

    # Verify that APIError is raised
    with pytest.raises(APIError) as excinfo:
        chronicle_client.find_udm_field_values(query="invalid:query")

    # Verify the error message
    assert "Chronicle API request failed" in str(excinfo.value)
    assert "Bad Request: Invalid query parameter" in str(excinfo.value)


def test_find_udm_field_values_json_error(chronicle_client):
    """Test JSON parsing error for UDM field values search."""
    # Mock a response with invalid JSON
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    # Configure the mock session
    chronicle_client.session.get.return_value = mock_response

    # Verify that SecOpsError is raised
    with pytest.raises(SecOpsError) as excinfo:
        chronicle_client.find_udm_field_values(query="elev")

    # Verify the error message
    assert "Failed to parse response as JSON" in str(excinfo.value)
    assert "Invalid JSON" in str(excinfo.value)
