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
"""Integration tests for featured content rules in Chronicle API.

These tests require valid credentials and API access.
"""
import pytest

from secops import SecOpsClient

from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.fixture(scope="module")
def chronicle():
    """Fixture to create a Chronicle client for testing."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    return client.chronicle(**CHRONICLE_CONFIG)


@pytest.mark.integration
def test_list_featured_content_rules_basic(chronicle):
    """Test basic listing of featured content rules."""
    rules = chronicle.list_featured_content_rules()
    assert isinstance(rules, dict)
    assert "featuredContentRules" in rules
    assert isinstance(rules["featuredContentRules"], list)

    print(f"\nFound {len(rules['featuredContentRules'])} featured rules")

    if rules["featuredContentRules"]:
        first_rule = rules["featuredContentRules"][0]
        assert "name" in first_rule
        print(f"First rule: {first_rule.get('name')}")


@pytest.mark.integration
def test_list_featured_content_rules_with_pagination(chronicle):
    """Test listing featured content rules with pagination."""
    page_size = 5
    result = chronicle.list_featured_content_rules(page_size=page_size)

    assert isinstance(result, dict)
    assert "featuredContentRules" in result
    assert isinstance(result["featuredContentRules"], list)
    assert len(result["featuredContentRules"]) <= page_size

    print(
        f"\nPaginated result: {len(result['featuredContentRules'])} "
        f"rules (page_size={page_size})"
    )

    if "nextPageToken" in result:
        print("Next page token available")
        next_page = chronicle.list_featured_content_rules(
            page_size=page_size, page_token=result["nextPageToken"]
        )
        assert isinstance(next_page, dict)
        assert "featuredContentRules" in next_page
        print(f"Next page: {len(next_page['featuredContentRules'])} rules")


@pytest.mark.integration
def test_list_featured_content_rules_with_filter(chronicle):
    """Test listing featured content rules with filter expression."""
    filter_expr = 'rule_precision:"Precise"'
    result = chronicle.list_featured_content_rules(
        filter_expression=filter_expr
    )

    assert isinstance(result, dict)
    assert "featuredContentRules" in result
    assert isinstance(result["featuredContentRules"], list)

    print(
        f"\nFiltered by precision: "
        f"{len(result['featuredContentRules'])} rules"
    )

    if result["featuredContentRules"]:
        for rule in result["featuredContentRules"][:3]:
            print(f"  - {rule.get('name')}")
