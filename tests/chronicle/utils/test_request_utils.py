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
# """Tests for request helper functions."""
from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    DEFAULT_PAGE_SIZE,
    chronicle_request,
    chronicle_paginated_request,
)
from secops.exceptions import APIError


@pytest.fixture
def client() -> Mock:
    # Construct mocked ChronicleClient
    client = Mock()
    client.instance_id = "instances/instance-1"
    client.base_url = Mock(return_value="https://example.test/chronicle")
    client.session = Mock()
    return client


def _mock_response(
    *,
    status_code: int = 200,
    json_value: Any | None = None,
    json_raises: bool = False,
    text: str = "",
) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.text = text

    if json_raises:
        response.json.side_effect = ValueError("non-json")
    else:
        response.json.return_value = json_value

    return response


# ---------------------------------------------------------------------------
# chronicle_request() tests
# ---------------------------------------------------------------------------


def test_chronicle_request_success_json(client: Mock) -> None:
    # Test successful JSON response
    response = _mock_response(status_code=200, json_value={"ok": True})
    client.session.request.return_value = response

    output = chronicle_request(
        client=client,
        method="GET",
        endpoint_path="curatedRules",
        api_version=APIVersion.V1ALPHA,
        params={"pageSize": 10},
    )

    assert output == {"ok": True}

    client.base_url.assert_called_once_with(APIVersion.V1ALPHA)
    client.session.request.assert_called_once_with(
        method="GET",
        url="https://example.test/chronicle/instances/instance-1/curatedRules",
        params={"pageSize": 10},
        json=None,
    )


def test_chronicle_request_non_json_body_raises(client: Mock) -> None:
    # Test that a non-JSON body response raises an error
    response = _mock_response(
        status_code=200, json_raises=True, text="not json"
    )
    client.session.request.return_value = response

    with pytest.raises(APIError, match="Expected JSON response"):
        chronicle_request(
            client=client,
            method="GET",
            endpoint_path="curatedRules",
            api_version=APIVersion.V1ALPHA,
        )


def test_chronicle_request_status_mismatch_with_json_includes_json(
    client: Mock,
) -> None:
    # Test that a non-expected status with a JSON body raises an error
    response = _mock_response(status_code=400, json_value={"error": "bad"})
    client.session.request.return_value = response

    with pytest.raises(
        APIError,
        match=r"API request failed: status=400, response=\{'error': 'bad'\}",
    ):
        chronicle_request(
            client=client,
            method="GET",
            endpoint_path="curatedRules",
            api_version=APIVersion.V1ALPHA,
        )


def test_chronicle_request_status_mismatch_non_json_includes_text(
    client: Mock,
) -> None:
    # Test that a non-expected status without a JSON body raises an error
    response = _mock_response(status_code=500, json_raises=True, text="boom")
    client.session.request.return_value = response

    with pytest.raises(
        APIError, match=r"API request failed: status=500, response_text=boom"
    ):
        chronicle_request(
            client=client,
            method="GET",
            endpoint_path="curatedRules",
            api_version=APIVersion.V1ALPHA,
        )


def test_chronicle_request_custom_error_message_used(client: Mock) -> None:
    # Test that a custom error message is returned when provided
    response = _mock_response(
        status_code=404, json_value={"message": "not found"}
    )
    client.session.request.return_value = response

    with pytest.raises(
        APIError, match=r"Failed to get curated rule: status=404"
    ):
        chronicle_request(
            client=client,
            method="GET",
            endpoint_path="curatedRules/ur_1",
            api_version=APIVersion.V1ALPHA,
            error_message="Failed to get curated rule",
        )


# ---------------------------------------------------------------------------
# chronicle_paginated_request() tests
# ---------------------------------------------------------------------------


def test_paginated_request_single_page_mode_page_size_returns_upstream_json(
    client: Mock,
) -> None:
    # Test single_page_mode triggers when page_size is provided
    response = _mock_response(
        status_code=200, json_value={"items": [1], "nextPageToken": "t2"}
    )
    client.session.request.return_value = response

    output = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="items",
        page_size=10,
    )

    assert output == {"items": [1], "nextPageToken": "t2"}

    client.session.request.assert_called_once()
    _, kwargs = client.session.request.call_args
    assert kwargs["params"] == {"pageSize": 10}


def test_paginated_request_single_page_mode_page_token_returns_upstream_json(
    client: Mock,
) -> None:
    # Test single_page_mode triggers when page_token is provided
    response = _mock_response(
        status_code=200, json_value={"items": [1], "nextPageToken": "t2"}
    )
    client.session.request.return_value = response

    output = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="items",
        page_token="t1",
    )

    assert output == {"items": [1], "nextPageToken": "t2"}

    _, kwargs = client.session.request.call_args
    assert kwargs["params"] == {
        "pageSize": DEFAULT_PAGE_SIZE,
        "pageToken": "t1",
    }


def test_paginated_request_auto_paginates_aggregates_items_and_removes_token(
    client: Mock,
) -> None:
    # Test auto-pagination when both page_size and page_token are None
    resp1 = _mock_response(
        status_code=200,
        json_value={
            "curatedRules": [{"id": 1}],
            "nextPageToken": "t2",
            "meta": {"x": 1},
        },
    )
    resp2 = _mock_response(
        status_code=200,
        json_value={"curatedRules": [{"id": 2}], "meta": {"x": 1}},
    )
    client.session.request.side_effect = [resp1, resp2]

    output = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
    )

    # Shape preserved from first response, but items aggregated, token removed
    assert output["meta"] == {"x": 1}
    assert output["curatedRules"] == [{"id": 1}, {"id": 2}]
    assert "nextPageToken" not in output

    assert client.session.request.call_count == 2
    call1 = client.session.request.call_args_list[0].kwargs
    call2 = client.session.request.call_args_list[1].kwargs
    assert call1["params"] == {"pageSize": DEFAULT_PAGE_SIZE}
    assert call2["params"] == {"pageSize": DEFAULT_PAGE_SIZE, "pageToken": "t2"}


def test_paginated_request_auto_mode_list_response_returns_list(
    client: Mock,
) -> None:
    # Test that if upstream returns a top-level list, the helper returns it immediately (no pagination possible)
    response = _mock_response(
        status_code=200, json_value=[{"id": 1}, {"id": 2}]
    )
    client.session.request.return_value = response

    output = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="feeds",
        items_key="feeds",
    )

    assert output == [{"id": 1}, {"id": 2}]
    assert client.session.request.call_count == 1


def test_paginated_request_unexpected_response_type_raises(
    client: Mock,
) -> None:
    # Test that an unexpected response type returns an error
    response = _mock_response(status_code=200, json_value="not a dict or list")
    client.session.request.return_value = response

    with pytest.raises(
        APIError, match=r"Unexpected response type for curatedRules: str"
    ):
        chronicle_paginated_request(
            client=client,
            api_version=APIVersion.V1ALPHA,
            path="curatedRules",
            items_key="curatedRules",
        )


def test_paginated_request_items_key_not_list_raises(client: Mock) -> None:
    # Test that an incorrect items_key raises an error
    response = _mock_response(
        status_code=200, json_value={"curatedRules": {"id": 1}}
    )
    client.session.request.return_value = response

    with pytest.raises(APIError, match=r"Expected 'curatedRules' to be a list"):
        chronicle_paginated_request(
            client=client,
            api_version=APIVersion.V1ALPHA,
            path="curatedRules",
            items_key="curatedRules",
        )


def test_paginated_request_no_results_returns_dict_with_empty_list(
    client: Mock,
) -> None:
    # Test that no results gets returned as a dict with an empty list
    response = _mock_response(status_code=200, json_value={"curatedRules": []})
    client.session.request.return_value = response

    output = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
    )

    assert output["curatedRules"] == []
    assert "nextPageToken" not in output


def test_paginated_request_extra_params_not_mutated(client: Mock) -> None:
    # Test that extra params provided don't get mutated
    extra = {"filter": "x"}
    response = _mock_response(status_code=200, json_value={"curatedRules": []})
    client.session.request.return_value = response

    chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
        extra_params=extra,
    )

    # Ensure we didn't mutate the caller's dict
    assert extra == {"filter": "x"}

    # Ensure merged into params as expected
    _, kwargs = client.session.request.call_args
    assert kwargs["params"] == {"pageSize": DEFAULT_PAGE_SIZE, "filter": "x"}


def test_paginated_request_single_page_mode_list_only_dict_extracts_items(client: Mock) -> None:
    # Single page mode when page_size is provided; list_only should return just the list under items_key.
    resp = _mock_response(
        status_code=200,
        json_value={"curatedRules": [{"id": 1}], "nextPageToken": "t2", "meta": {"x": 1}},
    )
    client.session.request.return_value = resp

    out = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
        page_size=10,
        as_list=True,
    )

    assert out == [{"id": 1}]

    _, kwargs = client.session.request.call_args
    assert kwargs["params"] == {"pageSize": 10}


def test_paginated_request_single_page_mode_list_only_dict_missing_key_returns_empty_list(client: Mock) -> None:
    # If dict response does not include items_key, list_only should return [] (consistent with .get default)
    resp = _mock_response(status_code=200, json_value={"meta": {"x": 1}, "nextPageToken": "t2"})
    client.session.request.return_value = resp

    out = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
        page_size=10,
        as_list=True,
    )

    assert out == []


def test_paginated_request_single_page_mode_list_only_list_passthrough(client: Mock) -> None:
    # If upstream returns a top-level list and list_only=True, it should be returned as-is.
    resp = _mock_response(status_code=200, json_value=[{"id": 1}, {"id": 2}])
    client.session.request.return_value = resp

    out = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="feeds",
        items_key="feeds",
        page_size=10,
        as_list=True,
    )

    assert out == [{"id": 1}, {"id": 2}]


def test_paginated_request_single_page_mode_list_only_items_key_not_list_raises(client: Mock) -> None:
    # list_only=True should still validate that items_key is a list when present
    resp = _mock_response(status_code=200, json_value={"curatedRules": {"id": 1}})
    client.session.request.return_value = resp

    with pytest.raises(APIError, match=r"Expected 'curatedRules' to be a list"):
        chronicle_paginated_request(
            client=client,
            api_version=APIVersion.V1ALPHA,
            path="curatedRules",
            items_key="curatedRules",
            page_size=10,
            as_list=True,
        )


def test_paginated_request_auto_mode_list_only_aggregates_items(client: Mock) -> None:
    # Auto mode (no page_size/page_token): list_only=True should return aggregated flat list.
    resp1 = _mock_response(
        status_code=200,
        json_value={"curatedRules": [{"id": 1}], "nextPageToken": "t2", "meta": {"x": 1}},
    )
    resp2 = _mock_response(
        status_code=200,
        json_value={"curatedRules": [{"id": 2}], "meta": {"x": 1}},
    )
    client.session.request.side_effect = [resp1, resp2]

    out = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
        as_list=True,
    )

    assert out == [{"id": 1}, {"id": 2}]
    assert client.session.request.call_count == 2

    call1 = client.session.request.call_args_list[0].kwargs
    call2 = client.session.request.call_args_list[1].kwargs
    assert call1["params"] == {"pageSize": DEFAULT_PAGE_SIZE}
    assert call2["params"] == {"pageSize": DEFAULT_PAGE_SIZE, "pageToken": "t2"}


def test_paginated_request_auto_mode_list_only_empty_returns_empty_list(client: Mock) -> None:
    resp = _mock_response(status_code=200, json_value={"curatedRules": []})
    client.session.request.return_value = resp

    out = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="curatedRules",
        items_key="curatedRules",
        as_list=True,
    )

    assert out == []


def test_paginated_request_auto_mode_list_only_list_response_returns_list(client: Mock) -> None:
    # Auto mode + top-level list response: return list and stop.
    resp = _mock_response(status_code=200, json_value=[{"id": 1}, {"id": 2}])
    client.session.request.return_value = resp

    out = chronicle_paginated_request(
        client=client,
        api_version=APIVersion.V1ALPHA,
        path="feeds",
        items_key="feeds",
        as_list=True,
    )

    assert out == [{"id": 1}, {"id": 2}]
    assert client.session.request.call_count == 1


def test_chronicle_request_builds_url_for_rpc_colon_prefix(client: Mock) -> None:
    resp = _mock_response(status_code=200, json_value={"ok": True})
    client.session.request.return_value = resp

    chronicle_request(
        client=client,
        method="POST",
        endpoint_path=":validateQuery",
        api_version=APIVersion.V1ALPHA,
    )

    _, kwargs = client.session.request.call_args
    assert kwargs["url"] == "https://example.test/chronicle/instances/instance-1:validateQuery"


def test_chronicle_request_builds_url_for_legacy_segment(client: Mock) -> None:
    resp = _mock_response(status_code=200, json_value={"ok": True})
    client.session.request.return_value = resp

    chronicle_request(
        client=client,
        method="GET",
        endpoint_path="legacy:legacySearchCuratedDetections",
        api_version=APIVersion.V1ALPHA,
    )

    _, kwargs = client.session.request.call_args
    assert kwargs["url"] == "https://example.test/chronicle/instances/instance-1/legacy:legacySearchCuratedDetections"
