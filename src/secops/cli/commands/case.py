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
"""Google SecOps CLI case commands"""

import json
import sys

from secops.cli.utils.common_args import add_pagination_args
from secops.cli.utils.formatters import output_formatter
from secops.exceptions import APIError


def setup_case_command(subparsers):
    """Set up the case command parser."""
    case_parser = subparsers.add_parser("case", help="Manage cases")

    # Legacy argument for backward compatibility
    case_parser.add_argument("--ids", help="Comma-separated list of case IDs")
    case_parser.set_defaults(func=handle_case_command)

    case_subparsers = case_parser.add_subparsers(
        dest="case_command", help="Case command"
    )

    # Get single case command
    get_parser = case_subparsers.add_parser(
        "get", help="Get a single case by ID"
    )
    get_parser.add_argument(
        "--id", required=True, help="Case ID or resource name"
    )
    get_parser.add_argument(
        "--expand", help="Expand fields (e.g., 'tags,products')"
    )
    get_parser.set_defaults(func=handle_case_get_command)

    # List cases command
    list_parser = case_subparsers.add_parser(
        "list", help="List cases with filtering"
    )
    add_pagination_args(list_parser)
    list_parser.add_argument(
        "--filter", help="Filter expression for filtering cases"
    )
    list_parser.add_argument(
        "--order-by",
        "--order_by",
        dest="order_by",
        help="Comma-separated list of fields to order by",
    )
    list_parser.add_argument(
        "--expand", help="Expand fields (e.g., 'tags,products')"
    )
    list_parser.add_argument(
        "--distinct-by",
        "--distinct_by",
        dest="distinct_by",
        help="Field to distinct cases by",
    )
    list_parser.add_argument(
        "--as-list",
        "--as_list",
        dest="as_list",
        action="store_true",
        help="Return list of cases instead of dict with metadata",
    )
    list_parser.set_defaults(func=handle_case_list_command)

    # Update case command
    update_parser = case_subparsers.add_parser("update", help="Update a case")
    update_parser.add_argument(
        "--id", required=True, help="Case ID or resource name"
    )
    update_parser.add_argument(
        "--data",
        required=True,
        help="JSON string with case fields to update",
    )
    update_parser.add_argument(
        "--update-mask",
        "--update_mask",
        dest="update_mask",
        help="Comma-separated list of fields to update",
    )
    update_parser.set_defaults(func=handle_case_patch_command)

    # Merge cases command
    merge_parser = case_subparsers.add_parser(
        "merge", help="Merge multiple cases into one"
    )
    merge_parser.add_argument(
        "--source-ids",
        "--source_ids",
        dest="source_ids",
        required=True,
        help="Comma-separated list of case IDs to merge (source cases)",
    )
    merge_parser.add_argument(
        "--target-id",
        "--target_id",
        dest="target_id",
        required=True,
        type=int,
        help="Case ID to merge into (target case)",
    )
    merge_parser.set_defaults(func=handle_case_merge_command)

    # Bulk add tag command
    bulk_add_tag_parser = case_subparsers.add_parser(
        "bulk-add-tag", help="Add tags to multiple cases"
    )
    bulk_add_tag_parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated list of case IDs (integers)",
    )
    bulk_add_tag_parser.add_argument(
        "--tags",
        required=True,
        help="Comma-separated list of tags to add",
    )
    bulk_add_tag_parser.set_defaults(func=handle_case_bulk_add_tag_command)

    # Bulk assign command
    bulk_assign_parser = case_subparsers.add_parser(
        "bulk-assign", help="Assign multiple cases to a user"
    )
    bulk_assign_parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated list of case IDs (integers)",
    )
    bulk_assign_parser.add_argument(
        "--username", required=True, help="Username to assign cases to"
    )
    bulk_assign_parser.set_defaults(func=handle_case_bulk_assign_command)

    # Bulk change priority command
    bulk_priority_parser = case_subparsers.add_parser(
        "bulk-change-priority", help="Change priority of multiple cases"
    )
    bulk_priority_parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated list of case IDs (integers)",
    )
    bulk_priority_parser.add_argument(
        "--priority",
        required=True,
        choices=[
            "UNSPECIFIED",
            "INFO",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
            "PRIORITY_UNSPECIFIED",
            "PRIORITY_INFO",
            "PRIORITY_LOW",
            "PRIORITY_MEDIUM",
            "PRIORITY_HIGH",
            "PRIORITY_CRITICAL",
        ],
        help="Priority level to set",
    )
    bulk_priority_parser.set_defaults(
        func=handle_case_bulk_change_priority_command
    )

    # Bulk change stage command
    bulk_stage_parser = case_subparsers.add_parser(
        "bulk-change-stage", help="Change stage of multiple cases"
    )
    bulk_stage_parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated list of case IDs (integers)",
    )
    bulk_stage_parser.add_argument(
        "--stage", required=True, help="Stage to set for the cases"
    )
    bulk_stage_parser.set_defaults(func=handle_case_bulk_change_stage_command)

    # Bulk close command
    bulk_close_parser = case_subparsers.add_parser(
        "bulk-close", help="Close multiple cases"
    )
    bulk_close_parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated list of case IDs (integers)",
    )
    bulk_close_parser.add_argument(
        "--close-reason",
        "--close_reason",
        dest="close_reason",
        required=True,
        choices=[
            "UNSPECIFIED",
            "MALICIOUS",
            "NOT_MALICIOUS",
            "MAINTENANCE",
            "INCONCLUSIVE",
            "UNKNOWN",
            "CLOSE_REASON_UNSPECIFIED",
        ],
        help="Reason for closing the cases",
    )
    bulk_close_parser.add_argument(
        "--root-cause",
        "--root_cause",
        dest="root_cause",
        help="Root cause for closing cases",
    )
    bulk_close_parser.add_argument(
        "--close-comment",
        "--close_comment",
        dest="close_comment",
        help="Comment to add when closing",
    )
    bulk_close_parser.set_defaults(func=handle_case_bulk_close_command)

    # Bulk reopen command
    bulk_reopen_parser = case_subparsers.add_parser(
        "bulk-reopen", help="Reopen multiple cases"
    )
    bulk_reopen_parser.add_argument(
        "--ids",
        required=True,
        help="Comma-separated list of case IDs (integers)",
    )
    bulk_reopen_parser.add_argument(
        "--reopen-comment",
        "--reopen_comment",
        dest="reopen_comment",
        required=True,
        help="Comment to add when reopening cases",
    )
    bulk_reopen_parser.set_defaults(func=handle_case_bulk_reopen_command)


def handle_case_command(args, chronicle):
    """Handle case command (legacy behavior with --ids)."""
    # If --ids is provided without subcommand, use legacy behavior
    if args.ids and not args.case_command:
        handle_case_get_batch_command(args, chronicle)
    elif not args.case_command:
        # No subcommand and no --ids, show help
        print("Error: No subcommand or --ids provided", file=sys.stderr)
        sys.exit(1)


def handle_case_get_batch_command(args, chronicle):
    """Handle case get-batch command."""
    try:
        case_ids = [case_id.strip() for case_id in args.ids.split(",")]
        result = chronicle.get_cases(case_ids)

        # Convert CaseList to dictionary for output
        cases_dict = {
            "cases": [
                {
                    "id": case.id,
                    "display_name": case.display_name,
                    "stage": case.stage,
                    "priority": case.priority,
                    "status": case.status,
                    "soar_platform_info": (
                        {
                            "case_id": case.soar_platform_info.case_id,
                            "platform_type": (
                                case.soar_platform_info.platform_type
                            ),
                        }
                        if case.soar_platform_info
                        else None
                    ),
                    "alert_ids": case.alert_ids,
                }
                for case in result.cases
            ]
        }
        output_formatter(cases_dict, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_get_command(args, chronicle):
    """Handle case get command."""
    try:
        case = chronicle.get_case(args.id, expand=args.expand)
        case_dict = {
            "id": case.id,
            "display_name": case.display_name,
            "stage": case.stage,
            "priority": case.priority,
            "status": case.status,
        }
        if case.soar_platform_info:
            case_dict["soar_platform_info"] = {
                "case_id": case.soar_platform_info.case_id,
                "platform_type": case.soar_platform_info.platform_type,
            }
        if case.alert_ids:
            case_dict["alert_ids"] = case.alert_ids
        output_formatter(case_dict, args.output)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_list_command(args, chronicle):
    """Handle case list command."""
    try:
        result = chronicle.list_cases(
            page_size=args.page_size,
            page_token=args.page_token,
            filter_query=args.filter,
            order_by=args.order_by,
            expand=args.expand,
            distinct_by=args.distinct_by,
            as_list=args.as_list,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_patch_command(args, chronicle):
    """Handle case patch command."""
    try:
        case_data = json.loads(args.data)
        case = chronicle.patch_case(
            args.id, case_data, update_mask=args.update_mask
        )
        case_dict = {
            "id": case.id,
            "display_name": case.display_name,
            "stage": case.stage,
            "priority": case.priority,
            "status": case.status,
        }
        output_formatter(case_dict, args.output)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_merge_command(args, chronicle):
    """Handle case merge command."""
    try:
        source_ids = [
            int(case_id.strip()) for case_id in args.source_ids.split(",")
        ]
        result = chronicle.merge_cases(source_ids, args.target_id)
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_bulk_add_tag_command(args, chronicle):
    """Handle case bulk-add-tag command."""
    try:
        case_ids = [int(case_id.strip()) for case_id in args.ids.split(",")]
        tags = [tag.strip() for tag in args.tags.split(",")]
        result = chronicle.execute_bulk_add_tag(case_ids, tags)
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_bulk_assign_command(args, chronicle):
    """Handle case bulk-assign command."""
    try:
        case_ids = [int(case_id.strip()) for case_id in args.ids.split(",")]
        result = chronicle.execute_bulk_assign(case_ids, args.username)
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_bulk_change_priority_command(args, chronicle):
    """Handle case bulk-change-priority command."""
    try:
        case_ids = [int(case_id.strip()) for case_id in args.ids.split(",")]
        result = chronicle.execute_bulk_change_priority(case_ids, args.priority)
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_bulk_change_stage_command(args, chronicle):
    """Handle case bulk-change-stage command."""
    try:
        case_ids = [int(case_id.strip()) for case_id in args.ids.split(",")]
        result = chronicle.execute_bulk_change_stage(case_ids, args.stage)
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_bulk_close_command(args, chronicle):
    """Handle case bulk-close command."""
    try:
        case_ids = [int(case_id.strip()) for case_id in args.ids.split(",")]
        result = chronicle.execute_bulk_close(
            case_ids,
            args.close_reason,
            root_cause=args.root_cause,
            close_comment=args.close_comment,
        )
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_case_bulk_reopen_command(args, chronicle):
    """Handle case bulk-reopen command."""
    try:
        case_ids = [int(case_id.strip()) for case_id in args.ids.split(",")]
        result = chronicle.execute_bulk_reopen(case_ids, args.reopen_comment)
        output_formatter(result, args.output)
    except ValueError as e:
        print(f"Error: Invalid case ID format - {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
