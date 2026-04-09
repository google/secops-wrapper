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
"""Google SecOps CLI marketplace integration commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_marketplace_integrations_command(subparsers):
    """Setup marketplace integration command"""
    mp_parser = subparsers.add_parser(
        "marketplace",
        help="Manage Chronicle marketplace integration",
    )
    lvl1 = mp_parser.add_subparsers(
        dest="mp_command", help="Marketplace integration command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List marketplace integrations")
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing marketplace integrations",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing marketplace integrations",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_mp_integration_list_command)

    # get command
    get_parser = lvl1.add_parser(
        "get", help="Get marketplace integration details"
    )
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the marketplace integration to get",
        dest="integration_name",
        required=True,
    )
    get_parser.set_defaults(func=handle_mp_integration_get_command)

    # diff command
    diff_parser = lvl1.add_parser(
        "diff",
        help="Get marketplace integration diff between "
        "installed and latest version",
    )
    diff_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the marketplace integration to diff",
        dest="integration_name",
        required=True,
    )
    diff_parser.set_defaults(func=handle_mp_integration_diff_command)

    # install command
    install_parser = lvl1.add_parser(
        "install", help="Install or update a marketplace integration"
    )
    install_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the marketplace integration to install or update",
        dest="integration_name",
        required=True,
    )
    install_parser.add_argument(
        "--override-mapping",
        action="store_true",
        help="Override existing mapping",
        dest="override_mapping",
    )
    install_parser.add_argument(
        "--staging",
        action="store_true",
        help="Whether to install the integration in "
        "staging environment (true/false)",
        dest="staging",
    )
    install_parser.add_argument(
        "--version",
        type=str,
        help="Version of the marketplace integration to install",
        dest="version",
    )
    install_parser.add_argument(
        "--restore-from-snapshot",
        action="store_true",
        help="Whether to restore the integration from existing snapshot "
        "(true/false)",
        dest="restore_from_snapshot",
    )
    install_parser.set_defaults(func=handle_mp_integration_install_command)

    # uninstall command
    uninstall_parser = lvl1.add_parser(
        "uninstall", help="Uninstall a marketplace integration"
    )
    uninstall_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the marketplace integration to uninstall",
        dest="integration_name",
        required=True,
    )
    uninstall_parser.set_defaults(func=handle_mp_integration_uninstall_command)


def handle_mp_integration_list_command(args, chronicle):
    """Handle marketplace integration list command"""
    try:
        out = chronicle.soar.list_marketplace_integrations(
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing marketplace integrations: {e}", file=sys.stderr)
        sys.exit(1)


def handle_mp_integration_get_command(args, chronicle):
    """Handle marketplace integration get command"""
    try:
        out = chronicle.soar.get_marketplace_integration(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting marketplace integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_mp_integration_diff_command(args, chronicle):
    """Handle marketplace integration diff command"""
    try:
        out = chronicle.soar.get_marketplace_integration_diff(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting marketplace integration diff: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_mp_integration_install_command(args, chronicle):
    """Handle marketplace integration install command"""
    try:
        out = chronicle.soar.install_marketplace_integration(
            integration_name=args.integration_name,
            override_mapping=args.override_mapping,
            staging=args.staging,
            version=args.version,
            restore_from_snapshot=args.restore_from_snapshot,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error installing marketplace integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_mp_integration_uninstall_command(args, chronicle):
    """Handle marketplace integration uninstall command"""
    try:
        out = chronicle.soar.uninstall_marketplace_integration(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error uninstalling marketplace integration: {e}", file=sys.stderr
        )
        sys.exit(1)
