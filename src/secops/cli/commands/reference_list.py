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
"""Google SecOps CLI reference list commands"""

import sys

from secops.chronicle.reference_list import (
    ReferenceListSyntaxType,
    ReferenceListView,
)
from secops.cli.utils.formatters import output_formatter


def setup_reference_list_command(subparsers):
    """Set up the reference list command parser."""
    rl_parser = subparsers.add_parser(
        "reference-list", help="Manage reference lists"
    )
    rl_subparsers = rl_parser.add_subparsers(
        dest="rl_command", help="Reference list command"
    )
    rl_parser.set_defaults(func=lambda args, _: rl_parser.print_help())

    # List reference lists command
    list_parser = rl_subparsers.add_parser("list", help="List reference lists")
    list_parser.add_argument(
        "--view", choices=["BASIC", "FULL"], default="BASIC", help="View type"
    )
    list_parser.set_defaults(func=handle_rl_list_command)

    # Get reference list command
    get_parser = rl_subparsers.add_parser(
        "get", help="Get reference list details"
    )
    get_parser.add_argument("--name", required=True, help="Reference list name")
    get_parser.add_argument(
        "--view", choices=["BASIC", "FULL"], default="FULL", help="View type"
    )
    get_parser.set_defaults(func=handle_rl_get_command)

    # Create reference list command
    create_parser = rl_subparsers.add_parser(
        "create", help="Create a reference list"
    )
    create_parser.add_argument(
        "--name", required=True, help="Reference list name"
    )
    create_parser.add_argument(
        "--description", default="", help="Reference list description"
    )
    create_parser.add_argument(
        "--entries", help="Comma-separated list of entries"
    )
    create_parser.add_argument(
        "--syntax-type",
        "--syntax_type",
        dest="syntax_type",
        choices=["STRING", "REGEX", "CIDR"],
        default="STRING",
        help="Syntax type",
    )
    create_parser.add_argument(
        "--entries-file",
        "--entries_file",
        dest="entries_file",
        help="Path to file containing entries (one per line)",
    )
    create_parser.set_defaults(func=handle_rl_create_command)

    # Update reference list command
    update_parser = rl_subparsers.add_parser(
        "update", help="Update a reference list"
    )
    update_parser.add_argument(
        "--name", required=True, help="Reference list name"
    )
    update_parser.add_argument(
        "--description", help="New reference list description"
    )
    update_parser.add_argument(
        "--entries", help="Comma-separated list of entries"
    )
    update_parser.add_argument(
        "--entries-file",
        "--entries_file",
        dest="entries_file",
        help="Path to file containing entries (one per line)",
    )
    update_parser.set_defaults(func=handle_rl_update_command)

    # Note: Reference List deletion is currently not supported by the API


def handle_rl_list_command(args, chronicle):
    """Handle reference list list command."""
    try:
        view = ReferenceListView[args.view]
        result = chronicle.list_reference_lists(view=view)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rl_get_command(args, chronicle):
    """Handle reference list get command."""
    try:
        view = ReferenceListView[args.view]
        result = chronicle.get_reference_list(args.name, view=view)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rl_create_command(args, chronicle):
    """Handle reference list create command."""
    try:
        # Get entries from file or command line
        entries = []
        if args.entries_file:
            try:
                with open(args.entries_file, encoding="utf-8") as f:
                    entries = [line.strip() for line in f if line.strip()]
            except OSError as e:
                print(f"Error reading entries file: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.entries:
            entries = [e.strip() for e in args.entries.split(",")]

        syntax_type = ReferenceListSyntaxType[args.syntax_type]

        result = chronicle.create_reference_list(
            name=args.name,
            description=args.description,
            entries=entries,
            syntax_type=syntax_type,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rl_update_command(args, chronicle):
    """Handle reference list update command."""
    try:
        # Get entries from file or command line
        entries = None
        if args.entries_file:
            try:
                with open(args.entries_file, encoding="utf-8") as f:
                    entries = [line.strip() for line in f if line.strip()]
            except OSError as e:
                print(f"Error reading entries file: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.entries:
            entries = [e.strip() for e in args.entries.split(",")]

        result = chronicle.update_reference_list(
            name=args.name, description=args.description, entries=entries
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
