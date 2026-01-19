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
"""Example usage of the Google SecOps SDK for Investigations."""

import argparse
import json

from secops import SecOpsClient
from secops.chronicle import DetectionType


def get_client(project_id, customer_id, region):
    """Initialize and return the Chronicle client.

    Args:
        project_id: Google Cloud Project ID.
        customer_id: Chronicle Customer ID (UUID).
        region: Chronicle region (us or eu).

    Returns:
        Chronicle client instance.
    """
    client = SecOpsClient()
    chronicle = client.chronicle(
        customer_id=customer_id, project_id=project_id, region=region
    )
    return chronicle


def example_list_investigations(chronicle):
    """Example 1: List Investigations."""
    print("\n=== Example 1: List Investigations ===")

    try:
        response = chronicle.list_investigations(page_size=10)

        investigations = response.get("investigations", [])
        total_size = response.get("totalSize", 0)
        next_page_token = response.get("nextPageToken")

        print(f"\nFound {len(investigations)} investigation(s) in this page")
        print(f"Total investigations matching request: {total_size}")

        if investigations:
            print("\nFirst investigation details:")
            sample = investigations[0]
            print(f"Name: {sample.get('name')}")
            print(f"Display Name: {sample.get('displayName', 'N/A')}")
            print(f"Status: {sample.get('status', 'N/A')}")
            print(f"Verdict: {sample.get('verdict', 'N/A')}")
            print(f"Confidence: {sample.get('confidence', 'N/A')}")
            print(f"Summary: {sample.get('summary', 'N/A')[:100]}...")

            investigation_id = sample.get("name", "").split("/")[-1]
            print(f"Investigation ID: {investigation_id}")

        if next_page_token:
            print(f"\nNext page token available: {next_page_token[:20]}...")
        else:
            print("No investigations found in your Chronicle instance.")

    except Exception as e:
        print(f"Error listing investigations: {e}")


def example_get_investigation(chronicle, investigation_id):
    """Example 2: Get Investigation by ID.

    Args:
        chronicle: Chronicle client instance.
        investigation_id: ID of the investigation to retrieve.
    """
    print("\n=== Example 2: Get Investigation by ID ===")

    if not investigation_id:
        print("No investigation ID provided.")
        return

    try:
        print(f"\nRetrieving investigation ID: {investigation_id}")
        investigation = chronicle.get_investigation(investigation_id)

        print("\nInvestigation details:")
        print(f"Name: {investigation.get('name')}")
        print(f"Display Name: {investigation.get('displayName', 'N/A')}")
        print(f"Status: {investigation.get('status', 'N/A')}")
        print(f"Verdict: {investigation.get('verdict', 'N/A')}")
        print(f"Confidence: {investigation.get('confidence', 'N/A')}")
        print(f"Trigger Type: {investigation.get('triggerType', 'N/A')}")

        summary = investigation.get("summary", "")
        if summary:
            print(f"Summary: {summary[:200]}...")

        next_steps = investigation.get("nextSteps", [])
        if next_steps:
            print(f"\nRecommended next steps ({len(next_steps)}):")
            for idx, step in enumerate(next_steps[:3], 1):
                print(f"  {idx}. {step.get('title', 'N/A')}")

        findings = investigation.get("findings", [])
        if findings:
            print(f"\nFindings: {len(findings)} finding(s)")

        entities = investigation.get("entities", [])
        if entities:
            print(f"Entities: {len(entities)} entity/entities")

        alerts = investigation.get("alerts", {}).get("ids", [])
        if alerts:
            print(f"Associated alerts: {len(alerts)} alert(s)")

        cases = investigation.get("cases", {}).get("ids", [])
        if cases:
            print(f"Associated cases: {len(cases)} case(s)")

    except Exception as e:
        print(f"Error getting investigation: {e}")


def example_fetch_associated_investigations(chronicle, alert_id):
    """Example 3: Fetch Associated Investigations for Alert.

    Args:
        chronicle: Chronicle client instance.
        alert_id: Alert ID to fetch investigations for.
    """
    print("\n=== Example 3: Fetch Associated Investigations ===")

    if not alert_id:
        print("No alert ID provided. Skipping this example.")
        return

    try:
        print(f"\nFetching investigations for alert ID: {alert_id}")

        response = chronicle.fetch_associated_investigations(
            detection_type=DetectionType.ALERT,
            alert_ids=[alert_id],
            association_limit_per_detection=5,
        )

        associations_list = response.get("associationsList", {})
        experimental_alert = response.get("experimentalAlert", {})

        print(f"\nResponse contains {len(associations_list)} alert(s)")

        for alert_key, association_data in associations_list.items():
            print(f"\nAlert ID: {alert_key}")

            is_experimental = experimental_alert.get(alert_key, False)
            if is_experimental:
                print("  Note: This is an experimental alert")

            investigations = association_data.get("investigations", [])
            print(f"  Associated investigations: {len(investigations)}")

            for idx, inv in enumerate(investigations, 1):
                print(f"\n  Investigation {idx}:")
                print(f"    Name: {inv.get('name')}")
                print(f"    Display Name: {inv.get('displayName', 'N/A')}")
                print(f"    Status: {inv.get('status', 'N/A')}")
                print(f"    Verdict: {inv.get('verdict', 'N/A')}")

        if not associations_list:
            print("No associated investigations found.")

    except Exception as e:
        print(f"Error fetching associated investigations: {e}")


def example_trigger_investigation(chronicle, alert_id):
    """Example 4: Trigger Investigation for Alert.

    Args:
        chronicle: Chronicle client instance.
        alert_id: Alert ID to trigger investigation for.
    """
    print("\n=== Example 4: Trigger Investigation ===")

    if not alert_id:
        print(
            "No alert ID provided. Please provide an alert ID to "
            "trigger an investigation."
        )
        return

    try:
        print(f"\nTriggering investigation for alert ID: {alert_id}")
        print(
            "Note: This will create a new investigation. "
            "Use with caution in production."
        )

        confirmation = (
            input("\nDo you want to proceed? (yes/no): ").strip().lower()
        )
        if confirmation != "yes":
            print("Skipping investigation trigger.")
            return

        investigation = chronicle.trigger_investigation(alert_id)

        print("\nInvestigation triggered successfully!")
        print(f"Name: {investigation.get('name')}")
        print(f"Display Name: {investigation.get('displayName', 'N/A')}")
        print(f"Status: {investigation.get('status', 'N/A')}")
        print(f"Trigger Type: {investigation.get('triggerType', 'N/A')}")

        investigation_id = investigation.get("name", "").split("/")[-1]
        print(f"Investigation ID: {investigation_id}")

    except Exception as e:
        print(f"Error triggering investigation: {e}")
        print(
            "Note: Make sure the alert ID exists and is valid for "
            "investigation."
        )


def example_list_investigations_with_pagination(chronicle):
    """Example 5: List Investigations with Pagination."""
    print("\n=== Example 5: List Investigations with Pagination ===")

    try:
        page_size = 5
        total_fetched = 0
        page_num = 1
        next_page_token = None

        print(f"\nFetching investigations (page size: {page_size})")

        while True:
            response = chronicle.list_investigations(
                page_size=page_size, page_token=next_page_token
            )

            investigations = response.get("investigations", [])
            next_page_token = response.get("nextPageToken")

            print(f"\nPage {page_num}:")
            print(f"  Investigations in this page: {len(investigations)}")
            total_fetched += len(investigations)

            for idx, inv in enumerate(investigations, 1):
                print(
                    f"  {idx}. {inv.get('name', 'N/A')} - "
                    f"{inv.get('status', 'N/A')}"
                )

            page_num += 1

            if not next_page_token or page_num > 3:
                break

        print(f"\nTotal investigations fetched: {total_fetched}")
        if next_page_token:
            print("More pages available...")

    except Exception as e:
        print(f"Error during pagination: {e}")


EXAMPLES = {
    "1": example_list_investigations,
    "2": example_get_investigation,
    "3": example_fetch_associated_investigations,
    "4": example_trigger_investigation,
    "5": example_list_investigations_with_pagination,
}


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(
        description="Run Chronicle Investigations examples"
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
            "Example number to run (1-5). "
            "If not specified, runs all applicable examples."
        ),
    )
    parser.add_argument(
        "--investigation_id", help="Investigation ID for example 2"
    )
    parser.add_argument("--alert_id", help="Alert ID for examples 3 and 4")

    args = parser.parse_args()

    chronicle = get_client(args.project_id, args.customer_id, args.region)

    if args.example:
        if args.example in EXAMPLES:
            example_func = EXAMPLES[args.example]
            if args.example == "2":
                investigation_id = args.investigation_id
                if not investigation_id:
                    print(
                        "No investigation ID provided. "
                        "Fetching from list operation..."
                    )
                    try:
                        response = chronicle.list_investigations(page_size=1)
                        investigations = response.get("investigations", [])
                        if investigations:
                            investigation_id = (
                                investigations[0].get("name", "").split("/")[-1]
                            )
                            print(f"Using investigation ID: {investigation_id}")
                        else:
                            print("No investigations found.")
                    except Exception as e:
                        print(f"Error fetching investigation ID: {e}")
                example_func(chronicle, investigation_id)
            elif args.example in ["3", "4"]:
                example_func(chronicle, args.alert_id)
            else:
                example_func(chronicle)
        else:
            print(
                f"Invalid example number. "
                f"Available examples: {', '.join(sorted(EXAMPLES.keys()))}"
            )
    else:
        print("Running all applicable examples...")
        example_list_investigations(chronicle)

        investigation_id = args.investigation_id
        if not investigation_id:
            print(
                "\nNo investigation ID provided. "
                "Fetching from list operation..."
            )
            try:
                response = chronicle.list_investigations(page_size=1)
                investigations = response.get("investigations", [])
                if investigations:
                    investigation_id = (
                        investigations[0].get("name", "").split("/")[-1]
                    )
                    print(f"Using investigation ID: {investigation_id}")
            except Exception as e:
                print(f"Error fetching investigation ID: {e}")

        if investigation_id:
            example_get_investigation(chronicle, investigation_id)

        if args.alert_id:
            example_fetch_associated_investigations(chronicle, args.alert_id)

        example_list_investigations_with_pagination(chronicle)

        print(
            "\n\nNote: Example 4 (trigger investigation) requires "
            "confirmation and was skipped in batch mode."
        )
        print("Run it separately with: --example 4 --alert_id YOUR_ALERT_ID")


if __name__ == "__main__":
    main()
