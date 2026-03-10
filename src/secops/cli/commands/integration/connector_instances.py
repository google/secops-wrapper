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
"""Google SecOps CLI connector instances commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_connector_instances_command(subparsers):
    """Setup connector instances command"""
    instances_parser = subparsers.add_parser(
        "connector-instances",
        help="Manage connector instances",
    )
    lvl1 = instances_parser.add_subparsers(
        dest="connector_instances_command",
        help="Connector instances command",
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List connector instances")
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
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing instances",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing instances",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_connector_instances_list_command)

    # get command
    get_parser = lvl1.add_parser(
        "get", help="Get a specific connector instance"
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
        "--connector-instance-id",
        type=str,
        help="ID of the connector instance to get",
        dest="connector_instance_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_connector_instances_get_command)

    # delete command
    delete_parser = lvl1.add_parser(
        "delete", help="Delete a connector instance"
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
        "--connector-instance-id",
        type=str,
        help="ID of the connector instance to delete",
        dest="connector_instance_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_connector_instances_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new connector instance"
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
        "--environment",
        type=str,
        help="Environment for the connector instance",
        dest="environment",
        required=True,
    )
    create_parser.add_argument(
        "--display-name",
        type=str,
        help="Display name for the connector instance",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--interval-seconds",
        type=int,
        help="Interval in seconds for connector execution",
        dest="interval_seconds",
    )
    create_parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="Timeout in seconds for connector execution",
        dest="timeout_seconds",
    )
    create_parser.add_argument(
        "--enabled",
        action="store_true",
        help="Enable the connector instance",
        dest="enabled",
    )
    create_parser.set_defaults(func=handle_connector_instances_create_command)

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update a connector instance"
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
        "--connector-instance-id",
        type=str,
        help="ID of the connector instance to update",
        dest="connector_instance_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the connector instance",
        dest="display_name",
    )
    update_parser.add_argument(
        "--interval-seconds",
        type=int,
        help="New interval in seconds for connector execution",
        dest="interval_seconds",
    )
    update_parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="New timeout in seconds for connector execution",
        dest="timeout_seconds",
    )
    update_parser.add_argument(
        "--enabled",
        type=str,
        choices=["true", "false"],
        help="Enable or disable the connector instance",
        dest="enabled",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_connector_instances_update_command)

    # fetch-latest command
    fetch_parser = lvl1.add_parser(
        "fetch-latest",
        help="Get the latest definition of a connector instance",
    )
    fetch_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    fetch_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    fetch_parser.add_argument(
        "--connector-instance-id",
        type=str,
        help="ID of the connector instance",
        dest="connector_instance_id",
        required=True,
    )
    fetch_parser.set_defaults(
        func=handle_connector_instances_fetch_latest_command
    )

    # set-logs command
    logs_parser = lvl1.add_parser(
        "set-logs",
        help="Enable or disable log collection for a connector instance",
    )
    logs_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    logs_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    logs_parser.add_argument(
        "--connector-instance-id",
        type=str,
        help="ID of the connector instance",
        dest="connector_instance_id",
        required=True,
    )
    logs_parser.add_argument(
        "--enabled",
        type=str,
        choices=["true", "false"],
        help="Enable or disable log collection",
        dest="enabled",
        required=True,
    )
    logs_parser.set_defaults(func=handle_connector_instances_set_logs_command)

    # run-ondemand command
    run_parser = lvl1.add_parser(
        "run-ondemand",
        help="Run a connector instance on demand",
    )
    run_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    run_parser.add_argument(
        "--connector-id",
        type=str,
        help="ID of the connector",
        dest="connector_id",
        required=True,
    )
    run_parser.add_argument(
        "--connector-instance-id",
        type=str,
        help="ID of the connector instance to run",
        dest="connector_instance_id",
        required=True,
    )
    run_parser.set_defaults(
        func=handle_connector_instances_run_ondemand_command
    )


def handle_connector_instances_list_command(args, chronicle):
    """Handle connector instances list command"""
    try:
        out = chronicle.list_connector_instances(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing connector instances: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_get_command(args, chronicle):
    """Handle connector instance get command"""
    try:
        out = chronicle.get_connector_instance(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting connector instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_delete_command(args, chronicle):
    """Handle connector instance delete command"""
    try:
        chronicle.delete_connector_instance(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
        )
        print(
            f"Connector instance {args.connector_instance_id}"
            f" deleted successfully"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting connector instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_create_command(args, chronicle):
    """Handle connector instance create command"""
    try:
        out = chronicle.create_connector_instance(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            environment=args.environment,
            display_name=args.display_name,
            interval_seconds=args.interval_seconds,
            timeout_seconds=args.timeout_seconds,
            enabled=args.enabled,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating connector instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_update_command(args, chronicle):
    """Handle connector instance update command"""
    try:
        # Convert enabled string to boolean if provided
        enabled = None
        if args.enabled:
            enabled = args.enabled.lower() == "true"

        out = chronicle.update_connector_instance(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
            display_name=args.display_name,
            interval_seconds=args.interval_seconds,
            timeout_seconds=args.timeout_seconds,
            enabled=enabled,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating connector instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_fetch_latest_command(args, chronicle):
    """Handle fetch latest connector instance definition command"""
    try:
        out = chronicle.get_connector_instance_latest_definition(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error fetching latest connector instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_set_logs_command(args, chronicle):
    """Handle set connector instance logs collection command"""
    try:
        enabled = args.enabled.lower() == "true"
        out = chronicle.set_connector_instance_logs_collection(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
            enabled=enabled,
        )
        status = "enabled" if enabled else "disabled"
        print(f"Log collection {status} for connector instance successfully")
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error setting connector instance logs: {e}", file=sys.stderr)
        sys.exit(1)


def handle_connector_instances_run_ondemand_command(args, chronicle):
    """Handle run connector instance on demand command"""
    try:
        # Get the connector instance first
        connector_instance = chronicle.get_connector_instance(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
        )
        out = chronicle.run_connector_instance_on_demand(
            integration_name=args.integration_name,
            connector_id=args.connector_id,
            connector_instance_id=args.connector_instance_id,
            connector_instance=connector_instance,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error running connector instance on demand: {e}", file=sys.stderr
        )
        sys.exit(1)
