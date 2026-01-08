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
"""Tests for Chronicle investigation functions."""

import pytest
from unittest.mock import Mock, patch

from secops.chronicle.client import ChronicleClient
from secops.chronicle.investigations import (
    fetch_associated_investigations,
    get_investigation,
    list_investigations,
    trigger_investigation,
)
from secops.chronicle.models import DetectionType
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
    mock.json.return_value = {"success": True}
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock


def test_fetch_associated_investigations_with_alert_ids(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations with alert IDs."""
    mock_response.json.return_value = {
        "associationsList": {
            "alert1": {
                "investigations": [
                    {
                        "name": "projects/123/locations/us/instances/456/"
                        "investigations/inv1"
                    }
                ]
            }
        }
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client,
            detection_type=DetectionType.ALERT,
            alert_ids=["alert1", "alert2"],
            association_limit_per_detection=5,
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert "investigations:fetchAssociated" in call_args[1]["url"]
        assert call_args[1]["params"]["detectionType"] == "DETECTION_TYPE_ALERT"
        assert call_args[1]["params"]["alertIds"] == ["alert1", "alert2"]
        assert call_args[1]["params"]["associationLimitPerDetection"] == 5
        assert result["associationsList"] is not None


def test_fetch_associated_investigations_with_case_ids(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations with case IDs."""
    mock_response.json.return_value = {
        "associationsList": {
            "case1": {
                "investigations": [
                    {
                        "name": "projects/123/locations/us/instances/456/"
                        "investigations/inv1"
                    }
                ]
            }
        }
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client,
            detection_type=DetectionType.CASE,
            case_ids=["case1"],
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["detectionType"] == "DETECTION_TYPE_CASE"
        assert call_args[1]["params"]["caseIds"] == ["case1"]
        assert result["associationsList"] is not None


def test_fetch_associated_investigations_with_string_detection_type(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations with string detection type."""
    mock_response.json.return_value = {"associationsList": {}}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client,
            detection_type="DETECTION_TYPE_ALERT",
            alert_ids=["alert1"],
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["detectionType"] == "DETECTION_TYPE_ALERT"
        assert result is not None


def test_fetch_associated_investigations_with_enum_name(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations with enum name string."""
    mock_response.json.return_value = {"associationsList": {}}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client, detection_type="ALERT", alert_ids=["alert1"]
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["detectionType"] == "DETECTION_TYPE_ALERT"
        assert result is not None


def test_fetch_associated_investigations_with_order_by(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations with order_by parameter."""
    mock_response.json.return_value = {"associationsList": {}}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client,
            detection_type=DetectionType.ALERT,
            alert_ids=["alert1"],
            order_by="createTime desc",
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["orderBy"] == "createTime desc"
        assert result is not None


def test_fetch_associated_investigations_invalid_detection_type(
    chronicle_client,
):
    """Test fetch_associated_investigations with invalid detection type."""
    with pytest.raises(ValueError) as exc_info:
        fetch_associated_investigations(
            chronicle_client,
            detection_type="INVALID_TYPE",
            alert_ids=["alert1"],
        )

    assert "Invalid detection_type" in str(exc_info.value)
    assert "INVALID_TYPE" in str(exc_info.value)


def test_fetch_associated_investigations_error(
    chronicle_client, mock_error_response
):
    """Test fetch_associated_investigations with error response."""
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            fetch_associated_investigations(
                chronicle_client,
                detection_type=DetectionType.ALERT,
                alert_ids=["alert1"],
            )

        assert "Failed to fetch associated investigations" in str(
            exc_info.value
        )


def test_get_investigation_with_id(chronicle_client, mock_response):
    """Test get_investigation with investigation ID."""
    investigation_id = "82fb18cb-bfc0-4d7f-acf2-80508e145da2"
    mock_response.json.return_value = {
        "name": f"projects/123/locations/us/instances/456/investigations/"
        f"{investigation_id}",
        "verdict": "FALSE_POSITIVE",
        "status": "STATUS_COMPLETED_SUCCESS",
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = get_investigation(chronicle_client, investigation_id)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert f"investigations/{investigation_id}" in call_args[1]["url"]
        assert result["verdict"] == "FALSE_POSITIVE"
        assert result["status"] == "STATUS_COMPLETED_SUCCESS"


def test_get_investigation_with_full_resource_name(
    chronicle_client, mock_response
):
    """Test get_investigation with full resource name."""
    full_name = (
        "projects/123/locations/us/instances/456/investigations/"
        "82fb18cb-bfc0-4d7f-acf2-80508e145da2"
    )
    mock_response.json.return_value = {
        "name": full_name,
        "verdict": "MALICIOUS",
        "status": "STATUS_COMPLETED_SUCCESS",
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = get_investigation(chronicle_client, full_name)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert full_name in call_args[1]["url"]
        assert result["verdict"] == "MALICIOUS"


def test_get_investigation_error(chronicle_client, mock_error_response):
    """Test get_investigation with error response."""
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            get_investigation(
                chronicle_client, "82fb18cb-bfc0-4d7f-acf2-80508e145da2"
            )

        assert "Failed to get investigation" in str(exc_info.value)


def test_list_investigations_default(chronicle_client, mock_response):
    """Test list_investigations with default parameters."""
    mock_response.json.return_value = {
        "investigations": [
            {"name": "inv1", "verdict": "MALICIOUS"},
            {"name": "inv2", "verdict": "FALSE_POSITIVE"},
        ],
        "totalSize": 2,
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(chronicle_client)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert "investigations" in call_args[1]["url"]
        assert "params" in call_args[1]
        assert len(result["investigations"]) == 2


def test_list_investigations_with_page_size(chronicle_client, mock_response):
    """Test list_investigations with page_size parameter."""
    mock_response.json.return_value = {
        "investigations": [{"name": "inv1"}],
        "totalSize": 1,
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(chronicle_client, page_size=10)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["pageSize"] == 10
        assert result["totalSize"] == 1


def test_list_investigations_with_page_token(chronicle_client, mock_response):
    """Test list_investigations with page_token parameter."""
    mock_response.json.return_value = {
        "investigations": [{"name": "inv1"}],
        "nextPageToken": "token123",
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(
            chronicle_client, page_token="previous_token"
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["pageToken"] == "previous_token"
        assert result["nextPageToken"] == "token123"


def test_list_investigations_with_filter(chronicle_client, mock_response):
    """Test list_investigations with filter expression."""
    mock_response.json.return_value = {
        "investigations": [{"name": "inv1"}],
        "totalSize": 1,
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(
            chronicle_client, filter_expr='alertId="alert123"'
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["filter"] == 'alertId="alert123"'
        assert result["totalSize"] == 1


def test_list_investigations_with_order_by(chronicle_client, mock_response):
    """Test list_investigations with order_by parameter."""
    mock_response.json.return_value = {
        "investigations": [{"name": "inv1"}],
        "totalSize": 1,
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(
            chronicle_client, order_by="startTime desc"
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["orderBy"] == "startTime desc"
        assert result["totalSize"] == 1


def test_list_investigations_with_all_params(chronicle_client, mock_response):
    """Test list_investigations with all parameters."""
    mock_response.json.return_value = {
        "investigations": [{"name": "inv1"}],
        "nextPageToken": "next_token",
        "totalSize": 100,
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(
            chronicle_client,
            page_size=50,
            page_token="current_token",
            filter_expr='status="COMPLETED"',
            order_by="endTime",
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["pageSize"] == 50
        assert params["pageToken"] == "current_token"
        assert params["filter"] == 'status="COMPLETED"'
        assert params["orderBy"] == "endTime"
        assert result["totalSize"] == 100


def test_list_investigations_empty_results(chronicle_client, mock_response):
    """Test list_investigations with empty results."""
    mock_response.json.return_value = {"investigations": [], "totalSize": 0}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(chronicle_client)

        mock_request.assert_called_once()
        assert result["investigations"] == []
        assert result["totalSize"] == 0


def test_list_investigations_error(chronicle_client, mock_error_response):
    """Test list_investigations with error response."""
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            list_investigations(chronicle_client)

        assert "Failed to list investigations" in str(exc_info.value)


def test_trigger_investigation_success(chronicle_client, mock_response):
    """Test trigger_investigation with successful response."""
    alert_id = "de_e0b58924-dc71-ad17-8cc0-603b7d54b1ad"
    mock_response.json.return_value = {
        "name": "projects/123/locations/us/instances/456/investigations/inv1",
        "verdict": "UNSPECIFIED",
        "status": "STATUS_IN_PROGRESS",
        "alerts": {"ids": [alert_id]},
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = trigger_investigation(chronicle_client, alert_id)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert "investigations:trigger" in call_args[1]["url"]
        assert call_args[1]["json"]["alertId"] == alert_id
        assert result["status"] == "STATUS_IN_PROGRESS"
        assert alert_id in result["alerts"]["ids"]


def test_trigger_investigation_with_different_alert_format(
    chronicle_client, mock_response
):
    """Test trigger_investigation with different alert ID format."""
    alert_id = "alert_12345"
    mock_response.json.return_value = {
        "name": "projects/123/locations/us/instances/456/investigations/inv1",
        "verdict": "UNSPECIFIED",
        "status": "STATUS_IN_PROGRESS",
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = trigger_investigation(chronicle_client, alert_id)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["json"]["alertId"] == alert_id
        assert result["status"] == "STATUS_IN_PROGRESS"


def test_trigger_investigation_error(chronicle_client, mock_error_response):
    """Test trigger_investigation with error response."""
    with patch.object(
        chronicle_client.session, "request", return_value=mock_error_response
    ):
        with pytest.raises(APIError) as exc_info:
            trigger_investigation(
                chronicle_client, "de_e0b58924-dc71-ad17-8cc0-603b7d54b1ad"
            )

        assert "Failed to trigger investigation" in str(exc_info.value)


def test_fetch_associated_investigations_unspecified_type(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations with UNSPECIFIED type."""
    mock_response.json.return_value = {"associationsList": {}}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client,
            detection_type=DetectionType.UNSPECIFIED,
            alert_ids=["alert1"],
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert (
            call_args[1]["params"]["detectionType"]
            == "DETECTION_TYPE_UNSPECIFIED"
        )
        assert result is not None


def test_fetch_associated_investigations_no_optional_params(
    chronicle_client, mock_response
):
    """Test fetch_associated_investigations without optional params."""
    mock_response.json.return_value = {"associationsList": {}}

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = fetch_associated_investigations(
            chronicle_client,
            detection_type=DetectionType.ALERT,
            alert_ids=["alert1"],
        )

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert "associationLimitPerDetection" not in params
        assert "orderBy" not in params
        assert result is not None


def test_list_investigations_no_optional_params(
    chronicle_client, mock_response
):
    """Test list_investigations without optional parameters."""
    mock_response.json.return_value = {
        "investigations": [{"name": "inv1"}],
        "totalSize": 1,
    }

    with patch.object(
        chronicle_client.session, "request", return_value=mock_response
    ) as mock_request:
        result = list_investigations(chronicle_client)

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert "pageSize" not in params or params.get("pageSize") is None
        assert "pageToken" not in params or params.get("pageToken") is None
        assert "filter" not in params
        assert "orderBy" not in params
        assert result["totalSize"] == 1
