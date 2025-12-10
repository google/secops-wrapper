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
"""Google SecOps CLI alert commands"""

import sys

from secops.cli.utils.common_args import add_time_range_args
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_alert_command(subparsers):
    """Set up the alert command parser."""
    alert_parser = subparsers.add_parser("alert", help="Manage alerts")
    alert_parser.add_argument(
        "--snapshot-query",
        "--snapshot_query",
        dest="snapshot_query",
        help=(
            'Query to filter alerts (e.g. feedback_summary.status != "CLOSED")'
        ),
    )
    alert_parser.add_argument(
        "--baseline-query",
        "--baseline_query",
        dest="baseline_query",
        help="Baseline query for alerts",
    )
    alert_parser.add_argument(
        "--max-alerts",
        "--max_alerts",
        dest="max_alerts",
        type=int,
        default=100,
        help="Maximum alerts to return",
    )
    add_time_range_args(alert_parser)
    alert_parser.set_defaults(func=handle_alert_command)


def handle_alert_command(args, chronicle):
    """Handle alert command."""
    start_time, end_time = get_time_range(args)

    try:
        result = chronicle.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query=args.snapshot_query,
            baseline_query=args.baseline_query,
            max_alerts=args.max_alerts,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
