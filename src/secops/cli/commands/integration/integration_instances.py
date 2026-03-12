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
"""Google SecOps CLI integration instances commands"""

import json
import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_integration_instances_command(subparsers):
    """Setup integration instances command"""
    instances_parser = subparsers.add_parser(
        "instances",
        help="Manage integration instances",
    )
    lvl1 = instances_parser.add_subparsers(
        dest="integration_instances_command",
        help="Integration instances command",
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List integration instances")
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
        help="Filter string for listing instances",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing instances",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_integration_instances_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get integration instance details")
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    get_parser.add_argument(
        "--instance-id",
        type=str,
        help="ID of the instance to get",
        dest="instance_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_integration_instances_get_command)

    # delete command
    delete_parser = lvl1.add_parser(
        "delete", help="Delete an integration instance"
    )
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--instance-id",
        type=str,
        help="ID of the instance to delete",
        dest="instance_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_integration_instances_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new integration instance"
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
        help="Display name for the instance",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--environment",
        type=str,
        help="Environment name for the instance",
        dest="environment",
        required=True,
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the instance",
        dest="description",
    )
    create_parser.add_argument(
        "--instance-id",
        type=str,
        help="Custom ID for the instance",
        dest="instance_id",
    )
    create_parser.add_argument(
        "--config",
        type=str,
        help="JSON string of instance configuration",
        dest="config",
    )
    create_parser.set_defaults(func=handle_integration_instances_create_command)

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update an integration instance"
    )
    update_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    update_parser.add_argument(
        "--instance-id",
        type=str,
        help="ID of the instance to update",
        dest="instance_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the instance",
        dest="display_name",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the instance",
        dest="description",
    )
    update_parser.add_argument(
        "--config",
        type=str,
        help="JSON string of new instance configuration",
        dest="config",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_integration_instances_update_command)

    # test command
    test_parser = lvl1.add_parser(
        "test", help="Execute an integration instance test"
    )
    test_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    test_parser.add_argument(
        "--instance-id",
        type=str,
        help="ID of the instance to test",
        dest="instance_id",
        required=True,
    )
    test_parser.set_defaults(func=handle_integration_instances_test_command)

    # get-affected-items command
    affected_parser = lvl1.add_parser(
        "get-affected-items",
        help="Get items affected by an integration instance",
    )
    affected_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    affected_parser.add_argument(
        "--instance-id",
        type=str,
        help="ID of the instance",
        dest="instance_id",
        required=True,
    )
    affected_parser.set_defaults(
        func=handle_integration_instances_get_affected_items_command
    )

    # get-default command
    default_parser = lvl1.add_parser(
        "get-default",
        help="Get the default integration instance",
    )
    default_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    default_parser.set_defaults(
        func=handle_integration_instances_get_default_command
    )


def handle_integration_instances_list_command(args, chronicle):
    """Handle integration instances list command"""
    try:
        out = chronicle.list_integration_instances(
            integration_name=args.integration_name,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing integration instances: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_instances_get_command(args, chronicle):
    """Handle integration instance get command"""
    try:
        out = chronicle.get_integration_instance(
            integration_name=args.integration_name,
            integration_instance_id=args.instance_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_instances_delete_command(args, chronicle):
    """Handle integration instance delete command"""
    try:
        chronicle.delete_integration_instance(
            integration_name=args.integration_name,
            integration_instance_id=args.instance_id,
        )
        print(f"Integration instance {args.instance_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting integration instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_instances_create_command(args, chronicle):
    """Handle integration instance create command"""
    try:
        # Parse config if provided

        config = None
        if args.config:
            config = json.loads(args.config)

        out = chronicle.create_integration_instance(
            integration_name=args.integration_name,
            display_name=args.display_name,
            environment=args.environment,
            description=args.description,
            integration_instance_id=args.instance_id,
            config=config,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing config JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating integration instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_instances_update_command(args, chronicle):
    """Handle integration instance update command"""
    try:
        # Parse config if provided

        config = None
        if args.config:
            config = json.loads(args.config)

        out = chronicle.update_integration_instance(
            integration_name=args.integration_name,
            integration_instance_id=args.instance_id,
            display_name=args.display_name,
            description=args.description,
            config=config,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing config JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating integration instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_instances_test_command(args, chronicle):
    """Handle integration instance test command"""
    try:
        # Get the instance first
        instance = chronicle.get_integration_instance(
            integration_name=args.integration_name,
            integration_instance_id=args.instance_id,
        )

        out = chronicle.execute_integration_instance_test(
            integration_name=args.integration_name,
            integration_instance_id=args.instance_id,
            integration_instance=instance,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error testing integration instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_instances_get_affected_items_command(args, chronicle):
    """Handle get integration instance affected items command"""
    try:
        out = chronicle.get_integration_instance_affected_items(
            integration_name=args.integration_name,
            integration_instance_id=args.instance_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting integration instance affected items: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def handle_integration_instances_get_default_command(args, chronicle):
    """Handle get default integration instance command"""
    try:
        out = chronicle.get_default_integration_instance(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting default integration instance: {e}", file=sys.stderr
        )
        sys.exit(1)
