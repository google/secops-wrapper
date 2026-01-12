from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.models import APIVersion
from secops.exceptions import APIError

from secops.chronicle.udm_search import (
    fetch_udm_search_csv,
    fetch_udm_search_view,
    find_udm_field_values,
)


@pytest.fixture
def client() -> Mock:
    return Mock()


def test_fetch_udm_search_csv_calls_chronicle_request_with_expected_payload(client: Mock) -> None:
    expected = "timestamp,user\n2024-01-15T00:00:00Z,user1\n"

    start = datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc)
    end = datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc)

    with patch("secops.chronicle.udm_search.chronicle_request", return_value=expected) as req:
        result = fetch_udm_search_csv(
            client=client,
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=start,
            end_time=end,
            fields=["timestamp", "user"],
        )

    assert result == expected

    req.assert_called_once()
    kwargs = req.call_args.kwargs

    # Called with correct Chronicle endpoint
    assert req.call_args.args[0] is client
    assert kwargs["method"] == "POST"
    assert kwargs["endpoint_path"] == "legacy:legacyFetchUdmSearchCsv"
    assert kwargs["api_version"] == APIVersion.V1ALPHA

    # Payload correctness
    body = kwargs["json"]
    assert body["baselineQuery"] == 'metadata.event_type = "NETWORK_CONNECTION"'
    assert body["baselineTimeRange"]["startTime"] == start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    assert body["baselineTimeRange"]["endTime"] == end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    assert body["fields"]["fields"] == ["timestamp", "user"]
    assert body["caseInsensitive"] is True


def test_fetch_udm_search_view_filters_to_complete_results(client: Mock) -> None:
    # Module behaviour: ignore entries that are neither complete nor error
    json_resp = [
        {"complete": False},
        {"complete": False, "progress": 50},
        {"complete": True, "results": [{"id": 1}]},
    ]

    start = datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc)
    end = datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc)

    with patch("secops.chronicle.udm_search.chronicle_request", return_value=json_resp):
        result = fetch_udm_search_view(
            client=client,
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=start,
            end_time=end,
            max_events=1,
        )

    assert result == [{"complete": True, "results": [{"id": 1}]}]


def test_fetch_udm_search_view_returns_raw_when_no_complete_entries(client: Mock) -> None:
    # If no "complete" responses are present, module returns json_resp as-is
    json_resp = [{"foo": 1}, {"bar": 2}]

    start = datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc)
    end = datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc)

    with patch("secops.chronicle.udm_search.chronicle_request", return_value=json_resp):
        result = fetch_udm_search_view(
            client=client,
            query="q",
            start_time=start,
            end_time=end,
        )

    assert result == json_resp


def test_fetch_udm_search_view_raises_on_error_entry(client: Mock) -> None:
    json_resp = [{"error": "wrong, please try again later"}]

    start = datetime(2024, 1, 14, 23, 7, tzinfo=timezone.utc)
    end = datetime(2024, 1, 15, 0, 7, tzinfo=timezone.utc)

    with patch("secops.chronicle.udm_search.chronicle_request", return_value=json_resp):
        with pytest.raises(APIError, match=r"Chronicle API request failed: wrong, please try again later"):
            fetch_udm_search_view(
                client=client,
                query="q",
                start_time=start,
                end_time=end,
            )


def test_find_udm_field_values_basic_calls_chronicle_request(client: Mock) -> None:
    expected = {
        "valueMatches": [{"value": "elevated", "count": 15}],
        "fieldMatches": [{"field": "principal.process.file.full_path", "count": 12}],
        "fieldMatchRegex": ".*elev.*",
    }

    with patch("secops.chronicle.udm_search.chronicle_request", return_value=expected) as req:
        result = find_udm_field_values(client=client, query="elev")

    assert result == expected

    kwargs = req.call_args.kwargs
    assert req.call_args.args[0] is client
    assert kwargs["method"] == "GET"
    assert kwargs["endpoint_path"] == ":findUdmFieldValues"
    assert kwargs["api_version"] == APIVersion.V1ALPHA
    assert kwargs["params"] == {"query": "elev"}


def test_find_udm_field_values_with_page_size_passes_page_size(client: Mock) -> None:
    expected = {"valueMatches": [], "fieldMatches": [], "fieldMatchRegex": ".*elev.*"}

    with patch("secops.chronicle.udm_search.chronicle_request", return_value=expected) as req:
        result = find_udm_field_values(client=client, query="elev", page_size=10)

    assert result == expected
    assert req.call_args.kwargs["params"] == {"query": "elev", "pageSize": 10}
