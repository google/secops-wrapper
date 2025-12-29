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
"""Google SecOps CLI featured content rules commands"""

import sys

from secops.cli.utils.common_args import add_pagination_args
from secops.cli.utils.formatters import output_formatter


def setup_featured_content_rules_command(subparsers):
    """Set up the featured-content-rules command group."""
    parser = subparsers.add_parser(
        "featured-content-rules",
        help="Manage featured content rules from Chronicle Content Hub",
    )
    subparser = parser.add_subparsers(dest="featured_content_rules_cmd")
    parser.set_defaults(func=lambda args, _: parser.print_help())

    list_parser = subparser.add_parser(
        "list", help="List featured content rules"
    )
    add_pagination_args(list_parser)
    list_parser.add_argument(
        "--filter",
        "--filter-expression",
        dest="filter_expression",
        help=(
            "Filter expression. Supported filters: "
            "category_name, policy_name, rule_id, rule_precision, "
            "search_rule_name_or_description"
        ),
    )
    list_parser.set_defaults(func=handle_featured_content_rules_list_command)


def handle_featured_content_rules_list_command(args, chronicle):
    """List featured content rules."""
    try:
        out = chronicle.list_featured_content_rules(
            page_size=getattr(args, "page_size", None),
            page_token=getattr(args, "page_token", None),
            filter_expression=getattr(args, "filter_expression", None),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:
        print(f"Error listing featured content rules: {e}", file=sys.stderr)
        sys.exit(1)
