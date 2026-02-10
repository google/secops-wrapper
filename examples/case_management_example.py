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
"""Example demonstrating case management functionality with Chronicle."""

import argparse

from secops import SecOpsClient
from secops.chronicle import CasePriority
from secops.exceptions import APIError


def list_cases_example(chronicle):
    """Demonstrate listing cases with filtering and pagination.

    Args:
        chronicle: Initialized Chronicle client
    """
    print("\n=== Example 1: List Cases ===")

    try:
        # List cases with basic pagination
        result = chronicle.list_cases(
            page_size=10, filter_query='priority="PRIORITY_HIGH"'
        )

        print(f"Total cases: {result['totalSize']}")
        print(f"Cases in this page: {len(result['cases'])}")

        # Display first few cases
        for i, case in enumerate(result["cases"][:3], 1):
            print(f"\nCase {i}:")
            print(f"  ID: {case['name']}")
            print(f"  Display Name: {case['displayName']}")
            print(f"  Priority: {case['priority']}")
            print(f"  Stage: {case['stage']}")
            print(f"  Status: {case['status']}")

        # Check if there are more pages
        if result["nextPageToken"]:
            print(f"\nMore cases available (next page token exists)")

    except APIError as e:
        print(f"Error listing cases: {e}")


def get_case_example(chronicle, case_id):
    """Demonstrate getting a single case by ID.

    Args:
        chronicle: Initialized Chronicle client
        case_id: Case ID to retrieve
    """
    print("\n=== Example 2: Get Single Case ===")

    try:
        # Method 1: Using just the case ID (recommended - simpler)
        print("\nUsing just case ID:")
        case = chronicle.get_case(case_id, expand="tags,products")

        print(f"Case ID: {case.id}")
        print(f"Display Name: {case.display_name}")
        print(f"Priority: {case.priority}")
        print(f"Stage: {case.stage}")
        print(f"Status: {case.status}")

        if case.soar_platform_info:
            print(f"SOAR Platform: " f"{case.soar_platform_info.platform_type}")
            print(f"SOAR Case ID: {case.soar_platform_info.case_id}")

    except APIError as e:
        print(f"Error retrieving case: {e}")


def patch_case_example(chronicle, case_id):
    """Demonstrate updating a case using PATCH.

    Shows usage with just case ID for simplicity.

    Args:
        chronicle: Initialized Chronicle client
        case_id: Case ID to update
    """
    print("\n=== Example 3: Update Case (PATCH) ===")

    try:
        # Update specific fields using just the case ID
        # Note: Priority values are automatically normalized to PRIORITY_ format
        # You can use either "MEDIUM" or "PRIORITY_MEDIUM"
        case_data = {
            "priority": "MEDIUM",
            "displayName": "Updated Case Name",
        }

        updated_case = chronicle.patch_case(
            case_id, case_data, update_mask="priority,displayName"
        )

        print(f"Case updated successfully!")
        print(f"New Priority: {updated_case.priority}")
        print(f"New Display Name: {updated_case.display_name}")

    except APIError as e:
        print(f"Error updating case: {e}")


def bulk_add_tags_example(chronicle, case_ids):
    """Demonstrate adding tags to multiple cases.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to add tags to
    """
    print("\n=== Example 4: Bulk Add Tags ===")

    try:
        tags = ["security-review", "high-priority"]

        result = chronicle.execute_bulk_add_tag(case_ids, tags)

        print(f"Successfully added tags {tags} to {len(case_ids)} cases")
        print(f"Result: {result}")

    except APIError as e:
        print(f"Error adding tags: {e}")


def bulk_assign_example(chronicle, case_ids, username):
    """Demonstrate assigning multiple cases to a user.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to assign
        username: Username to assign cases to
    """
    print("\n=== Example 5: Bulk Assign Cases ===")

    try:
        result = chronicle.execute_bulk_assign(case_ids, username)

        print(f"Successfully assigned {len(case_ids)} cases to {username}")
        print(f"Result: {result}")

    except APIError as e:
        print(f"Error assigning cases: {e}")


def bulk_change_priority_example(chronicle, case_ids):
    """Demonstrate changing priority of multiple cases.

    Shows both string and enum usage.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to update
    """
    print("\n=== Example 6: Bulk Change Priority ===")

    try:
        # Example using enum (recommended)
        print("\nUsing CasePriority enum:")
        result = chronicle.execute_bulk_change_priority(
            case_ids, CasePriority.HIGH
        )

        print(
            f"Successfully changed priority to HIGH for "
            f"{len(case_ids)} cases"
        )
        print(f"Result: {result}")

        # Example using string (also supported)
        print("\nUsing string value:")
        result = chronicle.execute_bulk_change_priority(
            case_ids, "PRIORITY_MEDIUM"
        )

        print(
            f"Successfully changed priority to MEDIUM for "
            f"{len(case_ids)} cases"
        )
        print(f"Result: {result}")

    except APIError as e:
        print(f"Error changing priority: {e}")


def bulk_change_stage_example(chronicle, case_ids):
    """Demonstrate changing stage of multiple cases.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to update
    """
    print("\n=== Example 7: Bulk Change Stage ===")

    try:
        result = chronicle.execute_bulk_change_stage(case_ids, "Investigation")

        print(
            f"Successfully changed stage to Investigation for "
            f"{len(case_ids)} cases"
        )
        print(f"Result: {result}")

    except APIError as e:
        print(f"Error changing stage: {e}")


def bulk_close_example(chronicle, case_ids):
    """Demonstrate closing multiple cases.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to close
    """
    print("\n=== Example 8: Bulk Close Cases ===")

    try:
        # Valid close_reason values: MALICIOUS, NOT_MALICIOUS, MAINTENANCE,
        # INCONCLUSIVE, UNKNOWN, or CLOSE_REASON_UNSPECIFIED
        result = chronicle.execute_bulk_close(
            case_ids=case_ids,
            close_reason="NOT_MALICIOUS",
            root_cause="No threat detected",
            close_comment="Closed after thorough investigation",
        )

        print(f"Successfully closed {len(case_ids)} cases")
        print(f"Result: {result}")

    except APIError as e:
        print(f"Error closing cases: {e}")


def bulk_reopen_example(chronicle, case_ids):
    """Demonstrate reopening multiple cases.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to reopen
    """
    print("\n=== Example 9: Bulk Reopen Cases ===")

    try:
        result = chronicle.execute_bulk_reopen(
            case_ids, "Reopening for additional investigation"
        )

        print(f"Successfully reopened {len(case_ids)} cases")
        print(f"Result: {result}")

    except APIError as e:
        print(f"Error reopening cases: {e}")


def merge_cases_example(chronicle, case_ids, target_case_id):
    """Demonstrate merging multiple cases into one.

    Args:
        chronicle: Initialized Chronicle client
        case_ids: List of case IDs to merge
        target_case_id: ID of the case to merge into
    """
    print("\n=== Example 10: Merge Cases ===")

    try:
        result = chronicle.merge_cases(case_ids, target_case_id)

        if result.get("isRequestValid"):
            print(f"Successfully merged cases into case {target_case_id}")
            print(f"New Case ID: {result.get('newCaseId')}")
        else:
            print(f"Merge request invalid")
            print(f"Errors: {result.get('errors', [])}")

    except APIError as e:
        print(f"Error merging cases: {e}")


def parse_case_ids(value):
    """Parse comma-separated case IDs into list of integers."""
    try:
        return [int(id.strip()) for id in value.split(",")]
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid case ID format: {value}"
        ) from e


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(
        description="Example of case management with Chronicle"
    )
    parser.add_argument(
        "--customer_id", required=True, help="Chronicle instance ID"
    )
    parser.add_argument("--project_id", required=True, help="GCP project ID")
    parser.add_argument("--region", default="us", help="Chronicle API region")
    parser.add_argument(
        "--case_id",
        help="Specific case ID for single case operations",
    )
    parser.add_argument(
        "--case_ids",
        type=parse_case_ids,
        help="Comma-separated list of case IDs for bulk operations "
        "(e.g., 123,456,789)",
    )
    parser.add_argument(
        "--username",
        help="Username for case assignment operations",
    )

    args = parser.parse_args()

    # Initialize the client
    client = SecOpsClient()

    # Configure Chronicle client
    chronicle = client.chronicle(
        customer_id=args.customer_id,
        project_id=args.project_id,
        region=args.region,
    )

    # Run examples
    print("=" * 60)
    print("Chronicle Case Management Examples")
    print("=" * 60)

    # Example 1: List cases
    list_cases_example(chronicle)

    # Example 2: Get a single case (if case_id provided)
    if args.case_id:
        get_case_example(chronicle, args.case_id)

    # Example 3: Update a case (if case_id provided)
    if args.case_id:
        patch_case_example(chronicle, args.case_id)

    # Bulk operations (if case_ids provided)
    if args.case_ids:
        print(f"\nRunning bulk operations on {len(args.case_ids)} " f"cases")

        # Example 4: Add tags
        bulk_add_tags_example(chronicle, args.case_ids)

        # Example 5: Assign cases (if username provided)
        if args.username:
            bulk_assign_example(chronicle, args.case_ids, args.username)

        # Example 6: Change priority
        bulk_change_priority_example(chronicle, args.case_ids)

        # Example 7: Change stage
        bulk_change_stage_example(chronicle, args.case_ids)

        # Example 8: Close cases
        bulk_close_example(chronicle, args.case_ids)

        # Example 9: Reopen cases
        bulk_reopen_example(chronicle, args.case_ids)

        # Example 10: Merge cases (use first as target)
        if len(args.case_ids) > 1:
            target = args.case_ids[0]
            to_merge = args.case_ids[1:]
            merge_cases_example(chronicle, to_merge, target)

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
