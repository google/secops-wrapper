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
"""Google SecOps CLI search commands"""

import sys

from secops.cli.utils.common_args import (
    add_pagination_args,
    add_time_range_args,
)
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_search_command(subparsers):
    """Set up the search command parser.

    Args:
        subparsers: Subparsers object to add to
    """
    search_parser = subparsers.add_parser("search", help="Search UDM events")

    # Create mutually exclusive group for query types
    query_group = search_parser.add_mutually_exclusive_group()
    query_group.add_argument("--query", help="UDM query string")
    query_group.add_argument(
        "--nl-query",
        "--nl_query",
        dest="nl_query",
        help="Natural language query",
    )

    search_parser.add_argument(
        "--max-events",
        "--max_events",
        dest="max_events",
        type=int,
        default=100,
        help="Maximum events to return",
    )
    search_parser.add_argument(
        "--fields",
        help="Comma-separated list of fields to include in CSV output",
    )
    search_parser.add_argument(
        "--csv", action="store_true", help="Output in CSV format"
    )
    add_time_range_args(search_parser)
    search_parser.set_defaults(func=handle_search_command)

    search_subparser = search_parser.add_subparsers(
        dest="search_sub_commands", help="Search Sub Commands"
    )
    udm_field_value_search_parser = search_subparser.add_parser(
        "udm-field-values", help="Search UDM field values"
    )
    udm_field_value_search_parser.add_argument(
        "--query", required=True, help="UDM query string"
    )
    add_pagination_args(udm_field_value_search_parser)
    udm_field_value_search_parser.set_defaults(
        func=handle_find_udm_field_values_command
    )


def handle_search_command(args, chronicle):
    """Handle the search command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client
    """
    # Require query or nl_query
    if not args.query and not args.nl_query:
        print(
            "\nError: One of --query or --nl-query is required", file=sys.stderr
        )
        sys.exit(1)

    start_time, end_time = get_time_range(args)

    try:
        if args.csv and args.fields and args.query:
            fields = [f.strip() for f in args.fields.split(",")]
            result = chronicle.fetch_udm_search_csv(
                query=args.query,
                start_time=start_time,
                end_time=end_time,
                fields=fields,
            )
            print(result)
        elif args.nl_query:
            result = chronicle.nl_search(
                text=args.nl_query,
                start_time=start_time,
                end_time=end_time,
                max_events=args.max_events,
            )
            output_formatter(result, args.output)
        else:
            result = chronicle.search_udm(
                query=args.query,
                start_time=start_time,
                end_time=end_time,
                max_events=args.max_events,
            )
            output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_find_udm_field_values_command(args, chronicle):
    """Handle find UDM field values command."""
    try:
        result = chronicle.find_udm_field_values(
            query=args.query,
            page_size=args.page_size,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
