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
"""Google SecOps CLI stats commands"""

import sys

from secops.cli.utils.common_args import add_time_range_args
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_stats_command(subparsers):
    """Set up the stats command parser."""
    stats_parser = subparsers.add_parser("stats", help="Get UDM statistics")
    stats_parser.add_argument(
        "--query", required=True, help="Stats query string"
    )
    stats_parser.add_argument(
        "--max-events",
        "--max_events",
        dest="max_events",
        type=int,
        default=1000,
        help="Maximum events to process",
    )
    stats_parser.add_argument(
        "--max-values",
        "--max_values",
        dest="max_values",
        type=int,
        default=100,
        help="Maximum values per field",
    )
    stats_parser.add_argument(
        "--timeout",
        dest="timeout",
        type=int,
        default=120,
        help="Timeout (in seconds) for API request",
    )
    add_time_range_args(stats_parser)
    stats_parser.set_defaults(func=handle_stats_command)


def handle_stats_command(args, chronicle):
    """Handle the stats command."""
    start_time, end_time = get_time_range(args)

    try:
        result = chronicle.get_stats(
            query=args.query,
            start_time=start_time,
            end_time=end_time,
            max_events=args.max_events,
            max_values=args.max_values,
            timeout=args.timeout,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
