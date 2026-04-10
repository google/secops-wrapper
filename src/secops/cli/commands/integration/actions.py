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
"""Google SecOps CLI integration actions commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_actions_command(subparsers):
    """Setup integration actions command"""
    actions_parser = subparsers.add_parser(
        "actions",
        help="Manage integration actions",
    )
    lvl1 = actions_parser.add_subparsers(
        dest="actions_command", help="Integration actions command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List integration actions")
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
        help="Filter string for listing actions",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing actions",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_actions_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get integration action details")
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    get_parser.add_argument(
        "--action-id",
        type=str,
        help="ID of the action to get",
        dest="action_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_actions_get_command)

    # delete command
    delete_parser = lvl1.add_parser(
        "delete",
        help="Delete an integration action",
    )
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--action-id",
        type=str,
        help="ID of the action to delete",
        dest="action_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_actions_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new integration action"
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
        help="Display name for the action",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--code",
        type=str,
        help="Python code for the action",
        dest="code",
        required=True,
    )
    create_parser.add_argument(
        "--is-async",
        action="store_true",
        help="Whether the action is asynchronous",
        dest="is_async",
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the action",
        dest="description",
    )
    create_parser.add_argument(
        "--action-id",
        type=str,
        help="Custom ID for the action",
        dest="action_id",
    )
    create_parser.set_defaults(func=handle_actions_create_command)

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update an integration action"
    )
    update_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    update_parser.add_argument(
        "--action-id",
        type=str,
        help="ID of the action to update",
        dest="action_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the action",
        dest="display_name",
    )
    update_parser.add_argument(
        "--script",
        type=str,
        help="New Python script for the action",
        dest="script",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the action",
        dest="description",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_actions_update_command)

    # test command
    test_parser = lvl1.add_parser(
        "test", help="Execute an integration action test"
    )
    test_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    test_parser.add_argument(
        "--action-id",
        type=str,
        help="ID of the action to test",
        dest="action_id",
        required=True,
    )
    test_parser.set_defaults(func=handle_actions_test_command)

    # by-environment command
    by_env_parser = lvl1.add_parser(
        "by-environment",
        help="Get integration actions by environment",
    )
    by_env_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    by_env_parser.add_argument(
        "--environments",
        type=str,
        nargs="+",
        help="List of environments to filter by",
        dest="environments",
        required=True,
    )
    by_env_parser.add_argument(
        "--include-widgets",
        action="store_true",
        help="Whether to include widgets in the response",
        dest="include_widgets",
    )
    by_env_parser.set_defaults(func=handle_actions_by_environment_command)

    # template command
    template_parser = lvl1.add_parser(
        "template",
        help="Get a template for creating an action",
    )
    template_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    template_parser.add_argument(
        "--is-async",
        action="store_true",
        help="Whether to fetch template for async action",
        dest="is_async",
    )
    template_parser.set_defaults(func=handle_actions_template_command)


def handle_actions_list_command(args, chronicle):
    """Handle integration actions list command"""
    try:
        out = chronicle.soar.list_integration_actions(
            integration_name=args.integration_name,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing integration actions: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_get_command(args, chronicle):
    """Handle integration action get command"""
    try:
        out = chronicle.soar.get_integration_action(
            integration_name=args.integration_name,
            action_id=args.action_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration action: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_delete_command(args, chronicle):
    """Handle integration action delete command"""
    try:
        chronicle.soar.delete_integration_action(
            integration_name=args.integration_name,
            action_id=args.action_id,
        )
        print(f"Action {args.action_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting integration action: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_create_command(args, chronicle):
    """Handle integration action create command"""
    try:
        out = chronicle.soar.create_integration_action(
            integration_name=args.integration_name,
            display_name=args.display_name,
            script=args.code,  # CLI uses --code flag but API expects script
            timeout_seconds=300,  # Default 5 minutes
            enabled=True,  # Default to enabled
            script_result_name="result",  # Default result field name
            is_async=args.is_async,
            description=args.description,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating integration action: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_update_command(args, chronicle):
    """Handle integration action update command"""
    try:
        out = chronicle.soar.update_integration_action(
            integration_name=args.integration_name,
            action_id=args.action_id,
            display_name=args.display_name,
            script=(
                args.script if args.script else None
            ),  # CLI uses --code flag but API expects script
            description=args.description,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating integration action: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_test_command(args, chronicle):
    """Handle integration action test command"""
    try:
        # First get the action to test
        action = chronicle.soar.get_integration_action(
            integration_name=args.integration_name,
            action_id=args.action_id,
        )
        out = chronicle.soar.execute_integration_action_test(
            integration_name=args.integration_name,
            action_id=args.action_id,
            action=action,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error testing integration action: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_by_environment_command(args, chronicle):
    """Handle get actions by environment command"""
    try:
        out = chronicle.soar.get_integration_actions_by_environment(
            integration_name=args.integration_name,
            environments=args.environments,
            include_widgets=args.include_widgets,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting actions by environment: {e}", file=sys.stderr)
        sys.exit(1)


def handle_actions_template_command(args, chronicle):
    """Handle get action template command"""
    try:
        out = chronicle.soar.get_integration_action_template(
            integration_name=args.integration_name,
            is_async=args.is_async,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting action template: {e}", file=sys.stderr)
        sys.exit(1)
