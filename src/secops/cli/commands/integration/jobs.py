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
"""Google SecOps CLI integration jobs commands"""

import json
import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_jobs_command(subparsers):
    """Setup integration jobs command"""
    jobs_parser = subparsers.add_parser(
        "jobs",
        help="Manage integration jobs",
    )
    lvl1 = jobs_parser.add_subparsers(
        dest="jobs_command", help="Integration jobs command"
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List integration jobs")
    list_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing jobs",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing jobs",
        dest="order_by",
    )
    list_parser.add_argument(
        "--exclude-staging",
        action="store_true",
        help="Exclude staging jobs from the list",
        dest="exclude_staging",
    )
    list_parser.set_defaults(func=handle_jobs_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get integration job details")
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
        help="ID of the job to get",
        dest="job_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_jobs_get_command)

    # delete command
    delete_parser = lvl1.add_parser("delete", help="Delete an integration job")
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
        help="ID of the job to delete",
        dest="job_id",
        required=True,
    )
    delete_parser.set_defaults(func=handle_jobs_delete_command)

    # create command
    create_parser = lvl1.add_parser(
        "create",
        help="Create a new integration job",
    )
    create_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    create_parser.add_argument(
        "--display-name",
        type=str,
        help="Display name for the job",
        dest="display_name",
        required=True,
    )
    create_parser.add_argument(
        "--code",
        type=str,
        help="Python code for the job",
        dest="code",
        required=True,
    )
    create_parser.add_argument(
        "--description",
        type=str,
        help="Description of the job",
        dest="description",
    )
    create_parser.add_argument(
        "--job-id",
        type=str,
        help="Custom ID for the job",
        dest="job_id",
    )
    create_parser.add_argument(
        "--parameters",
        type=str,
        help="JSON string of job parameters",
        dest="parameters",
    )
    create_parser.set_defaults(func=handle_jobs_create_command)

    # update command
    update_parser = lvl1.add_parser("update", help="Update an integration job")
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
        help="ID of the job to update",
        dest="job_id",
        required=True,
    )
    update_parser.add_argument(
        "--display-name",
        type=str,
        help="New display name for the job",
        dest="display_name",
    )
    update_parser.add_argument(
        "--code",
        type=str,
        help="New Python code for the job",
        dest="code",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New description for the job",
        dest="description",
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
    update_parser.set_defaults(func=handle_jobs_update_command)

    # test command
    test_parser = lvl1.add_parser(
        "test", help="Execute an integration job test"
    )
    test_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    test_parser.add_argument(
        "--job-id",
        type=str,
        help="ID of the job to test",
        dest="job_id",
        required=True,
    )
    test_parser.set_defaults(func=handle_jobs_test_command)

    # template command
    template_parser = lvl1.add_parser(
        "template",
        help="Get a template for creating a job",
    )
    template_parser.add_argument(
        "--integration-name",
        type=str,
        help="Name of the integration",
        dest="integration_name",
        required=True,
    )
    template_parser.set_defaults(func=handle_jobs_template_command)


def handle_jobs_list_command(args, chronicle):
    """Handle integration jobs list command"""
    try:
        out = chronicle.list_integration_jobs(
            integration_name=args.integration_name,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            exclude_staging=args.exclude_staging,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing integration jobs: {e}", file=sys.stderr)
        sys.exit(1)


def handle_jobs_get_command(args, chronicle):
    """Handle integration job get command"""
    try:
        out = chronicle.get_integration_job(
            integration_name=args.integration_name,
            job_id=args.job_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting integration job: {e}", file=sys.stderr)
        sys.exit(1)


def handle_jobs_delete_command(args, chronicle):
    """Handle integration job delete command"""
    try:
        chronicle.delete_integration_job(
            integration_name=args.integration_name,
            job_id=args.job_id,
        )
        print(f"Job {args.job_id} deleted successfully")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error deleting integration job: {e}", file=sys.stderr)
        sys.exit(1)


def handle_jobs_create_command(args, chronicle):
    """Handle integration job create command"""
    try:
        # Parse parameters if provided
        parameters = None
        if args.parameters:
            parameters = json.loads(args.parameters)

        out = chronicle.create_integration_job(
            integration_name=args.integration_name,
            display_name=args.display_name,
            code=args.code,
            description=args.description,
            job_id=args.job_id,
            parameters=parameters,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error creating integration job: {e}", file=sys.stderr)
        sys.exit(1)


def handle_jobs_update_command(args, chronicle):
    """Handle integration job update command"""
    try:
        # Parse parameters if provided
        parameters = None
        if args.parameters:
            parameters = json.loads(args.parameters)

        out = chronicle.update_integration_job(
            integration_name=args.integration_name,
            job_id=args.job_id,
            display_name=args.display_name,
            code=args.code,
            description=args.description,
            parameters=parameters,
            update_mask=args.update_mask,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error updating integration job: {e}", file=sys.stderr)
        sys.exit(1)


def handle_jobs_test_command(args, chronicle):
    """Handle integration job test command"""
    try:
        # First get the job to test
        job = chronicle.get_integration_job(
            integration_name=args.integration_name,
            job_id=args.job_id,
        )
        out = chronicle.execute_integration_job_test(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job=job,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error testing integration job: {e}", file=sys.stderr)
        sys.exit(1)


def handle_jobs_template_command(args, chronicle):
    """Handle get job template command"""
    try:
        out = chronicle.get_integration_job_template(
            integration_name=args.integration_name,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting job template: {e}", file=sys.stderr)
        sys.exit(1)
