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
"""Google SecOps CLI integration managers commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_managers_command(subparsers):
    """Setup integration managers command"""
    managers_parser = subparsers.add_parser(
        "managers",
        help="Manage integration managers",
    )
    lvl1 = managers_parser.add_subparsers(
        dest="managers_command", help="Integration managers command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List integration managers")
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
        help="Filter string for listing managers",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing managers",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_managers_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get integration manager details")
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    get_parser.add_argument(
        "--manager-id",
        type=str,
        help="ID of the manager to get",
        dest="manager_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_managers_get_command)

    # delete command
    delete_parser = lvl1.add_parser(
        "delete",
        help="Delete an integration manager",
    )
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--manager-id",
        type=str,
        help="ID of the manager to delete",
        dest="manager_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_managers_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new integration manager"
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
        help="Display name for the manager",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--code",
        type=str,
        help="Python code for the manager",
        dest="code",
        required=True,
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the manager",
        dest="description",
    )
    create_parser.add_argument(
        "--manager-id",
        type=str,
        help="Custom ID for the manager",
        dest="manager_id",
    )
    create_parser.set_defaults(func=handle_managers_create_command)

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update an integration manager"
    )
    update_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    update_parser.add_argument(
        "--manager-id",
        type=str,
        help="ID of the manager to update",
        dest="manager_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the manager",
        dest="display_name",
    )
    update_parser.add_argument(
        "--code",
        type=str,
        help="New Python code for the manager",
        dest="code",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the manager",
        dest="description",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_managers_update_command)

    # template command
    template_parser = lvl1.add_parser(
        "template",
        help="Get a template for creating a manager",
    )
    template_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    template_parser.set_defaults(func=handle_managers_template_command)


def handle_managers_list_command(args, chronicle):
    """Handle integration managers list command"""
    try:
        out = chronicle.soar.list_integration_managers(
            integration_name=args.integration_name,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing integration managers: {e}", file=sys.stderr)
        sys.exit(1)


def handle_managers_get_command(args, chronicle):
    """Handle integration manager get command"""
    try:
        out = chronicle.soar.get_integration_manager(
            integration_name=args.integration_name,
            manager_id=args.manager_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration manager: {e}", file=sys.stderr)
        sys.exit(1)


def handle_managers_delete_command(args, chronicle):
    """Handle integration manager delete command"""
    try:
        chronicle.delete_integration_manager(
            integration_name=args.integration_name,
            manager_id=args.manager_id,
        )
        print(f"Manager {args.manager_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting integration manager: {e}", file=sys.stderr)
        sys.exit(1)


def handle_managers_create_command(args, chronicle):
    """Handle integration manager create command"""
    try:
        out = chronicle.soar.create_integration_manager(
            integration_name=args.integration_name,
            display_name=args.display_name,
            code=args.code,
            description=args.description,
            manager_id=args.manager_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating integration manager: {e}", file=sys.stderr)
        sys.exit(1)


def handle_managers_update_command(args, chronicle):
    """Handle integration manager update command"""
    try:
        out = chronicle.soar.update_integration_manager(
            integration_name=args.integration_name,
            manager_id=args.manager_id,
            display_name=args.display_name,
            code=args.code,
            description=args.description,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating integration manager: {e}", file=sys.stderr)
        sys.exit(1)


def handle_managers_template_command(args, chronicle):
    """Handle get manager template command"""
    try:
        out = chronicle.soar.get_integration_manager_template(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting manager template: {e}", file=sys.stderr)
        sys.exit(1)
