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
"""Google SecOps CLI rule commands"""

import json
import sys

from secops.cli.utils.common_args import (
    add_pagination_args,
    add_time_range_args,
)
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range
from secops.exceptions import APIError


def setup_rule_command(subparsers):
    """Set up the rule command parser."""
    rule_parser = subparsers.add_parser("rule", help="Manage detection rules")
    rule_subparsers = rule_parser.add_subparsers(
        dest="rule_command", help="Rule command"
    )
    rule_parser.set_defaults(func=lambda args, _: rule_parser.print_help())

    # List rules command
    list_parser = rule_subparsers.add_parser("list", help="List rules")
    add_pagination_args(list_parser)
    list_parser.add_argument(
        "--view",
        type=str,
        choices=[
            "BASIC",
            "FULL",
            "REVISION_METADATA_ONLY",
            "RULE_VIEW_UNSPECIFIED",
        ],
        default="FULL",
        help="The scope of fields to populate when returning the rules",
    )
    list_parser.set_defaults(func=handle_rule_list_command)

    # Get rule command
    get_parser = rule_subparsers.add_parser("get", help="Get rule details")
    get_parser.add_argument("--id", required=True, help="Rule ID")
    get_parser.set_defaults(func=handle_rule_get_command)

    # Create rule command
    create_parser = rule_subparsers.add_parser("create", help="Create a rule")
    create_parser.add_argument(
        "--file", required=True, help="File containing rule text"
    )
    create_parser.set_defaults(func=handle_rule_create_command)

    # Update rule command
    update_parser = rule_subparsers.add_parser("update", help="Update a rule")
    update_parser.add_argument("--id", required=True, help="Rule ID")
    update_parser.add_argument(
        "--file", required=True, help="File containing updated rule text"
    )
    update_parser.set_defaults(func=handle_rule_update_command)

    # Enable/disable rule command
    enable_parser = rule_subparsers.add_parser(
        "enable", help="Enable or disable a rule"
    )
    enable_parser.add_argument("--id", required=True, help="Rule ID")
    enable_parser.add_argument(
        "--enabled",
        choices=["true", "false"],
        required=True,
        help="Enable or disable the rule",
    )
    enable_parser.set_defaults(func=handle_rule_enable_command)

    alerting_parser = rule_subparsers.add_parser(
        "alerting", help="Enable or disable alerting for a rule"
    )
    alerting_parser.add_argument("--id", required=True, help="Rule ID")
    alerting_parser.add_argument(
        "--enabled",
        choices=["true", "false"],
        required=True,
        help="Enable or disable alerting",
    )
    alerting_parser.set_defaults(func=handle_rule_alerting_command)

    # Delete rule command
    delete_parser = rule_subparsers.add_parser("delete", help="Delete a rule")
    delete_parser.add_argument("--id", required=True, help="Rule ID")
    delete_parser.add_argument(
        "--force",
        action="store_true",
        help="Force deletion of rule with retrohunts",
    )
    delete_parser.set_defaults(func=handle_rule_delete_command)

    # Validate rule command
    validate_parser = rule_subparsers.add_parser(
        "validate", help="Validate a rule"
    )
    validate_parser.add_argument(
        "--file", required=True, help="File containing rule text"
    )
    validate_parser.set_defaults(func=handle_rule_validate_command)

    # Test rule command
    test_parser = rule_subparsers.add_parser(
        "test", help="Test a rule against historical data"
    )
    test_parser.add_argument(
        "--file", required=True, help="File containing rule text"
    )
    test_parser.add_argument(
        "--max-results",
        "--max_results",
        dest="max_results",
        type=int,
        default=100,
        help="Maximum results to return (1-10000, default 100)",
    )
    add_time_range_args(test_parser)
    test_parser.set_defaults(func=handle_rule_test_command)

    # Search rules command
    search_parser = rule_subparsers.add_parser("search", help="Search rules")
    search_parser.set_defaults(func=handle_rule_search_command)
    search_parser.add_argument(
        "--query", required=True, help="Rule query string in regex"
    )

    # Get rule deployment
    get_dep_parser = rule_subparsers.add_parser(
        "get-deployment", help="Get rule deployment"
    )
    get_dep_parser.add_argument("--id", required=True, help="Rule ID")
    get_dep_parser.set_defaults(func=handle_rule_get_deployment_command)

    # List rule deployments
    list_dep_parser = rule_subparsers.add_parser(
        "list-deployments", help="List rule deployments"
    )
    add_pagination_args(list_dep_parser)
    list_dep_parser.add_argument(
        "--filter",
        dest="filter_query",
        type=str,
        help="Filter query to restrict results.",
    )
    list_dep_parser.set_defaults(func=handle_rule_list_deployments_command)

    upd_parser = rule_subparsers.add_parser(
        "update-deployment", help="Update rule deployment fields"
    )
    upd_parser.add_argument("--id", required=True, help="Rule ID")
    upd_parser.add_argument(
        "--enabled",
        dest="enabled",
        choices=["true", "false"],
        help="Set enabled state",
    )
    upd_parser.add_argument(
        "--alerting",
        dest="alerting",
        choices=["true", "false"],
        help="Set alerting state",
    )
    upd_parser.add_argument(
        "--archived",
        dest="archived",
        choices=["true", "false"],
        help="Set archived state (requires enabled=false)",
    )
    upd_parser.add_argument(
        "--run-frequency",
        "--run_frequency",
        dest="run_frequency",
        choices=["LIVE", "HOURLY", "DAILY"],
        help="Set run frequency: LIVE, HOURLY, or DAILY",
    )
    upd_parser.set_defaults(func=handle_rule_update_deployment_command)

    # Detection list
    detection_parser = rule_subparsers.add_parser(
        "detections", help="List detections"
    )
    detection_parser.set_defaults(func=handle_rule_detections_command)
    detection_parser.add_argument(
        "--rule-id", "--rule_id", required=False, default="-", help="Rule ID"
    )
    detection_parser.add_argument(
        "--list-basis", "--list_basis", required=False, help="List basis"
    )
    detection_parser.add_argument(
        "--alert-state", "--alert_state", required=False, help="Alert state"
    )
    add_pagination_args(detection_parser)
    add_time_range_args(detection_parser)


def handle_rule_detections_command(args, chronicle):
    """Handle rule detections command."""
    try:
        start_time, end_time = get_time_range(args)
        result = chronicle.list_detections(
            args.rule_id,
            start_time,
            end_time,
            args.list_basis,
            args.alert_state,
            args.page_size,
            args.page_token,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_list_command(args, chronicle):
    """Handle rule list command."""
    try:
        result = chronicle.list_rules(
            view=args.view, page_size=args.page_size, page_token=args.page_token
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_get_command(args, chronicle):
    """Handle rule get command."""
    try:
        result = chronicle.get_rule(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_create_command(args, chronicle):
    """Handle rule create command."""
    try:
        with open(args.file, encoding="utf-8") as f:
            rule_text = f.read()

        result = chronicle.create_rule(rule_text)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_update_command(args, chronicle):
    """Handle rule update command."""
    try:
        with open(args.file, encoding="utf-8") as f:
            rule_text = f.read()

        result = chronicle.update_rule(args.id, rule_text)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_enable_command(args, chronicle):
    """Handle rule enable/disable command."""
    try:
        enabled = args.enabled.lower() == "true"
        result = chronicle.enable_rule(args.id, enabled=enabled)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_delete_command(args, chronicle):
    """Handle rule delete command."""
    try:
        result = chronicle.delete_rule(args.id, force=args.force)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_validate_command(args, chronicle):
    """Handle rule validate command."""
    try:
        with open(args.file, encoding="utf-8") as f:
            rule_text = f.read()

        result = chronicle.validate_rule(rule_text)
        if result.success:
            print("Rule is valid.")
        else:
            print(f"Rule is invalid: {result.message}")
            if result.position:
                print(
                    f'Error at line {result.position["startLine"]}, '
                    f'column {result.position["startColumn"]}'
                )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_test_command(args, chronicle):
    """Handle rule test command.

    This command tests a rule against historical data and outputs UDM events
    as JSON objects.
    """
    try:
        with open(args.file, encoding="utf-8") as f:
            rule_text = f.read()

        start_time, end_time = get_time_range(args)

        # Process streaming results
        all_events = []

        for result in chronicle.run_rule_test(
            rule_text, start_time, end_time, max_results=args.max_results
        ):
            if result.get("type") == "detection":
                detection = result.get("detection", {})
                result_events = detection.get("resultEvents", {})

                # Extract UDM events from resultEvents structure
                # resultEvents is an object with variable names as
                # keys (from the rule) and each variable contains an
                # eventSamples array with the actual events
                for _, event_data in result_events.items():
                    if (
                        isinstance(event_data, dict)
                        and "eventSamples" in event_data
                    ):
                        for sample in event_data.get("eventSamples", []):
                            if "event" in sample:
                                # Extract the actual UDM event
                                udm_event = sample.get("event")
                                all_events.append(udm_event)

        # Output all events as a single JSON array
        print(json.dumps(all_events))

    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

    return 0


def handle_rule_search_command(args, chronicle):
    """Handle rule search command."""
    try:
        result = chronicle.search_rules(args.query)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_get_deployment_command(args, chronicle):
    """Handle rule get-deployment command."""
    try:
        result = chronicle.get_rule_deployment(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_list_deployments_command(args, chronicle):
    """Handle rule list-deployments command."""
    try:
        result = chronicle.list_rule_deployments(
            page_size=args.page_size if hasattr(args, "page_size") else None,
            page_token=args.page_token if hasattr(args, "page_token") else None,
            filter_query=(
                args.filter_query if hasattr(args, "filter_query") else None
            ),
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_alerting_command(args, chronicle):
    """Handle rule alerting command."""
    try:
        enabled = args.enabled.lower() == "true"
        result = chronicle.set_rule_alerting(args.id, enabled=enabled)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_update_deployment_command(args, chronicle):
    """Handle rule update deployment command."""
    try:

        def _parse_bool(val):
            if val is None:
                return None
            return str(val).lower() == "true"

        result = chronicle.update_rule_deployment(
            rule_id=args.id,
            enabled=_parse_bool(args.enabled),
            alerting=_parse_bool(args.alerting),
            archived=_parse_bool(args.archived),
            run_frequency=args.run_frequency,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
