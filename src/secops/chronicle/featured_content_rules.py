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
"""Featured content rules functionality for Chronicle."""

from typing import Any

from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
)


def list_featured_content_rules(
    client,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_expression: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """List featured content rules from Chronicle Content Hub.

    Args:
        client: ChronicleClient instance
        page_size: Maximum number of featured content rules to return.
            If unspecified, at most 100 rules will be returned.
            Maximum value is 1000; values above 1000 will be coerced
            to 1000. If provided, returns dict with nextPageToken.
        page_token: Token for retrieving the next page of results.
        filter_expression: Optional filter expression. Supported filters:
            - category_name:"<category_name>" (OR operator for multiple)
            - policy_name:"<policy_name>" (OR operator for multiple)
            - rule_id:"ur_<id>" (OR operator for multiple)
            - rule_precision:"<rule_precision>" (Precise or Broad)
            - search_rule_name_or_description=~"<text>"
            Multiple filters can be combined with AND operator.

    Returns:
        If page_size is not provided: A dictionary containing a list of all
            featured content rules.
        If page_size is provided: A dictionary containing a list of
            featuredContentRules and a nextPageToken if more results are
            available.

    Raises:
        APIError: If the API request fails
    """
    extra_params = {}
    if filter_expression:
        extra_params["filter"] = filter_expression

    return chronicle_paginated_request(
        client,
        base_url=client.base_url,
        path="contentHub/featuredContentRules",
        items_key="featuredContentRules",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params if extra_params else None,
    )
