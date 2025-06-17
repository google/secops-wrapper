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
"""Utility script for checking Chronicle Data Export status."""

import argparse
import json
import os
import sys
from secops import SecOpsClient
from secops.exceptions import APIError


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Chronicle Data Export Status Checker")
    parser.add_argument("--project_id", required=True, help="GCP project ID")
    parser.add_argument("--customer_id", required=True, help="Chronicle customer ID")
    parser.add_argument("--region", default="us", help="Chronicle region (default: us)")
    parser.add_argument("--export_id", required=True, help="Data Export ID to check")
    parser.add_argument(
        "--cancel", action="store_true", help="Cancel the export if it's in progress"
    )
    parser.add_argument("--credentials", help="Path to service account JSON key file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    return parser.parse_args()


def main():
    """Run the utility."""
    args = parse_args()

    # Initialize the client
    if args.credentials:
        client = SecOpsClient(service_account_path=args.credentials)
    else:
        client = SecOpsClient()

    # Get Chronicle client
    chronicle = client.chronicle(
        customer_id=args.customer_id, project_id=args.project_id, region=args.region
    )

    try:
        # Get export status
        export = chronicle.get_data_export(args.export_id)

        # Output in JSON format if requested
        if args.json:
            print(json.dumps(export, indent=2))
            return 0

        # Extract export details
        status = export["data_export_status"]
        stage = status["stage"]
        progress = status.get("progress_percentage", 0)
        error = status.get("error", "")

        start_time = export["start_time"]
        end_time = export["end_time"]
        gcs_bucket = export["gcs_bucket"]

        log_type = export.get("log_type", "")
        export_all_logs = export.get("export_all_logs", False)

        # Print export details
        print(f"Export ID: {args.export_id}")
        print(f"Status: {stage}")
        print(f"Progress: {progress}%")

        if error:
            print(f"Error: {error}")

        print(f"\nTime Range: {start_time} to {end_time}")
        print(f"GCS Bucket: {gcs_bucket}")

        if log_type:
            print(f"Log Type: {log_type.split('/')[-1]}")
        elif export_all_logs:
            print("Exporting: ALL LOG TYPES")

        # If requested to cancel the export and it's in progress
        if args.cancel and stage in ["IN_QUEUE", "PROCESSING"]:
            proceed = input(
                f"Are you sure you want to cancel export {args.export_id}? (y/n): "
            )
            if proceed.lower() == "y":
                cancelled = chronicle.cancel_data_export(args.export_id)
                print(
                    f"\nExport cancelled. New status: {cancelled['data_export_status']['stage']}"
                )
                if cancelled["data_export_status"].get("error"):
                    print(
                        f"Cancellation error: {cancelled['data_export_status']['error']}"
                    )

        return 0

    except APIError as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
