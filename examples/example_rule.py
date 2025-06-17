#!/usr/bin/env python3
"""Example usage of the Google SecOps SDK for Chronicle Rule Management."""

from datetime import datetime, timedelta, timezone
from secops import SecOpsClient
from pprint import pprint
from secops.exceptions import APIError
import argparse
import sys
import time


def get_client(project_id, customer_id, region):
    """Initialize and return the Chronicle client.

    Args:
        project_id: Google Cloud project ID
        customer_id: Chronicle customer ID (UUID with dashes)
        region: Chronicle region (us or eu)

    Returns:
        Chronicle client instance
    """
    client = SecOpsClient()
    chronicle = client.chronicle(
        customer_id=customer_id, project_id=project_id, region=region
    )
    return chronicle


def get_time_range():
    """Get default time range for queries.

    Returns:
        Tuple of (start_time, end_time)
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)
    return start_time, end_time


def example_create_rule(chronicle):
    """Example 1: Create a Rule.

    Args:
        chronicle: Chronicle client instance

    Returns:
        Created rule information
    """
    print("\n=== Example 1: Create a Rule ===")

    # Define a simple rule
    rule_text = """
rule simple_network_rule {
    meta:
        description = "Example rule to detect large amounts of network connections"
        author = "SecOps SDK Example"
        severity = "Medium"
        priority = "Medium"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
        $e.principal.hostname != ""
    condition:
        $e
}
"""

    try:
        # Create the rule
        rule = chronicle.create_rule(rule_text)

        print("\nRule created successfully:")
        print(f"Rule ID: {rule.get('name', '').split('/')[-1]}")
        print(f"Rule Version: {rule.get('version_id', '')}")

        return rule
    except APIError as e:
        print(f"Error creating rule: {e}")
        return None


def example_list_rules(chronicle):
    """Example 2: List Rules.

    Args:
        chronicle: Chronicle client instance
    """
    print("\n=== Example 2: List Rules ===")

    try:
        rules = chronicle.list_rules()

        print(f"\nFound {len(rules.get('rules', []))} rules:")

        # Print details of each rule
        for idx, rule in enumerate(rules.get("rules", []), 1):
            rule_id = rule.get("name", "").split("/")[-1]
            rule_text = rule.get("text", "").split("\n")[0]  # Just get the first line
            enabled = rule.get("deployment", {}).get("enabled", False)

            print(f"\n{idx}. Rule ID: {rule_id}")
            print(f"   Enabled: {'Yes' if enabled else 'No'}")
            print(f"   Definition: {rule_text}")
    except APIError as e:
        print(f"Error listing rules: {e}")


def example_get_rule(chronicle, rule_id):
    """Example 3: Get Rule Details.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to get

    Returns:
        Rule details
    """
    print("\n=== Example 3: Get Rule Details ===")

    try:
        rule = chronicle.get_rule(rule_id)

        print("\nRule details:")
        print(f"Rule ID: {rule_id}")
        print(f"Version: {rule.get('version_id', '')}")
        print(f"Create Time: {rule.get('create_time', '')}")
        print(f"Deployment Enabled: {rule.get('deployment', {}).get('enabled', False)}")
        print(f"Deployment Live: {rule.get('deployment', {}).get('live', False)}")

        print("\nRule content:")
        print(rule.get("text", ""))

        return rule
    except APIError as e:
        print(f"Error getting rule: {e}")
        return None


def example_update_rule(chronicle, rule_id, rule):
    """Example 4: Update a Rule.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to update
        rule: Rule object with current details

    Returns:
        Updated rule information
    """
    print("\n=== Example 4: Update a Rule ===")

    if not rule:
        print("No rule to update")
        return None

    # Make a simple change to the rule - update the severity
    current_text = rule.get("text", "")
    if 'severity = "Medium"' in current_text:
        updated_text = current_text.replace('severity = "Medium"', 'severity = "High"')
    else:
        # Find and update the severity in a more generic way
        lines = current_text.split("\n")
        for i, line in enumerate(lines):
            if "severity" in line:
                lines[i] = '        severity = "High"'
                break
        updated_text = "\n".join(lines)

    try:
        # Update the rule
        updated_rule = chronicle.update_rule(rule_id, updated_text)

        print("\nRule updated successfully:")
        print(f"Rule ID: {rule_id}")
        print(f"New Version: {updated_rule.get('version_id', '')}")

        return updated_rule
    except APIError as e:
        print(f"Error updating rule: {e}")
        return None


def example_enable_rule(chronicle, rule_id):
    """Example 5: Enable a Rule.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to enable
    """
    print("\n=== Example 5: Enable a Rule ===")

    try:
        deployment = chronicle.enable_rule(rule_id)

        print("\nRule enabled successfully:")
        print(f"Rule ID: {rule_id}")
        print(f"Enabled: {deployment.get('enabled', False)}")
        print(f"Live: {deployment.get('live', False)}")
    except APIError as e:
        print(f"Error enabling rule: {e}")


def example_create_retrohunt(chronicle, rule_id):
    """Example 6: Create a Retrohunt.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to run retrohunt for

    Returns:
        Retrohunt operation information
    """
    print("\n=== Example 6: Create a Retrohunt ===")

    # Use the past 24 hours for retrohunt
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)

    try:
        retrohunt = chronicle.create_retrohunt(rule_id, start_time, end_time)

        operation_name = retrohunt.get("name", "")
        operation_id = operation_name.split("/")[-1] if operation_name else ""

        print("\nRetrohunt created successfully:")
        print(f"Rule ID: {rule_id}")
        print(f"Operation ID: {operation_id}")
        print(f"Start Time: {start_time.isoformat()}")
        print(f"End Time: {end_time.isoformat()}")

        return retrohunt
    except APIError as e:
        print(f"Error creating retrohunt: {e}")
        return None


def example_get_retrohunt(chronicle, rule_id, retrohunt):
    """Example 7: Get Retrohunt Status.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule the retrohunt is for
        retrohunt: Retrohunt operation information
    """
    print("\n=== Example 7: Get Retrohunt Status ===")

    if not retrohunt:
        print("No retrohunt to check")
        return

    operation_name = retrohunt.get("name", "")
    operation_id = operation_name.split("/")[-1] if operation_name else ""

    if not operation_id:
        print("No valid operation ID found")
        return

    try:
        # Get retrohunt status
        retrohunt_status = chronicle.get_retrohunt(rule_id, operation_id)

        print("\nRetrohunt status:")
        print(f"Rule ID: {rule_id}")
        print(f"Operation ID: {operation_id}")
        print(f"Status: {retrohunt_status.get('metadata', {}).get('status', {})}")
        print(
            f"Create Time: {retrohunt_status.get('metadata', {}).get('create_time', '')}"
        )
        print(f"Done: {retrohunt_status.get('metadata', {}).get('done', False)}")

        # Check if there's an error
        if retrohunt_status.get("metadata", {}).get("error"):
            print(f"Error: {retrohunt_status.get('metadata', {}).get('error')}")
    except APIError as e:
        print(f"Error getting retrohunt status: {e}")


def example_list_detections(chronicle, rule_id):
    """Example 8: List Detections for a Rule.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to list detections for
    """
    print("\n=== Example 8: List Detections for a Rule ===")

    try:
        detections = chronicle.list_detections(rule_id)

        detection_count = len(detections.get("detections", []))

        print(f"\nFound {detection_count} detections for rule {rule_id}:")

        # Print details of each detection
        for idx, detection in enumerate(detections.get("detections", []), 1):
            if idx > 5:  # Limit to first 5 detections
                print(f"\n... and {detection_count - 5} more detections")
                break

            detection_id = detection.get("id", "")
            create_time = detection.get("createTime", "")
            event_time = detection.get("eventTime", "")
            alerting = detection.get("alertState", "") == "ALERTING"

            print(f"\n{idx}. Detection ID: {detection_id}")
            print(f"   Create Time: {create_time}")
            print(f"   Event Time: {event_time}")
            print(f"   Alerting: {'Yes' if alerting else 'No'}")
    except APIError as e:
        print(f"Error listing detections: {e}")


def example_list_errors(chronicle, rule_id):
    """Example 9: List Errors for a Rule.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to list errors for
    """
    print("\n=== Example 9: List Errors for a Rule ===")

    try:
        errors = chronicle.list_errors(rule_id)

        error_count = len(errors.get("ruleExecutionErrors", []))

        print(f"\nFound {error_count} execution errors for rule {rule_id}:")

        # Print details of each error
        for idx, error in enumerate(errors.get("ruleExecutionErrors", []), 1):
            if idx > 5:  # Limit to first 5 errors
                print(f"\n... and {error_count - 5} more errors")
                break

            rule_version = (
                error.get("rule", "").split("@")[-1]
                if "@" in error.get("rule", "")
                else "latest"
            )
            create_time = error.get("create_time", "")
            error_message = error.get("error_message", "")

            print(f"\n{idx}. Rule Version: {rule_version}")
            print(f"   Create Time: {create_time}")
            print(f"   Error Message: {error_message}")
    except APIError as e:
        print(f"Error listing rule errors: {e}")


def example_search_rule_alerts(chronicle):
    """Example 10: Search Rule Alerts.

    Args:
        chronicle: Chronicle client instance
    """
    print("\n=== Example 10: Search Rule Alerts ===")

    # Use the past week for the search
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)

    try:
        # Search for alerts from rules
        alerts_response = chronicle.search_rule_alerts(
            start_time=start_time, end_time=end_time, page_size=10  # Limit to 10 alerts
        )

        # Extract all alerts from the nested structure
        all_alerts = []
        too_many_alerts = alerts_response.get("tooManyAlerts", False)

        # Process the ruleAlerts array which contains rule objects with embedded alerts
        for rule_alert in alerts_response.get("ruleAlerts", []):
            rule_metadata = rule_alert.get("ruleMetadata", {})
            rule_id = rule_metadata.get("ruleId", "Unknown")

            # Try different paths for rule ID
            if rule_id == "Unknown" and "properties" in rule_metadata:
                rule_id = rule_metadata.get("properties", {}).get("ruleId", "Unknown")

            rule_name = rule_metadata.get("properties", {}).get("name", "Unknown")

            # Get alerts for this rule
            rule_alerts = rule_alert.get("alerts", [])

            # Add rule information to each alert and add to our collection
            for alert in rule_alerts:
                # Add rule information to the alert
                alert["rule_id"] = rule_id
                alert["rule_name"] = rule_name
                all_alerts.append(alert)

        print(
            f"\nFound {len(all_alerts)} rule alerts from {len(alerts_response.get('ruleAlerts', []))} rules:"
        )
        if too_many_alerts:
            print(
                "Note: There were too many alerts matching your criteria. Results have been limited."
            )

        for idx, alert in enumerate(all_alerts, 1):
            # Extract alert details
            alert_id = alert.get("id", "N/A")
            rule_id = alert.get("rule_id", "N/A")
            rule_name = alert.get("rule_name", "Unknown Rule")
            detection_time = alert.get("detectionTimestamp", "Unknown")
            commit_time = alert.get("commitTimestamp", "Unknown")
            alerting_type = alert.get("alertingType", "Unknown")

            print(f"\n{idx}. Alert ID: {alert_id}")
            print(f"   Rule ID: {rule_id}")
            print(f"   Rule Name: {rule_name}")
            print(f"   Detection Time: {detection_time}")
            print(f"   Commit Time: {commit_time}")
            print(f"   Alerting Type: {alerting_type}")

            # Print event info if available (limited to avoid overload)
            if "resultEvents" in alert:
                event_samples = []
                for var_name, event_data in alert.get("resultEvents", {}).items():
                    if "eventSamples" in event_data:
                        for sample in event_data.get("eventSamples", []):
                            if "event" in sample:
                                event_samples.append(sample["event"])

                print(f"   Events: {len(event_samples)} event samples")
                if (
                    event_samples and idx <= 3
                ):  # Only show event details for first 3 alerts
                    first_event = event_samples[0]
                    print(
                        f"   First Event Type: {first_event.get('metadata', {}).get('eventType', 'Unknown')}"
                    )

                    # Show DNS query if this is a DNS event
                    dns_data = first_event.get("network", {}).get("dns", {})
                    if dns_data and "questions" in dns_data:
                        questions = dns_data.get("questions", [])
                        if questions:
                            print(
                                f"   DNS Query: {questions[0].get('name', 'Unknown')}"
                            )

            if idx >= 10:  # Limit detailed output to 10 alerts
                remaining = len(all_alerts) - 10
                if remaining > 0:
                    print(f"\n... and {remaining} more alerts")
                break
    except APIError as e:
        print(f"Error searching rule alerts: {e}")


def example_rule_set_management(chronicle):
    """Example 11: Rule Set Management.

    Args:
        chronicle: Chronicle client instance
    """
    print("\n=== Example 11: Rule Set Management ===")
    print("\nThis example requires specific category and rule set IDs.")
    print("In a real environment, you would update the following values:")

    # Example UUIDs (these are not real)
    category_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    rule_set_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

    print(f"\nCategory ID: {category_id}")
    print(f"Rule Set ID: {rule_set_id}")

    # Define deployments to update
    deployments = [
        {
            "category_id": category_id,
            "rule_set_id": rule_set_id,
            "precision": "broad",
            "enabled": True,
            "alerting": False,
        }
    ]

    print("\nSince this is just an example with placeholder IDs, we won't")
    print("actually make the API call. In a real environment, you would use:")
    print("\nchronicle.batch_update_curated_rule_set_deployments(deployments)")


def example_delete_rule(chronicle, rule_id):
    """Example 12: Delete a Rule.

    Args:
        chronicle: Chronicle client instance
        rule_id: ID of the rule to delete
    """
    print("\n=== Example 12: Delete a Rule ===")

    try:
        # Delete the rule
        result = chronicle.delete_rule(rule_id)

        print(f"\nRule {rule_id} deleted successfully")
    except APIError as e:
        print(f"Error deleting rule: {e}")


def example_validate_rule(chronicle):
    """Example 13: Rule Validation.

    Args:
        chronicle: Chronicle client instance
    """
    print("\n=== Example 13: Rule Validation ===")

    # Example of a valid rule
    valid_rule = """
rule test_rule {
    meta:
        description = "Test rule for validation"
        author = "Test Author"
        severity = "Low"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
    condition:
        $e
}
"""

    try:
        print("\nValidating a correct rule:")
        result = chronicle.validate_rule(valid_rule)
        if result.success:
            print("✅ Rule is valid")
        else:
            print(f"❌ Rule is invalid: {result.message}")
            if result.position:
                print(
                    f"   Error at line {result.position['startLine']}, column {result.position['startColumn']}"
                )

        # Example of an invalid rule (missing condition)
        invalid_rule = """
rule test_rule {
    meta:
        description = "Test rule for validation"
        author = "Test Author"
        severity = "Low"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
}
"""

        print("\nValidating an incorrect rule:")
        result = chronicle.validate_rule(invalid_rule)
        if result.success:
            print("✅ Rule is valid")
        else:
            print(f"❌ Rule is invalid: {result.message}")
            if result.position:
                print(
                    f"   Error at line {result.position['startLine']}, column {result.position['startColumn']}"
                )

    except APIError as e:
        print(f"Error validating rule: {str(e)}")


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(
        description="Run Chronicle Rule Management examples"
    )
    parser.add_argument("--project_id", required=True, help="Google Cloud Project ID")
    parser.add_argument(
        "--customer_id", required=True, help="Chronicle Customer ID (UUID)"
    )
    parser.add_argument("--region", default="us", help="Chronicle region (us or eu)")
    parser.add_argument(
        "--example",
        "-e",
        type=int,
        help="Example number to run (1-13). If not specified, runs all examples.",
    )

    args = parser.parse_args()

    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)

    # Dictionary to map example numbers to functions
    examples = {
        1: lambda: example_create_rule(chronicle),
        2: lambda: example_list_rules(chronicle),
        3: lambda rule_id: example_get_rule(chronicle, rule_id),
        4: lambda rule_id: example_update_rule(
            chronicle, rule_id, example_get_rule(chronicle, rule_id)
        ),
        5: lambda rule_id: example_enable_rule(chronicle, rule_id),
        6: lambda rule_id: example_create_retrohunt(chronicle, rule_id),
        7: lambda rule_id: (
            lambda retrohunt: (
                time.sleep(2),
                example_get_retrohunt(chronicle, rule_id, retrohunt),
            )
        )(example_create_retrohunt(chronicle, rule_id)),
        8: lambda rule_id: example_list_detections(chronicle, rule_id),
        9: lambda rule_id: example_list_errors(chronicle, rule_id),
        10: lambda: example_search_rule_alerts(chronicle),
        11: lambda: example_rule_set_management(chronicle),
        12: lambda rule_id: example_delete_rule(chronicle, rule_id),
        13: lambda: example_validate_rule(chronicle),
    }

    # Examples that require a rule ID
    REQUIRES_RULE_ID = {3, 4, 5, 6, 7, 8, 9, 12}

    if args.example:
        if args.example not in range(1, 14):
            print(f"Invalid example number. Available examples: 1-13")
            return

        if args.example == 1:
            created_rule = examples[1]()
            if created_rule:
                rule_id = created_rule.get("name", "").split("/")[-1]
                print(f"\nCreated rule with ID: {rule_id}")
                print("You can use this ID with other examples.")
        elif args.example in REQUIRES_RULE_ID:
            # Only ask for rule ID if the example needs it
            rule_id = input("\nPlease enter a rule ID to use for this example: ")
            if not rule_id:
                print("No rule ID provided.")
                return
            examples[args.example](rule_id)
        else:
            # Examples that don't need a rule ID
            examples[args.example]()
    else:
        # Run all examples in sequence
        print("\n=== Running all examples ===")
        print("This will create a rule and then perform various operations on it.")

        # Example 1: Create a rule
        created_rule = example_create_rule(chronicle)
        if not created_rule:
            print("Failed to create a rule. Cannot continue with other examples.")
            return

        rule_id = created_rule.get("name", "").split("/")[-1]

        # Example 2: List rules (doesn't need rule ID)
        example_list_rules(chronicle)

        # Examples that need rule ID
        examples[3](rule_id)  # Get rule details
        examples[4](rule_id)  # Update rule
        examples[5](rule_id)  # Enable rule

        # Example 6 & 7: Create retrohunt and get status
        examples[7](rule_id)

        # Example 8: List detections
        examples[8](rule_id)

        # Example 9: List errors
        examples[9](rule_id)

        # Examples that don't need rule ID
        examples[10]()  # Search rule alerts
        examples[11]()  # Rule set management

        # Example 12: Delete rule (needs rule ID)
        examples[12](rule_id)

        # Example 13: Validate rule (doesn't need rule ID)
        examples[13]()


if __name__ == "__main__":
    main()
