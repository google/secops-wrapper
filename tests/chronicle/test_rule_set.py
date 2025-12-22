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
"""Tests for Chronicle curated rule set functions."""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.rule_set import (
    _paginated_request,
    get_curated_rule,
    list_curated_rules,
    get_curated_rule_by_name,
    get_curated_rule_set,
    get_curated_rule_set_category,
    list_curated_rule_sets,
    list_curated_rule_set_categories,
    list_curated_rule_set_deployments,
    get_curated_rule_set_deployment,
    get_curated_rule_set_deployment_by_name,
    update_curated_rule_set_deployment,
    batch_update_curated_rule_set_deployments,
    search_curated_detections,
)
from secops.chronicle.models import AlertState, ListBasis
from secops.exceptions import APIError, SecOpsError


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
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    # Default return value, can be overridden in specific tests
    mock.json.return_value = {}
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response object."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception(
        "API Error"
    )  # To simulate requests.exceptions.HTTPError
    return mock


# --- get_curated_rule tests ---
def test_get_curated_rule_success(chronicle_client, mock_response):
    """Test get_curated_rule returns the JSON for a curated rule when the request succeeds."""
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/curatedRules/ur_abc-123",
        "displayName": "Test ABC 123",
    }
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mocked_request:
        result = get_curated_rule(chronicle_client, "ur_abc-123")
        assert result == mock_response.json.return_value
        # Verify URL
        expected_url = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            f"curatedRules/ur_abc-123"
        )
        mocked_request.assert_called_once_with(expected_url)


def test_get_curated_rule_error(chronicle_client, mock_error_response):
    """Test get_curated_rule raises APIError when the API returns non-200."""
    # Arrange
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        # Act and Assert
        with pytest.raises(APIError):
            get_curated_rule(chronicle_client, "ur_abc-123")


# --- helpers ---


def _page(items_key: str, items: list[dict], next_token: Optional[str] = None):
    """Helper function for paginated 200 OK responses."""
    data = {items_key: items}
    if next_token:
        data["nextPageToken"] = next_token
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = data
    return resp


# --- _paginated_request  tests ---


def test_paginated_request_auto_paginates_success(chronicle_client):
    p1 = _page("curatedRules", [{"name": ".../ur_1"}], next_token="t2")
    p2 = _page("curatedRules", [{"name": ".../ur_2"}])
    with patch.object(
        chronicle_client.session, "get", side_effect=[p1, p2]
    ) as mocked:
        result = _paginated_request(
            chronicle_client,
            path="curatedRules",
            items_key="curatedRules",
            page_size=None,
        )
        assert [r["name"] for r in result.get("curatedRules")] == [
            ".../ur_1",
            ".../ur_2",
        ]
        base = f"{chronicle_client.base_url}/{chronicle_client.instance_id}/curatedRules"
        assert mocked.call_args_list[0].args[0] == base
        assert mocked.call_args_list[0].kwargs["params"] == {"pageSize": 1000}
        assert mocked.call_args_list[1].kwargs["params"] == {
            "pageSize": 1000,
            "pageToken": "t2",
        }


def test_paginated_request_when_page_size_given_success(chronicle_client):
    p1 = _page("curatedRules", [{"name": ".../ur_1"}], next_token="t2")
    with patch.object(
        chronicle_client.session, "get", return_value=p1
    ) as mocked:
        result = _paginated_request(
            chronicle_client,
            path="curatedRules",
            items_key="curatedRules",
            page_size=1000,
        )
        assert [r["name"] for r in result.get("curatedRules")] == [".../ur_1"]
        # Only one call, no follow-up with nextPageToken
        assert mocked.call_count == 1
        assert mocked.call_args.kwargs["params"] == {"pageSize": 1000}


def test_paginated_request_error(chronicle_client, mock_error_response):
    """Test helper function _paginated_request raises APIError on HTTP errors."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            _paginated_request(
                chronicle_client,
                path="curatedRules",
                items_key="curatedRules",
            )


# --- list_curated_rule_sets & list_curated_rule_set_categories function tests ---
def test_list_curated_rules_success(chronicle_client, mock_response):
    """Test list_curated_rules"""
    mock_response.json.return_value = {"curatedRules": [{"name": "n1"}]}
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ):
        rules = list_curated_rules(chronicle_client, page_size=50)
        assert rules == {"curatedRules": [{"name": "n1"}]}


def test_list_curated_rules_error(chronicle_client, mock_error_response):
    """Test list_curated_rules failure."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            list_curated_rules(chronicle_client)


def test_list_curated_rule_sets_and_categories_success(
    chronicle_client, mock_response
):
    """Test the two list_ functions."""
    mock_response.json.side_effect = [
        {"curatedRuleSets": [{"name": "rs1"}]},
        {"curatedRuleSetCategories": [{"name": "cat1"}]},
    ]
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as mocked_response:
        rule_sets = list_curated_rule_sets(chronicle_client)
        categories = list_curated_rule_set_categories(chronicle_client)
        assert rule_sets == [{"name": "rs1"}]
        assert categories == [{"name": "cat1"}]
        # ensure two calls happened
        assert mocked_response.call_count == 2


def test_list_curated_rule_sets_and_categories_error(
    chronicle_client, mock_error_response
):
    """Test the two list_ functions error correctly."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            list_curated_rule_sets(chronicle_client)
            list_curated_rule_set_categories(chronicle_client)


# --- get_curated_rule_by_name tests---


def test_get_curated_rule_by_name_success(chronicle_client):
    """Test get_curated_rule_by_name returns the rule matching displayName (case-insensitive)."""
    p = _page(
        "curatedRules",
        [
            {"displayName": "Alpha", "name": ".../ur_A"},
            {"displayName": "Bravo", "name": ".../ur_B"},
        ],
    )
    with patch.object(chronicle_client.session, "get", return_value=p):
        out = get_curated_rule_by_name(chronicle_client, "bravo")
        assert out["name"].endswith("ur_B")


def test_get_curated_rule_by_name_error(chronicle_client):
    """Test get_curated_rule_by_name raises SecOpsError when not found."""
    p = _page("curatedRules", [{"displayName": "Alpha"}])
    with patch.object(chronicle_client.session, "get", return_value=p):
        with pytest.raises(SecOpsError):
            get_curated_rule_by_name(chronicle_client, "charlie")


# --- get_curated_rule_set tests ---


def test_get_curated_rule_set_success(chronicle_client, mock_response):
    """Test get_curated_rule_set returns the rule set matching name."""
    mock_response.json.return_value = {"name": ".../curatedRuleSets/crs_1"}
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as get_:
        out = get_curated_rule_set(chronicle_client, "crs_1")
        assert out["name"].endswith("/crs_1")
        expected = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "curatedRuleSetCategories/-/curatedRuleSets/crs_1"
        )
        get_.assert_called_once()
        assert get_.call_args.args[0] == expected


def test_get_curated_rule_set_error(chronicle_client, mock_error_response):
    """Test get_curated_rule_set raises APIError on HTTP errors."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            get_curated_rule_set(chronicle_client, "crs_1")


# --- get_curated_rule_set_category tests ---
def test_get_curated_rule_set_category_success(chronicle_client, mock_response):
    mock_response.json.return_value = {
        "name": ".../curatedRuleSetCategories/cat_1"
    }
    with patch.object(
        chronicle_client.session, "get", return_value=mock_response
    ) as get_:
        out = get_curated_rule_set_category(chronicle_client, "cat_1")
        assert out["name"].endswith("/cat_1")
        expected = (
            f"{chronicle_client.base_url}/{chronicle_client.instance_id}/"
            "curatedRuleSetCategories/cat_1"
        )
        assert get_.call_args.args[0] == expected


def test_get_curated_rule_set_category_error(
    chronicle_client, mock_error_response
):
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            get_curated_rule_set_category(chronicle_client, "cat_1")


# --- list_curated_rule_set_deployments ---


def test_list_deployments_success(chronicle_client):
    """Test list_curated_rule_set_deployments enriches deployments with displayName and respects filters."""
    deployments_page = _page(
        "curatedRuleSetDeployments",
        [
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1/curatedRuleSetDeployments/precise",
                "enabled": True,
                "alerting": False,
            },
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_2/curatedRuleSetDeployments/broad",
                "enabled": False,
                "alerting": True,
            },
        ],
    )
    rulesets_page = _page(
        "curatedRuleSets",
        [
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
                "displayName": "One",
            },
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_2",
                "displayName": "Two",
            },
        ],
    )

    # First: list deployments & list rulesets for enrichment
    with patch.object(
        chronicle_client.session,
        "get",
        side_effect=[deployments_page, rulesets_page],
    ):
        out = list_curated_rule_set_deployments(chronicle_client)
        names = {d["displayName"] for d in out}
        assert names == {"One", "Two"}

    # Now verify only_enabled and only_alerting filters
    with patch.object(
        chronicle_client.session,
        "get",
        side_effect=[deployments_page, rulesets_page],
    ):
        out_enabled = list_curated_rule_set_deployments(
            chronicle_client, only_enabled=True
        )
        assert len(out_enabled) == 1 and out_enabled[0]["displayName"] == "One"

    deployments_page_alerting = _page(
        "curatedRuleSetDeployments",
        [
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1/curatedRuleSetDeployments/precise",
                "enabled": True,
                "alerting": False,
            },
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_2/curatedRuleSetDeployments/broad",
                "enabled": False,
                "alerting": True,
            },
        ],
    )
    rulesets_page_alerting = _page(
        "curatedRuleSets",
        [
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
                "displayName": "One",
            },
            {
                "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_2",
                "displayName": "Two",
            },
        ],
    )

    with patch.object(
        chronicle_client.session,
        "get",
        side_effect=[deployments_page_alerting, rulesets_page_alerting],
    ):
        out_alerting = list_curated_rule_set_deployments(
            chronicle_client, only_alerting=True
        )
        assert (
            len(out_alerting) == 1 and out_alerting[0]["displayName"] == "Two"
        )


# --- get_curated_rule_set_deployment ---


def test_get_ruleset_deployment_success(chronicle_client, mock_response):
    """Test get_curated_rule_set_deployment returns the deployment matching name."""
    ruleset = Mock()
    ruleset.status_code = 200
    ruleset.json.return_value = {
        "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
        "displayName": "My Ruleset",
    }

    deployment = Mock()
    deployment.status_code = 200
    deployment.json.return_value = {"enabled": True, "alerting": False}

    with patch.object(
        chronicle_client.session, "get", side_effect=[ruleset, deployment]
    ) as mocked_request:
        out = get_curated_rule_set_deployment(
            chronicle_client, "crs_1", "precise"
        )
        assert out["displayName"] == "My Ruleset"

        dep_url = (
            f"{chronicle_client.base_url}/"
            f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1/"
            "curatedRuleSetDeployments/precise"
        )
        assert mocked_request.call_args_list[1].args[0] == dep_url


def test_get_ruleset_deployment_error_invalid_precision(chronicle_client):
    """Test get_curated_rule_set_deployment failure."""
    with pytest.raises(SecOpsError):
        get_curated_rule_set_deployment(chronicle_client, "crs_1", "medium")


def test_get_ruleset_deployment_ruleset_error_not_found(chronicle_client):
    """Test get_curated_rule_set_deployment failure when ruleset ID doesn't exist."""
    not_found = Mock()
    not_found.status_code = 404
    not_found.text = "Not found"

    with patch.object(chronicle_client.session, "get", return_value=not_found):
        with pytest.raises(APIError):
            get_curated_rule_set_deployment(
                chronicle_client, "crs_404", "precise"
            )


# --- get_curated_rule_set_deployment_by_name ---


def test_get_ruleset_deployment_by_name_success(chronicle_client):
    """Test get_curated_rule_set_deployment_by_name success."""
    rulesets_data = [
        {
            "name": f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
            "displayName": "Case Insensitive Name",
        }
    ]
    deployment = Mock()
    deployment.status_code = 200
    deployment.json.return_value = {"enabled": True}

    with patch(
        "secops.chronicle.rule_set.list_curated_rule_sets",
        return_value=rulesets_data,
    ):
        with patch.object(
            chronicle_client.session, "get", return_value=deployment
        ):
            out = get_curated_rule_set_deployment_by_name(
                chronicle_client, "case insensitive name", "broad"
            )
            assert out["enabled"] is True


def test_get_ruleset_deployment_by_name_error(chronicle_client):
    """Test get_curated_rule_set_deployment_by_name failure."""
    rulesets = _page("curatedRuleSets", [{"displayName": "Other"}])
    with patch.object(chronicle_client.session, "get", return_value=rulesets):
        with pytest.raises(SecOpsError):
            get_curated_rule_set_deployment_by_name(chronicle_client, "missing")


# --- update_curated_rule_set_deployment ---


def test_update_ruleset_deployment_success(
    chronicle_client,
):
    """Test update_curated_rule_set_deployment builds the correct PATCH payload and URL."""
    patch_resp = Mock()
    patch_resp.status_code = 200
    patch_resp.json.return_value = {"ok": True}
    with patch.object(
        chronicle_client.session, "patch", return_value=patch_resp
    ) as mocked_request:
        out = update_curated_rule_set_deployment(
            chronicle_client,
            {
                "category_id": "c1",
                "rule_set_id": "crs_1",
                "precision": "precise",
                "enabled": True,
                "alerting": False,
            },
        )
        assert out == {"ok": True}
        name = (
            f"{chronicle_client.instance_id}/curatedRuleSetCategories/c1/"
            "curatedRuleSets/crs_1/curatedRuleSetDeployments/precise"
        )
        expected_url = f"{chronicle_client.base_url}/{name}"
        mocked_request.assert_called_once()
        assert mocked_request.call_args.args[0] == expected_url
        assert mocked_request.call_args.kwargs["json"] == {
            "name": name,
            "precision": "precise",
            "enabled": True,
            "alerting": False,
        }


def test_update_ruleset_deployment_error_missing_fields(chronicle_client):
    """Test update_curated_rule_set_deployment failure."""
    with pytest.raises(ValueError):
        update_curated_rule_set_deployment(
            chronicle_client,
            {
                "category_id": "c1",
                # 'rule_set_id' missing
                "precision": "precise",
                "enabled": True,
            },
        )


def test_update_ruleset_deployment_error_http(
    chronicle_client, mock_error_response
):
    """Test update_curated_rule_set_deployment failure."""
    with patch.object(
        chronicle_client.session, "patch", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            update_curated_rule_set_deployment(
                chronicle_client,
                {
                    "category_id": "c1",
                    "rule_set_id": "crs_1",
                    "precision": "precise",
                    "enabled": True,
                },
            )


# --- batch_update_curated_rule_set_deployments ---


def test_batch_update_curated_rule_set_success(chronicle_client):
    """Test batch_update_curated_rule_set_deployments success."""
    post_resp = Mock()
    post_resp.status_code = 200
    post_resp.json.return_value = {"status": "ok"}
    with patch.object(
        chronicle_client.session, "post", return_value=post_resp
    ) as post_:
        out = batch_update_curated_rule_set_deployments(
            chronicle_client,
            [
                {
                    "category_id": "c1",
                    "rule_set_id": "r1",
                    "precision": "precise",
                    "enabled": True,
                    "alerting": True,
                },
                {
                    "category_id": "c2",
                    "rule_set_id": "r2",
                    "precision": "broad",
                    "enabled": False,
                },
            ],
        )
        assert out == {"status": "ok"}

        # Inspect payload
        payload = post_.call_args.kwargs["json"]
        assert payload["parent"].startswith(
            chronicle_client.instance_id + "/curatedRuleSetCategories/-"
        )
        reqs = payload["requests"]
        assert len(reqs) == 2
        assert reqs[0]["curated_rule_set_deployment"]["enabled"] is True
        assert reqs[0]["curated_rule_set_deployment"]["alerting"] is True
        assert reqs[0]["update_mask"]["paths"] == ["alerting", "enabled"]


def test_batch_update_curated_rule_set_error_missing_fields(chronicle_client):
    """Test batch_update_curated_rule_set_deployments failure."""
    with pytest.raises(ValueError):
        batch_update_curated_rule_set_deployments(
            chronicle_client,
            [
                {
                    "category_id": "c1",
                    "precision": "precise",
                    "enabled": True,
                },  # rule_set_id missing
            ],
        )


def test_batch_update_curated_rule_set_error_http(
    chronicle_client, mock_error_response
):
    """Test batch_update_curated_rule_set_deployments failure."""
    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            batch_update_curated_rule_set_deployments(
                chronicle_client,
                [
                    {
                        "category_id": "c1",
                        "rule_set_id": "r1",
                        "precision": "precise",
                        "enabled": True,
                    },
                ],
            )


# --- search_curated_detections tests ---


def test_search_curated_detections_success_with_results(chronicle_client):
    """Test search_curated_detections returns detections successfully."""
    detection_page = _page(
        "curatedDetections",
        [
            {
                "id": "det_123",
                "detectionTime": "2024-01-15T10:00:00Z",
                "ruleId": "ur_abc123",
            },
            {
                "id": "det_456",
                "detectionTime": "2024-01-15T11:00:00Z",
                "ruleId": "ur_abc123",
            },
        ],
    )
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            start_time=start_time,
            end_time=end_time,
            list_basis="DETECTION_TIME",
            alert_state="ALERTING",
        )
        assert "curatedDetections" in result
        assert len(result["curatedDetections"]) == 2
        assert result["curatedDetections"][0]["id"] == "det_123"
        # Verify URL and params
        expected_url = (
            f"{chronicle_client.base_url}/"
            f"{chronicle_client.instance_id}/"
            f"legacy:legacySearchCuratedDetections"
        )
        mocked.assert_called_once()
        assert mocked.call_args.args[0] == expected_url
        params = mocked.call_args.kwargs["params"]
        assert params["ruleId"] == "ur_abc123"
        assert params["listBasis"] == "DETECTION_TIME"
        assert params["alertState"] == "ALERTING"
        assert "startTime" in params
        assert "endTime" in params


def test_search_curated_detections_success_empty_results(chronicle_client):
    """Test search_curated_detections with no detections found."""
    detection_page = _page("curatedDetections", [])
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ):
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
        )
        assert "curatedDetections" in result
        assert len(result["curatedDetections"]) == 0


def test_search_curated_detections_with_enums(chronicle_client):
    """Test search_curated_detections using enum values."""
    detection_page = _page(
        "curatedDetections",
        [{"id": "det_789", "detectionTime": "2024-01-15T12:00:00Z"}],
    )
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_xyz789",
            list_basis=ListBasis.DETECTION_TIME,
            alert_state=AlertState.ALERTING,
        )
        assert len(result["curatedDetections"]) == 1
        # Verify enum values converted to strings
        params = mocked.call_args.kwargs["params"]
        assert params["listBasis"] == "DETECTION_TIME"
        assert params["alertState"] == "ALERTING"


def test_search_curated_detections_with_nested_detections(
    chronicle_client,
):
    """Test search_curated_detections with nested detections enabled."""
    detection_page = _page(
        "nestedDetectionSamples",
        [
            {
                "id": "det_nested_1",
                "detectionTime": "2024-01-15T10:00:00Z",
                "nestedDetections": [
                    {"id": "nested_1a"},
                    {"id": "nested_1b"},
                ],
            }
        ],
    )
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            include_nested_detections=True,
        )
        assert "nestedDetectionSamples" in result
        assert len(result["nestedDetectionSamples"]) == 1
        # Verify includeNestedDetections param
        params = mocked.call_args.kwargs["params"]
        assert params["includeNestedDetections"] is True


def test_search_curated_detections_with_pagination(chronicle_client):
    """Test search_curated_detections with manual pagination."""
    detection_page = _page(
        "curatedDetections",
        [{"id": "det_1"}],
        next_token="next_page_token",
    )
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ):
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            page_size=10,
        )
        assert "curatedDetections" in result
        assert len(result["curatedDetections"]) == 1
        assert result["nextPageToken"] == "next_page_token"


def test_search_curated_detections_auto_pagination(chronicle_client):
    """Test search_curated_detections with auto-pagination."""
    p1 = _page("curatedDetections", [{"id": "det_1"}], next_token="page2")
    p2 = _page("curatedDetections", [{"id": "det_2"}])
    with patch.object(
        chronicle_client.session, "get", side_effect=[p1, p2]
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
        )
        assert len(result["curatedDetections"]) == 2
        assert result["curatedDetections"][0]["id"] == "det_1"
        assert result["curatedDetections"][1]["id"] == "det_2"
        assert "nextPageToken" not in result
        assert mocked.call_count == 2


def test_search_curated_detections_with_max_resp_size(
    chronicle_client,
):
    """Test search_curated_detections with max response size limit."""
    detection_page = _page("curatedDetections", [{"id": "det_1"}])
    detection_page.json.return_value["respTooLargeDetectionsTruncated"] = True
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            max_resp_size_bytes=1048576,
        )
        assert result["respTooLargeDetectionsTruncated"] is True
        params = mocked.call_args.kwargs["params"]
        assert params["maxRespSizeBytes"] == 1048576


def test_search_curated_detections_with_page_token(chronicle_client):
    """Test search_curated_detections with page_token for continuation."""
    detection_page = _page("curatedDetections", [{"id": "det_2"}])
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            page_size=10,
            page_token="existing_token",
        )
        assert len(result["curatedDetections"]) == 1
        params = mocked.call_args.kwargs["params"]
        assert params["pageToken"] == "existing_token"


def test_search_curated_detections_minimal_params(chronicle_client):
    """Test search_curated_detections with only required parameters."""
    detection_page = _page("curatedDetections", [{"id": "det_1"}])
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
        )
        assert "curatedDetections" in result
        params = mocked.call_args.kwargs["params"]
        assert params["ruleId"] == "ur_abc123"
        assert params["listBasis"] == "DETECTION_TIME"
        assert "alertState" not in params
        assert "startTime" not in params
        assert "endTime" not in params


def test_search_curated_detections_with_all_filter_types(
    chronicle_client,
):
    """Test search_curated_detections with all list_basis types."""
    detection_page = _page("curatedDetections", [{"id": "det_1"}])

    # Test DETECTION_TIME
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis=ListBasis.DETECTION_TIME,
        )
        params = mocked.call_args.kwargs["params"]
        assert params["listBasis"] == "DETECTION_TIME"

    # Test CREATED_TIME
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis=ListBasis.CREATED_TIME,
        )
        params = mocked.call_args.kwargs["params"]
        assert params["listBasis"] == "CREATED_TIME"


def test_search_curated_detections_with_all_alert_states(
    chronicle_client,
):
    """Test search_curated_detections with all alert_state types."""
    detection_page = _page("curatedDetections", [{"id": "det_1"}])

    # Test ALERTING
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            alert_state=AlertState.ALERTING,
        )
        params = mocked.call_args.kwargs["params"]
        assert params["alertState"] == "ALERTING"

    # Test NOT_ALERTING
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            alert_state=AlertState.NOT_ALERTING,
        )
        params = mocked.call_args.kwargs["params"]
        assert params["alertState"] == "NOT_ALERTING"


def test_search_curated_detections_error_api_failure(
    chronicle_client, mock_error_response
):
    """Test search_curated_detections raises APIError on API failure."""
    with patch.object(
        chronicle_client.session, "get", return_value=mock_error_response
    ):
        with pytest.raises(APIError):
            search_curated_detections(
                chronicle_client,
                rule_id="ur_abc123",
                list_basis="DETECTION_TIME",
            )


def test_search_curated_detections_error_invalid_list_basis(
    chronicle_client,
):
    """Test search_curated_detections raises ValueError for invalid
    list_basis."""
    with pytest.raises(ValueError, match="Invalid list_basis"):
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="INVALID_BASIS",
        )


def test_search_curated_detections_error_invalid_alert_state(
    chronicle_client,
):
    """Test search_curated_detections raises ValueError for invalid
    alert_state."""
    with pytest.raises(ValueError, match="Invalid alert_state"):
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            alert_state="INVALID_STATE",
        )


def test_search_curated_detections_none_alert_state_allowed(
    chronicle_client,
):
    """Test search_curated_detections allows None for alert_state."""
    detection_page = _page("curatedDetections", [{"id": "det_1"}])
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        result = search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            list_basis="DETECTION_TIME",
            alert_state=None,
        )
        assert "curatedDetections" in result
        params = mocked.call_args.kwargs["params"]
        assert "alertState" not in params


def test_search_curated_detections_time_format(chronicle_client):
    """Test search_curated_detections formats time correctly."""
    detection_page = _page("curatedDetections", [{"id": "det_1"}])
    with patch.object(
        chronicle_client.session, "get", return_value=detection_page
    ) as mocked:
        end_time = datetime(2024, 1, 15, 23, 59, 59, 999999, timezone.utc)
        start_time = datetime(2024, 1, 1, 0, 0, 0, 0, timezone.utc)
        search_curated_detections(
            chronicle_client,
            rule_id="ur_abc123",
            start_time=start_time,
            end_time=end_time,
            list_basis="DETECTION_TIME",
        )
        params = mocked.call_args.kwargs["params"]
        assert params["startTime"] == "2024-01-01T00:00:00.000000Z"
        assert params["endTime"] == "2024-01-15T23:59:59.999999Z"
