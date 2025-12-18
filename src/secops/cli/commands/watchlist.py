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
"""Google SecOps CLI watchlist commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_time_range_args,
    add_pagination_args,
)


def setup_watchlist_command(subparsers):
    """Setup watchlist command"""
    watchlist_parser = subparsers.add_parser(
        "watchlist",
        help="Manage Chronicle watchlists",
    )
    lvl1 = watchlist_parser.add_subparsers(
        dest="watchlist_command", help="Watchlist command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List watchlists")
    add_time_range_args(list_parser)
    add_pagination_args(list_parser)
    list_parser.set_defaults(func=handle_watchlist_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get watchlist by ID")
    get_parser.add_argument(
        "--watchlist-id",
        type=str,
        help="ID of watchlist to get",
        dest="watchlist_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_watchlist_get_command)

    # delete command
    delete_parser = lvl1.add_parser("delete", help="Delete watchlist by ID")
    delete_parser.add_argument(
        "--watchlist-id",
        type=str,
        help="ID of the watchlist to delete",
        dest="watchlist_id",
        required=True,
    )
    delete_parser.add_argument(
        "--force",
        action="store_true",
        help="Flag to remove entities under watchlist",
    )
    delete_parser.set_defaults(func=handle_watchlist_delete_command)

    # create command
    create_parser = lvl1.add_parser("create", help="Create watchlist")
    create_parser.add_argument(
        "--name", type=str, help="Watchlist name", dest="name", required=True
    )
    create_parser.add_argument(
        "--display-name",
        type=str,
        help="Watchlist display name",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--multiplying-factor",
        type=float,
        help="Watchlist multiplying factor",
        dest="multiplying_factor",
        required=True,
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Watchlist description",
        dest="description",
        required=False,
    )
    create_parser.set_defaults(func=handle_watchlist_create_command)


def handle_watchlist_list_command(args, chronicle):
    """List watchlists"""
    try:
        out = chronicle.list_watchlists(
            page_size=getattr(args, "page_size", None),
            page_token=getattr(args, "page_token", None),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing watchlists: {e}", file=sys.stderr)
        sys.exit(1)


def handle_watchlist_get_command(args, chronicle):
    """Get watchlist by ID"""
    try:
        out = chronicle.get_watchlist(args.watchlist_id)
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting watchlist: {e}", file=sys.stderr)
        sys.exit(1)


def handle_watchlist_delete_command(args, chronicle):
    """Delete watchlist by ID"""
    try:
        out = chronicle.delete_watchlist(args.watchlist_id, args.force)
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting watchlist: {e}", file=sys.stderr)
        sys.exit(1)


def handle_watchlist_create_command(args, chronicle):
    """Create watchlist"""
    try:
        out = chronicle.create_watchlist(
            name=args.name,
            display_name=args.display_name,
            multiplying_factor=args.multiplying_factor,
            description=args.description,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating watchlist: {e}", file=sys.stderr)
        sys.exit(1)
