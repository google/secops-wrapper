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
"""Google SecOps CLI integration connectors commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_connectors_command(subparsers):
    """Setup integration connectors command"""
    connectors_parser = subparsers.add_parser(
        "connectors",
        help="Manage integration connectors",
    )
    lvl1 = connectors_parser.add_subparsers(
        dest="connectors_command", help="Integration connectors command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List integration connectors")
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
        help="Filter string for listing connectors",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing connectors",
        dest="order_by",
    )
    list_parser.set_defaults(
        func=handle_connectors_list_command,
    )

    # get command
    get_parser = lvl1.add_parser(
        "get", help="Get integration connector details"
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
        help="ID of the connector to get",
        dest="connector_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_connectors_get_command)

    # delete command
    delete_parser = lvl1.add_parser(
        "delete", help="Delete an integration connector"
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
        help="ID of the connector to delete",
        dest="connector_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_connectors_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new integration connector"
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
        help="Display name for the connector",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--code",
        type=str,
        help="Python code for the connector",
        dest="code",
        required=True,
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the connector",
        dest="description",
    )
    create_parser.add_argument(
        "--connector-id",
        type=str,
        help="Custom ID for the connector",
        dest="connector_id",
    )
    create_parser.set_defaults(func=handle_connectors_create_command)

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update an integration connector"
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
        help="ID of the connector to update",
        dest="connector_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the connector",
        dest="display_name",
    )
    update_parser.add_argument(
        "--code",
        type=str,
        help="New Python code for the connector",
        dest="code",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the connector",
        dest="description",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_connectors_update_command)

    # test command
    test_parser = lvl1.add_parser(
        "test", help="Execute an integration connector test"
    )
    test_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    test_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector to test",
        dest="connector_id",
        required=True,
    )
    test_parser.set_defaults(func=handle_connectors_test_command)

    # template command
    template_parser = lvl1.add_parser(
        "template",
        help="Get a template for creating a connector",
    )
    template_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    template_parser.set_defaults(func=handle_connectors_template_command)


def handle_connectors_list_command(args, chronicle):
    """Handle integration connectors list command"""
    try:
        out = chronicle.list_integration_connectors(
            integration_name=args.integration_name,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing integration connectors: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connectors_get_command(args, chronicle):
    """Handle integration connector get command"""
    try:
        out = chronicle.get_integration_connector(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration connector: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connectors_delete_command(args, chronicle):
    """Handle integration connector delete command"""
    try:
        chronicle.delete_integration_connector(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
        )
        print(f"Connector {args.connector_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting integration connector: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connectors_create_command(args, chronicle):
    """Handle integration connector create command"""
    try:
        out = chronicle.create_integration_connector(
            integration_name=args.integration_name,
            display_name=args.display_name,
            code=args.code,
            description=args.description,
            connector_id=args.connector_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating integration connector: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connectors_update_command(args, chronicle):
    """Handle integration connector update command"""
    try:
        out = chronicle.update_integration_connector(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            display_name=args.display_name,
            code=args.code,
            description=args.description,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating integration connector: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connectors_test_command(args, chronicle):
    """Handle integration connector test command"""
    try:
        # First get the connector to test
        connector = chronicle.get_integration_connector(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
        )
        out = chronicle.execute_integration_connector_test(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector=connector,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error testing integration connector: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connectors_template_command(args, chronicle):
    """Handle get connector template command"""
    try:
        out = chronicle.get_integration_connector_template(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting connector template: {e}", file=sys.stderr)
        sys.exit(1)
