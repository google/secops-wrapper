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
"""Google SecOps CLI integration logical operators commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_logical_operators_command(subparsers):
    """Setup integration logical operators command"""
    operators_parser = subparsers.add_parser(
        "logical-operators",
        help="Manage integration logical operators",
    )
    lvl1 = operators_parser.add_subparsers(
        dest="logical_operators_command",
        help="Integration logical operators command",
    )

    # list command
    list_parser = lvl1.add_parser(
        "list",
        help="List integration logical operators",
    )
    list_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing logical operators",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing logical operators",
        dest="order_by",
    )
    list_parser.add_argument(
        "--exclude-staging",
        action="store_true",
        help="Exclude staging logical operators from the response",
        dest="exclude_staging",
    )
    list_parser.add_argument(
        "--expand",
        type=str,
        help="Expand the response with full logical operator details",
        dest="expand",
    )
    list_parser.set_defaults(func=handle_logical_operators_list_command)

    # get command
    get_parser = lvl1.add_parser(
        "get",
        help="Get integration logical operator details",
    )
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    get_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator to get",
        dest="logical_operator_id",
        required=True,
    )
    get_parser.add_argument(
        "--expand",
        type=str,
        help="Expand the response with full logical operator details",
        dest="expand",
    )
    get_parser.set_defaults(func=handle_logical_operators_get_command)

    # delete command
    delete_parser = lvl1.add_parser(
        "delete",
        help="Delete an integration logical operator",
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
        help="ID of the logical operator to delete",
        dest="logical_operator_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_logical_operators_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create",
        help="Create a new integration logical operator",
    )
    create_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    create_parser.add_argument(
        "--display-name",
        type=str,
        help="Display name for the logical operator",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--script",
        type=str,
        help="Python script for the logical operator",
        dest="script",
        required=True,
    )
    create_parser.add_argument(
        "--script-timeout",
        type=str,
        help="Timeout for script execution (e.g., '60s')",
        dest="script_timeout",
        required=True,
    )
    create_parser.add_argument(
        "--enabled",
        action="store_true",
        help="Enable the logical operator (default: disabled)",
        dest="enabled",
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the logical operator",
        dest="description",
    )
    create_parser.set_defaults(func=handle_logical_operators_create_command)

    # update command
    update_parser = lvl1.add_parser(
        "update",
        help="Update an integration logical operator",
    )
    update_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    update_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator to update",
        dest="logical_operator_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the logical operator",
        dest="display_name",
    )
    update_parser.add_argument(
        "--script",
        type=str,
        help="New Python script for the logical operator",
        dest="script",
    )
    update_parser.add_argument(
        "--script-timeout",
        type=str,
        help="New timeout for script execution",
        dest="script_timeout",
    )
    update_parser.add_argument(
        "--enabled",
        type=lambda x: x.lower() == "true",
        help="Enable or disable the logical operator (true/false)",
        dest="enabled",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the logical operator",
        dest="description",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_logical_operators_update_command)

    # test command
    test_parser = lvl1.add_parser(
        "test",
        help="Execute an integration logical operator test",
    )
    test_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    test_parser.add_argument(
        "--logical-operator-id",
        type=str,
        help="ID of the logical operator to test",
        dest="logical_operator_id",
        required=True,
    )
    test_parser.set_defaults(func=handle_logical_operators_test_command)

    # template command
    template_parser = lvl1.add_parser(
        "template",
        help="Get logical operator template",
    )
    template_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    template_parser.set_defaults(func=handle_logical_operators_template_command)


def handle_logical_operators_list_command(args, chronicle):
    """Handle integration logical operators list command"""
    try:
        out = chronicle.list_integration_logical_operators(
            integration_name=args.integration_name,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            exclude_staging=args.exclude_staging,
            expand=args.expand,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error listing integration logical operators: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_logical_operators_get_command(args, chronicle):
    """Handle integration logical operator get command"""
    try:
        out = chronicle.get_integration_logical_operator(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
            expand=args.expand,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting integration logical operator: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_logical_operators_delete_command(args, chronicle):
    """Handle integration logical operator delete command"""
    try:
        chronicle.delete_integration_logical_operator(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
        )
        print(
            f"Logical operator {args.logical_operator_id} deleted successfully"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error deleting integration logical operator: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_logical_operators_create_command(args, chronicle):
    """Handle integration logical operator create command"""
    try:
        out = chronicle.create_integration_logical_operator(
            integration_name=args.integration_name,
            display_name=args.display_name,
            script=args.script,
            script_timeout=args.script_timeout,
            enabled=args.enabled,
            description=args.description,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error creating integration logical operator: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_logical_operators_update_command(args, chronicle):
    """Handle integration logical operator update command"""
    try:
        out = chronicle.update_integration_logical_operator(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
            display_name=args.display_name,
            script=args.script,
            script_timeout=args.script_timeout,
            enabled=args.enabled,
            description=args.description,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error updating integration logical operator: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_logical_operators_test_command(args, chronicle):
    """Handle integration logical operator test command"""
    try:
        # Get the logical operator first
        logical_operator = chronicle.get_integration_logical_operator(
            integration_name=args.integration_name,
            logical_operator_id=args.logical_operator_id,
        )

        out = chronicle.execute_integration_logical_operator_test(
            integration_name=args.integration_name,
            logical_operator=logical_operator,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error testing integration logical operator: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_logical_operators_template_command(args, chronicle):
    """Handle integration logical operator template command"""
    try:
        out = chronicle.get_integration_logical_operator_template(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting logical operator template: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
