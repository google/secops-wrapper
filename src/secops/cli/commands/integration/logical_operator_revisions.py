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
"""Google SecOps CLI integration logical operator revisions commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_logical_operator_revisions_command(subparsers):
    """Setup integration logical operator revisions command"""
    revisions_parser = subparsers.add_parser(
        "logical-operator-revisions",
        help="Manage integration logical operator revisions",
    )
    lvl1 = revisions_parser.add_subparsers(
        dest="logical_operator_revisions_command",
        help="Integration logical operator revisions command",
    )

    # list command
    list_parser = lvl1.add_parser(
        "list",
        help="List integration logical operator revisions",
    )
    list_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    list_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator",
        dest="logical_operator_id",
        required=True,
    )
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing revisions",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing revisions",
        dest="order_by",
    )
    list_parser.set_defaults(
        func=handle_logical_operator_revisions_list_command,
    )

    # delete command
    delete_parser = lvl1.add_parser(
        "delete",
        help="Delete an integration logical operator revision",
    )
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator",
        dest="logical_operator_id",
        required=True,
    )
    delete_parser.add_argument(
        "--revision-id",
        type=str,
        help="ID of the revision to delete",
        dest="revision_id",
        required=True,
    )
    delete_parser.set_defaults(
        func=handle_logical_operator_revisions_delete_command,
    )

    # create command
    create_parser = lvl1.add_parser(
        "create",
        help="Create a new integration logical operator revision",
    )
    create_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    create_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator",
        dest="logical_operator_id",
        required=True,
    )
    create_parser.add_argument(
        "--comment",
        type=str,
        help="Comment describing the revision",
        dest="comment",
    )
    create_parser.set_defaults(
        func=handle_logical_operator_revisions_create_command,
    )

    # rollback command
    rollback_parser = lvl1.add_parser(
        "rollback",
        help="Rollback logical operator to a previous revision",
    )
    rollback_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    rollback_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator",
        dest="logical_operator_id",
        required=True,
    )
    rollback_parser.add_argument(
        "--revision-id",
        type=str,
        help="ID of the revision to rollback to",
        dest="revision_id",
        required=True,
    )
    rollback_parser.set_defaults(
        func=handle_logical_operator_revisions_rollback_command,
    )


def handle_logical_operator_revisions_list_command(args, chronicle):
    """Handle integration logical operator revisions list command"""
    try:
        out = chronicle.list_integration_logical_operator_revisions(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing logical operator revisions: {e}", file=sys.stderr)
        sys.exit(1)


def handle_logical_operator_revisions_delete_command(args, chronicle):
    """Handle integration logical operator revision delete command"""
    try:
        chronicle.delete_integration_logical_operator_revision(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
            revision_id=args.revision_id,
        )
        print(
            f"Logical operator revision {args.revision_id} deleted successfully"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error deleting logical operator revision: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_logical_operator_revisions_create_command(args, chronicle):
    """Handle integration logical operator revision create command"""
    try:
        # Get the current logical operator to create a revision
        logical_operator = chronicle.get_integration_logical_operator(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
        )
        out = chronicle.create_integration_logical_operator_revision(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
            logical_operator=logical_operator,
            comment=args.comment,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error creating logical operator revision: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_logical_operator_revisions_rollback_command(args, chronicle):
    """Handle integration logical operator revision rollback command"""
    try:
        out = chronicle.rollback_integration_logical_operator_revision(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
            revision_id=args.revision_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error rolling back logical operator revision: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

