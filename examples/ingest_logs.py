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
"""Example demonstrating raw log ingestion with Chronicle."""

import json
import argparse
from datetime import datetime, timezone
from secops import SecOpsClient
from secops.exceptions import APIError


def create_sample_okta_log(username: str = "jdoe@example.com") -> str:
    """Create a sample OKTA log in JSON format.

    Args:
        username: The username to include in the log

    Returns:
        A JSON string representing an OKTA log
    """
    # Get current time in ISO format with Z timezone indicator
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create sample event
    okta_log = {
        "actor": {"displayName": "Joe Doe", "alternateId": username},
        "client": {
            "ipAddress": "192.168.1.100",
            "userAgent": {"os": "Mac OS X", "browser": "SAFARI"},
        },
        "displayMessage": "User login to Okta",
        "eventType": "user.session.start",
        "outcome": {"result": "SUCCESS"},
        "published": current_time,
    }

    return json.dumps(okta_log)


def create_sample_windows_log(username: str = "user123") -> str:
    """Create a sample Windows XML log.

    Args:
        username: The username to include in the log

    Returns:
        An XML string representing a Windows Event log
    """
    # Get current time in ISO format with Z timezone indicator
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return f"""<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
  <System>
    <Provider Name='Microsoft-Windows-Security-Auditing' Guid='{{54849625-5478-4994-A5BA-3E3B0328C30D}}'/>
    <EventID>4624</EventID>
    <Version>1</Version>
    <Level>0</Level>
    <Task>12544</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8020000000000000</Keywords>
    <TimeCreated SystemTime='{current_time}'/>
    <EventRecordID>202117513</EventRecordID>
    <Correlation/>
    <Execution ProcessID='656' ThreadID='700'/>
    <Channel>Security</Channel>
    <Computer>WIN-SERVER.xyz.net</Computer>
    <Security/>
  </System>
  <EventData>
    <Data Name='SubjectUserSid'>S-1-0-0</Data>
    <Data Name='SubjectUserName'>-</Data>
    <Data Name='TargetUserName'>{username}</Data>
    <Data Name='WorkstationName'>CLIENT-PC</Data>
    <Data Name='LogonType'>3</Data>
  </EventData>
</Event>"""


def ingest_single_log(chronicle_client):
    """Demonstrate ingesting a single raw log."""
    print("\n=== Ingesting a Single Log ===")

    # Create a sample OKTA log
    okta_log = create_sample_okta_log()
    print(f"Log Type: OKTA")

    try:
        # Ingest the log
        result = chronicle_client.ingest_log(log_type="OKTA", log_message=okta_log)
        print("Log successfully ingested!")
        print(f"Operation: {result.get('operation')}")

    except APIError as e:
        print(f"Error ingesting log: {e}")


def ingest_batch_logs(chronicle_client):
    """Demonstrate ingesting multiple logs in a batch."""
    print("\n=== Ingesting Multiple Logs in a Batch ===")

    # Create multiple sample logs
    logs = [
        create_sample_okta_log("user1@example.com"),
        create_sample_okta_log("user2@example.com"),
        create_sample_okta_log("user3@example.com"),
    ]

    print(f"Number of logs: {len(logs)}")
    print(f"Log Type: OKTA")

    try:
        # Ingest multiple logs in a single API call
        result = chronicle_client.ingest_log(log_type="OKTA", log_message=logs)
        print("All logs successfully ingested in a batch!")
        print(f"Operation: {result.get('operation')}")

    except APIError as e:
        print(f"Error ingesting logs: {e}")


def ingest_different_log_types(chronicle_client):
    """Demonstrate ingesting logs of different types."""
    print("\n=== Ingesting Different Log Types ===")

    # Create a Windows XML log
    windows_xml_log = create_sample_windows_log()
    print(f"Log Type: WINEVTLOG_XML")

    try:
        # Ingest the Windows XML log
        result = chronicle_client.ingest_log(
            log_type="WINEVTLOG_XML", log_message=windows_xml_log
        )
        print("Windows XML log successfully ingested!")
        print(f"Operation: {result.get('operation')}")

    except APIError as e:
        print(f"Error ingesting Windows XML log: {e}")

    # Demonstrate batch ingestion with multiple Windows logs
    print("\n=== Ingesting Multiple Windows Logs in a Batch ===")

    windows_logs = [
        create_sample_windows_log("admin"),
        create_sample_windows_log("guest"),
        create_sample_windows_log("system"),
    ]

    try:
        # Ingest multiple Windows XML logs in a single API call
        result = chronicle_client.ingest_log(
            log_type="WINEVTLOG_XML", log_message=windows_logs
        )
        print("All Windows XML logs successfully ingested in a batch!")
        print(f"Operation: {result.get('operation')}")

    except APIError as e:
        print(f"Error ingesting Windows XML logs: {e}")


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(
        description="Example of raw log ingestion with Chronicle"
    )
    parser.add_argument("--customer-id", required=True, help="Chronicle instance ID")
    parser.add_argument("--project-id", required=True, help="GCP project ID")
    parser.add_argument("--region", default="us", help="Chronicle API region")

    args = parser.parse_args()

    # Initialize the client
    client = SecOpsClient()

    # Configure Chronicle client
    chronicle = client.chronicle(
        customer_id=args.customer_id, project_id=args.project_id, region=args.region
    )

    # Run examples
    ingest_single_log(chronicle)
    ingest_batch_logs(chronicle)
    ingest_different_log_types(chronicle)


if __name__ == "__main__":
    main()
