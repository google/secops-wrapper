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
"""Google SecOps CLI feed commands"""

import sys

from secops.cli.utils.formatters import output_formatter


def setup_feed_command(subparsers):
    """Set up the feed command parser."""
    feed_parser = subparsers.add_parser("feed", help="Manage feeds")
    feed_subparsers = feed_parser.add_subparsers(
        dest="feed_command", help="Feed command"
    )
    feed_parser.set_defaults(func=lambda args, _: feed_parser.print_help())

    # List feeds command
    list_parser = feed_subparsers.add_parser("list", help="List feeds")
    list_parser.set_defaults(func=handle_feed_list_command)

    # Get feed command
    get_parser = feed_subparsers.add_parser("get", help="Get feed details")
    get_parser.add_argument("--id", required=True, help="Feed ID")
    get_parser.set_defaults(func=handle_feed_get_command)

    # Create feed command
    create_parser = feed_subparsers.add_parser("create", help="Create a feed")
    create_parser.add_argument(
        "--display-name", required=True, help="Feed display name"
    )
    create_parser.add_argument(
        "--details", required=True, help="Feed details as JSON string"
    )
    create_parser.set_defaults(func=handle_feed_create_command)

    # Update feed command
    update_parser = feed_subparsers.add_parser("update", help="Update a feed")
    update_parser.add_argument("--id", required=True, help="Feed ID")
    update_parser.add_argument(
        "--display-name", required=False, help="Feed display name"
    )
    update_parser.add_argument(
        "--details", required=False, help="Feed details as JSON string"
    )
    update_parser.set_defaults(func=handle_feed_update_command)

    # Delete feed command
    delete_parser = feed_subparsers.add_parser("delete", help="Delete a feed")
    delete_parser.add_argument("--id", required=True, help="Feed ID")
    delete_parser.set_defaults(func=handle_feed_delete_command)

    # Enable feed command
    enable_parser = feed_subparsers.add_parser("enable", help="Enable a feed")
    enable_parser.add_argument("--id", required=True, help="Feed ID")
    enable_parser.set_defaults(func=handle_feed_enable_command)

    # Disable feed command
    disable_parser = feed_subparsers.add_parser(
        "disable", help="Disable a feed"
    )
    disable_parser.add_argument("--id", required=True, help="Feed ID")
    disable_parser.set_defaults(func=handle_feed_disable_command)

    # Generate secret command
    generate_secret_parser = feed_subparsers.add_parser(
        "generate-secret", help="Generate a secret for a feed"
    )
    generate_secret_parser.add_argument("--id", required=True, help="Feed ID")
    generate_secret_parser.set_defaults(
        func=handle_feed_generate_secret_command
    )


def handle_feed_list_command(args, chronicle):
    """Handle feed list command."""
    try:
        result = chronicle.list_feeds()
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_get_command(args, chronicle):
    """Handle feed get command."""
    try:
        result = chronicle.get_feed(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_create_command(args, chronicle):
    """Handle feed create command."""
    try:
        result = chronicle.create_feed(args.display_name, args.details)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_update_command(args, chronicle):
    """Handle feed update command."""
    try:
        result = chronicle.update_feed(args.id, args.display_name, args.details)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_delete_command(args, chronicle):
    """Handle feed delete command."""
    try:
        result = chronicle.delete_feed(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_enable_command(args, chronicle):
    """Handle feed enable command."""
    try:
        result = chronicle.enable_feed(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_disable_command(args, chronicle):
    """Handle feed disable command."""
    try:
        result = chronicle.disable_feed(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_feed_generate_secret_command(args, chronicle):
    """Handle feed generate secret command."""
    try:
        result = chronicle.generate_secret(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
