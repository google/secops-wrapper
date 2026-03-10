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
"""Google SecOps CLI integration job instances commands"""

import json
import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_job_instances_command(subparsers):
    """Setup integration job instances command"""
    instances_parser = subparsers.add_parser(
        "job-instances",
        help="Manage job instances",
    )
    lvl1 = instances_parser.add_subparsers(
        dest="job_instances_command",
        help="Job instances command",
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List job instances")
    list_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    list_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job",
        dest="job_id",
        required=True,
    )
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing instances",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing instances",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_job_instances_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get a specific job instance")
    get_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    get_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job",
        dest="job_id",
        required=True,
    )
    get_parser.add_argument(
        "--job-instance-id",
        type=str,
        help="ID of the job instance to get",
        dest="job_instance_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_job_instances_get_command)

    # delete command
    delete_parser = lvl1.add_parser("delete", help="Delete a job instance")
    delete_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    delete_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job",
        dest="job_id",
        required=True,
    )
    delete_parser.add_argument(
        "--job-instance-id",
        type=str,
        help="ID of the job instance to delete",
        dest="job_instance_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_job_instances_delete_command)

    # create command
    create_parser = lvl1.add_parser("create", help="Create a new job instance")
    create_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    create_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job",
        dest="job_id",
        required=True,
    )
    create_parser.add_argument(
        "--environment",
        type=str,
        help="Environment for the job instance",
        dest="environment",
        required=True,
    )
    create_parser.add_argument(
        "--display-name",
        type=str,
        help="Display name for the job instance",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--schedule",
        type=str,
        help="Cron schedule for the job instance",
        dest="schedule",
    )
    create_parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="Timeout in seconds for job execution",
        dest="timeout_seconds",
    )
    create_parser.add_argument(
        "--enabled",
        action="store_true",
        help="Enable the job instance",
        dest="enabled",
    )
    create_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string of job parameters",
        dest="parameters",
    )
    create_parser.set_defaults(func=handle_job_instances_create_command)

    # update command
    update_parser = lvl1.add_parser("update", help="Update a job instance")
    update_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    update_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job",
        dest="job_id",
        required=True,
    )
    update_parser.add_argument(
        "--job-instance-id",
        type=str,
        help="ID of the job instance to update",
        dest="job_instance_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the job instance",
        dest="display_name",
    )
    update_parser.add_argument(
        "--schedule",
        type=str,
        help="New cron schedule for the job instance",
        dest="schedule",
    )
    update_parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="New timeout in seconds for job execution",
        dest="timeout_seconds",
    )
    update_parser.add_argument(
        "--enabled",
        type=str,
        choices=["true", "false"],
        help="Enable or disable the job instance",
        dest="enabled",
    )
    update_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string of new job parameters",
        dest="parameters",
    )
    update_parser.add_argument(
        "--update-mask",
        type=str,
        help="Comma-separated list of fields to update",
        dest="update_mask",
    )
    update_parser.set_defaults(func=handle_job_instances_update_command)

    # run-ondemand command
    run_parser = lvl1.add_parser(
        "run-ondemand",
        help="Run a job instance on demand",
    )
    run_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    run_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job",
        dest="job_id",
        required=True,
    )
    run_parser.add_argument(
        "--job-instance-id",
        type=str,
        help="ID of the job instance to run",
        dest="job_instance_id",
        required=True,
    )
    run_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string of parameters for this run",
        dest="parameters",
    )
    run_parser.set_defaults(func=handle_job_instances_run_ondemand_command)


def handle_job_instances_list_command(args, chronicle):
    """Handle job instances list command"""
    try:
        out = chronicle.list_integration_job_instances(
            integration_name=args.integration_name,
            job_id=args.job_id,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing job instances: {e}", file=sys.stderr)
        sys.exit(1)


def handle_job_instances_get_command(args, chronicle):
    """Handle job instance get command"""
    try:
        out = chronicle.get_integration_job_instance(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting job instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_job_instances_delete_command(args, chronicle):
    """Handle job instance delete command"""
    try:
        chronicle.delete_integration_job_instance(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
        )
        print(f"Job instance {args.job_instance_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting job instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_job_instances_create_command(args, chronicle):
    """Handle job instance create command"""
    try:
        # Parse parameters if provided
        parameters = None
        if args.parameters:
            parameters = json.loads(args.parameters)

        out = chronicle.create_integration_job_instance(
            integration_name=args.integration_name,
            job_id=args.job_id,
            environment=args.environment,
            display_name=args.display_name,
            schedule=args.schedule,
            timeout_seconds=args.timeout_seconds,
            enabled=args.enabled,
            parameters=parameters,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating job instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_job_instances_update_command(args, chronicle):
    """Handle job instance update command"""
    try:
        # Parse parameters if provided
        parameters = None
        if args.parameters:
            parameters = json.loads(args.parameters)

        # Convert enabled string to boolean if provided
        enabled = None
        if args.enabled:
            enabled = args.enabled.lower() == "true"

        out = chronicle.update_integration_job_instance(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
            display_name=args.display_name,
            schedule=args.schedule,
            timeout_seconds=args.timeout_seconds,
            enabled=enabled,
            parameters=parameters,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating job instance: {e}", file=sys.stderr)
        sys.exit(1)


def handle_job_instances_run_ondemand_command(args, chronicle):
    """Handle run job instance on demand command"""
    try:
        # Parse parameters if provided
        parameters = None
        if args.parameters:
            parameters = json.loads(args.parameters)

        # Get the job instance first
        job_instance = chronicle.get_integration_job_instance(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
        )

        out = chronicle.run_integration_job_instance_on_demand(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
            job_instance=job_instance,
            parameters=parameters,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error running job instance on demand: {e}", file=sys.stderr)
        sys.exit(1)
