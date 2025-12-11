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
"""Google SecOps CLI entity commands"""

import json
import sys

from secops.cli.utils.common_args import add_time_range_args
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.time_utils import get_time_range


def setup_entity_command(subparsers):
    """Set up the entity command parser."""
    entity_parser = subparsers.add_parser(
        "entity", help="Get entity information"
    )

    # A subparser object
    entity_subparsers = entity_parser.add_subparsers(
        dest="entity_subcommand", help="Entity subcommands"
    )

    entity_parser.add_argument(
        "--value", help="Entity value (IP, domain, hash, etc.)"
    )
    entity_parser.add_argument(
        "--entity-type",
        "--entity_type",
        dest="entity_type",
        help="Entity type hint",
    )
    add_time_range_args(entity_parser)
    entity_parser.set_defaults(func=handle_entity_command)

    # Ingest entities command as a subcommand
    entities_import_parser = entity_subparsers.add_parser(
        "import", help="Import entities"
    )
    entities_import_parser.add_argument(
        "--file",
        required=True,
        help="File containing entity(s) (in JSON format)",
    )
    entities_import_parser.add_argument(
        "--type", required=True, help="Log type"
    )
    entities_import_parser.set_defaults(func=handle_import_entities_command)


def handle_entity_command(args, chronicle):
    """Handle the entity command."""

    # If a subcommand is specified, this function should not be called.
    # However, if it is called with a subcommand, we should exit gracefully.
    if hasattr(args, "entity_subcommand") and args.entity_subcommand:
        print(
            "Error: Unexpected command handling for subcommand "
            f"{args.entity_subcommand}",
            file=sys.stderr,
        )
        sys.exit(1)

    # If no subcommand, --value is required
    if not args.value:
        print(
            "Error: --value is required when using the entity "
            "command without a subcommand",
            file=sys.stderr,
        )
        sys.exit(1)

    start_time, end_time = get_time_range(args)

    try:
        result = chronicle.summarize_entity(
            value=args.value,
            start_time=start_time,
            end_time=end_time,
            preferred_entity_type=args.entity_type,
        )

        # Handle alert_counts properly - could be different types based on API
        alert_counts_list = []
        if result.alert_counts:
            for ac in result.alert_counts:
                # Try different methods to convert to dict
                try:
                    if hasattr(ac, "_asdict"):
                        alert_counts_list.append(ac._asdict())
                    elif hasattr(ac, "__dict__"):
                        alert_counts_list.append(vars(ac))
                    else:
                        # If it's already a dict or another type, just use it
                        alert_counts_list.append(ac)
                except Exception:  # pylint: disable=broad-exception-caught
                    # If all conversion attempts fail, use string representation
                    alert_counts_list.append(str(ac))

        # Safely handle prevalence data which may not be available for
        # all entity types
        prevalence_list = []
        if result.prevalence:
            try:
                prevalence_list = [vars(p) for p in result.prevalence]
            except (
                Exception  # pylint: disable=broad-exception-caught
            ) as prev_err:
                print(
                    f"Warning: Unable to process prevalence data: {prev_err}",
                    file=sys.stderr,
                )

        # Convert the EntitySummary to a dictionary for output
        result_dict = {
            "primary_entity": result.primary_entity,
            "related_entities": result.related_entities,
            "alert_counts": alert_counts_list,
            "timeline": vars(result.timeline) if result.timeline else None,
            "prevalence": prevalence_list,
        }
        output_formatter(result_dict, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        if "Unsupported artifact type" in str(e):
            print(
                f"Error: The entity type for '{args.value}' is not supported. "
                "Try specifying a different entity type with --entity-type.",
                file=sys.stderr,
            )
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_import_entities_command(args, chronicle):
    """Handle import entities command."""
    try:
        with open(args.file, encoding="utf-8") as f:
            entities = json.load(f)

        result = chronicle.import_entities(
            entities=entities, log_type=args.type
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
