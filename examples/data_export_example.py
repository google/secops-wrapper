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
"""Example script for demonstrating Chronicle Data Export API functionality."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from secops import SecOpsClient
from secops.exceptions import APIError


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Chronicle Data Export API Example")
    parser.add_argument("--project_id", required=True, help="GCP project ID")
    parser.add_argument("--customer_id", required=True, help="Chronicle customer ID")
    parser.add_argument("--region", default="us", help="Chronicle region (default: us)")
    parser.add_argument("--bucket", required=True, help="GCS bucket name for export")
    parser.add_argument(
        "--days", type=int, default=1, help="Number of days to look back (default: 1)"
    )
    parser.add_argument("--log_type", help="Optional specific log type to export")
    parser.add_argument("--all_logs", action="store_true", help="Export all log types")
    parser.add_argument(
        "--list_only",
        action="store_true",
        help="Only list available log types, don't create export",
    )
    parser.add_argument("--credentials", help="Path to service account JSON key file")

    return parser.parse_args()


def main():
    """Run the example."""
    args = parse_args()

    # Set up time range for export
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=args.days)

    print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")

    # Initialize the client
    if args.credentials:
        print(f"Using service account credentials from {args.credentials}")
        client = SecOpsClient(service_account_path=args.credentials)
    else:
        print("Using application default credentials")
        client = SecOpsClient()

    # Get Chronicle client
    chronicle = client.chronicle(
        customer_id=args.customer_id, project_id=args.project_id, region=args.region
    )

    try:
        # Fetch available log types
        print("\nFetching available log types for export...")
        result = chronicle.fetch_available_log_types(
            start_time=start_time, end_time=end_time
        )

        log_types = result["available_log_types"]
        print(f"Found {len(log_types)} available log types for export")

        # Print available log types
        for i, log_type in enumerate(log_types[:10], 1):  # Show first 10
            short_name = log_type.log_type.split("/")[-1]
            print(f"{i}. {log_type.display_name} ({short_name})")
            print(f"   Available from {log_type.start_time} to {log_type.end_time}")

        if len(log_types) > 10:
            print(f"... and {len(log_types) - 10} more")

        # If list_only flag is set, exit here
        if args.list_only:
            print("\nList-only mode, not creating export")
            return 0

        # Validate export options
        if args.all_logs and args.log_type:
            print("Error: Cannot specify both --all_logs and --log_type")
            return 1

        if not args.all_logs and not args.log_type:
            print("Error: Must specify either --all_logs or --log_type")
            return 1

        # Format GCS bucket path
        gcs_bucket = f"projects/{args.project_id}/buckets/{args.bucket}"
        print(f"\nExporting to GCS bucket: {gcs_bucket}")

        # Create data export
        if args.log_type:
            # Find the matching log type to verify it exists
            matching_log_types = [
                lt for lt in log_types if lt.log_type.split("/")[-1] == args.log_type
            ]
            if not matching_log_types:
                print(
                    f"Warning: Log type '{args.log_type}' not found in available log types"
                )
                print("Available log types include:")
                for i, lt in enumerate(log_types[:5], 1):
                    print(f"  {lt.log_type.split('/')[-1]}")
                proceed = input("Proceed anyway? (y/n): ")
                if proceed.lower() != "y":
                    return 1

            print(f"Creating data export for log type: {args.log_type}")
            export = chronicle.create_data_export(
                gcs_bucket=gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                log_type=args.log_type,
            )
        else:
            print("Creating data export for ALL log types")
            export = chronicle.create_data_export(
                gcs_bucket=gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                export_all_logs=True,
            )

        # Get the export ID and print details
        export_id = export["name"].split("/")[-1]
        print(f"\nExport created successfully!")
        print(f"Export ID: {export_id}")
        print(f"Status: {export['data_export_status']['stage']}")

        # Poll for status a few times to show progress
        print("\nChecking export status:")

        for i in range(3):
            status = chronicle.get_data_export(export_id)
            stage = status["data_export_status"]["stage"]
            progress = status["data_export_status"].get("progress_percentage", 0)

            print(f"  Status: {stage}, Progress: {progress}%")

            if stage in ["FINISHED_SUCCESS", "FINISHED_FAILURE", "CANCELLED"]:
                break

            if i < 2:  # Don't wait after the last check
                print("  Waiting 5 seconds...")
                from time import sleep

                sleep(5)

        print("\nExport job is running. You can check its status later with:")
        print(f"  python export_status.py --export_id {export_id} ...")

        return 0

    except APIError as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
