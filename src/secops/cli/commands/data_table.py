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
"""Google SecOps CLI data table commands"""

import json
import sys

from secops.chronicle.data_table import DataTableColumnType
from secops.cli.utils.formatters import output_formatter


def setup_data_table_command(subparsers):
    """Set up the data table command parser."""
    dt_parser = subparsers.add_parser("data-table", help="Manage data tables")
    dt_subparsers = dt_parser.add_subparsers(
        dest="dt_command", help="Data table command"
    )
    dt_parser.set_defaults(func=lambda args, _: dt_parser.print_help())

    # List data tables command
    list_parser = dt_subparsers.add_parser("list", help="List data tables")
    list_parser.add_argument(
        "--order-by",
        "--order_by",
        dest="order_by",
        help="Order by field (only 'createTime asc' is supported)",
    )
    list_parser.set_defaults(func=handle_dt_list_command)

    # Get data table command
    get_parser = dt_subparsers.add_parser("get", help="Get data table details")
    get_parser.add_argument("--name", required=True, help="Data table name")
    get_parser.set_defaults(func=handle_dt_get_command)

    # Create data table command
    create_parser = dt_subparsers.add_parser(
        "create", help="Create a data table"
    )
    create_parser.add_argument("--name", required=True, help="Data table name")
    create_parser.add_argument(
        "--description", required=True, help="Data table description"
    )
    create_parser.add_argument(
        "--header",
        required=True,
        help=(
            "Header definition in JSON format. "
            'Example: \'{"col1":"STRING","col2":"CIDR"}\' or '
            'Example: \'{"col1":"entity.asset.ip","col2":"CIDR"}\''
        ),
    )
    create_parser.add_argument(
        "--column-options",
        "--column_options",
        help=(
            "Column options in JSON format. "
            'Example: \'{"col1":{"repeatedValues":true},'
            '"col2":{"keyColumns":true}}\''
        ),
    )

    create_parser.add_argument(
        "--rows",
        help=(
            'Rows in JSON format. Example: \'[["value1","192.168.1.0/24"],'
            '["value2","10.0.0.0/8"]]\''
        ),
    )
    create_parser.add_argument(
        "--scopes", help="Comma-separated list of scopes"
    )
    create_parser.set_defaults(func=handle_dt_create_command)

    # Delete data table command
    delete_parser = dt_subparsers.add_parser(
        "delete", help="Delete a data table"
    )
    delete_parser.add_argument("--name", required=True, help="Data table name")
    delete_parser.add_argument(
        "--force",
        action="store_true",
        help="Force deletion even if table has rows",
    )
    delete_parser.set_defaults(func=handle_dt_delete_command)

    # List rows command
    list_rows_parser = dt_subparsers.add_parser(
        "list-rows", help="List data table rows"
    )
    list_rows_parser.add_argument(
        "--name", required=True, help="Data table name"
    )
    list_rows_parser.add_argument(
        "--order-by",
        "--order_by",
        dest="order_by",
        help="Order by field (only 'createTime asc' is supported)",
    )
    list_rows_parser.set_defaults(func=handle_dt_list_rows_command)

    # Add rows command
    add_rows_parser = dt_subparsers.add_parser(
        "add-rows", help="Add rows to a data table"
    )
    add_rows_parser.add_argument(
        "--name", required=True, help="Data table name"
    )
    add_rows_parser.add_argument(
        "--rows",
        required=True,
        help=(
            'Rows in JSON format. Example: \'[["value1","192.168.1.0/24"],'
            '["value2","10.0.0.0/8"]]\''
        ),
    )
    add_rows_parser.set_defaults(func=handle_dt_add_rows_command)

    # Delete rows command
    delete_rows_parser = dt_subparsers.add_parser(
        "delete-rows", help="Delete rows from a data table"
    )
    delete_rows_parser.add_argument(
        "--name", required=True, help="Data table name"
    )
    delete_rows_parser.add_argument(
        "--row-ids",
        "--row_ids",
        dest="row_ids",
        required=True,
        help="Comma-separated list of row IDs",
    )
    delete_rows_parser.set_defaults(func=handle_dt_delete_rows_command)

    # Update data table command
    update_parser = dt_subparsers.add_parser(
        "update", help="Update a data table"
    )
    update_parser.add_argument("--name", required=True, help="Data table name")
    update_parser.add_argument(
        "--description", help="New data table description"
    )
    update_parser.add_argument(
        "--row-time-to-live",
        "--row_time_to_live",
        dest="row_time_to_live",
        help="New row time to live (e.g., '24h', '7d')",
    )
    update_parser.set_defaults(func=handle_dt_update_command)

    # Replace rows command
    replace_rows_parser = dt_subparsers.add_parser(
        "replace-rows", help="Replace all rows in a data table with new rows"
    )
    replace_rows_parser.add_argument(
        "--name", required=True, help="Data table name"
    )
    replace_rows_group = replace_rows_parser.add_mutually_exclusive_group(
        required=True
    )
    replace_rows_group.add_argument(
        "--rows",
        help=(
            "Rows as a JSON array of arrays. Example: "
            '\'[["value1","192.168.1.1"],'
            '["value2","10.0.0.0/8"]]\''
        ),
    )
    replace_rows_group.add_argument(
        "--rows-file",
        "--rows_file",
        help="Path to a JSON file containing rows as an array of arrays",
    )
    replace_rows_parser.set_defaults(func=handle_dt_replace_rows_command)

    # Update rows command
    update_rows_parser = dt_subparsers.add_parser(
        "update-rows", help="Update existing rows in a data table"
    )
    update_rows_parser.add_argument(
        "--name", required=True, help="Data table name"
    )
    update_rows_group = update_rows_parser.add_mutually_exclusive_group(
        required=True
    )
    update_rows_group.add_argument(
        "--rows",
        help=(
            "Row updates as a JSON array of objects. Each object must have "
            "'name' (full resource name) and 'values' (array of strings). "
            "Optional: 'update_mask' (comma-separated fields). Example: "
            '[{"name":"projects/.../dataTableRows/row1",'
            '"values":["val1","val2"],"update_mask":"values"}]'
        ),
    )
    update_rows_group.add_argument(
        "--rows-file",
        "--rows_file",
        dest="rows_file",
        help=(
            "Path to a JSON file containing row updates as an array "
            "of objects"
        ),
    )
    update_rows_parser.set_defaults(func=handle_dt_update_rows_command)


def handle_dt_list_command(args, chronicle):
    """Handle data table list command."""
    try:
        order_by = (
            args.order_by
            if hasattr(args, "order_by") and args.order_by
            else None
        )
        result = chronicle.list_data_tables(order_by=order_by)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_get_command(args, chronicle):
    """Handle data table get command."""
    try:
        result = chronicle.get_data_table(args.name)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_create_command(args, chronicle):
    """Handle data table create command."""
    try:
        # Parse header
        try:
            header_dict = json.loads(args.header)
            # Convert string values to DataTableColumnType enum
            header = {k: DataTableColumnType[v] for k, v in header_dict.items()}
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing header: {e}", file=sys.stderr)
            print(
                "Header should be a JSON object mapping column names to types "
                "(STRING, REGEX, CIDR) or entity mapping.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Parse column options if provided
        column_options = None
        if args.column_options:
            try:
                column_options = json.loads(args.column_options)
            except json.JSONDecodeError as e:
                print(f"Error parsing column options: {e}", file=sys.stderr)
                print(
                    "Column options should be a JSON object.", file=sys.stderr
                )
                sys.exit(1)

        # Parse rows if provided
        rows = None
        if args.rows:
            try:
                rows = json.loads(args.rows)
            except json.JSONDecodeError as e:
                print(f"Error parsing rows: {e}", file=sys.stderr)
                print("Rows should be a JSON array of arrays.", file=sys.stderr)
                sys.exit(1)

        # Parse scopes if provided
        scopes = None
        if args.scopes:
            scopes = [s.strip() for s in args.scopes.split(",")]

        result = chronicle.create_data_table(
            name=args.name,
            description=args.description,
            header=header,
            column_options=column_options,
            rows=rows,
            scopes=scopes,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_delete_command(args, chronicle):
    """Handle data table delete command."""
    try:
        result = chronicle.delete_data_table(args.name, force=args.force)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_list_rows_command(args, chronicle):
    """Handle data table list rows command."""
    try:
        order_by = (
            args.order_by
            if hasattr(args, "order_by") and args.order_by
            else None
        )
        result = chronicle.list_data_table_rows(args.name, order_by=order_by)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_add_rows_command(args, chronicle):
    """Handle data table add rows command."""
    try:
        try:
            rows = json.loads(args.rows)
        except json.JSONDecodeError as e:
            print(f"Error parsing rows: {e}", file=sys.stderr)
            print("Rows should be a JSON array of arrays.", file=sys.stderr)
            sys.exit(1)

        result = chronicle.create_data_table_rows(args.name, rows)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_delete_rows_command(args, chronicle):
    """Handle data table delete rows command."""
    try:
        row_ids = [id.strip() for id in args.row_ids.split(",")]
        result = chronicle.delete_data_table_rows(args.name, row_ids)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_replace_rows_command(args, chronicle):
    """Handle data table replace rows command.

    Replaces all rows in a data table with new rows from JSON input.
    """
    try:
        # Parse rows from either JSON string or file
        rows = None
        if args.rows:
            try:
                rows = json.loads(args.rows)
            except json.JSONDecodeError as e:
                print(f"Error parsing rows: {e}", file=sys.stderr)
                print("Rows should be a JSON array of arrays.", file=sys.stderr)
                sys.exit(1)
        elif args.rows_file:
            try:
                with open(args.rows_file, encoding="utf-8") as f:
                    rows = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading from file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Either --rows or --file must be specified", file=sys.stderr)
            sys.exit(1)

        result = chronicle.replace_data_table_rows(args.name, rows)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_update_command(args, chronicle):
    """Handle data table update command.

    Args:
        args: Command line arguments
        chronicle: Chronicle client
    """
    try:
        # Determine which fields need to be updated based on provided arguments
        update_mask = []
        if args.description is not None:
            update_mask.append("description")
        if args.row_time_to_live is not None:
            update_mask.append("row_time_to_live")

        # If no fields were specified, inform the user
        if not update_mask:
            print(
                "Error: At least one of --description or --row-time-to-live "
                "must be specified",
                file=sys.stderr,
            )
            sys.exit(1)

        # Call the API to update the data table
        result = chronicle.update_data_table(
            name=args.name,
            description=args.description,
            row_time_to_live=args.row_time_to_live,
            update_mask=update_mask,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dt_update_rows_command(args, chronicle):
    """Handle data table update rows command.

    Updates existing rows in a data table using their full resource names.

    Args:
        args: Command line arguments
        chronicle: Chronicle client
    """
    try:
        # Parse row updates from either JSON string or file
        row_updates = None
        if args.rows:
            try:
                row_updates = json.loads(args.rows)
            except json.JSONDecodeError as e:
                print(f"Error parsing row updates: {e}", file=sys.stderr)
                print(
                    "Row updates should be a JSON array of objects.",
                    file=sys.stderr,
                )
                sys.exit(1)
        elif args.rows_file:
            try:
                with open(args.rows_file, encoding="utf-8") as f:
                    row_updates = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading from file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(
                "Error: Either --rows or --rows-file " "must be specified",
                file=sys.stderr,
            )
            sys.exit(1)

        # Validate row updates structure
        if not isinstance(row_updates, list):
            print(
                "Error: Row updates must be an array of objects",
                file=sys.stderr,
            )
            sys.exit(1)

        result = chronicle.update_data_table_rows(
            name=args.name, row_updates=row_updates
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
