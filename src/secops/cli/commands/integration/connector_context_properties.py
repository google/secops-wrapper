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
"""Google SecOps CLI connector context properties commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_connector_context_properties_command(subparsers):
    """Setup connector context properties command"""
    properties_parser = subparsers.add_parser(
        "connector-context-properties",
        help="Manage connector context properties",
    )
    lvl1 = properties_parser.add_subparsers(
        dest="connector_context_properties_command",
        help="Connector context properties command",
    )

    # list command
    list_parser = lvl1.add_parser(
        "list", help="List connector context properties"
    )
    list_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    list_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    list_parser.add_argument(
        "--context-id",
        type=str,
        help="Context ID to filter properties",
        dest="context_id",
    )
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing properties",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing properties",
        dest="order_by",
    )
    list_parser.set_defaults(
        func=handle_connector_context_properties_list_command,
    )

    # get command
    get_parser = lvl1.add_parser(
        "get", help="Get a specific connector context property"
    )
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    get_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    get_parser.add_argument(
        "--context-id",
        type=str,
        help="Context ID of the property",
        dest="context_id",
        required=True,
    )
    get_parser.add_argument(
        "--property-id",
        type=str,
        help="ID of the property to get",
        dest="property_id",
        required=True,
    )
    get_parser.set_defaults(
        func=handle_connector_context_properties_get_command
    )

    # delete command
    delete_parser = lvl1.add_parser(
        "delete", help="Delete a connector context property"
    )
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    delete_parser.add_argument(
        "--context-id",
        type=str,
        help="Context ID of the property",
        dest="context_id",
        required=True,
    )
    delete_parser.add_argument(
        "--property-id",
        type=str,
        help="ID of the property to delete",
        dest="property_id",
        required=True,
    )
    delete_parser.set_defaults(
        func=handle_connector_context_properties_delete_command
    )

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new connector context property"
    )
    create_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    create_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    create_parser.add_argument(
        "--context-id",
        type=str,
        help="Context ID for the property",
        dest="context_id",
        required=True,
    )
    create_parser.add_argument(
        "--key",
        type=str,
        help="Key for the property",
        dest="key",
        required=True,
    )
    create_parser.add_argument(
        "--value",
        type=str,
        help="Value for the property",
        dest="value",
        required=True,
    )
    create_parser.set_defaults(
        func=handle_connector_context_properties_create_command
    )

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update a connector context property"
    )
    update_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    update_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    update_parser.add_argument(
        "--context-id",
        type=str,
        help="Context ID of the property",
        dest="context_id",
        required=True,
    )
    update_parser.add_argument(
        "--property-id",
        type=str,
        help="ID of the property to update",
        dest="property_id",
        required=True,
    )
    update_parser.add_argument(
        "--value",
        type=str,
        help="New value for the property",
        dest="value",
        required=True,
    )
    update_parser.set_defaults(
        func=handle_connector_context_properties_update_command
    )

    # clear-all command
    clear_parser = lvl1.add_parser(
        "clear-all", help="Delete all connector context properties"
    )
    clear_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    clear_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    clear_parser.add_argument(
        "--context-id",
        type=str,
        help="Context ID to clear all properties for",
        dest="context_id",
        required=True,
    )
    clear_parser.set_defaults(
        func=handle_connector_context_properties_clear_command
    )


def handle_connector_context_properties_list_command(args, chronicle):
    """Handle connector context properties list command"""
    try:
        out = chronicle.list_connector_context_properties(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            context_id=args.context_id,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error listing connector context properties: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_connector_context_properties_get_command(args, chronicle):
    """Handle connector context property get command"""
    try:
        out = chronicle.get_connector_context_property(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            context_id=args.context_id,
            context_property_id=args.property_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting connector context property: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_context_properties_delete_command(args, chronicle):
    """Handle connector context property delete command"""
    try:
        chronicle.delete_connector_context_property(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            context_id=args.context_id,
            context_property_id=args.property_id,
        )
        print(
            f"Connector context property "
            f"{args.property_id} deleted successfully"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error deleting connector context property: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_connector_context_properties_create_command(args, chronicle):
    """Handle connector context property create command"""
    try:
        out = chronicle.create_connector_context_property(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            context_id=args.context_id,
            key=args.key,
            value=args.value,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error creating connector context property: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_connector_context_properties_update_command(args, chronicle):
    """Handle connector context property update command"""
    try:
        out = chronicle.update_connector_context_property(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            context_id=args.context_id,
            context_property_id=args.property_id,
            value=args.value,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error updating connector context property: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_connector_context_properties_clear_command(args, chronicle):
    """Handle clear all connector context properties command"""
    try:
        chronicle.delete_all_connector_context_properties(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            context_id=args.context_id,
        )
        print(
            f"All connector context properties for context "
            f"{args.context_id} cleared successfully"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error clearing connector context properties: {e}", file=sys.stderr
        )
        sys.exit(1)
