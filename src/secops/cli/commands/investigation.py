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
"""Google SecOps CLI investigation commands"""

import sys

from secops.chronicle import DetectionType
from secops.cli.utils.formatters import output_formatter


def setup_investigation_command(subparsers):
    """Set up the investigation command parser.

    Args:
        subparsers: Subparser object from argparse
    """
    investigation_parser = subparsers.add_parser(
        "investigation", help="Manage investigations"
    )
    investigation_subparsers = investigation_parser.add_subparsers(
        dest="investigation_command", help="Investigation subcommands"
    )

    investigation_parser.set_defaults(
        func=lambda args, _: investigation_parser.print_help()
    )

    _setup_list_subcommand(investigation_subparsers)
    _setup_get_subcommand(investigation_subparsers)
    _setup_fetch_associated_subcommand(investigation_subparsers)
    _setup_trigger_subcommand(investigation_subparsers)


def _setup_list_subcommand(subparsers):
    """Set up the list investigations subcommand.

    Args:
        subparsers: Subparser object for investigation commands
    """
    list_parser = subparsers.add_parser("list", help="List investigations")
    list_parser.add_argument(
        "--page-size",
        "--page_size",
        dest="page_size",
        type=int,
        help="Maximum investigations to return (default 100, max 1000)",
    )
    list_parser.add_argument(
        "--page-token",
        "--page_token",
        dest="page_token",
        help="Page token for pagination",
    )
    list_parser.add_argument(
        "--filter",
        help="Filter expression (e.g., 'alertId=\"alert123\"')",
    )
    list_parser.add_argument(
        "--order-by",
        "--order_by",
        dest="order_by",
        help=("Order by field (e.g., 'startTime', 'endTime', 'displayName')"),
    )
    list_parser.set_defaults(func=_handle_list)


def _setup_get_subcommand(subparsers):
    """Set up the get investigation subcommand.

    Args:
        subparsers: Subparser object for investigation commands
    """
    get_parser = subparsers.add_parser("get", help="Get investigation by ID")
    get_parser.add_argument(
        "--id",
        dest="investigation_id",
        required=True,
        help="Investigation ID to retrieve",
    )
    get_parser.set_defaults(func=_handle_get)


def _setup_fetch_associated_subcommand(subparsers):
    """Set up fetch associated investigations subcommand.

    Args:
        subparsers: Subparser object for investigation commands
    """
    fetch_parser = subparsers.add_parser(
        "fetch-associated",
        help="Fetch investigations associated with alerts or cases",
    )
    fetch_parser.add_argument(
        "--detection-type",
        "--detection_type",
        dest="detection_type",
        required=True,
        choices=["ALERT", "CASE", "UNSPECIFIED"],
        help="Type of identifiers (ALERT, CASE, or UNSPECIFIED)",
    )
    fetch_parser.add_argument(
        "--alert-ids",
        "--alert_ids",
        dest="alert_ids",
        help="Comma-separated list of alert IDs (max 100)",
    )
    fetch_parser.add_argument(
        "--case-ids",
        "--case_ids",
        dest="case_ids",
        help="Comma-separated list of case IDs (max 100)",
    )
    fetch_parser.add_argument(
        "--association-limit",
        "--association_limit",
        dest="association_limit",
        type=int,
        help="Max associations per detection (default 1, max 5)",
    )
    fetch_parser.add_argument(
        "--order-by",
        "--order_by",
        dest="order_by",
        help="Order by field (e.g., 'createTime', 'updateTime')",
    )
    fetch_parser.set_defaults(func=_handle_fetch_associated)


def _setup_trigger_subcommand(subparsers):
    """Set up trigger investigation subcommand.

    Args:
        subparsers: Subparser object for investigation commands
    """
    trigger_parser = subparsers.add_parser(
        "trigger", help="Trigger investigation for an alert"
    )
    trigger_parser.add_argument(
        "--alert-id",
        "--alert_id",
        dest="alert_id",
        required=True,
        help="Alert ID to trigger investigation for",
    )
    trigger_parser.set_defaults(func=_handle_trigger)


def _handle_list(args, chronicle):
    """Handle list investigations command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client instance
    """
    try:
        result = chronicle.list_investigations(
            page_size=args.page_size,
            page_token=args.page_token,
            filter_expr=args.filter,
            order_by=args.order_by,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_get(args, chronicle):
    """Handle get investigation command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client instance
    """
    try:
        result = chronicle.get_investigation(
            investigation_id=args.investigation_id
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_fetch_associated(args, chronicle):
    """Handle fetch associated investigations command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client instance
    """
    if not args.alert_ids and not args.case_ids:
        print(
            "Error: Must provide either --alert-ids or --case-ids",
            file=sys.stderr,
        )
        sys.exit(1)

    alert_ids = None
    if args.alert_ids:
        alert_ids = [id.strip() for id in args.alert_ids.split(",")]

    case_ids = None
    if args.case_ids:
        case_ids = [id.strip() for id in args.case_ids.split(",")]

    detection_type = DetectionType[args.detection_type]

    try:
        result = chronicle.fetch_associated_investigations(
            detection_type=detection_type,
            alert_ids=alert_ids,
            case_ids=case_ids,
            association_limit_per_detection=args.association_limit,
            order_by=args.order_by,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_trigger(args, chronicle):
    """Handle trigger investigation command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client instance
    """
    try:
        result = chronicle.trigger_investigation(alert_id=args.alert_id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
