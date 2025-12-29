#!/usr/bin/env python3
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
"""Example script demonstrating Chronicle Featured Content Rules."""

import argparse

from secops.chronicle.client import ChronicleClient


def get_client(project_id: str, customer_id: str, region: str):
    """Initialize Chronicle client."""
    return ChronicleClient(
        project_id=project_id, customer_id=customer_id, region=region
    )


def featured_content_rules_list_example(chronicle):
    """Demonstrate featured content rules functionality."""
    try:
        print("\n[1] List All Featured Content Rules")
        print("-" * 70)
        result = chronicle.list_featured_content_rules()
        rules = result.get("featuredContentRules", [])
        print(f"Total rules found: {len(rules)}")

        if rules:
            print("\nFirst 3 rules:")
            for i, rule in enumerate(rules[:3], 1):
                name = rule.get("name", "")
                rule_id_extracted = name.split("/")[-1] if name else "N/A"
                content_metadata = rule.get("contentMetadata", {})
                display_name = content_metadata.get("displayName", "Unknown")
                severity = rule.get("severity", "UNSPECIFIED")
                print(
                    f"  {i}. {display_name} "
                    f"[{rule_id_extracted}] - {severity}"
                )

        print("\n[2] Paginated List (5 rules per page)")
        print("-" * 70)
        result = chronicle.list_featured_content_rules(page_size=5)
        featured_rules = result.get("featuredContentRules", [])
        next_token = result.get("nextPageToken")
        print(f"Rules in first page: {len(featured_rules)}")
        print(f"More pages available: {bool(next_token)}")

        print("\n[3] Filter expression")
        print("-" * 70)
        filter_expr = 'rule_precision:"Precise"'
        combined_rules_result = chronicle.list_featured_content_rules(
            filter_expression=filter_expr
        )
        combined_rules = combined_rules_result.get("featuredContentRules", [])
        print(f"Rules matching filter expression: {len(combined_rules)}")
    except Exception as e:
        print(f"\nError: {e}")


def main():
    """Main function to demonstrate featured content rules usage."""
    parser = argparse.ArgumentParser(
        description="Chronicle Featured Content Rules Example"
    )
    parser.add_argument(
        "--project_id",
        required=True,
        help="Google Cloud Project ID",
    )
    parser.add_argument(
        "--customer_id",
        required=True,
        help="Chronicle Customer ID (UUID)",
    )
    parser.add_argument(
        "--region",
        default="us",
        help="Chronicle region (default: us)",
    )

    args = parser.parse_args()

    chronicle = get_client(args.project_id, args.customer_id, args.region)

    print(
        f"\nConnected to Chronicle (Project: {args.project_id}, "
        f"Customer: {args.customer_id}, Region: {args.region})\n"
    )

    featured_content_rules_list_example(chronicle)


if __name__ == "__main__":
    main()
