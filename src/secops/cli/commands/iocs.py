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
"""Google SecOps CLI iocs commands"""

import sys

from secops.cli.utils.common_args import add_time_range_args
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_iocs_command(subparsers):
    """Set up the IOCs command parser."""
    iocs_parser = subparsers.add_parser("iocs", help="List IoCs")
    iocs_parser.add_argument(
        "--max-matches",
        "--max_matches",
        dest="max_matches",
        type=int,
        default=100,
        help="Maximum matches to return",
    )
    iocs_parser.add_argument(
        "--mandiant", action="store_true", help="Include Mandiant attributes"
    )
    iocs_parser.add_argument(
        "--prioritized",
        action="store_true",
        help="Only return prioritized IoCs",
    )
    add_time_range_args(iocs_parser)
    iocs_parser.set_defaults(func=handle_iocs_command)


def handle_iocs_command(args, chronicle):
    """Handle the IOCs command."""
    start_time, end_time = get_time_range(args)

    try:
        result = chronicle.list_iocs(
            start_time=start_time,
            end_time=end_time,
            max_matches=args.max_matches,
            add_mandiant_attributes=args.mandiant,
            prioritized_only=args.prioritized,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
