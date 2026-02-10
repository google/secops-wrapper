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
from secops.chronicle import case as case_module
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
    mock_return = {}

    with patch.object(
        case_module, "chronicle_request", return_value=mock_return
    ) as mock_request:
        result = execute_bulk_add_tag(
            chronicle_client, [123, 456], ["tag1", "tag2"]
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint_path"] == "cases:executeBulkAddTag"
        assert call_args[1]["json"] == {
            "casesIds": [123, 456],
            "tags": ["tag1", "tag2"],
        }
        assert result == {}


def test_execute_bulk_add_tag_api_error(chronicle_client):
    """Test bulk add tag with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to add tags to cases"),
    ):
        with pytest.raises(APIError, match="Failed to add tags to cases"):
            execute_bulk_add_tag(chronicle_client, [123], ["tag1"])


def test_execute_bulk_add_tag_empty_tags(chronicle_client):
    """Test bulk add tag with empty tags list."""
    with patch.object(case_module, "chronicle_request", return_value={}):
        result = execute_bulk_add_tag(chronicle_client, [123], [])
        assert result == {}


def test_execute_bulk_add_tag_json_parse_error(chronicle_client):
    """Test bulk add tag with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            execute_bulk_add_tag(chronicle_client, [123], ["tag1"])


# Tests for execute_bulk_assign


def test_execute_bulk_assign_success(chronicle_client):
    """Test successful bulk assign operation."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_assign(
            chronicle_client, [123, 456], "user@example.com"
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint_path"] == "cases:executeBulkAssign"
        assert call_args[1]["json"] == {
            "casesIds": [123, 456],
            "username": "user@example.com",
        }
        assert result == {}


def test_execute_bulk_assign_api_error(chronicle_client):
    """Test bulk assign with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to assign cases"),
    ):
        with pytest.raises(APIError, match="Failed to assign cases"):
            execute_bulk_assign(chronicle_client, [123], "user@example.com")


def test_execute_bulk_assign_json_parse_error(chronicle_client):
    """Test bulk assign with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            execute_bulk_assign(chronicle_client, [123], "user@example.com")


# Tests for execute_bulk_change_priority


def test_execute_bulk_change_priority_with_enum(chronicle_client):
    """Test bulk change priority using CasePriority enum."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_change_priority(
            chronicle_client, [123, 456], CasePriority.HIGH
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert (
            call_args[1]["endpoint_path"] == "cases:executeBulkChangePriority"
        )
        assert str(call_args[1]["json"]["priority"]) == "PRIORITY_HIGH"
        assert result == {}


def test_execute_bulk_change_priority_with_string(chronicle_client):
    """Test bulk change priority using string value."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_change_priority(
            chronicle_client, [123], "PRIORITY_MEDIUM"
        )

        call_args = mock_request.call_args
        assert str(call_args[1]["json"]["priority"]) == "PRIORITY_MEDIUM"
        assert result == {}


def test_execute_bulk_change_priority_api_error(chronicle_client):
    """Test bulk change priority with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to change case priority"),
    ):
        with pytest.raises(APIError, match="Failed to change case priority"):
            execute_bulk_change_priority(
                chronicle_client, [123], CasePriority.HIGH
            )


def test_execute_bulk_change_priority_json_parse_error(
    chronicle_client,
):
    """Test bulk change priority with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            execute_bulk_change_priority(
                chronicle_client, [123], CasePriority.LOW
            )


# Tests for execute_bulk_change_stage


def test_execute_bulk_change_stage_success(chronicle_client):
    """Test successful bulk change stage operation."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_change_stage(
            chronicle_client, [123, 456], "Investigation"
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint_path"] == "cases:executeBulkChangeStage"
        assert call_args[1]["json"] == {
            "casesIds": [123, 456],
            "stage": "Investigation",
        }
        assert result == {}


def test_execute_bulk_change_stage_api_error(chronicle_client):
    """Test bulk change stage with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to change case stage"),
    ):
        with pytest.raises(APIError, match="Failed to change case stage"):
            execute_bulk_change_stage(chronicle_client, [123], "InvalidStage")


def test_execute_bulk_change_stage_json_parse_error(chronicle_client):
    """Test bulk change stage with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            execute_bulk_change_stage(chronicle_client, [123], "Investigation")


# Tests for execute_bulk_close


def test_execute_bulk_close_success(chronicle_client):
    """Test successful bulk close operation."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_close(
            chronicle_client,
            [123, 456],
            "NOT_MALICIOUS",
            root_cause="No threat",
            close_comment="Resolved",
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint_path"] == "cases:executeBulkClose"
        json_body = call_args[1]["json"]
        assert json_body["casesIds"] == [123, 456]
        assert str(json_body["closeReason"]) == "NOT_MALICIOUS"
        assert json_body["rootCause"] == "No threat"
        assert json_body["closeComment"] == "Resolved"
        assert result == {}


def test_execute_bulk_close_minimal_params(chronicle_client):
    """Test bulk close with minimal parameters."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_close(chronicle_client, [123], "MALICIOUS")

        call_args = mock_request.call_args
        json_body = call_args[1]["json"]
        assert json_body["casesIds"] == [123]
        assert str(json_body["closeReason"]) == "MALICIOUS"
        assert result == {}


def test_execute_bulk_close_empty_response(chronicle_client):
    """Test bulk close with empty response text."""
    with patch.object(case_module, "chronicle_request", return_value={}):
        result = execute_bulk_close(chronicle_client, [123], "INCONCLUSIVE")
        assert result == {}


def test_execute_bulk_close_with_dynamic_params(chronicle_client):
    """Test bulk close with dynamic parameters."""
    dynamic_params = [{"key": "value1"}, {"key": "value2"}]

    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_close(
            chronicle_client,
            [123],
            "MAINTENANCE",
            dynamic_parameters=dynamic_params,
        )

        call_args = mock_request.call_args
        assert call_args[1]["json"]["dynamicParameters"] == dynamic_params
        assert result == {}


def test_execute_bulk_close_api_error(chronicle_client):
    """Test bulk close with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to close cases"),
    ):
        with pytest.raises(APIError, match="Failed to close cases"):
            execute_bulk_close(chronicle_client, [123], "MALICIOUS")


def test_execute_bulk_close_json_parse_error(chronicle_client):
    """Test bulk close with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            execute_bulk_close(chronicle_client, [123], "UNKNOWN")


# Tests for execute_bulk_reopen


def test_execute_bulk_reopen_success(chronicle_client):
    """Test successful bulk reopen operation."""
    with patch.object(
        case_module, "chronicle_request", return_value={}
    ) as mock_request:
        result = execute_bulk_reopen(
            chronicle_client, [123, 456], "Reopening for review"
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint_path"] == "cases:executeBulkReopen"
        assert call_args[1]["json"] == {
            "casesIds": [123, 456],
            "reopenComment": "Reopening for review",
        }
        assert result == {}


def test_execute_bulk_reopen_empty_response(chronicle_client):
    """Test bulk reopen with empty response text."""
    with patch.object(case_module, "chronicle_request", return_value={}):
        result = execute_bulk_reopen(chronicle_client, [123], "Reopen")
        assert result == {}


def test_execute_bulk_reopen_api_error(chronicle_client):
    """Test bulk reopen with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to reopen cases"),
    ):
        with pytest.raises(APIError, match="Failed to reopen cases"):
            execute_bulk_reopen(chronicle_client, [123], "Reopen")


def test_execute_bulk_reopen_json_parse_error(chronicle_client):
    """Test bulk reopen with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            execute_bulk_reopen(chronicle_client, [123], "Reopen")


# Tests for get_case


def test_get_case_with_id(chronicle_client, mock_case_data):
    """Test get case using just case ID."""
    with patch.object(
        case_module, "chronicle_request", return_value=mock_case_data
    ) as mock_request:
        result = get_case(chronicle_client, "12345")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint_path"] == "cases/12345"
        assert not call_args[1]["params"]

        assert isinstance(result, Case)
        assert result.id == "12345"
        assert result.display_name == "Test Case"
        assert result.priority == "PRIORITY_HIGH"


def test_get_case_with_full_name(chronicle_client, mock_case_data):
    """Test get case using full resource name."""
    full_name = (
        "projects/test-project/locations/us/instances/"
        "test-customer/cases/12345"
    )

    with patch.object(
        case_module, "chronicle_request", return_value=mock_case_data
    ) as mock_request:
        result = get_case(chronicle_client, full_name)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["endpoint_path"] == full_name

        assert isinstance(result, Case)
        assert result.id == "12345"


def test_get_case_with_expand(chronicle_client, mock_case_data):
    """Test get case with expand parameter."""
    with patch.object(
        case_module, "chronicle_request", return_value=mock_case_data
    ) as mock_request:
        result = get_case(chronicle_client, "12345", expand="tags,products")

        call_args = mock_request.call_args
        assert call_args[1]["params"] == {"expand": "tags,products"}
        assert isinstance(result, Case)


def test_get_case_api_error(chronicle_client):
    """Test get case with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to get case"),
    ):
        with pytest.raises(APIError, match="Failed to get case"):
            get_case(chronicle_client, "99999")


def test_get_case_json_parse_error(chronicle_client):
    """Test get case with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            get_case(chronicle_client, "12345")


# Tests for list_cases


def test_list_cases_with_page_size(chronicle_client, mock_case_data):
    """Test list cases with page_size (single page)."""
    mock_return = {
        "cases": [mock_case_data],
        "nextPageToken": "next-token",
        "totalSize": 100,
    }

    with patch.object(
        case_module,
        "chronicle_paginated_request",
        return_value=mock_return,
    ) as mock_paginated:
        result = list_cases(chronicle_client, page_size=10)

        mock_paginated.assert_called_once()
        call_args = mock_paginated.call_args
        assert call_args[1]["page_size"] == 10
        assert call_args[1]["items_key"] == "cases"

        assert len(result["cases"]) == 1
        assert result["nextPageToken"] == "next-token"
        assert result["totalSize"] == 100


def test_list_cases_auto_pagination(chronicle_client, mock_case_data):
    """Test list cases auto-pagination (page_size=None)."""
    mock_case_data_2 = mock_case_data.copy()
    mock_case_data_2["id"] = "67890"

    mock_return = {
        "cases": [mock_case_data, mock_case_data_2],
        "nextPageToken": "",
        "totalSize": 2,
    }

    with patch.object(
        case_module,
        "chronicle_paginated_request",
        return_value=mock_return,
    ) as mock_paginated:
        result = list_cases(chronicle_client, page_size=None)

        mock_paginated.assert_called_once()
        call_args = mock_paginated.call_args
        assert call_args[1]["page_size"] is None

        assert len(result["cases"]) == 2
        assert result["nextPageToken"] == ""
        assert result["totalSize"] == 2


def test_list_cases_with_filters(chronicle_client, mock_case_data):
    """Test list cases with filter, order, and expand."""
    mock_return = {
        "cases": [mock_case_data],
        "nextPageToken": "",
        "totalSize": 1,
    }

    with patch.object(
        case_module,
        "chronicle_paginated_request",
        return_value=mock_return,
    ) as mock_paginated:
        result = list_cases(
            chronicle_client,
            page_size=50,
            filter_query='priority="HIGH"',
            order_by="createdTime desc",
            expand="tags",
            distinct_by="priority",
        )

        call_args = mock_paginated.call_args
        extra_params = call_args[1]["extra_params"]
        assert extra_params["filter"] == 'priority="HIGH"'
        assert extra_params["orderBy"] == "createdTime desc"
        assert extra_params["expand"] == "tags"
        assert extra_params["distinctBy"] == "priority"


def test_list_cases_with_page_token(chronicle_client, mock_case_data):
    """Test list cases with page token."""
    mock_return = {
        "cases": [mock_case_data],
        "nextPageToken": "",
        "totalSize": 1,
    }

    with patch.object(
        case_module,
        "chronicle_paginated_request",
        return_value=mock_return,
    ) as mock_paginated:
        result = list_cases(
            chronicle_client, page_size=10, page_token="some-token"
        )

        call_args = mock_paginated.call_args
        assert call_args[1]["page_token"] == "some-token"


def test_list_cases_api_error(chronicle_client):
    """Test list cases with API error."""
    with patch.object(
        case_module,
        "chronicle_paginated_request",
        side_effect=APIError("Failed to list cases"),
    ):
        with pytest.raises(APIError):
            list_cases(chronicle_client, page_size=10)


def test_list_cases_json_parse_error(chronicle_client):
    """Test list cases with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_paginated_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            list_cases(chronicle_client, page_size=10)


def test_list_cases_empty_results(chronicle_client):
    """Test list cases with no results."""
    mock_return = {
        "cases": [],
        "nextPageToken": "",
        "totalSize": 0,
    }

    with patch.object(
        case_module,
        "chronicle_paginated_request",
        return_value=mock_return,
    ):
        result = list_cases(chronicle_client, page_size=10)

        assert len(result["cases"]) == 0
        assert result["totalSize"] == 0


# Tests for merge_cases


def test_merge_cases_success(chronicle_client):
    """Test successful merge cases operation."""
    mock_return = {
        "newCaseId": 999,
        "isRequestValid": True,
    }

    with patch.object(
        case_module, "chronicle_request", return_value=mock_return
    ) as mock_request:
        result = merge_cases(chronicle_client, [123, 456], 789)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint_path"] == "cases:merge"
        assert set(call_args[1]["json"]["casesIds"]) == {123, 456, 789}
        assert call_args[1]["json"]["caseToMergeWith"] == 789
        assert result["newCaseId"] == 999
        assert result["isRequestValid"] is True


def test_merge_cases_invalid_request(chronicle_client):
    """Test merge cases with invalid request."""
    mock_return = {
        "isRequestValid": False,
        "errors": ["Cannot merge cases from different tenants"],
    }

    with patch.object(
        case_module, "chronicle_request", return_value=mock_return
    ):
        result = merge_cases(chronicle_client, [123, 456], 789)

        assert result["isRequestValid"] is False
        assert len(result["errors"]) == 1


def test_merge_cases_api_error(chronicle_client):
    """Test merge cases with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to merge cases"),
    ):
        with pytest.raises(APIError, match="Failed to merge cases"):
            merge_cases(chronicle_client, [123, 456], 789)


def test_merge_cases_json_parse_error(chronicle_client):
    """Test merge cases with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            merge_cases(chronicle_client, [123, 456], 789)


# Tests for patch_case


def test_patch_case_with_id(chronicle_client, mock_case_data):
    """Test patch case using just case ID."""
    updated_data = mock_case_data.copy()
    updated_data["priority"] = "PRIORITY_CRITICAL"

    case_update = {"priority": "PRIORITY_CRITICAL"}

    with patch.object(
        case_module, "chronicle_request", return_value=updated_data
    ) as mock_request:
        result = patch_case(
            chronicle_client,
            "12345",
            case_update,
            update_mask="priority",
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "PATCH"
        assert call_args[1]["endpoint_path"] == "cases/12345"
        assert str(call_args[1]["json"]["priority"]) == "PRIORITY_CRITICAL"
        assert call_args[1]["params"] == {"updateMask": "priority"}

        assert isinstance(result, Case)
        assert result.priority == "PRIORITY_CRITICAL"


def test_patch_case_with_full_name(chronicle_client, mock_case_data):
    """Test patch case using full resource name."""
    full_name = (
        "projects/test-project/locations/us/instances/"
        "test-customer/cases/12345"
    )

    with patch.object(
        case_module, "chronicle_request", return_value=mock_case_data
    ) as mock_request:
        result = patch_case(chronicle_client, full_name, {"status": "CLOSED"})

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["endpoint_path"] == full_name
        assert isinstance(result, Case)


def test_patch_case_without_update_mask(chronicle_client, mock_case_data):
    """Test patch case without update mask."""
    with patch.object(
        case_module, "chronicle_request", return_value=mock_case_data
    ) as mock_request:
        result = patch_case(
            chronicle_client, "12345", {"displayName": "Updated"}
        )

        call_args = mock_request.call_args
        assert call_args[1]["params"] is None
        assert isinstance(result, Case)


def test_patch_case_multiple_fields(chronicle_client, mock_case_data):
    """Test patch case with multiple fields."""
    updated_data = mock_case_data.copy()
    updated_data["priority"] = "PRIORITY_LOW"
    updated_data["stage"] = "Closed"

    case_update = {
        "priority": "PRIORITY_LOW",
        "stage": "Closed",
    }

    with patch.object(
        case_module, "chronicle_request", return_value=updated_data
    ) as mock_request:
        result = patch_case(
            chronicle_client,
            "12345",
            case_update,
            update_mask="priority,stage",
        )

        call_args = mock_request.call_args
        assert str(call_args[1]["json"]["priority"]) == "PRIORITY_LOW"
        assert call_args[1]["json"]["stage"] == "Closed"
        assert result.priority == "PRIORITY_LOW"
        assert result.stage == "Closed"


def test_patch_case_api_error(chronicle_client):
    """Test patch case with API error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Failed to patch case"),
    ):
        with pytest.raises(APIError, match="Failed to patch case"):
            patch_case(chronicle_client, "99999", {"status": "CLOSED"})


def test_patch_case_json_parse_error(chronicle_client):
    """Test patch case with JSON parsing error."""
    with patch.object(
        case_module,
        "chronicle_request",
        side_effect=APIError("Expected JSON response"),
    ):
        with pytest.raises(APIError):
            patch_case(chronicle_client, "12345", {"status": "CLOSED"})
