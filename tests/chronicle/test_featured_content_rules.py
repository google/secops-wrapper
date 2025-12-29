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
"""Tests for Chronicle featured content rules functions."""

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.client import ChronicleClient
from secops.chronicle.featured_content_rules import (
    list_featured_content_rules,
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
            customer_id="test-customer",
            project_id="test-project",
        )


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock API response object."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {}
    return mock


@pytest.fixture
def mock_error_response() -> Mock:
    """Create a mock error API response object."""
    mock = Mock()
    mock.status_code = 400
    mock.text = "Error message"
    mock.raise_for_status.side_effect = Exception("API Error")
    return mock


def test_list_featured_content_rules_success_without_params(
    chronicle_client,
):
    """Test list_featured_content_rules without parameters."""
    expected: Dict[str, Any] = {
        "featuredContentRules": [
            {
                "name": "projects/test/locations/us/instances/test/"
                "contentHub/featuredContentRules/ur_123",
                "severity": "HIGH",
                "contentMetadata": {
                    "displayName": "Test Rule 1",
                    "description": "Test description",
                },
            },
            {
                "name": "projects/test/locations/us/instances/test/"
                "contentHub/featuredContentRules/ur_456",
                "severity": "MEDIUM",
                "contentMetadata": {
                    "displayName": "Test Rule 2",
                    "description": "Another test rule",
                },
            },
        ]
    }

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(chronicle_client)

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url,
            path="contentHub/featuredContentRules",
            items_key="featuredContentRules",
            page_size=None,
            page_token=None,
            extra_params=None,
        )


def test_list_featured_content_rules_with_page_size(chronicle_client):
    """Test list_featured_content_rules with page_size parameter."""
    expected: Dict[str, Any] = {
        "featuredContentRules": [
            {
                "name": "projects/test/locations/us/instances/test/"
                "contentHub/featuredContentRules/ur_123",
                "severity": "HIGH",
            },
        ],
        "nextPageToken": "token-abc-123",
    }

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(chronicle_client, page_size=10)

        assert result == expected
        assert "nextPageToken" in result

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url,
            path="contentHub/featuredContentRules",
            items_key="featuredContentRules",
            page_size=10,
            page_token=None,
            extra_params=None,
        )


def test_list_featured_content_rules_with_page_token(chronicle_client):
    """Test list_featured_content_rules with page_token parameter."""
    expected: Dict[str, Any] = {
        "featuredContentRules": [
            {
                "name": "projects/test/locations/us/instances/test/"
                "contentHub/featuredContentRules/ur_789",
                "severity": "LOW",
            },
        ]
    }

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(
            chronicle_client, page_token="token-xyz-789"
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url,
            path="contentHub/featuredContentRules",
            items_key="featuredContentRules",
            page_size=None,
            page_token="token-xyz-789",
            extra_params=None,
        )


def test_list_featured_content_rules_with_filter_expression(
    chronicle_client,
):
    """Test list_featured_content_rules with filter_expression."""
    expected: Dict[str, Any] = {
        "featuredContentRules": [
            {
                "name": "projects/test/locations/us/instances/test/"
                "contentHub/featuredContentRules/ur_precise_1",
                "severity": "HIGH",
                "rulePrecision": "Precise",
            },
        ]
    }

    filter_expr = 'rule_precision:"Precise"'

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(
            chronicle_client, filter_expression=filter_expr
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url,
            path="contentHub/featuredContentRules",
            items_key="featuredContentRules",
            page_size=None,
            page_token=None,
            extra_params={"filter": filter_expr},
        )


def test_list_featured_content_rules_with_all_parameters(
    chronicle_client,
):
    """Test list_featured_content_rules with all parameters."""
    expected: Dict[str, Any] = {
        "featuredContentRules": [
            {
                "name": "projects/test/locations/us/instances/test/"
                "contentHub/featuredContentRules/ur_filtered",
                "severity": "CRITICAL",
            },
        ],
        "nextPageToken": "next-token-123",
    }

    filter_expr = (
        'category_name:"Threat Detection" AND ' 'rule_precision:"Precise"'
    )

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(
            chronicle_client,
            page_size=5,
            page_token="current-token",
            filter_expression=filter_expr,
        )

        assert result == expected

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url,
            path="contentHub/featuredContentRules",
            items_key="featuredContentRules",
            page_size=5,
            page_token="current-token",
            extra_params={"filter": filter_expr},
        )


def test_list_featured_content_rules_empty_results(chronicle_client):
    """Test list_featured_content_rules with empty results."""
    expected: Dict[str, Any] = {"featuredContentRules": []}

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(chronicle_client)

        assert result == expected
        assert result["featuredContentRules"] == []

        mock_paginated.assert_called_once()


def test_list_featured_content_rules_api_error(chronicle_client):
    """Test list_featured_content_rules raises APIError on failure."""
    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        side_effect=APIError("Failed to list featuredContentRules"),
    ):
        with pytest.raises(APIError) as exc_info:
            list_featured_content_rules(chronicle_client)

        assert "Failed to list featuredContentRules" in str(exc_info.value)


def test_list_featured_content_rules_invalid_filter_error(
    chronicle_client,
):
    """Test list_featured_content_rules with invalid filter."""
    error_msg = (
        "invalid filter. The request only supports the following "
        "filters: 'category_name', 'policy_name', 'rule_id', "
        "'rule_precision', 'search_rule_name_or_description'"
    )

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        side_effect=APIError(error_msg),
    ):
        with pytest.raises(APIError) as exc_info:
            list_featured_content_rules(
                chronicle_client,
                filter_expression='invalid_field:"value"',
            )

        assert "invalid filter" in str(exc_info.value)


def test_list_featured_content_rules_max_page_size(chronicle_client):
    """Test list_featured_content_rules with maximum page size."""
    expected: Dict[str, Any] = {
        "featuredContentRules": [{"name": f"rule_{i}"} for i in range(1000)],
        "nextPageToken": "token-for-next-1000",
    }

    with patch(
        "secops.chronicle.featured_content_rules."
        "chronicle_paginated_request",
        return_value=expected,
    ) as mock_paginated:
        result = list_featured_content_rules(chronicle_client, page_size=1000)

        assert result == expected
        assert len(result["featuredContentRules"]) == 1000

        mock_paginated.assert_called_once_with(
            chronicle_client,
            base_url=chronicle_client.base_url,
            path="contentHub/featuredContentRules",
            items_key="featuredContentRules",
            page_size=1000,
            page_token=None,
            extra_params=None,
        )
