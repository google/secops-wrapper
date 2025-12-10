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
"""Google SecOps CLI UDM search commands"""

import sys

from secops.cli.utils.common_args import add_time_range_args
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_udm_search_view_command(subparsers):
    """Set up the udm-search-view command parser.

    Args:
        subparsers: Subparsers object to add to
    """
    udm_search_view_parser = subparsers.add_parser(
        "udm-search-view", help="Fetch UDM search view results"
    )

    # Create a mutually exclusive group for query input
    query_group = udm_search_view_parser.add_mutually_exclusive_group(
        required=True
    )
    query_group.add_argument("--query", help="UDM query string")
    query_group.add_argument(
        "--query-file",
        "--query_file",
        dest="query_file",
        help="File containing UDM query",
    )

    # Add snapshot query option
    udm_search_view_parser.add_argument(
        "--snapshot-query",
        "--snapshot_query",
        dest="snapshot_query",
        help="Query for filtering alerts",
    )

    # Add max events and detections parameters
    udm_search_view_parser.add_argument(
        "--max-events",
        "--max_events",
        dest="max_events",
        type=int,
        default=10000,
        help="Maximum events to return",
    )
    udm_search_view_parser.add_argument(
        "--max-detections",
        "--max_detections",
        dest="max_detections",
        type=int,
        default=1000,
        help="Maximum detections to return",
    )

    # Add case sensitivity option
    udm_search_view_parser.add_argument(
        "--case-sensitive",
        "--case_sensitive",
        dest="case_sensitive",
        action="store_true",
        default=False,
        help="Perform case-sensitive search",
    )

    # Add common time range arguments
    add_time_range_args(udm_search_view_parser)

    # Set the handler function
    udm_search_view_parser.set_defaults(func=handle_udm_search_view_command)


def handle_udm_search_view_command(args, chronicle):
    """Handle the udm-search-view command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client instance
    """
    start_time, end_time = get_time_range(args)

    # Process query from file or argument
    query = args.query
    if args.query_file:
        try:
            with open(args.query_file, encoding="utf-8") as f:
                query = f.read()
        except OSError as e:
            print(f"Error reading query file: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        # Build parameters for fetch_udm_search_view
        params = {
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
            "max_events": args.max_events,
            "max_detections": args.max_detections,
            "case_insensitive": not args.case_sensitive,
        }

        # Add snapshot_query only if it's provided
        if hasattr(args, "snapshot_query") and args.snapshot_query:
            params["snapshot_query"] = args.snapshot_query

        result = chronicle.fetch_udm_search_view(**params)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
