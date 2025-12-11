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
"""Google SecOps CLI forwarder commands"""

import json
import sys

from secops.cli.utils.common_args import add_pagination_args
from secops.exceptions import APIError


def setup_forwarder_command(subparsers):
    """Set up the forwarder command parser."""
    forwarder_parser = subparsers.add_parser(
        "forwarder", help="Manage log forwarders"
    )
    forwarder_subparsers = forwarder_parser.add_subparsers(
        dest="forwarder_command", help="Forwarder command"
    )
    forwarder_parser.set_defaults(
        func=lambda args, _: forwarder_parser.print_help()
    )

    # Create forwarder command
    create_parser = forwarder_subparsers.add_parser(
        "create", help="Create a new forwarder"
    )
    create_parser.add_argument(
        "--display-name",
        "--display_name",
        dest="display_name",
        required=True,
        help="Display name for the new forwarder",
    )
    create_parser.add_argument(
        "--metadata", help="JSON string of metadata to attach to the forwarder"
    )
    create_parser.add_argument(
        "--upload-compression",
        "--upload_compression",
        dest="upload_compression",
        choices=["true", "false"],
        help="Enable upload compression",
    )
    create_parser.add_argument(
        "--enable-server",
        "--enable_server",
        dest="enable_server",
        choices=["true", "false"],
        help="Enable server functionality on the forwarder",
    )
    create_parser.add_argument(
        "--regex-filters",
        "--regex_filters",
        dest="regex_filters",
        help="JSON string of regex filters to apply at the forwarder level",
    )
    create_parser.add_argument(
        "--graceful-timeout",
        "--graceful_timeout",
        dest="graceful_timeout",
        help="Timeout after which the forwarder returns a bad readiness check",
    )
    create_parser.add_argument(
        "--drain-timeout",
        "--drain_timeout",
        dest="drain_timeout",
        help="Timeout after which the forwarder waits for connections to close",
    )
    create_parser.add_argument(
        "--http-settings",
        "--http_settings",
        dest="http_settings",
        help="JSON string of HTTP-specific server settings",
    )
    create_parser.set_defaults(func=handle_forwarder_create_command)

    # Update forwarder command
    patch_parser = forwarder_subparsers.add_parser(
        "update", help="Update an existing forwarder"
    )
    patch_parser.add_argument(
        "--id", required=True, help="ID of the forwarder to update"
    )
    patch_parser.add_argument(
        "--display-name",
        "--display_name",
        dest="display_name",
        help="New display name for the forwarder",
    )
    patch_parser.add_argument(
        "--metadata", help="JSON string of metadata to attach to the forwarder"
    )
    patch_parser.add_argument(
        "--upload-compression",
        "--upload_compression",
        dest="upload_compression",
        choices=["true", "false"],
        help="Whether uploaded data should be compressed",
    )
    patch_parser.add_argument(
        "--enable-server",
        "--enable_server",
        dest="enable_server",
        choices=["true", "false"],
        help="Enable server functionality on the forwarder",
    )
    patch_parser.add_argument(
        "--regex-filters",
        "--regex_filters",
        dest="regex_filters",
        help="JSON string of regex filters to apply at the forwarder level",
    )
    patch_parser.add_argument(
        "--graceful-timeout",
        "--graceful_timeout",
        dest="graceful_timeout",
        help="Timeout after which the forwarder returns a bad readiness check",
    )
    patch_parser.add_argument(
        "--drain-timeout",
        "--drain_timeout",
        dest="drain_timeout",
        help="Timeout after which the forwarder waits for connections to close",
    )
    patch_parser.add_argument(
        "--http-settings",
        "--http_settings",
        dest="http_settings",
        help="JSON string of HTTP-specific server settings",
    )
    patch_parser.add_argument(
        "--update-mask",
        "--update_mask",
        dest="update_mask",
        help="Comma-separated list of field paths to update",
    )
    patch_parser.set_defaults(func=handle_forwarder_patch_command)

    # List forwarders command
    list_parser = forwarder_subparsers.add_parser(
        "list", help="List all forwarders"
    )
    add_pagination_args(list_parser)
    list_parser.set_defaults(func=handle_forwarder_list_command)

    # Get forwarder command
    get_parser = forwarder_subparsers.add_parser(
        "get", help="Get details of a specific forwarder"
    )
    get_parser.add_argument(
        "--id", required=True, help="ID of the forwarder to retrieve"
    )
    get_parser.set_defaults(func=handle_forwarder_get_command)

    # Get or create forwarder command
    get_or_create_parser = forwarder_subparsers.add_parser(
        "get-or-create", help="Get an existing forwarder or create a new one"
    )
    get_or_create_parser.add_argument(
        "--display-name",
        "--display_name",
        dest="display_name",
        default="Wrapper-SDK-Forwarder",
        help="Display name to find or create (default: Wrapper-SDK-Forwarder)",
    )
    get_or_create_parser.set_defaults(
        func=handle_forwarder_get_or_create_command
    )

    # Delete forwarder command
    delete_parser = forwarder_subparsers.add_parser(
        "delete", help="Delete a specific forwarder"
    )
    delete_parser.add_argument(
        "--id", required=True, help="ID of the forwarder to delete"
    )
    delete_parser.set_defaults(func=handle_forwarder_delete_command)


def handle_forwarder_create_command(args, chronicle):
    """Handle creating a new forwarder."""
    try:
        # Parse JSON strings into Python objects
        metadata = None
        regex_filters = None
        http_settings = None

        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("Error: Metadata must be valid JSON", file=sys.stderr)
                sys.exit(1)

        if args.regex_filters:
            try:
                regex_filters = json.loads(args.regex_filters)
            except json.JSONDecodeError:
                print(
                    "Error: Regex filters must be valid JSON", file=sys.stderr
                )
                sys.exit(1)

        if args.http_settings:
            try:
                http_settings = json.loads(args.http_settings)
            except json.JSONDecodeError:
                print(
                    "Error: HTTP settings must be valid JSON", file=sys.stderr
                )
                sys.exit(1)

        # Convert string values to appropriate types
        upload_compression = None
        if args.upload_compression:
            upload_compression = args.upload_compression.lower() == "true"

        enable_server = None
        if args.enable_server:
            enable_server = args.enable_server.lower() == "true"

        result = chronicle.create_forwarder(
            display_name=args.display_name,
            metadata=metadata,
            upload_compression=upload_compression,
            enable_server=enable_server,
            regex_filters=regex_filters,
            graceful_timeout=args.graceful_timeout,
            drain_timeout=args.drain_timeout,
            http_settings=http_settings,
        )

        print(json.dumps(result, indent=2))
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_forwarder_list_command(args, chronicle):
    """Handle listing all forwarders."""
    try:
        result = chronicle.list_forwarders(
            page_size=args.page_size, page_token=args.page_token
        )
        print(json.dumps(result, indent=2))
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_forwarder_get_command(args, chronicle):
    """Handle getting a specific forwarder."""
    try:
        result = chronicle.get_forwarder(forwarder_id=args.id)
        print(json.dumps(result, indent=2))
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_forwarder_get_or_create_command(args, chronicle):
    """Handle getting or creating a forwarder."""
    try:
        result = chronicle.get_or_create_forwarder(
            display_name=args.display_name
        )
        print(json.dumps(result, indent=2))
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting query: {e}", file=sys.stderr)
        sys.exit(1)


def handle_forwarder_patch_command(args, chronicle):
    """Handle updating an existing forwarder."""
    try:
        # Process metadata if provided
        metadata = None
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print(
                    f"Error: Invalid JSON in metadata: {args.metadata}",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Process regex filters if provided
        regex_filters = None
        if args.regex_filters:
            try:
                regex_filters = json.loads(args.regex_filters)
            except json.JSONDecodeError:
                print(
                    "Error: Invalid JSON in regex_filters: "
                    f"{args.regex_filters}",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Process HTTP settings if provided
        http_settings = None
        if args.http_settings:
            try:
                http_settings = json.loads(args.http_settings)
            except json.JSONDecodeError:
                print(
                    "Error: Invalid JSON in http_settings: "
                    f"{args.http_settings}",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Process boolean flags
        upload_compression = None
        if args.upload_compression:
            upload_compression = args.upload_compression.lower() == "true"

        enable_server = None
        if args.enable_server:
            enable_server = args.enable_server.lower() == "true"

        # Process update_mask
        update_mask = None
        if args.update_mask:
            update_mask = [
                field.strip() for field in args.update_mask.split(",")
            ]

        result = chronicle.update_forwarder(
            forwarder_id=args.id,
            display_name=args.display_name,
            metadata=metadata,
            upload_compression=upload_compression,
            enable_server=enable_server,
            regex_filters=regex_filters,
            graceful_timeout=args.graceful_timeout,
            drain_timeout=args.drain_timeout,
            http_settings=http_settings,
            update_mask=update_mask,
        )
        print(json.dumps(result, indent=2))
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error patching forwarder: {e}", file=sys.stderr)
        sys.exit(1)


def handle_forwarder_delete_command(args, chronicle):
    """Handle deleting a specific forwarder."""
    try:
        chronicle.delete_forwarder(forwarder_id=args.id)
        print(
            json.dumps(
                {
                    "success": True,
                    "message": f"Forwarder {args.id} deleted successfully",
                },
                indent=2,
            )
        )
    except APIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting forwarder: {e}", file=sys.stderr)
        sys.exit(1)
