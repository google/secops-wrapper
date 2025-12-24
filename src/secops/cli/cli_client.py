"""
Command line entrypoint for SecOps CLI
"""

import argparse
import sys

from secops import SecOpsClient
from secops.chronicle import ChronicleClient
from secops.cli.commands.alert import setup_alert_command
from secops.cli.commands.case import setup_case_command
from secops.cli.commands.config import setup_config_command
from secops.cli.commands.curated_rule import setup_curated_rules_command
from secops.cli.commands.dashboard import setup_dashboard_command
from secops.cli.commands.featured_content_rules import (
    setup_featured_content_rules_command,
)
from secops.cli.commands.dashboard_query import setup_dashboard_query_command
from secops.cli.commands.data_table import setup_data_table_command
from secops.cli.commands.entity import setup_entity_command
from secops.cli.commands.export import setup_export_command
from secops.cli.commands.feed import setup_feed_command
from secops.cli.commands.forwarder import setup_forwarder_command
from secops.cli.commands.gemini import setup_gemini_command
from secops.cli.commands.help import setup_help_command
from secops.cli.commands.iocs import setup_iocs_command
from secops.cli.commands.log import setup_log_command
from secops.cli.commands.log_processing import (
    setup_log_processing_command,
)
from secops.cli.commands.parser import setup_parser_command
from secops.cli.commands.parser_extension import setup_parser_extension_command
from secops.cli.commands.reference_list import setup_reference_list_command
from secops.cli.commands.rule import setup_rule_command
from secops.cli.commands.rule_exclusion import setup_rule_exclusion_command
from secops.cli.commands.search import setup_search_command
from secops.cli.commands.stats import setup_stats_command
from secops.cli.commands.udm_search import setup_udm_search_view_command
from secops.cli.commands.watchlist import setup_watchlist_command
from secops.cli.utils.common_args import add_chronicle_args, add_common_args
from secops.cli.utils.config_utils import load_config
from secops.exceptions import AuthenticationError, SecOpsError


def _print_help_instructions():
    """Print help instructions to CLI for missing configuration."""
    print(
        "\nPlease run the config command to set up your configuration:",
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


def setup_client(
    args: argparse.Namespace,
) -> tuple[SecOpsClient, ChronicleClient]:
    """Backwards-compatible wrapper used by tests and external code.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (SecOpsClient, Chronicle client)
    """
    client_kwargs = {}
    if getattr(args, "service_account", None):
        client_kwargs["service_account_path"] = args.service_account
    client = SecOpsClient(**client_kwargs)
    config = load_config() or {}
    return _setup_client_core(args, client, config)


def _setup_client_core(
    args: argparse.Namespace,
    client: SecOpsClient,
    config: dict[str, str],
) -> tuple[SecOpsClient, ChronicleClient]:
    """Set up and return SecOpsClient and Chronicle client based on args or
    config file. Args take precedence over config file.

    Args:
        args: Command line arguments
        client: SecOpsClient instance
        config: Configuration dictionary

    Returns:
        Tuple of (SecOpsClient, Chronicle client)
    """
    try:
        # Define required arguments for Chronicle client
        required_args = ["customer_id", "project_id"]
        chronicle_kwargs = {}

        # Build kwargs with precedence: CLI args > config file > None
        optional_args = ["region", "api_version"]
        for arg in required_args + optional_args:
            # Check CLI args first
            if hasattr(args, arg) and getattr(args, arg):
                # Map api_version to default_api_version for chronicle()
                key = "default_api_version" if arg == "api_version" else arg
                chronicle_kwargs[key] = getattr(args, arg)
            # Fall back to config if not in args
            elif arg in config:
                # Map api_version to default_api_version for chronicle()
                key = "default_api_version" if arg == "api_version" else arg
                chronicle_kwargs[key] = config[arg]

        # Check for missing required arguments
        missing = [
            arg for arg in required_args if not chronicle_kwargs.get(arg)
        ]
        if missing:
            print(
                "Error: Missing required configuration parameters:",
                ", ".join(missing),
                file=sys.stderr,
            )
            _print_help_instructions()
            sys.exit(1)

        chronicle = client.chronicle(**chronicle_kwargs)
        return client, chronicle
    except (AuthenticationError, SecOpsError) as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        print("\nFor authentication using ADC, run:", file=sys.stderr)
        print("  gcloud auth application-default login", file=sys.stderr)
        print("\nFor configuration help, run:", file=sys.stderr)
        print("  secops help --topic config", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser."""
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
    setup_log_processing_command(subparsers)
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
    setup_featured_content_rules_command(subparsers)
    setup_config_command(subparsers)
    setup_help_command(subparsers)
    setup_dashboard_command(subparsers)
    setup_dashboard_query_command(subparsers)
    setup_watchlist_command(subparsers)

    return parser


def run(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Run the CLI

    Args:
        args: Command line arguments
        parser: Argument parser
    """
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle config commands directly without setting up Chronicle client
    if args.command == "config" or args.command == "help":
        args.func(args)
        return

    # Set up client
    _, chronicle = setup_client(args)

    # Execute command
    args.func(args, chronicle)


def main() -> None:
    """Main entry point for the CLI."""

    parser = build_parser()
    args = parser.parse_args()

    run(args, parser)


if __name__ == "__main__":
    main()
