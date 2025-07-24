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
"""Example script demonstrating Chronicle Rule Exclusions functionality."""

import argparse
import uuid
from datetime import datetime, timedelta

from secops.chronicle.client import ChronicleClient
from secops.chronicle.rule_exclusion import RuleExclusionType


def get_client(project_id, customer_id, region):
    """Initialize and return the Chronicle client.

    Args:
        project_id: Google Cloud Project ID
        customer_id: Chronicle Customer ID (UUID)
        region: Chronicle region (us or eu)

    Returns:
        Chronicle client instance
    """
    return ChronicleClient(
        project_id=project_id, customer_id=customer_id, region=region
    )


def example_create_rule_exclusion(chronicle):
    """Create a new rule exclusion.

    Args:
        chronicle: ChronicleClient instance

    Returns:
        Created rule exclusion ID if successful, None otherwise
    """
    print("\n=== Create Rule Exclusion ===")

    display_name = "Test Rule Exclusion - " + f"{uuid.uuid4()}"
    refinement_type = RuleExclusionType.DETECTION_EXCLUSION.value
    query = '(ip = "8.8.8.8")'

    try:
        print(f"\nCreating rule exclusion: {display_name}")
        new_exclusion = chronicle.create_rule_exclusion(
            display_name=display_name,
            refinement_type=refinement_type,
            query=query,
        )
        exclusion_id = new_exclusion["name"].split("/")[-1]
        print(f"Created rule exclusion with ID: {exclusion_id}")
        return exclusion_id
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating rule exclusion: {e}")
        return None


def example_get_rule_exclusion(chronicle, exclusion_id):
    """Get rule exclusion details.

    Args:
        chronicle: ChronicleClient instance
        exclusion_id: ID of the rule exclusion
    """
    print("\n=== Get Rule Exclusion Details ===")

    try:
        exclusion_details = chronicle.get_rule_exclusion(exclusion_id)
        print("\nRule exclusion details:")
        print(f"Name: {exclusion_details.get('name')}")
        print(f"Display Name: {exclusion_details.get('display_name')}")
        print(f"Query: {exclusion_details.get('query')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting rule exclusion: {e}")


def example_list_rule_exclusions(chronicle):
    """List all rule exclusions.

    Args:
        chronicle: ChronicleClient instance
    """
    print("\n=== List Rule Exclusions ===")

    try:
        exclusions = chronicle.list_rule_exclusions(page_size=10)
        print(
            f"\nFound {len(exclusions.get('findingsRefinements', []))} "
            "rule exclusions"
        )
        for exclusion in exclusions.get("findingsRefinements", []):
            print(f"- {exclusion.get('display_name')}: {exclusion.get('name')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing rule exclusions: {e}")


def example_update_rule_exclusion(chronicle, exclusion_id):
    """Update rule exclusion.

    Args:
        chronicle: ChronicleClient instance
        exclusion_id: ID of the rule exclusion
    """
    print("\n=== Update Rule Exclusion ===")

    try:
        print("\nUpdating rule exclusion...")
        updated_exclusion = chronicle.patch_rule_exclusion(
            exclusion_id=exclusion_id,
            display_name="Updated Test Rule Exclusion",
            query='(domain="google.com")',
            update_mask="display_name,query",
        )
        print(f"Updated display name: {updated_exclusion.get('display_name')}")
        print(f"Updated query: {updated_exclusion.get('query')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating rule exclusion: {e}")


def example_get_deployment_status(chronicle, exclusion_id):
    """Get deployment status.

    Args:
        chronicle: ChronicleClient instance
        exclusion_id: ID of the rule exclusion
    """
    print("\n=== Get Deployment Status ===")

    try:
        deployment = chronicle.get_rule_exclusion_deployment(exclusion_id)
        print("\nDeployment status:")
        print(f"Enabled: {deployment.get('enabled', False)}")
        print(f"Archived: {deployment.get('archived', False)}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting deployment status: {e}")


def example_update_deployment(chronicle, exclusion_id):
    """Update deployment settings.

    Args:
        chronicle: ChronicleClient instance
        exclusion_id: ID of the rule exclusion
    """
    print("\n=== Update Deployment Settings ===")

    try:
        print("\nUpdating deployment settings...")
        updated_deployment = chronicle.update_rule_exclusion_deployment(
            exclusion_id,
            enabled=False,  # Disabling
            archived=True,  # Archiving
            detection_exclusion_application={
                "curatedRules": [],
                "curatedRuleSets": [],
                "rules": [],
            },
        )
        print(f"Enabled: {updated_deployment.get('enabled', False)}")
        print(f"Archived: {updated_deployment.get('archived', False)}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating deployment: {e}")


def example_compute_activity(chronicle, exclusion_id):
    """Compute activity statistics.

    Args:
        chronicle: ChronicleClient instance
        exclusion_id: ID of the rule exclusion
    """
    print("\n=== Compute Activity Statistics ===")

    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        print("\nComputing activity for last 7 days...")
        activity = chronicle.compute_rule_exclusion_activity(
            exclusion_id, start_time=start_time, end_time=end_time
        )
        print(f"Activity statistics: {activity}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error computing activity: {e}")


# Map of example functions
EXAMPLES = {
    "1": example_create_rule_exclusion,
    "2": example_get_rule_exclusion,
    "3": example_list_rule_exclusions,
    "4": example_update_rule_exclusion,
    "5": example_get_deployment_status,
    "6": example_update_deployment,
    "7": example_compute_activity,
}


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(
        description="Run Chronicle Rule Exclusions API examples"
    )
    parser.add_argument(
        "--project_id", required=True, help="Google Cloud Project ID"
    )
    parser.add_argument(
        "--customer_id", required=True, help="Chronicle Customer ID (UUID)"
    )
    parser.add_argument(
        "--region", default="us", help="Chronicle region (us or eu)"
    )
    parser.add_argument(
        "--example",
        "-e",
        help=(
            "Example number to run (1-7). If not specified, runs all examples."
        ),
    )

    args = parser.parse_args()

    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)

    # Track the exclusion ID for examples that need it
    exclusion_id = None

    if args.example:
        if args.example not in EXAMPLES:
            print(
                "Invalid example number. "
                f"Available examples: {', '.join(EXAMPLES.keys())}"
            )
            return

        # Example 1 and 2
        if args.example == "1" or args.example == "3":
            exclusion_id = EXAMPLES[args.example](chronicle)
        # Other Examples require an exclusion ID, so create one first
        else:
            print("Creating a rule exclusion first...")
            exclusion_id = example_create_rule_exclusion(chronicle)
            if exclusion_id:
                EXAMPLES[args.example](chronicle, exclusion_id)
    else:
        # Run all examples in order
        exclusion_id = example_create_rule_exclusion(chronicle)
        if exclusion_id:
            for example_num in sorted(EXAMPLES.keys())[
                1:
            ]:  # Skip example 1 as we already created
                if example_num == "3":
                    EXAMPLES[example_num](chronicle)
                else:
                    EXAMPLES[example_num](chronicle, exclusion_id)


if __name__ == "__main__":
    main()
