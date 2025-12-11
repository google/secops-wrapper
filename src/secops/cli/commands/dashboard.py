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
"""Google SecOps CLI dashboard commands"""

import json
import sys

from secops.cli.utils.common_args import add_pagination_args
from secops.cli.utils.formatters import output_formatter
from secops.exceptions import APIError, SecOpsError


def setup_dashboard_command(subparsers):
    """Set up dashboard commands."""
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Manage Chronicle dashboards"
    )
    dashboard_subparsers = dashboard_parser.add_subparsers(
        dest="dashboard_command",
        help="Dashboard command to execute",
    )
    dashboard_parser.set_defaults(
        func=lambda args, _: dashboard_parser.print_help()
    )

    # List dashboards
    list_parser = dashboard_subparsers.add_parser(
        "list", help="List dashboards"
    )
    add_pagination_args(list_parser)
    list_parser.set_defaults(func=handle_dashboard_list_command)

    # Get dashboard
    get_parser = dashboard_subparsers.add_parser(
        "get", help="Get dashboard details"
    )
    get_parser.add_argument(
        "--dashboard-id",
        "--dashboard_id",
        help="Dashboard ID",
        required=True,
    )
    get_parser.add_argument(
        "--view", help="Dashboard view", choices=["BASIC", "FULL"]
    )
    get_parser.set_defaults(func=handle_dashboard_get_command)

    # Create dashboard
    create_parser = dashboard_subparsers.add_parser(
        "create", help="Create a new dashboard"
    )
    create_parser.add_argument(
        "--display-name",
        "--display_name",
        required=True,
        help="Dashboard display name",
    )
    create_parser.add_argument("--description", help="Dashboard description")
    create_parser.add_argument(
        "--access-type",
        "--access_type",
        choices=["PRIVATE", "PUBLIC"],
        required=True,
        help="Dashboard access type",
    )
    filters_group = create_parser.add_mutually_exclusive_group()
    filters_group.add_argument(
        "--filters",
        "--filters",
        help="List of filters to apply to the dashboard",
    )
    filters_group.add_argument(
        "--filters-file",
        "--filters_file",
        help="File containing list of filters to apply to the dashboard",
    )
    charts_group = create_parser.add_mutually_exclusive_group()
    charts_group.add_argument(
        "--charts",
        "--charts",
        help="List of charts to include in the dashboard",
    )
    charts_group.add_argument(
        "--charts-file",
        "--charts_file",
        help="File containing list of charts to include in the dashboard",
    )
    create_parser.set_defaults(func=handle_dashboard_create_command)

    # Update Dashboard
    create_parser = dashboard_subparsers.add_parser(
        "update", help="Update an existing dashboard"
    )
    create_parser.add_argument(
        "--dashboard-id",
        "--dashboard_id",
        required=True,
        help="Dashboard ID",
    )
    create_parser.add_argument(
        "--display-name",
        "--display_name",
        help="Updated Dashboard display name",
    )
    create_parser.add_argument("--description", help="Dashboard description")
    update_filters_group = create_parser.add_mutually_exclusive_group()
    update_filters_group.add_argument(
        "--filters",
        "--filters",
        help="List of filters to apply to the dashboard",
    )
    update_filters_group.add_argument(
        "--filters-file",
        "--filters_file",
        help="File containing list of filters to apply to the dashboard",
    )
    update_charts_group = create_parser.add_mutually_exclusive_group()
    update_charts_group.add_argument(
        "--charts",
        "--charts",
        help="List of charts to include in the dashboard",
    )
    update_charts_group.add_argument(
        "--charts-file",
        "--charts_file",
        help="File containing list of charts to include in the dashboard",
    )
    create_parser.set_defaults(func=handle_dashboard_update_command)

    # Delete Dashboard
    delete_parser = dashboard_subparsers.add_parser(
        "delete", help="Delete an existing dashboard"
    )
    delete_parser.add_argument(
        "--dashboard-id", "--dashboard_id", required=True, help="Dashboard ID"
    )
    delete_parser.set_defaults(func=handle_dashboard_delete_command)

    # Duplicate dashboard
    duplicate_parser = dashboard_subparsers.add_parser(
        "duplicate", help="Duplicate an existing dashboard"
    )
    duplicate_parser.add_argument(
        "--dashboard-id",
        "--dashboard_id",
        required=True,
        help="Source dashboard ID",
    )
    duplicate_parser.add_argument(
        "--display-name",
        "--display_name",
        required=True,
        help="New dashboard display name",
    )
    duplicate_parser.add_argument(
        "--description", help="New dashboard description"
    )
    duplicate_parser.add_argument(
        "--access-type",
        "--access_type",
        choices=["PRIVATE", "PUBLIC"],
        required=True,
        help="New dashboard access type",
    )
    duplicate_parser.set_defaults(func=handle_dashboard_duplicate_command)

    # Add chart
    add_chart_parser = dashboard_subparsers.add_parser(
        "add-chart", help="Add a chart to a dashboard"
    )
    add_chart_parser.add_argument(
        "--dashboard-id", "--dashboard_id", help="Dashboard ID", required=True
    )
    add_chart_parser.add_argument(
        "--display-name",
        "--display_name",
        required=True,
        help="Chart display name",
    )
    add_chart_parser.add_argument("--description", help="Chart description")
    chart_layout_group = add_chart_parser.add_mutually_exclusive_group(
        required=True
    )
    chart_layout_group.add_argument(
        "--chart-layout",
        "--chart_layout",
        help="Chart layout in JSON string",
    )
    chart_layout_group.add_argument(
        "--chart-layout-file",
        "--chart_layout_file",
        help="File containing chart layout in JSON string",
    )
    query_group = add_chart_parser.add_mutually_exclusive_group()
    query_group.add_argument("--query", help="Query for the chart")
    query_group.add_argument(
        "--query-file",
        "--query_file",
        help="File containing query for the chart",
    )
    add_chart_parser.add_argument(
        "--interval", help="Time interval JSON string"
    )
    add_chart_parser.add_argument(
        "--tile-type",
        "--tile_type",
        choices=["VISUALIZATION", "BUTTON"],
        help="Tile type for the chart",
        required=True,
    )
    chart_datasource_group = add_chart_parser.add_mutually_exclusive_group()
    chart_datasource_group.add_argument(
        "--chart-datasource",
        "--chart_datasource",
        help="Chart datasource JSON string",
    )
    chart_datasource_group.add_argument(
        "--chart-datasource-file",
        "--chart_datasource_file",
        help="File containing chart datasource JSON string",
    )
    visualization_group = add_chart_parser.add_mutually_exclusive_group()
    visualization_group.add_argument(
        "--visualization",
        "--visualization",
        help="Visualization for the chart in JSON string",
    )
    visualization_group.add_argument(
        "--visualization-file",
        "--visualization_file",
        help="File containing visualization for the chart in JSON string",
    )
    drill_down_config_group = add_chart_parser.add_mutually_exclusive_group()
    drill_down_config_group.add_argument(
        "--drill-down-config",
        "--drill_down_config",
        help="Drill down configuration for the chart in JSON string",
    )
    drill_down_config_group.add_argument(
        "--drill-down-config-file",
        "--drill_down_config_file",
        help=(
            "File containing drill down configuration for "
            "the chart in JSON string"
        ),
    )
    add_chart_parser.set_defaults(func=handle_dashboard_add_chart_command)

    # Remove chart
    remove_chart_parser = dashboard_subparsers.add_parser(
        "remove-chart", help="Remove a chart from a dashboard"
    )
    remove_chart_parser.add_argument(
        "--dashboard-id", "--dashboard_id", help="Dashboard ID"
    )
    remove_chart_parser.add_argument(
        "--chart-id", "--chart_id", help="Chart ID to remove"
    )
    remove_chart_parser.set_defaults(func=handle_dashboard_remove_chart_command)

    # Get chart
    get_chart_parser = dashboard_subparsers.add_parser(
        "get-chart", help="Get a chart from a dashboard"
    )
    get_chart_parser.add_argument("--id", help="Chart ID to get")
    get_chart_parser.set_defaults(func=handle_dashboard_get_chart_command)

    # Edit Chart
    edit_chart_parser = dashboard_subparsers.add_parser(
        "edit-chart", help="Edit an existing chart in a dashboard"
    )
    edit_chart_parser.add_argument(
        "--dashboard-id", "--dashboard_id", help="Dashboard ID", required=True
    )
    dashboard_query_group = edit_chart_parser.add_mutually_exclusive_group()
    dashboard_query_group.add_argument(
        "--dashboard-query",
        "--dashboard_query",
        help="Dashboard query JSON string",
    )
    dashboard_query_group.add_argument(
        "--dashboard-query-from-file",
        "--dashboard_query_from_file",
        help="File containing dashboard query JSON string",
    )
    dashboard_chart_group = edit_chart_parser.add_mutually_exclusive_group()
    dashboard_chart_group.add_argument(
        "--dashboard-chart",
        "--dashboard_chart",
        help="Dashboard chart JSON string",
    )
    dashboard_chart_group.add_argument(
        "--dashboard-chart-from-file",
        "--dashboard_chart_from_file",
        help="File containing dashboard chart JSON string",
    )
    edit_chart_parser.set_defaults(func=handle_dashboard_edit_chart_command)

    # Import Dashboard
    import_dashboard_parser = dashboard_subparsers.add_parser(
        "import", help="Import a dashboard"
    )

    # Dashboard data arguments
    dashboard_data_group = import_dashboard_parser.add_mutually_exclusive_group(
        required=True
    )
    dashboard_data_group.add_argument(
        "--dashboard-data",
        "--dashboard_data",
        help="Dashboard data as JSON string",
    )
    dashboard_data_group.add_argument(
        "--dashboard-data-file",
        "--dashboard_data_file",
        help="File containing dashboard data in JSON format",
    )

    # Chart data arguments (optional)
    chart_data_group = import_dashboard_parser.add_mutually_exclusive_group()
    chart_data_group.add_argument(
        "--chart-data",
        "--chart_data",
        help="Dashboard chart data as JSON string",
    )
    chart_data_group.add_argument(
        "--chart-data-file",
        "--chart_data_file",
        help="File containing dashboard chart data in JSON format",
    )

    # Query data arguments (optional)
    query_data_group = import_dashboard_parser.add_mutually_exclusive_group()
    query_data_group.add_argument(
        "--query-data",
        "--query_data",
        help="Dashboard query data as JSON string",
    )
    query_data_group.add_argument(
        "--query-data-file",
        "--query_data_file",
        help="File containing dashboard query data in JSON format",
    )

    import_dashboard_parser.set_defaults(func=handle_dashboard_import_command)

    # Export Dashboard
    export_dashboard_parser = dashboard_subparsers.add_parser(
        "export", help="Export a dashboard"
    )

    # Dashboard data arguments
    export_dashboard_parser.add_argument(
        "--dashboard-names",
        "--dashboard_names",
        help="List of comma-separated dashboard names to export",
    )

    export_dashboard_parser.set_defaults(func=handle_dashboard_export_command)


def handle_dashboard_list_command(args, chronicle):
    """Handle list dashboards command."""
    try:
        result = chronicle.list_dashboards(
            page_size=args.page_size, page_token=args.page_token
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing dashboards: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_get_command(args, chronicle):
    """Handle get dashboard command."""
    try:
        result = chronicle.get_dashboard(
            dashboard_id=args.dashboard_id, view=args.view
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting dashboard: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_create_command(args, chronicle):
    """Handle create dashboard command."""
    try:
        filters = args.filters if args.filters else None
        charts = args.charts if args.charts else None
        if args.filters_file:
            with open(args.filters_file, encoding="utf-8") as f:
                filters = f.read()

        if args.charts_file:
            with open(args.charts_file, encoding="utf-8") as f:
                charts = f.read()

        result = chronicle.create_dashboard(
            display_name=args.display_name,
            access_type=args.access_type,
            description=args.description,
            filters=filters,
            charts=charts,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating dashboard: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_update_command(args, chronicle):
    """Handle update dashboard command."""
    try:
        filters = args.filters if args.filters else None
        charts = args.charts if args.charts else None
        if args.filters_file:
            try:
                with open(args.filters_file, encoding="utf-8") as f:
                    filters = f.read()
            except OSError as e:
                print(f"Error reading filters file: {e}", file=sys.stderr)
                sys.exit(1)

        if args.charts_file:
            try:
                with open(args.charts_file, encoding="utf-8") as f:
                    charts = f.read()
            except OSError as e:
                print(f"Error reading charts file: {e}", file=sys.stderr)
                sys.exit(1)

        result = chronicle.update_dashboard(
            dashboard_id=args.dashboard_id,
            display_name=args.display_name,
            description=args.description,
            filters=filters,
            charts=charts,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating dashboard: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_delete_command(args, chronicle):
    """Handle delete dashboard command."""
    try:
        result = chronicle.delete_dashboard(dashboard_id=args.dashboard_id)
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting dashboard: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_duplicate_command(args, chronicle):
    """Handle duplicate dashboard command."""
    try:
        result = chronicle.duplicate_dashboard(
            dashboard_id=args.dashboard_id,
            display_name=args.display_name,
            access_type=args.access_type,
            description=args.description,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error duplicating dashboard: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_add_chart_command(args, chronicle):
    """Handle add chart to dashboard command."""
    try:
        # Process query from file or argument
        query = args.query if args.query else None
        if args.query_file:
            try:
                with open(args.query_file, encoding="utf-8") as f:
                    query = f.read()
            except OSError as e:
                print(f"Error reading query file: {e}", file=sys.stderr)
                sys.exit(1)
        chart_layout = args.chart_layout if args.chart_layout else None
        if args.chart_layout_file:
            try:
                with open(args.chart_layout_file, encoding="utf-8") as f:
                    chart_layout = f.read()
            except OSError as e:
                print(f"Error reading chart layout file: {e}", file=sys.stderr)
                sys.exit(1)

        visualization = args.visualization if args.visualization else None
        if args.visualization_file:
            try:
                with open(args.visualization_file, encoding="utf-8") as f:
                    visualization = f.read()
            except OSError as e:
                print(f"Error reading visualization file: {e}", file=sys.stderr)
                sys.exit(1)

        drill_down_config = (
            args.drill_down_config if args.drill_down_config else None
        )
        if args.drill_down_config_file:
            try:
                with open(args.drill_down_config_file, encoding="utf-8") as f:
                    drill_down_config = f.read()
            except OSError as e:
                print(
                    f"Error reading drill down config file: {e}",
                    file=sys.stderr,
                )
                sys.exit(1)

        chart_datasource = (
            args.chart_datasource if args.chart_datasource else None
        )
        if args.chart_datasource_file:
            try:
                with open(args.chart_datasource_file, encoding="utf-8") as f:
                    chart_datasource = f.read()
            except OSError as e:
                print(
                    f"Error reading chart datasource file: {e}",
                    file=sys.stderr,
                )
                sys.exit(1)

        result = chronicle.add_chart(
            dashboard_id=args.dashboard_id,
            display_name=args.display_name,
            chart_layout=chart_layout,
            tile_type=args.tile_type,
            chart_datasource=chart_datasource,
            visualization=visualization,
            drill_down_config=drill_down_config,
            description=args.description,
            query=query,
            interval=args.interval,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error adding chart: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_remove_chart_command(args, chronicle):
    """Handle remove chart command."""
    try:
        result = chronicle.remove_chart(
            dashboard_id=args.dashboard_id,
            chart_id=args.chart_id,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error removing chart: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_get_chart_command(args, chronicle):
    """Handle get chart command."""
    try:
        result = chronicle.get_chart(chart_id=args.id)
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting chart: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_edit_chart_command(args, chronicle):
    """Handle edit chart command."""
    try:
        dashboard_query = args.dashboard_query if args.dashboard_query else None
        dashboard_chart = args.dashboard_chart if args.dashboard_chart else None
        if args.dashboard_query_from_file:
            try:
                with open(
                    args.dashboard_query_from_file, encoding="utf-8"
                ) as f:
                    dashboard_query = f.read()
            except OSError as e:
                print(
                    f"Error reading dashboard query file: {e}", file=sys.stderr
                )
                sys.exit(1)

        if args.dashboard_chart_from_file:
            try:
                with open(
                    args.dashboard_chart_from_file, encoding="utf-8"
                ) as f:
                    dashboard_chart = f.read()
            except OSError as e:
                print(
                    f"Error reading dashboard chart file: {e}", file=sys.stderr
                )
                sys.exit(1)

        result = chronicle.edit_chart(
            dashboard_id=args.dashboard_id,
            dashboard_query=dashboard_query,
            dashboard_chart=dashboard_chart,
        )
        output_formatter(result, args.output)
    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error editing chart: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_import_command(args, chronicle):
    """Handle import dashboard command."""
    try:
        # Initialize variables for the data components
        dashboard_data = None
        chart_data = None
        query_data = None

        # Process dashboard data from argument or file
        if args.dashboard_data:
            dashboard_data = args.dashboard_data
        elif args.dashboard_data_file:
            try:
                with open(args.dashboard_data_file, encoding="utf-8") as f:
                    dashboard_data = f.read()
            except OSError as e:
                print(
                    f"Error reading dashboard data file: {e}", file=sys.stderr
                )
                sys.exit(1)

        # Process chart data from argument or file (if provided)
        if args.chart_data:
            chart_data = args.chart_data
        elif args.chart_data_file:
            try:
                with open(args.chart_data_file, encoding="utf-8") as f:
                    chart_data = f.read()
            except OSError as e:
                print(f"Error reading chart data file: {e}", file=sys.stderr)
                sys.exit(1)

        # Process query data from argument or file (if provided)
        if args.query_data:
            query_data = args.query_data
        elif args.query_data_file:
            try:
                with open(args.query_data_file, encoding="utf-8") as f:
                    query_data = f.read()
            except OSError as e:
                print(f"Error reading query data file: {e}", file=sys.stderr)
                sys.exit(1)

        # Convert JSON strings to dictionaries
        try:
            if isinstance(dashboard_data, str):
                dashboard_data = json.loads(dashboard_data)

            if chart_data and isinstance(chart_data, str):
                chart_data = json.loads(chart_data)

            if query_data and isinstance(query_data, str):
                query_data = json.loads(query_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON data: {e}", file=sys.stderr)
            sys.exit(1)

        # Construct the payload
        dashboard = {}

        # Add dashboard data if provided
        if dashboard_data:
            dashboard["dashboard"] = dashboard_data

        # Add chart data if provided
        if chart_data:
            dashboard["dashboardCharts"] = (
                chart_data if isinstance(chart_data, list) else [chart_data]
            )

        # Add query data if provided
        if query_data:
            dashboard["dashboardQueries"] = (
                query_data if isinstance(query_data, list) else [query_data]
            )

        # Call the import_dashboard method
        result = chronicle.import_dashboard(dashboard)
        output_formatter(result, args.output)

    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except SecOpsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error importing dashboard: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dashboard_export_command(args, chronicle):
    """Handle export dashboard command."""
    try:
        # Initialize variables for the data components
        dashboard_names = []

        # Process dashboard names from argument
        dashboard_names_data = args.dashboard_names

        # Convert string to list of string
        dashboard_names = dashboard_names_data.split(",")

        # Call the export_dashboard method
        result = chronicle.export_dashboard(dashboard_names=dashboard_names)
        output_formatter(result, args.output)

    except APIError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)
    except SecOpsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error importing dashboard: {e}", file=sys.stderr)
        sys.exit(1)
