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
"""Google SecOps CLI rule retrohunt commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_time_range_args,
    add_pagination_args,
    add_as_list_arg,
)
from secops.cli.utils.time_utils import parse_datetime


def setup_rule_retrohunt_command(subparsers):
    """Setup rule retrohunt command"""
    retrohunt_parser = subparsers.add_parser(
        "rule-retrohunt",
        help="Rule Retrohunt commands",
        description="Rule Retrohunt commands",
    )
    lvl1 = retrohunt_parser.add_subparsers(
        dest="command", help="Rule Retrohunt command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List rule retrohunts")
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--rule-id",
        type=str,
        help="ID of the rule to get retrohunts for",
        dest="rule_id",
        required=True,
    )
    list_parser.set_defaults(func=handle_retrohunt_list_command)

    # create command
    create_parser = lvl1.add_parser("create", help="create rule retrohunt")
    add_time_range_args(create_parser, required=True)
    create_parser.add_argument(
        "--rule-id",
        type=str,
        help="ID of the rule to create a retrohunt for",
        dest="rule_id",
        required=True,
    )
    create_parser.set_defaults(func=handle_rule_retrohunt_create_command)

    # get command
    get_parser = lvl1.add_parser("get", help="get a rule retrohunt")
    get_parser.add_argument(
        "--rule-id",
        type=str,
        help="ID of the rule to get retrohunt for",
        dest="rule_id",
        required=True,
    )
    get_parser.add_argument(
        "--operation-id",
        type=str,
        help="Operation ID of the retrohunt",
        dest="operation_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_get_retrohunt_command)


def handle_retrohunt_list_command(args, chronicle):
    """List rule retrohunts"""
    try:
        out = chronicle.list_retrohunts(
            rule_id=args.rule_id,
            page_size=args.page_size,
            page_token=args.page_token,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing rule retrohunts: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_retrohunt_create_command(args, chronicle):
    """Create rule retrohunt"""
    try:
        out = chronicle.create_retrohunt(
            rule_id=args.rule_id,
            start_time=parse_datetime(args.start_time),
            end_time=parse_datetime(args.end_time),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating rule retrohunt: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_retrohunt_command(args, chronicle):
    """Get a rule retrohunt"""
    try:
        out = chronicle.get_retrohunt(
            rule_id=args.rule_id,
            operation_id=args.operation_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting rule retrohunt: {e}", file=sys.stderr)
        sys.exit(1)
