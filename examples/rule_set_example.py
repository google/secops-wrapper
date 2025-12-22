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
"""Example script demonstrating Chronicle Rule Set functionality."""

import argparse
from datetime import datetime, timedelta, timezone

from secops.chronicle.client import ChronicleClient
from secops.chronicle.models import AlertState, ListBasis


def get_client(project_id: str, customer_id: str, region: str):
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


def example_list_curated_rule_sets(chronicle):
    """List all curated rule sets.

    Args:
        chronicle: ChronicleClient instance

    Returns:
        List of rule set IDs for further operations
    """
    print("\n=== List Curated Rule Sets ===")

    try:
        result = chronicle.list_curated_rule_sets(page_size=10)
        rule_sets = result.get("curatedRuleSets", [])
        print(f"\nFound {len(rule_sets)} curated rule sets")
        if result.get("nextPageToken"):
            print("More results available (nextPageToken present)")

        # Return the first few rule sets for use in other examples
        results = []
        for i, rule_set in enumerate(rule_sets[:5]):
            # Full name format: projects/PROJECT/locations/LOCATION/curatedRuleSetCategories/CATEGORY_ID/curatedRuleSets/RULE_SET_ID
            name = rule_set.get("name", "")

            # Extract rule set ID from the full name
            rule_set_id = name.split("/")[-1] if name else ""

            # Extract category ID from the full name
            category_parts = name.split("/curatedRuleSets/")[0].split("/")
            category_id = category_parts[-1] if len(category_parts) > 1 else ""

            display_name = rule_set.get("displayName", "Unknown")
            print(f"- {display_name}: {rule_set_id}")

            results.append(
                {
                    "name": name,
                    "rule_set_id": rule_set_id,
                    "category_id": category_id,
                    "display_name": display_name,
                }
            )

        return results
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing curated rule sets: {e}")
        return []


def example_get_curated_rule_set(chronicle, rule_set_id):
    """Get a specific curated rule set by ID.

    Args:
        chronicle: ChronicleClient instance
        rule_set_id: ID of the rule set to get
    """
    print("\n=== Get Curated Rule Set ===")

    try:
        rule_set = chronicle.get_curated_rule_set(rule_set_id)
        print("\nCurated Rule Set details:")
        print(f"Name: {rule_set.get('name')}")
        print(f"Display Name: {rule_set.get('displayName')}")
        print(f"Description: {rule_set.get('description')}")
        print(f"Category: {rule_set.get('ruleSetCategory')}")
        print(f"Rules Count: {len(rule_set.get('ruleIds', []))}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule set: {e}")


def example_list_curated_rule_set_categories(chronicle):
    """List all curated rule set categories.

    Args:
        chronicle: ChronicleClient instance

    Returns:
        List of category IDs for further operations
    """
    print("\n=== List Curated Rule Set Categories ===")

    try:
        result = chronicle.list_curated_rule_set_categories(page_size=10)
        categories = result.get("curatedRuleSetCategories", [])
        print(f"\nFound {len(categories)} curated rule set categories")
        if result.get("nextPageToken"):
            print("More results available (nextPageToken present)")

        results = []
        for i, category in enumerate(categories[:5]):
            # Full name format: projects/PROJECT/locations/LOCATION/curatedRuleSetCategories/CATEGORY_ID
            name = category.get("name", "")

            # Extract category ID from the full name
            category_id = name.split("/")[-1] if name else ""

            display_name = category.get("displayName", "Unknown")
            print(f"- {display_name}: {category_id}")

            results.append(
                {
                    "name": name,
                    "category_id": category_id,
                    "display_name": display_name,
                }
            )

        return results
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing curated rule set categories: {e}")
        return []


def example_get_curated_rule_set_category(chronicle, category_id):
    """Get a specific curated rule set category by ID.

    Args:
        chronicle: ChronicleClient instance
        category_id: ID of the category to get
    """
    print("\n=== Get Curated Rule Set Category ===")

    try:
        category = chronicle.get_curated_rule_set_category(category_id)
        print("\nCurated Rule Set Category details:")
        print(f"Name: {category.get('name')}")
        print(f"Display Name: {category.get('displayName')}")
        print(f"Description: {category.get('description', 'No description')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule set category: {e}")


def example_list_curated_rules(chronicle):
    """List all curated rules.

    Args:
        chronicle: ChronicleClient instance

    Returns:
        List of rule IDs for further operations
    """
    print("\n=== List Curated Rules ===")

    try:
        result = chronicle.list_curated_rules(page_size=10)
        rules = result.get("curatedRules", [])
        print(f"\nFound {len(rules)} curated rules")
        if result.get("nextPageToken"):
            print("More results available (nextPageToken present)")

        results = []
        for i, rule in enumerate(rules[:5]):
            # Full name format: projects/PROJECT/locations/LOCATION/curatedRules/RULE_ID
            name = rule.get("name", "")

            # Extract rule ID from the full name
            rule_id = name.split("/")[-1] if name else ""

            display_name = rule.get("displayName", "Unknown")
            print(f"- {display_name}: {rule_id}")

            results.append(
                {"name": name, "rule_id": rule_id, "display_name": display_name}
            )

        return results
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing curated rules: {e}")
        return []


def example_get_curated_rule(chronicle, rule_id):
    """Get a specific curated rule by ID.

    Args:
        chronicle: ChronicleClient instance
        rule_id: ID of the rule to get
    """
    print("\n=== Get Curated Rule ===")

    try:
        rule = chronicle.get_curated_rule(rule_id)
        print("\nCurated Rule details:")
        print(f"Name: {rule.get('name')}")
        print(f"Display Name: {rule.get('displayName')}")
        print(f"Description: {rule.get('description')}")
        print(f"Severity: {rule.get('severity')}")
        print(f"MITRE ATT&CK Tactics: {rule.get('mitreTactics', [])}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule: {e}")


def example_get_curated_rule_by_name(chronicle, display_name):
    """Get a curated rule by display name.

    Args:
        chronicle: ChronicleClient instance
        display_name: Display name of the rule to find
    """
    print("\n=== Get Curated Rule By Name ===")

    try:
        print(f"\nSearching for rule with display name: {display_name}")
        rule = chronicle.get_curated_rule_by_name(display_name)
        print("\nCurated Rule details:")
        print(f"Name: {rule.get('name')}")
        print(f"Display Name: {rule.get('displayName')}")
        print(f"Description: {rule.get('description')}")
        print(f"Severity: {rule.get('severity')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule by name: {e}")


def example_search_curated_detections(chronicle, rule_id):
    """Search for detections generated by a specific curated rule.

    Args:
        chronicle: ChronicleClient instance
        rule_id: ID of the curated rule to search detections for

    Returns:
        Number of detections found
    """
    print("\n=== Search Curated Detections ===")
    print(f"Searching detections for rule: {rule_id}")

    try:
        # Search for detections from the last 7 days
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)

        result = chronicle.search_curated_detections(
            rule_id=rule_id,
            start_time=start_time,
            end_time=end_time,
            list_basis=ListBasis.DETECTION_TIME,
            alert_state=AlertState.ALERTING,
            page_size=10,
        )

        detections = result.get("curatedDetections", [])
        print(
            f"\nFound {len(detections)} alerting detections "
            f"in the last 7 days"
        )

        for i, detection in enumerate(detections[:3], 1):
            print(f"\nDetection {i}:")
            print(f"  ID: {detection.get('id', 'N/A')}")
            print(
                f"  Detection Time: " f"{detection.get('detectionTime', 'N/A')}"
            )

        next_page_token = result.get("nextPageToken")
        if next_page_token:
            print(
                "\nMore results available. Use page_token "
                "to retrieve next page."
            )

        return len(detections)

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error searching curated detections: {e}")
        return 0


def example_list_curated_rule_set_deployments(chronicle):
    """List all curated rule set deployments.

    Args:
        chronicle: ChronicleClient instance

    Returns:
        Dictionary with rule set ID and deployment details
    """
    print("\n=== List Curated Rule Set Deployments ===")

    try:
        result = chronicle.list_curated_rule_set_deployments(
            page_size=10, only_enabled=False
        )
        deployments = result.get("curatedRuleSetDeployments", [])
        print(f"\nFound {len(deployments)} " "curated rule set deployments")
        if result.get("nextPageToken"):
            print("More results available (nextPageToken present)")

        if deployments:
            # Return the first deployment for use in other examples
            deployment = deployments[0]

            # Full name format: projects/PROJECT/locations/LOCATION/curatedRuleSetCategories/CATEGORY_ID/curatedRuleSets/RULE_SET_ID/curatedRuleSetDeployments/PRECISION
            name = deployment.get("name", "")

            # Parse name to extract IDs
            parts = name.split("/")
            precision = parts[-1] if len(parts) > 0 else "precise"

            # The full rule set path is everything before /curatedRuleSetDeployments/{precision}
            rule_set_path = "/".join(parts[:-2]) if len(parts) > 2 else ""

            # Extract rule set ID - it's the part after the last /curatedRuleSets/ segment
            rule_set_segments = rule_set_path.split("/curatedRuleSets/")
            rule_set_id = (
                rule_set_segments[-1] if len(rule_set_segments) > 1 else ""
            )

            # Extract category ID - it's the part after the last /curatedRuleSetCategories/ but before /curatedRuleSets/
            if len(rule_set_segments) > 1:
                category_path = rule_set_segments[0]
                category_segments = category_path.split(
                    "/curatedRuleSetCategories/"
                )
                category_id = (
                    category_segments[-1] if len(category_segments) > 1 else ""
                )
            else:
                category_id = ""

            display_name = deployment.get("displayName", "Unknown")
            print(f"- {display_name}")
            print(f"  Enabled: {deployment.get('enabled', False)}")
            print(f"  Alerting: {deployment.get('alerting', False)}")
            print(f"  Precision: {deployment.get('precision', 'Unknown')}")

            return {
                "name": name,
                "rule_set_path": rule_set_path,
                "rule_set_id": rule_set_id,
                "category_id": category_id,
                "display_name": display_name,
                "precision": precision,
            }
        return None
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing curated rule set deployments: {e}")
        return None


def example_get_curated_rule_set_deployment(
    chronicle, rule_set_id, precision="precise"
):
    """Get deployment status of a curated rule set by ID.

    Args:
        chronicle: ChronicleClient instance
        rule_set_id: ID of the rule set
        precision: Precision level ("precise" or "broad")
    """
    print("\n=== Get Curated Rule Set Deployment ===")

    try:
        print(f"\nGetting deployment for rule set ID: {rule_set_id}")
        deployment = chronicle.get_curated_rule_set_deployment(
            rule_set_id, precision
        )
        print("\nDeployment details:")
        print(f"Name: {deployment.get('name')}")
        print(f"Display Name: {deployment.get('displayName')}")
        print(f"Enabled: {deployment.get('enabled', False)}")
        print(f"Alerting: {deployment.get('alerting', False)}")
        print(f"Precision: {deployment.get('precision')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule set deployment: {e}")


def example_get_curated_rule_set_deployment_by_name(
    chronicle, display_name, precision="precise"
):
    """Get deployment status of a curated rule set by name.

    Args:
        chronicle: ChronicleClient instance
        display_name: Display name of the rule set
        precision: Precision level ("precise" or "broad")
    """
    print("\n=== Get Curated Rule Set Deployment By Name ===")

    try:
        print(f"\nGetting deployment for rule set: {display_name}")
        deployment = chronicle.get_curated_rule_set_deployment_by_name(
            display_name, precision
        )
        print("\nDeployment details:")
        print(f"Name: {deployment.get('name')}")
        print(f"Display Name: {deployment.get('displayName')}")
        print(f"Enabled: {deployment.get('enabled', False)}")
        print(f"Alerting: {deployment.get('alerting', False)}")
        print(f"Precision: {deployment.get('precision')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule set deployment by name: {e}")


def example_update_curated_rule_set_deployment(
    chronicle, category_id, rule_set_id, precision="precise"
):
    """Update deployment settings of a curated rule set.

    Args:
        chronicle: ChronicleClient instance
        category_id: ID of the category
        rule_set_id: ID of the rule set
        precision: Precision level ("precise" or "broad")

    Returns:
        Original deployment status for later cleanup
    """
    print("\n=== Update Curated Rule Set Deployment ===")

    try:
        print(f"\nCategory ID: {category_id}")
        print(f"Rule Set ID: {rule_set_id}")
        print(f"Precision: {precision}")

        # First get the current deployment state
        current = chronicle.get_curated_rule_set_deployment(
            rule_set_id, precision
        )
        original_state = {
            "category_id": category_id,
            "rule_set_id": rule_set_id,
            "precision": precision,
            "enabled": current.get("enabled", False),
            "alerting": current.get("alerting", False),
        }
        print(
            f"\nCurrent deployment state: Enabled={original_state['enabled']}, "
            f"Alerting={original_state['alerting']}"
        )

        print(f"\nUpdating deployment for rule set ID: {rule_set_id}")

        # Configuration for updating the deployment
        deployment_config = {
            "category_id": category_id,
            "rule_set_id": rule_set_id,
            "precision": precision,
            "enabled": True,  # Enable the rule set
            "alerting": True,  # Enable alerting for the rule set
        }

        # Update the deployment
        updated = chronicle.update_curated_rule_set_deployment(
            deployment_config
        )

        print("\nUpdated deployment details:")
        print(f"Name: {updated.get('name')}")
        print(f"Enabled: {updated.get('enabled', False)}")
        print(f"Alerting: {updated.get('alerting', False)}")
        print(f"Precision: {updated.get('precision')}")

        return original_state
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating curated rule set deployment: {e}")
        return None


def example_cleanup_rule_set_deployment(
    chronicle, category_id, rule_set_id, original_state
):
    """Revert deployment settings of a curated rule set to original state.

    Args:
        chronicle: ChronicleClient instance
        category_id: ID of the category
        rule_set_id: ID of the rule set
        original_state: Dictionary containing original configuration and states
    """
    print("\n=== Cleanup: Revert Rule Set Deployment ===")

    if not original_state:
        print("No original state provided, cannot revert")
        return

    try:
        # Get values from original_state, falling back to parameters if not present
        category_id = original_state.get("category_id", category_id)
        rule_set_id = original_state.get("rule_set_id", rule_set_id)
        precision = original_state.get("precision", "precise")

        print(f"\nReverting deployment for rule set ID: {rule_set_id}")
        print(
            f"Restoring to: Enabled={original_state.get('enabled', False)}, "
            f"Alerting={original_state.get('alerting', False)}"
        )

        # Configuration for reverting the deployment
        deployment_config = {
            "category_id": category_id,
            "rule_set_id": rule_set_id,
            "precision": precision,
            "enabled": original_state.get("enabled", False),
            "alerting": original_state.get("alerting", False),
        }

        # Update the deployment back to original state
        reverted = chronicle.update_curated_rule_set_deployment(
            deployment_config
        )

        print("\nReverted deployment details:")
        print(f"Name: {reverted.get('name')}")
        print(f"Enabled: {reverted.get('enabled', False)}")
        print(f"Alerting: {reverted.get('alerting', False)}")
        print(f"Precision: {reverted.get('precision')}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error reverting curated rule set deployment: {e}")


# Map of example functions
EXAMPLES = {
    "1": example_list_curated_rule_sets,
    "2": example_get_curated_rule_set,
    "3": example_list_curated_rule_set_categories,
    "4": example_get_curated_rule_set_category,
    "5": example_list_curated_rules,
    "6": example_get_curated_rule,
    "7": example_get_curated_rule_by_name,
    "8": example_search_curated_detections,
    "9": example_list_curated_rule_set_deployments,
    "10": example_get_curated_rule_set_deployment,
    "11": example_get_curated_rule_set_deployment_by_name,
    "12": example_update_curated_rule_set_deployment,
    "13": example_cleanup_rule_set_deployment,
}


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(
        description="Run Chronicle Rule Set API examples"
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
            "Example number to run (1-12). If not specified, runs all examples."
        ),
    )
    parser.add_argument(
        "--rule_name", help="Rule display name for get_by_name examples"
    )
    parser.add_argument(
        "--rule_set_name", help="Rule set display name for get_by_name examples"
    )

    args = parser.parse_args()

    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)

    # Data needed across examples
    rule_sets = None
    categories = None
    rules = None
    deployment_info = None

    if args.example:
        if args.example not in EXAMPLES:
            print(
                "Invalid example number. "
                f"Available examples: {', '.join(EXAMPLES.keys())}"
            )
            return

        # Examples that don't need additional input
        if args.example in ["1", "3", "5", "9"]:
            if args.example == "1":
                rule_sets = EXAMPLES[args.example](chronicle)
            elif args.example == "3":
                categories = EXAMPLES[args.example](chronicle)
            elif args.example == "5":
                rules = EXAMPLES[args.example](chronicle)
            elif args.example == "9":
                deployment_info = EXAMPLES[args.example](chronicle)

        # Examples that need rule_set_id
        elif args.example == "2":
            if not rule_sets:
                rule_sets = example_list_curated_rule_sets(chronicle)

            if rule_sets:
                EXAMPLES[args.example](chronicle, rule_sets[0]["rule_set_id"])

        # Examples that need category_id
        elif args.example == "4":
            if not categories:
                categories = example_list_curated_rule_set_categories(chronicle)

            if categories:
                EXAMPLES[args.example](chronicle, categories[0]["category_id"])

        # Examples that need rule_id (6 and 8)
        elif args.example in ["6", "8"]:
            if not rules:
                rules = example_list_curated_rules(chronicle)

            if rules:
                EXAMPLES[args.example](chronicle, rules[0]["rule_id"])

        # Examples that need rule_name
        elif args.example == "7":
            EXAMPLES[args.example](chronicle, args.rule_name)

        # Examples that need rule_set_id and precision
        elif args.example == "10":
            if not rule_sets:
                rule_sets = example_list_curated_rule_sets(chronicle)

            if rule_sets:
                EXAMPLES[args.example](chronicle, rule_sets[0]["rule_set_id"])

        # Examples that need rule_set_name and precision
        elif args.example == "11":
            EXAMPLES[args.example](chronicle, args.rule_set_name)

        # Examples that need category_id, rule_set_id and precision
        elif args.example == "12":
            if not rule_sets:
                rule_sets = example_list_curated_rule_sets(chronicle)

            if rule_sets:
                original_state = EXAMPLES[args.example](
                    chronicle,
                    rule_sets[0]["category_id"],
                    rule_sets[0]["rule_set_id"],
                )
                # Perform cleanup after update
                if original_state and args.example != "13":
                    example_cleanup_rule_set_deployment(
                        chronicle,
                        rule_sets[0]["category_id"],
                        rule_sets[0]["rule_set_id"],
                        original_state,
                    )
    else:
        # Run all examples in order
        print("\nRunning all Rule Set examples...")

        # Examples that return data we need for other examples
        rule_sets = example_list_curated_rule_sets(chronicle)
        categories = example_list_curated_rule_set_categories(chronicle)
        rules = example_list_curated_rules(chronicle)
        deployment_info = example_list_curated_rule_set_deployments(chronicle)

        # If we have the needed data, run the dependent examples
        if rule_sets and len(rule_sets) > 0:
            print(
                f"\nUsing rule set: {rule_sets[0]['display_name']} (ID: {rule_sets[0]['rule_set_id']})"
            )
            example_get_curated_rule_set(chronicle, rule_sets[0]["rule_set_id"])

        if categories and len(categories) > 0:
            print(
                f"\nUsing category: {categories[0]['display_name']} (ID: {categories[0]['category_id']})"
            )
            example_get_curated_rule_set_category(
                chronicle, categories[0]["category_id"]
            )

        if rules and len(rules) > 0:
            print(
                f"\nUsing rule: {rules[0]['display_name']} (ID: {rules[0]['rule_id']})"
            )
            example_get_curated_rule(chronicle, rules[0]["rule_id"])

            # Search for detections for this rule
            example_search_curated_detections(chronicle, rules[0]["rule_id"])

        # Examples that use display names (prioritize arguments, fallback to list results)
        # For curated rule by name
        if args.rule_name:
            # Use the user-provided rule name
            print(
                f"\nLooking up rule by display name: {args.rule_name} (user-provided)"
            )
            rule_display_name = args.rule_name
        elif rules and len(rules) > 0:
            # Fallback: use the display name from the first rule in the list
            rule_display_name = rules[0]["display_name"]
            print(
                f"\nLooking up rule by display name: {rule_display_name} (from list)"
            )
        else:
            # Default fallback
            rule_display_name = "Remote Code Execution via Web Request"
            print(
                f"\nLooking up rule by display name: {rule_display_name} (default)"
            )

        example_get_curated_rule_by_name(chronicle, rule_display_name)

        # For curated rule set deployment by name
        if args.rule_set_name:
            # Use the user-provided rule set name
            print(
                f"\nLooking up rule set deployment by name: {args.rule_set_name} (user-provided)"
            )
            rule_set_display_name = args.rule_set_name
        elif rule_sets and len(rule_sets) > 0:
            # Fallback: use the display name from the first rule set in the list
            rule_set_display_name = rule_sets[0]["display_name"]
            print(
                f"\nLooking up rule set deployment by name: {rule_set_display_name} (from list)"
            )
        else:
            # Default fallback
            rule_set_display_name = "Cloud Security"
            print(
                f"\nLooking up rule set deployment by name: {rule_set_display_name} (default)"
            )

        example_get_curated_rule_set_deployment_by_name(
            chronicle, rule_set_display_name
        )

        # Examples that need data from other examples
        if rule_sets and len(rule_sets) > 0:
            example_get_curated_rule_set_deployment(
                chronicle, rule_sets[0]["rule_set_id"]
            )

        # Update example only if we have all the data
        if rule_sets and len(rule_sets) > 0:
            print(
                f"\nUpdating and then reverting rule set: {rule_sets[0]['display_name']}"
            )
            print(f"Category ID: {rule_sets[0]['category_id']}")
            print(f"Rule set ID: {rule_sets[0]['rule_set_id']}")

            original_state = example_update_curated_rule_set_deployment(
                chronicle,
                rule_sets[0]["category_id"],
                rule_sets[0]["rule_set_id"],
            )

            # Cleanup after update
            if original_state:
                example_cleanup_rule_set_deployment(
                    chronicle,
                    rule_sets[0]["category_id"],
                    rule_sets[0]["rule_set_id"],
                    original_state,
                )


if __name__ == "__main__":
    main()
