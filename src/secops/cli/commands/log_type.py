# Copyright 2026 Google LLC
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
"""CLI for ParserValidationToolingService under Log Type command group"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.exceptions import APIError, SecOpsError


def setup_log_type_commands(subparsers):
    """Set up the log_type service commands for Parser Validation."""
    log_type_parser = subparsers.add_parser(
        "log-type",
        help="Log Type related operations (including Parser Validation)",
    )

    log_type_subparsers = log_type_parser.add_subparsers(
        title="Log Type Commands",
        dest="log_type_command",
        help="Log Type sub-command to execute",
    )

    if sys.version_info >= (3, 7):
        log_type_subparsers.required = True

    log_type_parser.set_defaults(
        func=lambda args, chronicle: log_type_parser.print_help()
    )

    # --- trigger-checks command ---
    trigger_github_checks_parser = log_type_subparsers.add_parser(
        "trigger-checks", help="Trigger GitHub checks for a parser"
    )
    trigger_github_checks_parser.add_argument(
        "--associated-pr",
        "--associated_pr",
        required=True,
        help='The PR string (e.g., "owner/repo/pull/123").',
    )
    trigger_github_checks_parser.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help='The string name of the LogType enum (e.g., "DUMMY_LOGTYPE").',
    )
    trigger_github_checks_parser.set_defaults(
        func=handle_trigger_checks_command
    )

    # --- get-analysis-report command ---
    get_report_parser = log_type_subparsers.add_parser(
        "get-analysis-report", help="Get a parser analysis report"
    )
    get_report_parser.add_argument(
        "--log-type",
        "--log_type",
        required=True,
        help="The log type of the parser.",
    )
    get_report_parser.add_argument(
        "--parser-id",
        "--parser_id",
        required=True,
        help="The ID of the parser.",
    )
    get_report_parser.add_argument(
        "--report-id",
        "--report_id",
        required=True,
        help="The ID of the analysis report.",
    )
    get_report_parser.set_defaults(func=handle_get_analysis_report_command)


def handle_trigger_checks_command(args, chronicle):
    """Handle trigger checks command."""
    try:
        result = chronicle.trigger_github_checks(
            associated_pr=args.associated_pr,
            log_type=args.log_type,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except SecOpsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error triggering GitHub checks: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_analysis_report_command(args, chronicle):
    """Handle get analysis report command."""
    try:
        result = chronicle.get_analysis_report(
            log_type=args.log_type,
            parser_id=args.parser_id,
            report_id=args.report_id,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except SecOpsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error fetching analysis report: {e}", file=sys.stderr)
        sys.exit(1)
