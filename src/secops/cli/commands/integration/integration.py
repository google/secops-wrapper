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
"""Google SecOps CLI integration commands"""

import json
import sys

from secops.chronicle.models import (
    DiffType,
    IntegrationType,
    PythonVersion,
    TargetMode,
)
from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_integrations_command(subparsers):
    """Setup integrations command"""
    integrations_parser = subparsers.add_parser(
        "integrations", help="Manage SecOps integrations"
    )
    lvl1 = integrations_parser.add_subparsers(
        dest="integrations_command", help="Integrations command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List integrations")
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing integrations",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing integrations",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_integration_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get integration details")
    get_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to get details for",
        dest="integration_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_integration_get_command)

    # delete command
    delete_parser = lvl1.add_parser("delete", help="Delete an integration")
    delete_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to delete",
        dest="integration_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_integration_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create", help="Create a new custom integration"
    )
    create_parser.add_argument(
        "--display-name",
        type=str,
        help="Display name for the integration (max 150 characters)",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--staging",
        action="store_true",
        help="Create the integration in staging mode",
        dest="staging",
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the integration (max 1,500 characters)",
        dest="description",
    )
    create_parser.add_argument(
        "--image-base64",
        type=str,
        help="Integration image encoded as a base64 string (max 5 MB)",
        dest="image_base64",
    )
    create_parser.add_argument(
        "--svg-icon",
        type=str,
        help="Integration SVG icon string (max 1 MB)",
        dest="svg_icon",
    )
    create_parser.add_argument(
        "--python-version",
        type=str,
        choices=[v.value for v in PythonVersion],
        help="Python version for the integration",
        dest="python_version",
    )
    create_parser.add_argument(
        "--integration-type",
        type=str,
        choices=[t.value for t in IntegrationType],
        help="Integration type",
        dest="integration_type",
    )
    create_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string representing a list of integration parameters",
        dest="parameters",
    )
    create_parser.add_argument(
        "--categories",
        type=str,
        help="Comma-separated list of categories for the integration",
        dest="categories",
    )
    create_parser.set_defaults(func=handle_integration_create_command)

    # download command
    download_parser = lvl1.add_parser(
        "download",
        help="Download an integration package as a ZIP file",
    )
    download_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to download",
        dest="integration_id",
        required=True,
    )
    download_parser.add_argument(
        "--output-file",
        type=str,
        help="Path to write the downloaded ZIP file to",
        dest="output_file",
        required=True,
    )
    download_parser.set_defaults(func=handle_integration_download_command)

    # download-dependency command
    download_dep_parser = lvl1.add_parser(
        "download-dependency",
        help="Download a Python dependency for a custom integration",
    )
    download_dep_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration",
        dest="integration_id",
        required=True,
    )
    download_dep_parser.add_argument(
        "--dependency-name",
        type=str,
        help=(
            "Dependency name to download. Can include version or "
            "repository, e.g. 'requests==2.31.0'"
        ),
        dest="dependency_name",
        required=True,
    )
    download_dep_parser.set_defaults(
        func=handle_download_integration_dependency_command
    )

    # export-items command
    export_items_parser = lvl1.add_parser(
        "export-items",
        help="Export specific items from an integration as a ZIP file",
    )
    export_items_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to export items from",
        dest="integration_id",
        required=True,
    )
    export_items_parser.add_argument(
        "--output-file",
        type=str,
        help="Path to write the exported ZIP file to",
        dest="output_file",
        required=True,
    )
    export_items_parser.add_argument(
        "--actions",
        type=str,
        nargs="+",
        help="IDs of actions to export",
        dest="actions",
    )
    export_items_parser.add_argument(
        "--jobs",
        type=str,
        nargs="+",
        help="IDs of jobs to export",
        dest="jobs",
    )
    export_items_parser.add_argument(
        "--connectors",
        type=str,
        nargs="+",
        help="IDs of connectors to export",
        dest="connectors",
    )
    export_items_parser.add_argument(
        "--managers",
        type=str,
        nargs="+",
        help="IDs of managers to export",
        dest="managers",
    )
    export_items_parser.add_argument(
        "--transformers",
        type=str,
        nargs="+",
        help="IDs of transformers to export",
        dest="transformers",
    )
    export_items_parser.add_argument(
        "--logical-operators",
        type=str,
        nargs="+",
        help="IDs of logical operators to export",
        dest="logical_operators",
    )
    export_items_parser.set_defaults(
        func=handle_export_integration_items_command
    )

    # affected-items command
    affected_parser = lvl1.add_parser(
        "affected-items",
        help="Get items affected by changes to an integration",
    )
    affected_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to check",
        dest="integration_id",
        required=True,
    )
    affected_parser.set_defaults(
        func=handle_get_integration_affected_items_command
    )

    # agent-integrations command
    agent_parser = lvl1.add_parser(
        "agent-integrations",
        help="Get integrations installed on a specific agent",
    )
    agent_parser.add_argument(
        "--agent-id",
        type=str,
        help="Identifier of the agent",
        dest="agent_id",
        required=True,
    )
    agent_parser.set_defaults(func=handle_get_agent_integrations_command)

    # dependencies command
    deps_parser = lvl1.add_parser(
        "dependencies",
        help="Get Python dependencies for a custom integration",
    )
    deps_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration",
        dest="integration_id",
        required=True,
    )
    deps_parser.set_defaults(func=handle_get_integration_dependencies_command)

    # restricted-agents command
    restricted_parser = lvl1.add_parser(
        "restricted-agents",
        help="Get agents restricted from running an updated integration",
    )
    restricted_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration",
        dest="integration_id",
        required=True,
    )
    restricted_parser.add_argument(
        "--required-python-version",
        type=str,
        choices=[v.value for v in PythonVersion],
        help="Python version required for the updated integration",
        dest="required_python_version",
        required=True,
    )
    restricted_parser.add_argument(
        "--push-request",
        action="store_true",
        help="Indicates the integration is being pushed to a different mode",
        dest="push_request",
    )
    restricted_parser.set_defaults(
        func=handle_get_integration_restricted_agents_command
    )

    # diff command
    diff_parser = lvl1.add_parser(
        "diff", help="Get the configuration diff for an integration"
    )
    diff_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration",
        dest="integration_id",
        required=True,
    )
    diff_parser.add_argument(
        "--diff-type",
        type=str,
        choices=[d.value for d in DiffType],
        help=(
            "Type of diff to retrieve. "
            "COMMERCIAL: diff against the marketplace version. "
            "PRODUCTION: diff between staging and production. "
            "STAGING: diff between production and staging."
        ),
        dest="diff_type",
        default=DiffType.COMMERCIAL.value,
    )
    diff_parser.set_defaults(func=handle_get_integration_diff_command)

    # transition command
    transition_parser = lvl1.add_parser(
        "transition",
        help="Transition an integration to production or staging",
    )
    transition_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to transition",
        dest="integration_id",
        required=True,
    )
    transition_parser.add_argument(
        "--target-mode",
        type=str,
        choices=[t.value for t in TargetMode],
        help="Target mode to transition the integration to",
        dest="target_mode",
        required=True,
    )
    transition_parser.set_defaults(func=handle_transition_integration_command)

    # update command
    update_parser = lvl1.add_parser(
        "update", help="Update an existing integration's metadata"
    )
    update_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to update",
        dest="integration_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the integration (max 150 characters)",
        dest="display_name",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the integration (max 1,500 characters)",
        dest="description",
    )
    update_parser.add_argument(
        "--image-base64",
        type=str,
        help="New integration image encoded as a base64 string (max 5 MB)",
        dest="image_base64",
    )
    update_parser.add_argument(
        "--svg-icon",
        type=str,
        help="New integration SVG icon string (max 1 MB)",
        dest="svg_icon",
    )
    update_parser.add_argument(
        "--python-version",
        type=str,
        choices=[v.value for v in PythonVersion],
        help="Python version for the integration",
        dest="python_version",
    )
    update_parser.add_argument(
        "--integration-type",
        type=str,
        choices=[t.value for t in IntegrationType],
        help="Integration type",
        dest="integration_type",
    )
    update_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string representing a list of integration parameters",
        dest="parameters",
    )
    update_parser.add_argument(
        "--categories",
        type=str,
        help="Comma-separated list of categories for the integration",
        dest="categories",
    )
    update_parser.add_argument(
        "--staging",
        action="store_true",
        help="Set the integration to staging mode",
        dest="staging",
    )
    update_parser.add_argument(
        "--dependencies-to-remove",
        type=str,
        nargs="+",
        help="List of dependency names to remove from the integration",
        dest="dependencies_to_remove",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help=(
            "Comma-separated list of fields to update. "
            "If not provided, all supplied fields are updated."
        ),
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_update_integration_command)

    # update-custom command
    update_custom_parser = lvl1.add_parser(
        "update-custom",
        help=(
            "Update a custom integration definition including "
            "parameters and dependencies"
        ),
    )
    update_custom_parser.add_argument(
        "--integration-id",
        type=str,
        help="ID of the integration to update",
        dest="integration_id",
        required=True,
    )
    update_custom_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the integration (max 150 characters)",
        dest="display_name",
    )
    update_custom_parser.add_argument(
        "--description",
        type=str,
        help="New description for the integration (max 1,500 characters)",
        dest="description",
    )
    update_custom_parser.add_argument(
        "--image-base64",
        type=str,
        help="New integration image encoded as a base64 string (max 5 MB)",
        dest="image_base64",
    )
    update_custom_parser.add_argument(
        "--svg-icon",
        type=str,
        help="New integration SVG icon string (max 1 MB)",
        dest="svg_icon",
    )
    update_custom_parser.add_argument(
        "--python-version",
        type=str,
        choices=[v.value for v in PythonVersion],
        help="Python version for the integration",
        dest="python_version",
    )
    update_custom_parser.add_argument(
        "--integration-type",
        type=str,
        choices=[t.value for t in IntegrationType],
        help="Integration type",
        dest="integration_type",
    )
    update_custom_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string representing a list of integration parameters",
        dest="parameters",
    )
    update_custom_parser.add_argument(
        "--categories",
        type=str,
        help="Comma-separated list of categories for the integration",
        dest="categories",
    )
    update_custom_parser.add_argument(
        "--staging",
        action="store_true",
        help="Set the integration to staging mode",
        dest="staging",
    )
    update_custom_parser.add_argument(
        "--dependencies-to-remove",
        type=str,
        nargs="+",
        help="List of dependency names to remove from the integration",
        dest="dependencies_to_remove",
    )
    update_custom_parser.add_argument(
        "--update-mask",
        type=str,
        help=(
            "Comma-separated list of fields to update. "
            "If not provided, all supplied fields are updated."
        ),
        dest="update_mask",
    )
    update_custom_parser.set_defaults(
        func=handle_updated_custom_integration_command
    )


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def handle_integration_list_command(args, chronicle):
    """Handle list integrations command"""
    try:
        out = chronicle.soar.list_integrations(
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing integrations: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_get_command(args, chronicle):
    """Handle get integration command"""
    try:
        out = chronicle.soar.get_integration(
            integration_name=args.integration_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_delete_command(args, chronicle):
    """Handle delete integration command"""
    try:
        chronicle.soar.delete_integration(
            integration_name=args.integration_id,
        )
        print(f"Integration {args.integration_id} deleted successfully.")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_create_command(args, chronicle):
    """Handle create integration command"""
    try:
        out = chronicle.soar.create_integration(
            display_name=args.display_name,
            staging=args.staging,
            description=args.description,
            image_base64=args.image_base64,
            svg_icon=args.svg_icon,
            python_version=(
                PythonVersion(args.python_version)
                if args.python_version
                else None
            ),
            integration_type=(
                IntegrationType(args.integration_type)
                if args.integration_type
                else None
            ),
            parameters=(
                json.loads(args.parameters)
                if getattr(args, "parameters", None)
                else None
            ),
            categories=(
                [c.strip() for c in args.categories.split(",")]
                if getattr(args, "categories", None)
                else None
            ),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_integration_download_command(args, chronicle):
    """Handle download integration command"""
    try:
        zip_bytes = chronicle.soar.download_integration(
            integration_name=args.integration_id,
        )
        with open(args.output_file, "wb") as f:
            f.write(zip_bytes)
        print(
            f"Integration {args.integration_id} downloaded to "
            f"{args.output_file}."
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error downloading integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_download_integration_dependency_command(args, chronicle):
    """Handle download integration dependencies command"""
    try:
        out = chronicle.soar.download_integration_dependency(
            integration_name=args.integration_id,
            dependency_name=args.dependency_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error downloading integration dependencies: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_export_integration_items_command(args, chronicle):
    """Handle export integration items command"""
    try:
        zip_bytes = chronicle.soar.export_integration_items(
            integration_name=args.integration_id,
            actions=args.actions,
            jobs=args.jobs,
            connectors=args.connectors,
            managers=args.managers,
            transformers=args.transformers,
            logical_operators=args.logical_operators,
        )
        with open(args.output_file, "wb") as f:
            f.write(zip_bytes)
        print(f"Integration items exported to {args.output_file}.")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error exporting integration items: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_integration_affected_items_command(args, chronicle):
    """Handle get integration affected items command"""
    try:
        out = chronicle.soar.get_integration_affected_items(
            integration_name=args.integration_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration affected items: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_agent_integrations_command(args, chronicle):
    """Handle get agent integration command"""
    try:
        out = chronicle.soar.get_agent_integrations(
            agent_id=args.agent_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting agent integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_integration_dependencies_command(args, chronicle):
    """Handle get integration dependencies command"""
    try:
        out = chronicle.soar.get_integration_dependencies(
            integration_name=args.integration_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration dependencies: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_integration_restricted_agents_command(args, chronicle):
    """Handle get integration restricted agent command"""
    try:
        out = chronicle.soar.get_integration_restricted_agents(
            integration_name=args.integration_id,
            required_python_version=PythonVersion(args.required_python_version),
            push_request=args.push_request,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting integration restricted agent: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_get_integration_diff_command(args, chronicle):
    """Handle get integration diff command"""
    try:
        out = chronicle.soar.get_integration_diff(
            integration_name=args.integration_id,
            diff_type=DiffType(args.diff_type),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration diff: {e}", file=sys.stderr)
        sys.exit(1)


def handle_transition_integration_command(args, chronicle):
    """Handle transition integration command"""
    try:
        out = chronicle.soar.transition_integration(
            integration_name=args.integration_id,
            target_mode=TargetMode(args.target_mode),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error transitioning integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_update_integration_command(args, chronicle):
    """Handle update integration command"""
    try:
        out = chronicle.soar.update_integration(
            integration_name=args.integration_id,
            display_name=args.display_name,
            description=args.description,
            image_base64=args.image_base64,
            svg_icon=args.svg_icon,
            python_version=(
                PythonVersion(args.python_version)
                if args.python_version
                else None
            ),
            integration_type=(
                IntegrationType(args.integration_type)
                if args.integration_type
                else None
            ),
            parameters=(
                json.loads(args.parameters)
                if getattr(args, "parameters", None)
                else None
            ),
            categories=(
                [c.strip() for c in args.categories.split(",")]
                if getattr(args, "categories", None)
                else None
            ),
            staging=args.staging if "staging" in vars(args) else None,
            dependencies_to_remove=args.dependencies_to_remove,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating integration: {e}", file=sys.stderr)
        sys.exit(1)


def handle_updated_custom_integration_command(args, chronicle):
    """Handle update custom integration command"""
    try:
        out = chronicle.soar.update_custom_integration(
            integration_name=args.integration_id,
            display_name=args.display_name,
            description=args.description,
            image_base64=args.image_base64,
            svg_icon=args.svg_icon,
            python_version=(
                PythonVersion(args.python_version)
                if args.python_version
                else None
            ),
            integration_type=(
                IntegrationType(args.integration_type)
                if args.integration_type
                else None
            ),
            parameters=(
                json.loads(args.parameters)
                if getattr(args, "parameters", None)
                else None
            ),
            categories=(
                [c.strip() for c in args.categories.split(",")]
                if getattr(args, "categories", None)
                else None
            ),
            staging=args.staging or None,
            dependencies_to_remove=args.dependencies_to_remove,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating custom integration: {e}", file=sys.stderr)
        sys.exit(1)
