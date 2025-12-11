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
"""Google SecOps CLI dashboard query commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.exceptions import APIError


def setup_dashboard_query_command(subparsers):
    """Set up dashboard query command."""
    dashboard_query_parser = subparsers.add_parser(
        "dashboard-query", help="Manage Chronicle dashboard queries"
    )
    dashboard_query_subparsers = dashboard_query_parser.add_subparsers(
        dest="dashboard_query_command",
        help="Dashboard query command to execute",
    )
    dashboard_query_parser.set_defaults(
        func=lambda args, _: dashboard_query_parser.print_help()
    )

    # Execute query
    execute_query_parser = dashboard_query_subparsers.add_parser(
        "execute", help="Execute a dashboard query"
    )
    execute_query_parser.add_argument("--query", help="Query to execute")
    execute_query_parser.add_argument(
        "--query-file", "--query_file", help="File containing query to execute"
    )
    execute_query_parser.add_argument(
        "--interval",
        required=True,
        help="Time interval JSON string",
    )
    eq_filters_group = execute_query_parser.add_mutually_exclusive_group()
    eq_filters_group.add_argument(
        "--filters-file",
        "--filters_file",
        help="File containing filters for the query in JSON string",
    )
    eq_filters_group.add_argument(
        "--filters",
        "--filters",
        help="Filters for the query in JSON string",
    )
    execute_query_parser.add_argument(
        "--clear-cache",
        "--clear_cache",
        choices=["true", "false"],
        help="Clear cache for the query",
    )
    execute_query_parser.set_defaults(
        func=handle_dashboard_query_execute_command
    )

    # Get query
    get_query_parser = dashboard_query_subparsers.add_parser(
        "get", help="Get a dashboard query"
    )
    get_query_parser.add_argument("--id", required=True, help="Query ID")
    get_query_parser.set_defaults(func=handle_dashboard_query_get_command)


def handle_dashboard_query_execute_command(args, chronicle):
    """Handle execute dashboard query command."""
    try:
        # Process query from file or argument
        if args.query_file and args.query:
            print(
                "Error: Only one of query or query-file can be specified.",
                file=sys.stderr,
            )
            sys.exit(1)

        query = args.query if args.query else None
        if args.query_file:
            try:
                with open(args.query_file, encoding="utf-8") as f:
                    query = f.read()
            except OSError as e:
                print(f"Error reading query file: {e}", file=sys.stderr)
                sys.exit(1)

        if not query:
            print("Error: No query provided", file=sys.stderr)
            sys.exit(1)

        result = chronicle.execute_dashboard_query(
            query=query,
            interval=args.interval,
            filters=args.filters,
            clear_cache=args.clear_cache,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error executing query: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_query_get_command(args, chronicle):
    """Handle get dashboard query command."""
    try:
        result = chronicle.get_dashboard_query(query_id=args.id)
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting query: {e}", file=sys.stderr)
        sys.exit(1)
