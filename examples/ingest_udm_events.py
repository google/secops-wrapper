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
"""Example demonstrating UDM event ingestion with Chronicle."""

import uuid
import argparse
from datetime import datetime, timezone
from secops import SecOpsClient
from secops.exceptions import APIError


def create_sample_network_event():
    """Create a sample network connection UDM event."""
    # Generate a unique ID
    event_id = str(uuid.uuid4())

    # Get current time in ISO 8601 format with Z timezone indicator
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create sample event
    return {
        "metadata": {
            "id": event_id,
            "event_timestamp": current_time,
            "event_type": "NETWORK_CONNECTION",
            "product_name": "Example Script",
            "vendor_name": "Google",
        },
        "principal": {
            "hostname": "workstation-1",
            "ip": "192.168.1.100",
            "port": 52734,
        },
        "target": {"ip": "203.0.113.10", "port": 443},
        "network": {"application_protocol": "HTTPS", "direction": "OUTBOUND"},
    }


def create_sample_process_event():
    """Create a sample process launch UDM event."""
    # Generate a unique ID
    event_id = str(uuid.uuid4())

    # Get current time in ISO 8601 format with Z timezone indicator
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create sample event
    return {
        "metadata": {
            "id": event_id,
            "event_timestamp": current_time,
            "event_type": "PROCESS_LAUNCH",
            "product_name": "Example Script",
            "vendor_name": "Google",
        },
        "principal": {
            "hostname": "workstation-1",
            "process": {
                "command_line": "python example.py",
                "pid": 12345,
                "file": {
                    "full_path": "/usr/bin/python3",
                    "md5": "a7e3d34b39e9eb618cb2ca3fd32cbf90",  # Example hash
                },
            },
            "user": {"userid": "user123"},
        },
    }


def ingest_single_event(chronicle_client):
    """Demonstrate ingesting a single UDM event."""
    print("\n=== Ingesting a Single UDM Event ===")

    # Create a sample event
    event = create_sample_network_event()
    print(f"Event ID: {event['metadata']['id']}")
    print(f"Event Type: {event['metadata']['event_type']}")

    try:
        # Ingest the event
        result = chronicle_client.ingest_udm(udm_events=event)
        print("Event successfully ingested!")
        print(f"API Response: {result}")

    except APIError as e:
        print(f"Error ingesting event: {e}")


def ingest_multiple_events(chronicle_client):
    """Demonstrate ingesting multiple UDM events."""
    print("\n=== Ingesting Multiple UDM Events ===")

    # Create sample events
    network_event = create_sample_network_event()
    process_event = create_sample_process_event()

    print(f"Network Event ID: {network_event['metadata']['id']}")
    print(f"Process Event ID: {process_event['metadata']['id']}")

    try:
        # Ingest both events
        result = chronicle_client.ingest_udm(udm_events=[network_event, process_event])
        print("Events successfully ingested!")
        print(f"API Response: {result}")

    except APIError as e:
        print(f"Error ingesting events: {e}")


def ingest_event_without_id(chronicle_client):
    """Demonstrate automatic ID generation."""
    print("\n=== Ingesting Event Without ID (Auto-Generated) ===")

    # Create event without ID
    event = create_sample_network_event()
    del event["metadata"]["id"]  # Remove the ID

    try:
        # Ingest the event - ID will be automatically generated
        result = chronicle_client.ingest_udm(udm_events=event)
        print("Event successfully ingested with auto-generated ID!")
        print(f"API Response: {result}")

    except APIError as e:
        print(f"Error ingesting event: {e}")


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(
        description="Example of UDM event ingestion with Chronicle"
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
    ingest_single_event(chronicle)
    ingest_multiple_events(chronicle)
    ingest_event_without_id(chronicle)


if __name__ == "__main__":
    main()
