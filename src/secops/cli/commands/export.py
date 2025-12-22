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
"""Google SecOps CLI export commands"""

import sys

from secops.cli.utils.common_args import (
    add_pagination_args,
    add_time_range_args,
)
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_export_command(subparsers):
    """Set up the data export command parser."""
    export_parser = subparsers.add_parser("export", help="Manage data exports")
    export_subparsers = export_parser.add_subparsers(
        dest="export_command", help="Export command"
    )
    export_parser.set_defaults(func=lambda args, _: export_parser.print_help())

    # List available log types command
    log_types_parser = export_subparsers.add_parser(
        "log-types", help="List available log types for export"
    )
    add_time_range_args(log_types_parser)
    add_pagination_args(log_types_parser)
    log_types_parser.set_defaults(func=handle_export_log_types_command)

    # Create export command
    create_parser = export_subparsers.add_parser(
        "create", help="Create a data export"
    )
    create_parser.add_argument(
        "--gcs-bucket",
        "--gcs_bucket",
        dest="gcs_bucket",
        required=True,
        help="GCS bucket in format 'projects/PROJECT_ID/buckets/BUCKET_NAME'",
    )
    create_parser.add_argument(
        "--log-type",
        "--log_type",
        dest="log_type",
        help="Single log type to export (deprecated, use --log-types instead)",
    )
    create_parser.add_argument(
        "--log-types",
        "--log_types",
        dest="log_types",
        help="Comma-separated list of log types to export",
    )
    create_parser.add_argument(
        "--all-logs",
        "--all_logs",
        dest="all_logs",
        action="store_true",
        help="Export all log types",
    )
    add_time_range_args(create_parser)
    create_parser.set_defaults(func=handle_export_create_command)

    # List exports command
    list_parser = export_subparsers.add_parser("list", help="List data exports")
    list_parser.add_argument(
        "--filter", dest="filters", help="Filter string for listing exports"
    )
    add_pagination_args(list_parser)
    list_parser.set_defaults(func=handle_export_list_command)

    # Update export command
    update_parser = export_subparsers.add_parser(
        "update", help="Update an existing data export"
    )
    update_parser.add_argument(
        "--id", required=True, help="Export ID to update"
    )
    update_parser.add_argument(
        "--gcs-bucket",
        "--gcs_bucket",
        dest="gcs_bucket",
        help=(
            "New GCS bucket in format "
            "'projects/PROJECT_ID/buckets/BUCKET_NAME'"
        ),
    )
    update_parser.add_argument(
        "--log-types",
        "--log_types",
        dest="log_types",
        help="Comma-separated list of log types to export",
    )
    add_time_range_args(update_parser)
    update_parser.set_defaults(func=handle_export_update_command)

    # Get export status command
    status_parser = export_subparsers.add_parser(
        "status", help="Get export status"
    )
    status_parser.add_argument("--id", required=True, help="Export ID")
    status_parser.set_defaults(func=handle_export_status_command)

    # Cancel export command
    cancel_parser = export_subparsers.add_parser(
        "cancel", help="Cancel an export"
    )
    cancel_parser.add_argument("--id", required=True, help="Export ID")
    cancel_parser.set_defaults(func=handle_export_cancel_command)


def handle_export_log_types_command(args, chronicle):
    """Handle export log types command."""
    start_time, end_time = get_time_range(args)

    try:
        result = chronicle.fetch_available_log_types(
            start_time=start_time, end_time=end_time, page_size=args.page_size
        )

        # Convert to a simple dict for output
        log_types_dict = {
            "log_types": [
                {
                    "log_type": lt.log_type.split("/")[-1],
                    "display_name": lt.display_name,
                    "start_time": lt.start_time.isoformat(),
                    "end_time": lt.end_time.isoformat(),
                }
                for lt in result["available_log_types"]
            ],
            "next_page_token": result.get("next_page_token", ""),
        }

        output_formatter(log_types_dict, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_export_create_command(args, chronicle):
    """Handle export create command."""
    start_time, end_time = get_time_range(args)

    try:
        # First, try to fetch available log types to see if there are any
        available_logs = chronicle.fetch_available_log_types(
            start_time=start_time, end_time=end_time
        )

        if not available_logs.get("available_log_types") and not args.log_type:
            print(
                "Warning: No log types are available for export in "
                "the specified time range.",
                file=sys.stderr,
            )
            print(
                "You may need to adjust your time range or check your "
                "Chronicle instance configuration.",
                file=sys.stderr,
            )
            if args.all_logs:
                print(
                    "Creating export with --all-logs flag anyway...",
                    file=sys.stderr,
                )
            else:
                print(
                    "Error: Cannot create export without specifying a log type "
                    "when no log types are available.",
                    file=sys.stderr,
                )
                sys.exit(1)

        # If log_type is specified, check if it exists in available log types
        if args.log_type and available_logs.get("available_log_types"):
            log_type_found = False
            for lt in available_logs.get("available_log_types", []):
                if lt.log_type.endswith(
                    "/" + args.log_type
                ) or lt.log_type.endswith("/logTypes/" + args.log_type):
                    log_type_found = True
                    break

            if not log_type_found:
                print(
                    f"Warning: Log type '{args.log_type}' not found in "
                    "available log types.",
                    file=sys.stderr,
                )
                print("Available log types:", file=sys.stderr)
                for lt in available_logs.get("available_log_types", [])[
                    :5
                ]:  # Show first 5
                    print(f'  {lt.log_type.split("/")[-1]}', file=sys.stderr)
                print("Attempting to create export anyway...", file=sys.stderr)

        # Proceed with export creation
        if args.all_logs:
            result = chronicle.create_data_export(
                gcs_bucket=args.gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                export_all_logs=True,
            )
        elif args.log_type:
            # Single log type (legacy method)
            result = chronicle.create_data_export(
                gcs_bucket=args.gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                log_type=args.log_type,
            )
        elif args.log_types:
            # Multiple log types
            log_types_list = [
                log_type.strip() for log_type in args.log_types.split(",")
            ]
            result = chronicle.create_data_export(
                gcs_bucket=args.gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                log_types=log_types_list,
            )
        else:
            print(
                "Error: Either --log-type, --log-types, or --all-logs "
                "must be specified",
                file=sys.stderr,
            )
            sys.exit(1)

        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_msg = str(e)
        print(f"Error: {error_msg}", file=sys.stderr)

        # Provide helpful advice based on common errors
        if "unrecognized log type" in error_msg.lower():
            print("\nPossible solutions:", file=sys.stderr)
            print(
                "1. Verify the log type exists in your Chronicle instance",
                file=sys.stderr,
            )
            print(
                "2. Try using 'secops export log-types' to see "
                "available log types",
                file=sys.stderr,
            )
            print(
                "3. Check if your time range contains data for this log type",
                file=sys.stderr,
            )
            print(
                "4. Make sure your GCS bucket is properly formatted as "
                "'projects/PROJECT_ID/buckets/BUCKET_NAME'",
                file=sys.stderr,
            )
        elif (
            "permission" in error_msg.lower()
            or "unauthorized" in error_msg.lower()
        ):
            print(
                "\nPossible authentication or permission issues:",
                file=sys.stderr,
            )
            print(
                "1. Verify your credentials have access to Chronicle and the "
                "specified GCS bucket",
                file=sys.stderr,
            )
            print(
                "2. Check if your service account has the required IAM roles",
                file=sys.stderr,
            )

        sys.exit(1)


def handle_export_status_command(args, chronicle):
    """Handle export status command."""
    try:
        result = chronicle.get_data_export(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_export_cancel_command(args, chronicle):
    """Handle export cancel command."""
    try:
        result = chronicle.cancel_data_export(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_export_list_command(args, chronicle):
    """Handle listing data exports command."""
    try:
        result = chronicle.list_data_export(
            filters=args.filters,
            page_size=args.page_size,
            page_token=args.page_token,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_export_update_command(args, chronicle):
    """Handle updating an existing data export command."""
    # Get the start_time and end_time if provided
    start_time = None
    end_time = None
    if (hasattr(args, "start_time") and args.start_time) or (
        hasattr(args, "time_window") and args.time_window
    ):
        start_time, end_time = get_time_range(args)

    # Convert log_types string to list if provided
    log_types = None
    if args.log_types:
        log_types = [log_type.strip() for log_type in args.log_types.split(",")]

    try:
        result = chronicle.update_data_export(
            data_export_id=args.id,
            gcs_bucket=args.gcs_bucket if hasattr(args, "gcs_bucket") else None,
            start_time=start_time,
            end_time=end_time,
            log_types=log_types,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
