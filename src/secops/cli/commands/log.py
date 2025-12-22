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
"""Google SecOps CLI log commands"""

import json
import sys

from secops.cli.utils.formatters import output_formatter


def setup_log_command(subparsers):
    """Set up the log command parser."""
    log_parser = subparsers.add_parser("log", help="Ingest logs")
    log_subparsers = log_parser.add_subparsers(help="Log command")
    log_parser.set_defaults(func=lambda args, _: log_parser.print_help())

    # Ingest log command
    ingest_parser = log_subparsers.add_parser("ingest", help="Ingest raw logs")
    ingest_parser.add_argument("--type", required=True, help="Log type")
    ingest_parser.add_argument("--file", help="File containing log data")
    ingest_parser.add_argument(
        "--message", help="Log message (alternative to file)"
    )
    ingest_parser.add_argument(
        "--forwarder-id",
        "--forwarder_id",
        dest="forwarder_id",
        help="Custom forwarder ID",
    )
    ingest_parser.add_argument(
        "--force", action="store_true", help="Force unknown log type"
    )
    ingest_parser.add_argument(
        "--labels",
        help="JSON string or comma-separated key=value pairs for custom labels",
    )
    ingest_parser.set_defaults(func=handle_log_ingest_command)

    # Ingest UDM command
    udm_parser = log_subparsers.add_parser(
        "ingest-udm", help="Ingest UDM events"
    )
    udm_parser.add_argument(
        "--file", required=True, help="File containing UDM event(s)"
    )
    udm_parser.set_defaults(func=handle_udm_ingest_command)

    # List log types command
    types_parser = log_subparsers.add_parser(
        "types", help="List available log types"
    )
    types_parser.add_argument("--search", help="Search term for log types")
    types_parser.add_argument(
        "--page-size",
        "--page_size",
        dest="page_size",
        type=int,
        help="Number of results per page (fetches single page only)",
    )
    types_parser.add_argument(
        "--page-token",
        "--page_token",
        dest="page_token",
        help="Page token for pagination",
    )
    types_parser.set_defaults(func=handle_log_types_command)

    generate_udm_mapping_parser = log_subparsers.add_parser(
        "generate-udm-mapping", help="Generate UDM mapping"
    )
    generate_udm_mapping_parser.add_argument(
        "--log-format", "--log_format", dest="log_format", help="Log format"
    )
    udm_log_group = generate_udm_mapping_parser.add_mutually_exclusive_group()
    udm_log_group.add_argument("--log", help="Sample log content as a string")
    udm_log_group.add_argument(
        "--log-file",
        "--log_file",
        help="Path to file containing sample log content",
    )
    generate_udm_mapping_parser.add_argument(
        "--use-array-bracket-notation",
        "--use_array_bracket_notation",
        choices=["true", "false"],
        dest="use_array_bracket_notation",
        help="Use array bracket notation",
    )
    generate_udm_mapping_parser.add_argument(
        "--compress-array-fields",
        "--compress_array_fields",
        choices=["true", "false"],
        dest="compress_array_fields",
        help="Compress array fields",
    )
    generate_udm_mapping_parser.set_defaults(
        func=handle_generate_udm_mapping_command
    )


def handle_log_ingest_command(args, chronicle):
    """Handle log ingestion command."""
    try:
        log_message = args.message
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                log_message = f.read()

        # Process labels if provided
        labels = None
        if args.labels:
            # Try parsing as JSON first
            try:
                labels = json.loads(args.labels)
            except json.JSONDecodeError:
                # If not valid JSON, try parsing as comma-separated
                # key=value pairs
                labels = {}
                for pair in args.labels.split(","):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        labels[key.strip()] = value.strip()
                    else:
                        print(
                            f"Warning: Ignoring invalid label format: {pair}",
                            file=sys.stderr,
                        )

                if not labels:
                    print(
                        "Warning: No valid labels found. Labels should be in "
                        "JSON format or comma-separated key=value pairs.",
                        file=sys.stderr,
                    )

        result = chronicle.ingest_log(
            log_type=args.type,
            log_message=log_message,
            forwarder_id=args.forwarder_id,
            force_log_type=args.force,
            labels=labels,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_udm_ingest_command(args, chronicle):
    """Handle UDM ingestion command."""
    try:
        with open(args.file, encoding="utf-8") as f:
            udm_events = json.load(f)

        result = chronicle.ingest_udm(udm_events=udm_events)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_log_types_command(args, chronicle):
    """Handle listing log types command."""
    try:
        page_size = getattr(args, "page_size", None)
        page_token = getattr(args, "page_token", None)

        if args.search:
            # Search always fetches all log types for complete results
            if page_size or page_token:
                print(
                    "Warning: Pagination params are ignored for search. "
                    "Search operates on all log types.",
                    file=sys.stderr,
                )
            result = chronicle.search_log_types(args.search)
        else:
            result = chronicle.get_all_log_types(
                page_size=page_size,
                page_token=page_token,
            )

        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_generate_udm_mapping_command(args, chronicle):
    """Handle generate UDM mapping command."""
    try:
        log = ""
        if args.log_file:
            with open(args.log_file, encoding="utf-8") as f:
                log = f.read()
        elif args.log:
            log = args.log
        else:
            print("Error: log or log_file must be specified", file=sys.stderr)
            sys.exit(1)

        result = chronicle.generate_udm_key_value_mappings(
            log_format=args.log_format,
            log=log,
            use_array_bracket_notation=args.use_array_bracket_notation,
            compress_array_fields=args.compress_array_fields,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
