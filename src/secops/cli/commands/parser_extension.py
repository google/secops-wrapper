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
"""Google SecOps CLI parser extension commands"""

import sys
from typing import Any

from secops.cli.utils.common_args import add_pagination_args
from secops.cli.utils.formatters import output_formatter
from secops.exceptions import APIError


def setup_parser_extension_command(subparsers: Any) -> None:
    """Setup parser extension subcommands.

    Args:
        subparsers: Subparsers object to add to
    """
    parser_ext = subparsers.add_parser(
        "parser-extension",
        help="Manage parser extensions",
    )
    parser_ext_sub = parser_ext.add_subparsers(dest="subcommand")
    parser_ext.set_defaults(func=lambda args, _: parser_ext.print_help())

    # Create parser extension
    create = parser_ext_sub.add_parser(
        "create",
        help="Create a new parser extension",
    )
    create.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help="Log type for the parser extension",
    )

    # Log input options
    log_group = create.add_mutually_exclusive_group()
    log_group.add_argument("--log", help="Sample log content as a string")
    log_group.add_argument(
        "--log-file",
        "--log_file",
        help="Path to file containing sample log content",
    )

    # Processing options (mutually exclusive)
    processing_group = create.add_mutually_exclusive_group(required=True)
    processing_group.add_argument(
        "--parser-config",
        "--parser_config",
        help="Parser Configuration(CBN snippet code)",
    )
    processing_group.add_argument(
        "--parser-config-file",
        "--parser_config_file",
        help="Path to file containing Parser Config(CBN snippet code)",
    )
    processing_group.add_argument(
        "--field-extractors",
        "--field_extractors",
        help=(
            "JSON string defining field extractors "
            '(e.g. \'{"field1": "value1", "field2": "value2"}\')'
        ),
    )
    processing_group.add_argument(
        "--dynamic-parsing",
        "--dynamic_parsing",
        help=(
            "JSON string defining dynamic parsing configuration "
            '(e.g. \'{"field1": "value1", "field2": "value2"}\')'
        ),
    )
    create.set_defaults(func=handle_parser_extension_create_command)

    # Get parser extension
    get = parser_ext_sub.add_parser(
        "get",
        help="Get details of a parser extension",
    )
    get.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help="Log type of the parser extension",
    )
    get.add_argument(
        "--id",
        required=True,
        help="ID of the parser extension",
    )
    get.set_defaults(func=handle_parser_extension_get_command)

    # List parser extensions
    list_cmd = parser_ext_sub.add_parser(
        "list",
        help="List parser extensions",
    )
    list_cmd.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help="Log type to list parser extensions for",
    )
    add_pagination_args(list_cmd)
    list_cmd.set_defaults(func=handle_parser_extension_list_command)

    # Activate parser extension
    activate = parser_ext_sub.add_parser(
        "activate",
        help="Activate a parser extension",
    )
    activate.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help="Log type of the parser extension",
    )
    activate.add_argument(
        "--id",
        required=True,
        help="ID of the parser extension to activate",
    )
    activate.set_defaults(func=handle_parser_extension_activate_command)

    # Delete parser extension
    delete = parser_ext_sub.add_parser(
        "delete",
        help="Delete a parser extension",
    )
    delete.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help="Log type of the parser extension",
    )
    delete.add_argument(
        "--id",
        required=True,
        help="ID of the parser extension to delete",
    )
    delete.set_defaults(func=handle_parser_extension_delete_command)


def handle_parser_extension_create_command(args, chronicle):
    """Handle parser extension create command."""
    try:
        # Handle log input
        log = None
        if args.log:
            log = args.log
        elif args.log_file:
            try:
                with open(args.log_file, encoding="utf-8") as f:
                    log = f.read().strip()
            except OSError as e:
                print(f"Error reading log file: {e}", file=sys.stderr)
                sys.exit(1)

        # Handle CBN snippet input
        parser_config = None
        if args.parser_config:
            parser_config = args.parser_config
        elif args.parser_config_file:
            try:
                with open(args.parser_config_file, encoding="utf-8") as f:
                    parser_config = f.read().strip()
            except OSError as e:
                print(f"Error reading CBN snippet file: {e}", file=sys.stderr)
                sys.exit(1)

        # Get field extractors and dynamic parsing input directly
        field_extractors = args.field_extractors
        dynamic_parsing = args.dynamic_parsing

        # Validate that exactly one of parser_config, field_extractors,
        # or dynamic_parsing is provided
        options = [parser_config, field_extractors, dynamic_parsing]
        if sum(1 for opt in options if opt is not None) != 1:
            print(
                "Error: Exactly one of --parser_config, --field-extractors, or "
                "--dynamic-parsing must be provided",
                file=sys.stderr,
            )
            sys.exit(1)

        result = chronicle.create_parser_extension(
            log_type=args.log_type,
            log=log,
            parser_config=parser_config,
            field_extractors=field_extractors,
            dynamic_parsing=dynamic_parsing,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating parser extension: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_extension_get_command(args, chronicle):
    """Handle parser extension get command."""
    try:
        result = chronicle.get_parser_extension(args.log_type, args.id)
        output_formatter(result, args.output)
    except APIError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_parser_extension_list_command(args, chronicle):
    """Handle parser extension list command."""
    try:
        result = chronicle.list_parser_extensions(
            args.log_type,
            page_size=args.page_size,
            page_token=args.page_token,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_parser_extension_activate_command(args, chronicle):
    """Handle parser extension activate command."""
    try:
        chronicle.activate_parser_extension(args.log_type, args.id)
        print(f"Successfully activated parser extension {args.id}")
    except APIError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def handle_parser_extension_delete_command(args, chronicle):
    """Handle parser extension delete command."""
    try:
        chronicle.delete_parser_extension(args.log_type, args.id)
        print(f"Successfully deleted parser extension {args.id}")
    except APIError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
