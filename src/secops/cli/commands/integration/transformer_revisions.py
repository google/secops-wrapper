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
"""Google SecOps CLI integration transformer revisions commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_transformer_revisions_command(subparsers):
    """Setup integration transformer revisions command"""
    revisions_parser = subparsers.add_parser(
        "transformer-revisions",
        help="Manage integration transformer revisions",
    )
    lvl1 = revisions_parser.add_subparsers(
        dest="transformer_revisions_command",
        help="Integration transformer revisions command",
    )

    # list command
    list_parser = lvl1.add_parser(
        "list",
        help="List integration transformer revisions",
    )
    list_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    list_parser.add_argument(
        "--transformer-id",
        type=str,
        help="ID of the transformer",
        dest="transformer_id",
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
        func=handle_transformer_revisions_list_command,
    )

    # delete command
    delete_parser = lvl1.add_parser(
        "delete",
        help="Delete an integration transformer revision",
    )
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--transformer-id",
        type=str,
        help="ID of the transformer",
        dest="transformer_id",
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
        func=handle_transformer_revisions_delete_command,
    )

    # create command
    create_parser = lvl1.add_parser(
        "create",
        help="Create a new integration transformer revision",
    )
    create_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    create_parser.add_argument(
        "--transformer-id",
        type=str,
        help="ID of the transformer",
        dest="transformer_id",
        required=True,
    )
    create_parser.add_argument(
        "--comment",
        type=str,
        help="Comment describing the revision",
        dest="comment",
    )
    create_parser.set_defaults(
        func=handle_transformer_revisions_create_command,
    )

    # rollback command
    rollback_parser = lvl1.add_parser(
        "rollback",
        help="Rollback transformer to a previous revision",
    )
    rollback_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    rollback_parser.add_argument(
        "--transformer-id",
        type=str,
        help="ID of the transformer",
        dest="transformer_id",
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
        func=handle_transformer_revisions_rollback_command,
    )


def handle_transformer_revisions_list_command(args, chronicle):
    """Handle integration transformer revisions list command"""
    try:
        out = chronicle.list_integration_transformer_revisions(
            integration_name=args.integration_name,
            transformer_id=args.transformer_id,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing transformer revisions: {e}", file=sys.stderr)
        sys.exit(1)


def handle_transformer_revisions_delete_command(args, chronicle):
    """Handle integration transformer revision delete command"""
    try:
        chronicle.delete_integration_transformer_revision(
            integration_name=args.integration_name,
            transformer_id=args.transformer_id,
            revision_id=args.revision_id,
        )
        print(f"Transformer revision {args.revision_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error deleting transformer revision: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_transformer_revisions_create_command(args, chronicle):
    """Handle integration transformer revision create command"""
    try:
        # Get the current transformer to create a revision
        transformer = chronicle.get_integration_transformer(
            integration_name=args.integration_name,
            transformer_id=args.transformer_id,
        )
        out = chronicle.create_integration_transformer_revision(
            integration_name=args.integration_name,
            transformer_id=args.transformer_id,
            transformer=transformer,
            comment=args.comment,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error creating transformer revision: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_transformer_revisions_rollback_command(args, chronicle):
    """Handle integration transformer revision rollback command"""
    try:
        out = chronicle.rollback_integration_transformer_revision(
            integration_name=args.integration_name,
            transformer_id=args.transformer_id,
            revision_id=args.revision_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error rolling back transformer revision: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
