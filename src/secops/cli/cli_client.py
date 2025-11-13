"""
Command line entrypoint for SecOps CLI
"""

import argparse
import sys
from typing import Any, Tuple

from secops import SecOpsClient
from secops.cli.commands.config import setup_config_command
from secops.cli.commands.search import setup_search_command
from secops.cli.commands.udm_search import setup_udm_search_view_command
from secops.cli.commands.stats import setup_stats_command
from secops.cli.commands.entity import setup_entity_command
from secops.cli.commands.iocs import setup_iocs_command
from secops.cli.commands.log import setup_log_command
from secops.cli.commands.parser import setup_parser_command
from secops.cli.commands.feed import setup_feed_command
from secops.cli.commands.rule import setup_rule_command
from secops.cli.commands.alert import setup_alert_command
from secops.cli.commands.case import setup_case_command
from secops.cli.commands.export import setup_export_command
from secops.cli.commands.gemini import setup_gemini_command
from secops.cli.commands.help import setup_help_command
from secops.cli.commands.data_table import setup_data_table_command
from secops.cli.commands.reference_list import setup_reference_list_command
from secops.cli.commands.rule_exclusion import setup_rule_exclusion_command
from secops.cli.commands.parser_extension import setup_parser_extension_command
from secops.cli.commands.dashboard import setup_dashboard_command
from secops.cli.commands.dashboard_query import setup_dashboard_query_command
from secops.cli.commands.forwarder import setup_forwarder_command
from secops.cli.commands.curated_rule import setup_curated_rules_command
from secops.cli.utils.common_args import (
    add_common_args,
    add_chronicle_args,
)
from secops.cli.utils.config_utils import load_config
from secops.exceptions import AuthenticationError, SecOpsError


def setup_client(args: argparse.Namespace) -> Tuple[SecOpsClient, Any]:
    """Set up and return SecOpsClient and Chronicle client based on args.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (SecOpsClient, Chronicle client)
    """
    # Authentication setup
    client_kwargs = {}
    if args.service_account:
        client_kwargs["service_account_path"] = args.service_account

    # Create client
    try:
        client = SecOpsClient(**client_kwargs)

        # Initialize Chronicle client if required
        if (
            hasattr(args, "customer_id")
            or hasattr(args, "project_id")
            or hasattr(args, "region")
        ):
            chronicle_kwargs = {}
            if hasattr(args, "customer_id") and args.customer_id:
                chronicle_kwargs["customer_id"] = args.customer_id
            if hasattr(args, "project_id") and args.project_id:
                chronicle_kwargs["project_id"] = args.project_id
            if hasattr(args, "region") and args.region:
                chronicle_kwargs["region"] = args.region

            # Check if required args for Chronicle client are present
            missing_args = []
            if not chronicle_kwargs.get("customer_id"):
                missing_args.append("customer_id")
            if not chronicle_kwargs.get("project_id"):
                missing_args.append("project_id")

            if missing_args:
                print(
                    "Error: Missing required configuration parameters:",
                    ", ".join(missing_args),
                    file=sys.stderr,
                )
                print(
                    "\nPlease run the config command to set up your "
                    "configuration:",
                    file=sys.stderr,
                )
                print(
                    "  secops config set --customer-id YOUR_CUSTOMER_ID "
                    "--project-id YOUR_PROJECT_ID",
                    file=sys.stderr,
                )
                print(
                    "\nOr provide them as command-line options:",
                    file=sys.stderr,
                )
                print(
                    "  secops --customer-id YOUR_CUSTOMER_ID --project-id "
                    "YOUR_PROJECT_ID [command]",
                    file=sys.stderr,
                )
                print("\nFor help finding these values, run:", file=sys.stderr)
                print("  secops help --topic customer-id", file=sys.stderr)
                print("  secops help --topic project-id", file=sys.stderr)
                sys.exit(1)

            chronicle = client.chronicle(**chronicle_kwargs)
            return client, chronicle

        return client, None
    except (AuthenticationError, SecOpsError) as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        print("\nFor authentication using ADC, run:", file=sys.stderr)
        print("  gcloud auth application-default login", file=sys.stderr)
        print("\nFor configuration help, run:", file=sys.stderr)
        print("  secops help --topic config", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Google SecOps CLI")

    # Global arguments
    add_common_args(parser)
    add_chronicle_args(parser)

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", help="Command to execute"
    )

    # Set up individual command parsers
    setup_search_command(subparsers)
    setup_udm_search_view_command(subparsers)
    setup_stats_command(subparsers)
    setup_entity_command(subparsers)
    setup_iocs_command(subparsers)
    setup_log_command(subparsers)
    setup_parser_command(subparsers)
    setup_parser_extension_command(subparsers)
    setup_feed_command(subparsers)
    setup_rule_command(subparsers)
    setup_alert_command(subparsers)
    setup_case_command(subparsers)
    setup_export_command(subparsers)
    setup_gemini_command(subparsers)
    setup_data_table_command(subparsers)
    setup_reference_list_command(subparsers)
    setup_rule_exclusion_command(subparsers)
    setup_forwarder_command(subparsers)
    setup_curated_rules_command(subparsers)
    setup_config_command(subparsers)
    setup_help_command(subparsers)
    setup_dashboard_command(subparsers)
    setup_dashboard_query_command(subparsers)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle config commands directly without setting up Chronicle client
    if args.command == "config" or args.command == "help":
        args.func(args)
        return

    # Check if this is a Chronicle-related command that requires configuration
    chronicle_commands = [
        "search",
        "udm-search-view",
        "stats",
        "entity",
        "iocs",
        "rule",
        "alert",
        "case",
        "export",
        "gemini",
        "rule-exclusion",
        "curated-rule",
        "forwarder",
        "dashboard",
    ]
    requires_chronicle = any(cmd in args.command for cmd in chronicle_commands)

    if requires_chronicle:
        # Check for required configuration before attempting to
        # create the client
        config = load_config()
        customer_id = args.customer_id or config.get("customer_id")
        project_id = args.project_id or config.get("project_id")

        if not customer_id or not project_id:
            missing = []
            if not customer_id:
                missing.append("customer_id")
            if not project_id:
                missing.append("project_id")

            print(
                f'Error: Missing required configuration: {", ".join(missing)}',
                file=sys.stderr,
            )
            print("\nPlease set up your configuration first:", file=sys.stderr)
            print(
                "  secops config set --customer-id YOUR_CUSTOMER_ID "
                "--project-id YOUR_PROJECT_ID --region YOUR_REGION",
                file=sys.stderr,
            )
            print(
                "\nOr provide them directly on the command line:",
                file=sys.stderr,
            )
            print(
                "  secops --customer-id YOUR_CUSTOMER_ID --project-id "
                f"YOUR_PROJECT_ID --region YOUR_REGION {args.command}",
                file=sys.stderr,
            )
            print("\nNeed help finding these values?", file=sys.stderr)
            print("  secops help --topic customer-id", file=sys.stderr)
            print("  secops help --topic project-id", file=sys.stderr)
            print("\nFor general configuration help:", file=sys.stderr)
            print("  secops help --topic config", file=sys.stderr)
            sys.exit(1)

    # Set up client
    client, chronicle = setup_client(args)  # pylint: disable=unused-variable

    # Execute command
    if hasattr(args, "func"):
        if not requires_chronicle or chronicle is not None:
            args.func(args, chronicle)
        else:
            print(
                "Error: Chronicle client required for this command",
                file=sys.stderr,
            )
            print("\nFor help with configuration:", file=sys.stderr)
            print("  secops help --topic config", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
