"""
Command line handlers and helpers for SecOps CLI
"""

import argparse
import base64
import sys

from secops.cli.utils.common_args import add_pagination_args
from secops.cli.utils.formatters import output_formatter
from secops.exceptions import APIError, SecOpsError


def setup_parser_command(subparsers):
    """Set up the parser command parser."""

    parser_parser = subparsers.add_parser("parser", help="Manage Parsers")
    parser_subparsers = parser_parser.add_subparsers(
        dest="parser_command", help="Parser command"
    )
    parser_parser.set_defaults(func=lambda args, _: parser_parser.print_help())

    # --- Activate Parser Command ---
    activate_parser_sub = parser_subparsers.add_parser(
        "activate", help="Activate a custom parser."
    )
    activate_parser_sub.add_argument(
        "--log-type", type=str, help="Log type of the parser."
    )
    activate_parser_sub.add_argument(
        "--id", type=str, help="ID of the parser to activate."
    )
    activate_parser_sub.set_defaults(func=handle_parser_activate_command)

    # --- Activate Release Candidate Parser Command ---
    activate_rc_parser_sub = parser_subparsers.add_parser(
        "activate-rc", help="Activate the release candidate parser."
    )
    activate_rc_parser_sub.add_argument(
        "--log-type", type=str, help="Log type of the parser."
    )
    activate_rc_parser_sub.add_argument(
        "--id", type=str, help="ID of the release candidate parser to activate."
    )
    activate_rc_parser_sub.set_defaults(func=handle_parser_activate_rc_command)

    # --- Copy Parser Command ---
    copy_parser_sub = parser_subparsers.add_parser(
        "copy", help="Make a copy of a prebuilt parser."
    )
    copy_parser_sub.add_argument(
        "--log-type", type=str, help="Log type of the parser to copy."
    )
    copy_parser_sub.add_argument(
        "--id", type=str, help="ID of the parser to copy."
    )
    copy_parser_sub.set_defaults(func=handle_parser_copy_command)

    # --- Create Parser Command ---
    create_parser_sub = parser_subparsers.add_parser(
        "create", help="Create a new parser."
    )
    create_parser_sub.add_argument(
        "--log-type", type=str, help="Log type for the new parser."
    )
    create_parser_code_group = create_parser_sub.add_mutually_exclusive_group(
        required=True
    )
    create_parser_code_group.add_argument(
        "--parser-code", type=str, help="Content of the new parser (CBN code)."
    )
    create_parser_code_group.add_argument(
        "--parser-code-file",
        type=str,
        help="Path to a file containing the parser code (CBN code).",
    )
    create_parser_sub.add_argument(
        "--validated-on-empty-logs",
        action="store_true",
        help=(
            "Whether the parser is validated on empty logs "
            "(default: True if not specified, only use flag for True)."
        ),
    )
    create_parser_sub.set_defaults(func=handle_parser_create_command)

    # --- Deactivate Parser Command ---
    deactivate_parser_sub = parser_subparsers.add_parser(
        "deactivate", help="Deactivate a custom parser."
    )
    deactivate_parser_sub.add_argument(
        "--log-type", type=str, help="Log type of the parser."
    )
    deactivate_parser_sub.add_argument(
        "--id", type=str, help="ID of the parser to deactivate."
    )
    deactivate_parser_sub.set_defaults(func=handle_parser_deactivate_command)

    # --- Delete Parser Command ---
    delete_parser_sub = parser_subparsers.add_parser(
        "delete", help="Delete a parser."
    )
    delete_parser_sub.add_argument(
        "--log-type", type=str, help="Log type of the parser."
    )
    delete_parser_sub.add_argument(
        "--id", type=str, help="ID of the parser to delete."
    )
    delete_parser_sub.add_argument(
        "--force",
        action="store_true",
        help="Forcefully delete an ACTIVE parser.",
    )
    delete_parser_sub.set_defaults(func=handle_parser_delete_command)

    # --- Get Parser Command ---
    get_parser_sub = parser_subparsers.add_parser(
        "get", help="Get a parser by ID."
    )
    get_parser_sub.add_argument(
        "--log-type", type=str, help="Log type of the parser."
    )
    get_parser_sub.add_argument(
        "--id", type=str, help="ID of the parser to retrieve."
    )
    get_parser_sub.set_defaults(func=handle_parser_get_command)

    # --- List Parsers Command ---
    list_parsers_sub = parser_subparsers.add_parser(
        "list", help="List parsers."
    )
    list_parsers_sub.add_argument(
        "--log-type",
        type=str,
        default="-",
        help="Log type to filter by (default: '-' for all).",
    )
    add_pagination_args(list_parsers_sub)
    list_parsers_sub.add_argument(
        "--filter",
        type=str,
        help="Filter expression to apply (e.g., 'state=ACTIVE').",
    )
    list_parsers_sub.set_defaults(func=handle_parser_list_command)

    # --- Run Parser Command ---
    run_parser_sub = parser_subparsers.add_parser(
        "run",
        help="Run parser against sample logs for evaluation.",
        description=(
            "Evaluate a parser by running it against sample log entries. "
            "This helps test parser logic before deploying it."
        ),
        epilog=(
            "Examples:\n"
            "  # Run parser with inline code and logs:\n"
            "  secops parser run --log-type OKTA --parser-code 'filter {}' "
            "--log 'log1' --log 'log2'\n\n"
            "  # Run parser using files:\n"
            "  secops parser run --log-type WINDOWS "
            "--parser-code-file parser.conf --logs-file logs.txt\n\n"
            "  # Run parser with the active parser\n"
            "  secops parser run --log-type OKTA --log-file logs.txt\n\n"
            "  # Run parser with extension:\n"
            "  secops parser run --log-type CUSTOM --parser-code-file "
            "parser.conf \\\n    --parser-extension-code-file extension.conf "
            "--logs-file logs.txt"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    run_parser_sub.add_argument(
        "--log-type",
        type=str,
        required=True,
        help="Log type of the parser for evaluation (e.g., OKTA, WINDOWS_AD)",
    )
    run_parser_code_group = run_parser_sub.add_mutually_exclusive_group(
        required=False
    )
    run_parser_code_group.add_argument(
        "--parser-code",
        type=str,
        help="Content of the main parser (CBN code) to evaluate",
    )
    run_parser_code_group.add_argument(
        "--parser-code-file",
        type=str,
        help="Path to a file containing the main parser code (CBN code)",
    )
    run_parser_ext_group = run_parser_sub.add_mutually_exclusive_group(
        required=False
    )
    run_parser_ext_group.add_argument(
        "--parser-extension-code",
        type=str,
        help="Content of the parser extension (CBN snippet)",
    )
    run_parser_ext_group.add_argument(
        "--parser-extension-code-file",
        type=str,
        help=(
            "Path to a file containing the parser extension code (CBN snippet)"
        ),
    )
    run_parser_logs_group = run_parser_sub.add_mutually_exclusive_group(
        required=True
    )
    run_parser_logs_group.add_argument(
        "--log",
        action="append",
        help=(
            "Provide a raw log string to test. Can be specified multiple "
            "times for multiple logs"
        ),
    )
    run_parser_logs_group.add_argument(
        "--logs-file",
        type=str,
        help="Path to a file containing raw logs (one log per line)",
    )
    run_parser_sub.add_argument(
        "--statedump-allowed",
        action="store_true",
        help="Enable statedump filter for the parser configuration",
    )
    run_parser_sub.set_defaults(func=handle_parser_run_command)


def handle_parser_activate_command(args, chronicle):
    """Handle parser activate command."""
    try:
        result = chronicle.activate_parser(args.log_type, args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error activating parser: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_activate_rc_command(args, chronicle):
    """Handle parser activate-release-candidate command."""
    try:
        result = chronicle.activate_release_candidate_parser(
            args.log_type, args.id
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error activating release candidate parser: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_parser_copy_command(args, chronicle):
    """Handle parser copy command."""
    try:
        result = chronicle.copy_parser(args.log_type, args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error copying parser: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_create_command(args, chronicle):
    """Handle parser create command."""
    try:
        parser_code = ""
        if args.parser_code_file:
            try:
                with open(args.parser_code_file, encoding="utf-8") as f:
                    parser_code = f.read()
            except OSError as e:
                print(f"Error reading parser code file: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.parser_code:
            parser_code = args.parser_code
        else:
            raise SecOpsError(
                "Either --parser-code or --parser-code-file must be provided."
            )

        result = chronicle.create_parser(
            args.log_type, parser_code, args.validated_on_empty_logs
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating parser: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_deactivate_command(args, chronicle):
    """Handle parser deactivate command."""
    try:
        result = chronicle.deactivate_parser(args.log_type, args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deactivating parser: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_delete_command(args, chronicle):
    """Handle parser delete command."""
    try:
        result = chronicle.delete_parser(args.log_type, args.id, args.force)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting parser: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_get_command(args, chronicle):
    """Handle parser get command."""
    try:
        result = chronicle.get_parser(args.log_type, args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting parser: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_list_command(args, chronicle):
    """Handle parser list command."""
    try:
        result = chronicle.list_parsers(
            args.log_type, args.page_size, args.page_token, args.filter
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing parsers: {e}", file=sys.stderr)
        sys.exit(1)


def handle_parser_run_command(args, chronicle):
    """Handle parser run (evaluation) command."""
    try:
        # Read parser code
        parser_code = ""
        if args.parser_code_file:
            try:
                with open(args.parser_code_file, encoding="utf-8") as f:
                    parser_code = f.read()
            except OSError as e:
                print(f"Error reading parser code file: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.parser_code:
            parser_code = args.parser_code
        else:
            # If no parser code provided,
            # try to find an active parser for the log type
            parser_list_response = chronicle.list_parsers(
                args.log_type,
                page_size=1,
                filter="STATE=ACTIVE",
            )
            parsers = parser_list_response.get("parsers", [])
            if len(parsers) < 1:
                raise SecOpsError(
                    "No parser file provided and an active parser could not "
                    f"be found for log type '{args.log_type}'."
                )
            parser_code_encoded = parsers[0].get("cbn")
            parser_code = base64.b64decode(parser_code_encoded).decode("utf-8")

        # Read parser extension code (optional)
        parser_extension_code = ""
        if args.parser_extension_code_file:
            try:
                with open(
                    args.parser_extension_code_file, encoding="utf-8"
                ) as f:
                    parser_extension_code = f.read()
            except OSError as e:
                print(
                    f"Error reading parser extension code file: {e}",
                    file=sys.stderr,
                )
                sys.exit(1)
        elif args.parser_extension_code:
            parser_extension_code = args.parser_extension_code

        # Read logs
        logs = []
        if args.logs_file:
            try:
                with open(args.logs_file, encoding="utf-8") as f:
                    logs = [line.strip() for line in f if line.strip()]
            except OSError as e:
                print(f"Error reading logs file: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.log:
            logs = args.log

        if not logs:
            print(
                "Error: No logs provided. Use --log or --logs-file to provide "
                "log entries.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Call the API
        result = chronicle.run_parser(
            args.log_type,
            parser_code,
            parser_extension_code,
            logs,
            args.statedump_allowed,
        )

        output_formatter(result, args.output)

    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error running parser: {e}", file=sys.stderr)
        sys.exit(1)
