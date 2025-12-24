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
"""Integration tests for featured content rules CLI commands."""

import json
import subprocess

import pytest


@pytest.mark.integration
def test_cli_featured_content_rules_list_with_filter(cli_env, common_args):
    """Test featured-content-rules list command with filter."""
    cmd = (
        ["secops"]
        + common_args
        + [
            "featured-content-rules",
            "list",
            "--filter",
            'rule_precision:"Precise"',
        ]
    )

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    assert (
        result.returncode == 0
    ), f"Command failed with stderr: {result.stderr}"

    try:
        output = json.loads(result.stdout)
        assert isinstance(output, dict)
        assert "featuredContentRules" in output
        assert isinstance(output["featuredContentRules"], list)

        print(
            f"\nFiltered result: "
            f"{len(output['featuredContentRules'])} rules"
        )

    except json.JSONDecodeError:
        assert "Error:" not in result.stdout


@pytest.mark.integration
def test_cli_featured_content_rules_list_with_page_size(cli_env, common_args):
    """Test featured-content-rules list command with page size."""
    cmd = (
        ["secops"]
        + common_args
        + [
            "featured-content-rules",
            "list",
            "--page-size",
            "5",
        ]
    )

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    assert (
        result.returncode == 0
    ), f"Command failed with stderr: {result.stderr}"

    try:
        output = json.loads(result.stdout)
        assert isinstance(output, dict)
        assert "featuredContentRules" in output
        assert len(output["featuredContentRules"]) <= 5

        print(
            f"\nPaginated result: "
            f"{len(output['featuredContentRules'])} rules"
        )

        if "nextPageToken" in output:
            print("Next page token available")

    except json.JSONDecodeError:
        assert "Error:" not in result.stdout
