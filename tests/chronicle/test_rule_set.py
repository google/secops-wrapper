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
# """Tests for Chronicle curated rule set functions."""

from datetime import datetime, timezone
from unittest.mock import patch, Mock

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import APIVersion, AlertState, ListBasis
from secops.chronicle.rule_set import (
    get_curated_rule,
    get_curated_rule_by_name,
    list_curated_rules,
    list_curated_rule_sets,
    list_curated_rule_set_categories,
    get_curated_rule_set,
    get_curated_rule_set_category,
    list_curated_rule_set_deployments,
    get_curated_rule_set_deployment,
    get_curated_rule_set_deployment_by_name,
    update_curated_rule_set_deployment,
    batch_update_curated_rule_set_deployments,
    search_curated_detections,
)
from secops.exceptions import SecOpsError


@pytest.fixture
def chronicle_client():
    # Construct a client without exercising auth/session behaviour
    client = Mock(spec=ChronicleClient)
    client.instance_id = "instances/instance-1"
    return client


# -----------------------------------------------------------------------------
# Simple wrappers around chronicle_request()
# -----------------------------------------------------------------------------


def test_get_curated_rule_success(chronicle_client):
    expected = {"name": "curatedRules/ur_abc-123", "displayName": "Rule X"}

    with patch(
        "secops.chronicle.rule_set.chronicle_request", return_value=expected
    ) as req:
        out = get_curated_rule(chronicle_client, "ur_abc-123")
        assert out == expected

        req.assert_called_once()
        kwargs = req.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["api_version"] == APIVersion.V1ALPHA
        assert kwargs["endpoint_path"] == "curatedRules/ur_abc-123"
        assert (
            "Failed to get curated rule: ur_abc-123" in kwargs["error_message"]
        )


def test_get_curated_rule_set_success(chronicle_client):
    expected = {"name": "whatever", "displayName": "Ruleset 1"}

    with patch(
        "secops.chronicle.rule_set.chronicle_request", return_value=expected
    ) as req:
        out = get_curated_rule_set(chronicle_client, "crs_1")
        assert out == expected

        kwargs = req.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["api_version"] == APIVersion.V1ALPHA
        # rule_set.py builds the endpoint path; assert the important suffix
        assert kwargs["endpoint_path"].endswith("curatedRuleSets/crs_1")


def test_get_curated_rule_set_category_success(chronicle_client):
    expected = {
        "name": "curatedRuleSetCategories/cat_1",
        "displayName": "Category 1",
    }

    with patch(
        "secops.chronicle.rule_set.chronicle_request", return_value=expected
    ) as req:
        out = get_curated_rule_set_category(chronicle_client, "cat_1")
        assert out == expected

        kwargs = req.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["api_version"] == APIVersion.V1ALPHA
        assert kwargs["endpoint_path"] == "curatedRuleSetCategories/cat_1"


# -----------------------------------------------------------------------------
# Simple wrappers around chronicle_paginated_request()
# -----------------------------------------------------------------------------


def test_list_curated_rules_success(chronicle_client):
    expected = {
        "curatedRules": [{"name": "curatedRules/a"}],
        "nextPageToken": "t2",
    }

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        out = list_curated_rules(
            chronicle_client, page_size=100, page_token="t1"
        )
        assert out == expected

        kwargs = paged.call_args.kwargs
        assert kwargs["api_version"] == APIVersion.V1ALPHA
        assert kwargs["path"] == "curatedRules"
        assert kwargs["items_key"] == "curatedRules"
        assert kwargs["page_size"] == 100
        assert kwargs["page_token"] == "t1"


def test_list_curated_rule_sets_success(chronicle_client):
    expected = {"curatedRuleSets": [{"name": "rs1"}]}

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        out = list_curated_rule_sets(chronicle_client)
        assert out == expected

        kwargs = paged.call_args.kwargs
        assert kwargs["path"] == "curatedRuleSetCategories/-/curatedRuleSets"
        assert kwargs["items_key"] == "curatedRuleSets"


def test_list_curated_rule_set_categories_success(chronicle_client):
    expected = {"curatedRuleSetCategories": [{"name": "cat1"}]}

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        out = list_curated_rule_set_categories(chronicle_client)
        assert out == expected

        kwargs = paged.call_args.kwargs
        assert kwargs["path"] == "curatedRuleSetCategories"
        assert kwargs["items_key"] == "curatedRuleSetCategories"


# -----------------------------------------------------------------------------
# Functions that transform/search returned data
# -----------------------------------------------------------------------------


def test_get_curated_rule_by_name_success(chronicle_client):
    all_rules = {
        "curatedRules": [
            {"displayName": "Alpha", "name": "curatedRules/a"},
            {"displayName": "Bravo", "name": "curatedRules/b"},
        ]
    }

    with patch(
        "secops.chronicle.rule_set.list_curated_rules", return_value=all_rules
    ):
        out = get_curated_rule_by_name(chronicle_client, "bravo")
        assert out["name"] == "curatedRules/b"


def test_get_curated_rule_by_name_not_found(chronicle_client):
    all_rules = {
        "curatedRules": [{"displayName": "Alpha", "name": "curatedRules/a"}]
    }

    with patch(
        "secops.chronicle.rule_set.list_curated_rules", return_value=all_rules
    ):
        with pytest.raises(SecOpsError):
            get_curated_rule_by_name(chronicle_client, "missing")


def test_list_curated_rule_set_deployments_adds_display_names(chronicle_client):
    deployments = {
        "curatedRuleSetDeployments": [
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_1/curatedRuleSetDeployments/precise",
                "enabled": True,
                "alerting": False,
            },
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_2/curatedRuleSetDeployments/broad",
                "enabled": False,
                "alerting": True,
            },
        ]
    }
    rule_sets = {
        "curatedRuleSets": [
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
                "displayName": "One",
            },
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_2",
                "displayName": "Two",
            },
        ]
    }

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=deployments,
    ):
        with patch(
            "secops.chronicle.rule_set.list_curated_rule_sets",
            return_value=rule_sets,
        ):
            out = list_curated_rule_set_deployments(chronicle_client)

    items = out["curatedRuleSetDeployments"]
    assert {d["displayName"] for d in items} == {"One", "Two"}


def test_list_curated_rule_set_deployments_filters_enabled(chronicle_client):
    deployments = {
        "curatedRuleSetDeployments": [
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_1/curatedRuleSetDeployments/precise",
                "enabled": True,
            },
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_2/curatedRuleSetDeployments/broad",
                "enabled": False,
            },
        ]
    }
    rule_sets = {"curatedRuleSets": []}

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=deployments,
    ):
        with patch(
            "secops.chronicle.rule_set.list_curated_rule_sets",
            return_value=rule_sets,
        ):
            out = list_curated_rule_set_deployments(
                chronicle_client, only_enabled=True
            )

    assert len(out["curatedRuleSetDeployments"]) == 1
    assert out["curatedRuleSetDeployments"][0]["enabled"] is True


def test_get_curated_rule_set_deployment_success(chronicle_client):
    # First call returns the ruleset (for displayName), second returns the deployment details
    rule_set = {
        "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
        "displayName": "My Ruleset",
    }
    deployment = {"enabled": True, "alerting": False}

    with patch(
        "secops.chronicle.rule_set.get_curated_rule_set", return_value=rule_set
    ):
        with patch(
            "secops.chronicle.rule_set.chronicle_request",
            return_value=deployment,
        ) as req:
            out = get_curated_rule_set_deployment(
                chronicle_client, "crs_1", "precise"
            )

    assert out["enabled"] is True
    assert out["displayName"] == "My Ruleset"

    kwargs = req.call_args.kwargs
    assert kwargs["method"] == "GET"
    assert kwargs["api_version"] == APIVersion.V1ALPHA
    assert kwargs["endpoint_path"].endswith("curatedRuleSetDeployments/precise")


def test_get_curated_rule_set_deployment_invalid_precision(chronicle_client):
    with pytest.raises(SecOpsError):
        get_curated_rule_set_deployment(chronicle_client, "crs_1", "medium")


def test_get_curated_rule_set_deployment_by_name_success(chronicle_client):
    rule_sets = {
        "curatedRuleSets": [
            {
                "name": "instances/instance-1/curatedRuleSetCategories/c1/curatedRuleSets/crs_1",
                "displayName": "Ruleset A",
            },
        ]
    }
    deployment = {"enabled": True}

    with patch(
        "secops.chronicle.rule_set.list_curated_rule_sets",
        return_value=rule_sets,
    ):
        with patch(
            "secops.chronicle.rule_set.get_curated_rule_set_deployment",
            return_value=deployment,
        ) as g:
            out = get_curated_rule_set_deployment_by_name(
                chronicle_client, "ruleset a", "broad"
            )

    assert out == deployment
    g.assert_called_once()


def test_update_curated_rule_set_deployment_success(chronicle_client):
    expected = {"ok": True}

    with patch(
        "secops.chronicle.rule_set.chronicle_request", return_value=expected
    ) as req:
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
    assert out == expected

    kwargs = req.call_args.kwargs
    assert kwargs["method"] == "PATCH"
    assert kwargs["api_version"] == APIVersion.V1ALPHA
    assert (
        kwargs["endpoint_path"]
        == "curatedRuleSetCategories/c1/curatedRuleSets/crs_1/curatedRuleSetDeployments/precise"
    )
    assert kwargs["json"]["enabled"] is True


def test_batch_update_curated_rule_set_deployments_success(chronicle_client):
    expected = {"status": "ok"}

    with patch(
        "secops.chronicle.rule_set.chronicle_request", return_value=expected
    ) as req:
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

    assert out == expected
    kwargs = req.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["api_version"] == APIVersion.V1ALPHA
    assert (
        kwargs["endpoint_path"]
        == "curatedRuleSetCategories/-/curatedRuleSets/-/curatedRuleSetDeployments:batchUpdate"
    )


# -----------------------------------------------------------------------------
# search_curated_detections() — validate params and items_key selection
# -----------------------------------------------------------------------------


def test_search_curated_detections_builds_params(chronicle_client):
    expected = {"curatedDetections": [{"id": "d1"}]}
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        out = search_curated_detections(
            chronicle_client,
            rule_id="ur_1",
            start_time=start,
            end_time=end,
            list_basis=ListBasis.DETECTION_TIME,
            alert_state=AlertState.ALERTING,
        )

    assert out == expected
    kwargs = paged.call_args.kwargs
    assert kwargs["path"] == "legacy:legacySearchCuratedDetections"
    assert kwargs["items_key"] == "curatedDetections"
    params = kwargs["extra_params"]
    assert params["ruleId"] == "ur_1"
    assert params["listBasis"] == "DETECTION_TIME"
    assert params["alertState"] == "ALERTING"
    assert params["startTime"].endswith("Z")
    assert params["endTime"].endswith("Z")


def test_search_curated_detections_nested_switches_items_key(chronicle_client):
    expected = {"nestedDetectionSamples": [{"id": "n1"}]}

    with patch(
        "secops.chronicle.rule_set.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        out = search_curated_detections(
            chronicle_client,
            rule_id="ur_1",
            include_nested_detections=True,
        )

    assert out == expected
    assert paged.call_args.kwargs["items_key"] == "nestedDetectionSamples"
    assert (
        paged.call_args.kwargs["extra_params"]["includeNestedDetections"]
        is True
    )


def test_search_curated_detections_invalid_list_basis(chronicle_client):
    with pytest.raises(ValueError):
        search_curated_detections(
            chronicle_client, rule_id="ur_1", list_basis="INVALID"
        )


def test_search_curated_detections_invalid_alert_state(chronicle_client):
    with pytest.raises(ValueError):
        search_curated_detections(
            chronicle_client,
            rule_id="ur_1",
            list_basis="DETECTION_TIME",
            alert_state="INVALID",
        )
