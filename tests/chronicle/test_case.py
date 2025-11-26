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
"""Tests for Chronicle case management functions."""

import pytest
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.case import (
    CasePriority,
    execute_bulk_add_tag,
    execute_bulk_assign,
    execute_bulk_change_priority,
    execute_bulk_change_stage,
    execute_bulk_close,
    execute_bulk_reopen,
    get_case,
    list_cases,
    merge_cases,
    patch_case,
)
from secops.chronicle.models import Case
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer",
            project_id="test-project",
            region="us",
        )


@pytest.fixture
def mock_case_data():
    """Create mock case data."""
    return {
        "id": "12345",
        "displayName": "Test Case",
        "stage": "Investigation",
        "priority": "PRIORITY_HIGH",
        "status": "OPEN",
    }


# Tests for execute_bulk_add_tag


def test_execute_bulk_add_tag_success(chronicle_client):
    """Test successful bulk add tag operation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_add_tag(
            chronicle_client, [123, 456], ["tag1", "tag2"]
        )

        # Verify correct endpoint and payload
        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:executeBulkAddTag"
        )
        mock_post.assert_called_once_with(
            expected_url,
            json={"casesIds": [123, 456], "tags": ["tag1", "tag2"]},
        )
        assert result == {}


def test_execute_bulk_add_tag_api_error(chronicle_client):
    """Test bulk add tag with API error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid request"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to add tags to cases"):
            execute_bulk_add_tag(chronicle_client, [123], ["tag1"])


def test_execute_bulk_add_tag_empty_tags(chronicle_client):
    """Test bulk add tag with empty tags list."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        result = execute_bulk_add_tag(chronicle_client, [123], [])
        assert result == {}


def test_execute_bulk_add_tag_json_parse_error(chronicle_client):
    """Test bulk add tag with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse bulk add tag response"
        ):
            execute_bulk_add_tag(chronicle_client, [123], ["tag1"])


# Tests for execute_bulk_assign


def test_execute_bulk_assign_success(chronicle_client):
    """Test successful bulk assign operation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_assign(
            chronicle_client, [123, 456], "user@example.com"
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:executeBulkAssign"
        )
        mock_post.assert_called_once_with(
            expected_url,
            json={"casesIds": [123, 456], "username": "user@example.com"},
        )
        assert result == {}


def test_execute_bulk_assign_api_error(chronicle_client):
    """Test bulk assign with API error."""
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.text = "Permission denied"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to assign cases"):
            execute_bulk_assign(chronicle_client, [123], "user@example.com")


def test_execute_bulk_assign_json_parse_error(chronicle_client):
    """Test bulk assign with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse bulk assign response"
        ):
            execute_bulk_assign(chronicle_client, [123], "user@example.com")


# Tests for execute_bulk_change_priority


def test_execute_bulk_change_priority_with_enum(chronicle_client):
    """Test bulk change priority using CasePriority enum."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_change_priority(
            chronicle_client, [123, 456], CasePriority.HIGH
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:executeBulkChangePriority"
        )
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == expected_url
        assert call_args[1]["json"]["priority"] == "PRIORITY_HIGH"
        assert result == {}


def test_execute_bulk_change_priority_with_string(chronicle_client):
    """Test bulk change priority using string value."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_change_priority(
            chronicle_client, [123], "PRIORITY_MEDIUM"
        )

        call_args = mock_post.call_args
        assert call_args[1]["json"]["priority"] == "PRIORITY_MEDIUM"
        assert result == {}


def test_execute_bulk_change_priority_api_error(chronicle_client):
    """Test bulk change priority with API error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to change case priority"):
            execute_bulk_change_priority(
                chronicle_client, [123], CasePriority.HIGH
            )


def test_execute_bulk_change_priority_json_parse_error(
    chronicle_client,
):
    """Test bulk change priority with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse bulk change priority response"
        ):
            execute_bulk_change_priority(
                chronicle_client, [123], CasePriority.LOW
            )


# Tests for execute_bulk_change_stage


def test_execute_bulk_change_stage_success(chronicle_client):
    """Test successful bulk change stage operation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_change_stage(
            chronicle_client, [123, 456], "Investigation"
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:executeBulkChangeStage"
        )
        mock_post.assert_called_once_with(
            expected_url,
            json={"casesIds": [123, 456], "stage": "Investigation"},
        )
        assert result == {}


def test_execute_bulk_change_stage_api_error(chronicle_client):
    """Test bulk change stage with API error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid stage"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to change case stage"):
            execute_bulk_change_stage(chronicle_client, [123], "InvalidStage")


def test_execute_bulk_change_stage_json_parse_error(chronicle_client):
    """Test bulk change stage with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse bulk change stage response"
        ):
            execute_bulk_change_stage(chronicle_client, [123], "Investigation")


# Tests for execute_bulk_close


def test_execute_bulk_close_success(chronicle_client):
    """Test successful bulk close operation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "{}"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_close(
            chronicle_client,
            [123, 456],
            "FALSE_POSITIVE",
            root_cause="No threat",
            close_comment="Resolved",
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:executeBulkClose"
        )
        mock_post.assert_called_once_with(
            expected_url,
            json={
                "casesIds": [123, 456],
                "closeReason": "FALSE_POSITIVE",
                "rootCause": "No threat",
                "closeComment": "Resolved",
            },
        )
        assert result == {}


def test_execute_bulk_close_minimal_params(chronicle_client):
    """Test bulk close with minimal parameters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "{}"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_close(chronicle_client, [123], "RESOLVED")

        call_args = mock_post.call_args
        assert call_args[1]["json"] == {
            "casesIds": [123],
            "closeReason": "RESOLVED",
        }
        assert result == {}


def test_execute_bulk_close_empty_response(chronicle_client):
    """Test bulk close with empty response text."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = ""

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        result = execute_bulk_close(chronicle_client, [123], "RESOLVED")
        assert result == {}


def test_execute_bulk_close_with_dynamic_params(chronicle_client):
    """Test bulk close with dynamic parameters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "{}"
    mock_response.json.return_value = {}

    dynamic_params = [{"key": "value1"}, {"key": "value2"}]

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_close(
            chronicle_client,
            [123],
            "RESOLVED",
            dynamic_parameters=dynamic_params,
        )

        call_args = mock_post.call_args
        assert call_args[1]["json"]["dynamicParameters"] == dynamic_params
        assert result == {}


def test_execute_bulk_close_api_error(chronicle_client):
    """Test bulk close with API error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid close reason"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to close cases"):
            execute_bulk_close(chronicle_client, [123], "INVALID")


def test_execute_bulk_close_json_parse_error(chronicle_client):
    """Test bulk close with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "not empty"
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse bulk close response"
        ):
            execute_bulk_close(chronicle_client, [123], "RESOLVED")


# Tests for execute_bulk_reopen


def test_execute_bulk_reopen_success(chronicle_client):
    """Test successful bulk reopen operation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "{}"
    mock_response.json.return_value = {}

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = execute_bulk_reopen(
            chronicle_client, [123, 456], "Reopening for review"
        )

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:executeBulkReopen"
        )
        mock_post.assert_called_once_with(
            expected_url,
            json={
                "casesIds": [123, 456],
                "reopenComment": "Reopening for review",
            },
        )
        assert result == {}


def test_execute_bulk_reopen_empty_response(chronicle_client):
    """Test bulk reopen with empty response text."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = ""

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        result = execute_bulk_reopen(chronicle_client, [123], "Reopen")
        assert result == {}


def test_execute_bulk_reopen_api_error(chronicle_client):
    """Test bulk reopen with API error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Cannot reopen closed cases"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to reopen cases"):
            execute_bulk_reopen(chronicle_client, [123], "Reopen")


def test_execute_bulk_reopen_json_parse_error(chronicle_client):
    """Test bulk reopen with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "not empty"
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse bulk reopen response"
        ):
            execute_bulk_reopen(chronicle_client, [123], "Reopen")


# Tests for get_case


def test_get_case_with_id(chronicle_client, mock_case_data):
    """Test get case using just case ID."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_case_data

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = get_case(chronicle_client, "12345")

        # Verify URL construction
        expected_url = (
            f"{chronicle_client.base_url}/"
            f"{chronicle_client.instance_id}/cases/12345"
        )
        mock_get.assert_called_once_with(expected_url, params={})

        assert isinstance(result, Case)
        assert result.id == "12345"
        assert result.display_name == "Test Case"
        assert result.priority == "PRIORITY_HIGH"


def test_get_case_with_full_name(chronicle_client, mock_case_data):
    """Test get case using full resource name."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_case_data

    full_name = (
        "projects/test-project/locations/us/instances/"
        "test-customer/cases/12345"
    )

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = get_case(chronicle_client, full_name)

        expected_url = f"{chronicle_client.base_url}/{full_name}"
        mock_get.assert_called_once_with(expected_url, params={})

        assert isinstance(result, Case)
        assert result.id == "12345"


def test_get_case_with_expand(chronicle_client, mock_case_data):
    """Test get case with expand parameter."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_case_data

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = get_case(chronicle_client, "12345", expand="tags,products")

        call_args = mock_get.call_args
        assert call_args[1]["params"] == {"expand": "tags,products"}
        assert isinstance(result, Case)


def test_get_case_api_error(chronicle_client):
    """Test get case with API error."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Case not found"

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to get case"):
            get_case(chronicle_client, "99999")


def test_get_case_json_parse_error(chronicle_client):
    """Test get case with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to parse case response"):
            get_case(chronicle_client, "12345")


# Tests for list_cases


def test_list_cases_with_page_size(chronicle_client, mock_case_data):
    """Test list cases with page_size (single page)."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cases": [mock_case_data],
        "nextPageToken": "next-token",
        "totalSize": 100,
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_cases(chronicle_client, page_size=10)

        # Verify only one API call was made
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["pageSize"] == "10"

        assert len(result["cases"]) == 1
        assert result["nextPageToken"] == "next-token"
        assert result["totalSize"] == 100


def test_list_cases_auto_pagination(chronicle_client, mock_case_data):
    """Test list cases auto-pagination (page_size=None)."""
    # Mock two pages of results
    mock_response_1 = Mock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = {
        "cases": [mock_case_data],
        "nextPageToken": "page2-token",
        "totalSize": 2,
    }

    mock_case_data_2 = mock_case_data.copy()
    mock_case_data_2["id"] = "67890"

    mock_response_2 = Mock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = {
        "cases": [mock_case_data_2],
        "nextPageToken": "",
        "totalSize": 2,
    }

    with patch.object(
        chronicle_client.session,
        "get",
        side_effect=[mock_response_1, mock_response_2],
    ) as mock_get:
        result = list_cases(chronicle_client, page_size=None)

        # Verify two API calls were made
        assert mock_get.call_count == 2

        # Verify all cases were collected
        assert len(result["cases"]) == 2
        assert result["nextPageToken"] == ""
        assert result["totalSize"] == 2


def test_list_cases_with_filters(chronicle_client, mock_case_data):
    """Test list cases with filter, order, and expand."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cases": [mock_case_data],
        "nextPageToken": "",
        "totalSize": 1,
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_cases(
            chronicle_client,
            page_size=50,
            filter_query='priority="HIGH"',
            order_by="createdTime desc",
            expand="tags",
            distinct_by="priority",
        )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["filter"] == 'priority="HIGH"'
        assert params["orderBy"] == "createdTime desc"
        assert params["expand"] == "tags"
        assert params["distinctBy"] == "priority"


def test_list_cases_with_page_token(chronicle_client, mock_case_data):
    """Test list cases with page token."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cases": [mock_case_data],
        "nextPageToken": "",
        "totalSize": 1,
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = list_cases(
            chronicle_client, page_size=10, page_token="some-token"
        )

        call_args = mock_get.call_args
        assert call_args[1]["params"]["pageToken"] == "some-token"


def test_list_cases_api_error(chronicle_client):
    """Test list cases with API error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to list cases"):
            list_cases(chronicle_client, page_size=10)


def test_list_cases_json_parse_error(chronicle_client):
    """Test list cases with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse list cases response"
        ):
            list_cases(chronicle_client, page_size=10)


def test_list_cases_empty_results(chronicle_client):
    """Test list cases with no results."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "cases": [],
        "nextPageToken": "",
        "totalSize": 0,
    }

    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ):
        result = list_cases(chronicle_client, page_size=10)

        assert len(result["cases"]) == 0
        assert result["totalSize"] == 0


# Tests for merge_cases


def test_merge_cases_success(chronicle_client):
    """Test successful merge cases operation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "newCaseId": 999,
        "isRequestValid": True,
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = merge_cases(chronicle_client, [123, 456], 789)

        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "cases:merge"
        )
        mock_post.assert_called_once_with(
            expected_url,
            json={"casesIds": [123, 456], "caseToMergeWith": 789},
        )
        assert result["newCaseId"] == 999
        assert result["isRequestValid"] is True


def test_merge_cases_invalid_request(chronicle_client):
    """Test merge cases with invalid request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "isRequestValid": False,
        "errors": ["Cannot merge cases from different tenants"],
    }

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        result = merge_cases(chronicle_client, [123, 456], 789)

        assert result["isRequestValid"] is False
        assert len(result["errors"]) == 1


def test_merge_cases_api_error(chronicle_client):
    """Test merge cases with API error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid case IDs"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to merge cases"):
            merge_cases(chronicle_client, [123, 456], 789)


def test_merge_cases_json_parse_error(chronicle_client):
    """Test merge cases with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "post", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse merge cases response"
        ):
            merge_cases(chronicle_client, [123, 456], 789)


# Tests for patch_case


def test_patch_case_with_id(chronicle_client, mock_case_data):
    """Test patch case using just case ID."""
    updated_data = mock_case_data.copy()
    updated_data["priority"] = "PRIORITY_CRITICAL"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = updated_data

    case_update = {"priority": "PRIORITY_CRITICAL"}

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = patch_case(
            chronicle_client,
            "12345",
            case_update,
            update_mask="priority",
        )

        expected_url = (
            f"{chronicle_client.base_url}/"
            f"{chronicle_client.instance_id}/cases/12345"
        )
        mock_patch.assert_called_once()
        call_args = mock_patch.call_args
        assert call_args[0][0] == expected_url
        assert call_args[1]["json"] == case_update
        assert call_args[1]["params"] == {"updateMask": "priority"}

        assert isinstance(result, Case)
        assert result.priority == "PRIORITY_CRITICAL"


def test_patch_case_with_full_name(chronicle_client, mock_case_data):
    """Test patch case using full resource name."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_case_data

    full_name = (
        "projects/test-project/locations/us/instances/"
        "test-customer/cases/12345"
    )

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = patch_case(chronicle_client, full_name, {"status": "CLOSED"})

        expected_url = f"{chronicle_client.base_url}/{full_name}"
        call_args = mock_patch.call_args
        assert call_args[0][0] == expected_url
        assert isinstance(result, Case)


def test_patch_case_without_update_mask(chronicle_client, mock_case_data):
    """Test patch case without update mask."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_case_data

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = patch_case(
            chronicle_client, "12345", {"displayName": "Updated"}
        )

        call_args = mock_patch.call_args
        assert call_args[1]["params"] == {}
        assert isinstance(result, Case)


def test_patch_case_multiple_fields(chronicle_client, mock_case_data):
    """Test patch case with multiple fields."""
    updated_data = mock_case_data.copy()
    updated_data["priority"] = "PRIORITY_LOW"
    updated_data["stage"] = "Closed"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = updated_data

    case_update = {
        "priority": "PRIORITY_LOW",
        "stage": "Closed",
    }

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ):
        result = patch_case(
            chronicle_client,
            "12345",
            case_update,
            update_mask="priority,stage",
        )

        assert result.priority == "PRIORITY_LOW"
        assert result.stage == "Closed"


def test_patch_case_api_error(chronicle_client):
    """Test patch case with API error."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Case not found"

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ):
        with pytest.raises(APIError, match="Failed to patch case"):
            patch_case(chronicle_client, "99999", {"status": "CLOSED"})


def test_patch_case_json_parse_error(chronicle_client):
    """Test patch case with JSON parsing error."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(
        chronicle_client.session, "patch", return_value=mock_response
    ):
        with pytest.raises(
            APIError, match="Failed to parse patch case response"
        ):
            patch_case(chronicle_client, "12345", {"status": "CLOSED"})
