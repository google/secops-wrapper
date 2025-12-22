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
"""Google SecOps CLI rule exclusion commands"""

import sys

from secops.cli.utils.common_args import (
    add_pagination_args,
    add_time_range_args,
)
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_rule_exclusion_command(subparsers):
    """Set up the rule exclusion command parser."""
    re_parser = subparsers.add_parser(
        "rule-exclusion", help="Manage rule exclusions"
    )
    re_subparsers = re_parser.add_subparsers(
        dest="re_command", help="Rule exclusion command"
    )
    re_parser.set_defaults(func=lambda args, _: re_parser.print_help())

    # Create rule exclusion command
    create_parser = re_subparsers.add_parser(
        "create", help="Create a rule exclusion"
    )
    create_parser.add_argument(
        "--display-name", required=True, help="Rule exclusion display name"
    )
    create_parser.add_argument(
        "--type",
        dest="refinement_type",
        choices=["DETECTION_EXCLUSION", "FINDINGS_REFINEMENT_TYPE_UNSPECIFIED"],
        required=True,
        help="Rule exclusion refinement type",
    )
    create_parser.add_argument(
        "--query", required=True, help="Rule exclusion query"
    )
    create_parser.set_defaults(func=handle_rule_exclusion_create_command)

    # Get rule exclusion command
    get_parser = re_subparsers.add_parser("get", help="Get a rule exclusion")
    get_parser.add_argument("--id", required=True, help="Rule exclusion id")
    get_parser.set_defaults(func=handle_rule_exclusion_get_command)

    # List rule exclusions command
    list_parser = re_subparsers.add_parser("list", help="List rule exclusions")
    add_pagination_args(list_parser)
    list_parser.set_defaults(func=handle_rule_exclusion_list_command)

    # Update rule exclusion command
    update_parser = re_subparsers.add_parser(
        "update", help="Update a rule exclusion"
    )
    update_parser.add_argument("--id", required=True, help="Rule exclusion id")
    update_parser.add_argument(
        "--display-name", help="Rule exclusion display name"
    )
    update_parser.add_argument(
        "--type",
        dest="refinement_type",
        choices=["DETECTION_EXCLUSION", "FINDINGS_REFINEMENT_TYPE_UNSPECIFIED"],
        help="Rule exclusion refinement type",
    )
    update_parser.add_argument("--query", help="Rule exclusion query")
    update_parser.add_argument(
        "--update-mask",
        "--update_mask",
        help="Comma-separated list of fields to update",
    )
    update_parser.set_defaults(func=handle_rule_exclusion_patch_command)

    # Compute rule exclusion activity command
    activity_parser = re_subparsers.add_parser(
        "compute-activity",
        help=(
            "Compute findings refinement activity"
            " for a specific rule exclision"
        ),
    )
    activity_parser.add_argument(
        "--id", required=True, help="Rule exclusion id"
    )
    add_time_range_args(activity_parser)
    activity_parser.set_defaults(func=handle_rule_exclusion_activity_command)

    # Get rule exclusion deployment command
    get_deployment_parser = re_subparsers.add_parser(
        "get-deployment", help="Get rule exclusion deployment"
    )
    get_deployment_parser.add_argument(
        "--id", required=True, help="Rule exclusion id"
    )
    get_deployment_parser.set_defaults(
        func=handle_rule_exclusion_get_deployment_command
    )

    # Update rule exclusion deployment command
    update_deployment_parser = re_subparsers.add_parser(
        "update-deployment", help="Update rule exclusion deployment"
    )
    update_deployment_parser.add_argument(
        "--id", required=True, help="Rule exclusion id"
    )
    update_deployment_parser.add_argument(
        "--enabled", choices=["true", "false"], help="Rule exclusion enabled"
    )
    update_deployment_parser.add_argument(
        "--archived", choices=["true", "false"], help="Rule exclusion archived"
    )
    update_deployment_parser.add_argument(
        "--detection-exclusion-application",
        "--detection_exclusion_application",
        dest="detection_exclusion_application",
        help="Rule exclusion detection exclusion application as JSON string",
    )
    update_deployment_parser.add_argument(
        "--update-mask",
        "--update_mask",
        help="Comma-separated list of fields to update",
    )
    update_deployment_parser.set_defaults(
        func=handle_rule_exclusion_update_deployment_command
    )


def handle_rule_exclusion_create_command(args, chronicle):
    """Handle rule exclusion create command."""
    try:
        result = chronicle.create_rule_exclusion(
            display_name=args.display_name,
            refinement_type=args.refinement_type,
            query=args.query,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_exclusion_get_command(args, chronicle):
    """Handle rule exclusion get command."""
    try:
        result = chronicle.get_rule_exclusion(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_exclusion_list_command(args, chronicle):
    """Handle rule exclusion list command."""
    try:
        page_size = args.page_size if hasattr(args, "page_size") else 100
        page_token = args.page_token if hasattr(args, "page_token") else None

        result = chronicle.list_rule_exclusions(
            page_size=page_size, page_token=page_token
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_exclusion_patch_command(args, chronicle):
    """Handle rule exclusion patch command."""
    try:
        result = chronicle.patch_rule_exclusion(
            exclusion_id=args.id,
            display_name=args.display_name,
            refinement_type=args.refinement_type,
            query=args.query,
            update_mask=args.update_mask,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_exclusion_activity_command(args, chronicle):
    """Handle rule exclusion activity command."""
    try:
        # Get time range from arguments
        start_time, end_time = get_time_range(args)

        result = chronicle.compute_rule_exclusion_activity(
            exclusion_id=args.id, start_time=start_time, end_time=end_time
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_exclusion_get_deployment_command(args, chronicle):
    """Handle rule exclusion get deployment command."""
    try:
        result = chronicle.get_rule_exclusion_deployment(exclusion_id=args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_exclusion_update_deployment_command(args, chronicle):
    """Handle rule exclusion update deployment command."""
    try:

        result = chronicle.update_rule_exclusion_deployment(
            exclusion_id=args.id,
            enabled=args.enabled,
            archived=args.archived,
            detection_exclusion_application=(
                args.detection_exclusion_application
            ),
            update_mask=args.update_mask,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
