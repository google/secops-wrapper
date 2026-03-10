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
"""Google SecOps CLI job instance logs commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import (
    add_pagination_args,
    add_as_list_arg,
)


def setup_job_instance_logs_command(subparsers):
    """Setup job instance logs command"""
    logs_parser = subparsers.add_parser(
        "job-instance-logs",
        help="View job instance logs",
    )
    lvl1 = logs_parser.add_subparsers(
        dest="job_instance_logs_command",
        help="Job instance logs command",
    )

    # list command
    list_parser = lvl1.add_parser("list", help="List job instance logs")
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
    list_parser.add_argument(
        "--job-instance-id",
        type=str,
        help="ID of the job instance",
        dest="job_instance_id",
        required=True,
    )
    add_pagination_args(list_parser)
    add_as_list_arg(list_parser)
    list_parser.add_argument(
        "--filter-string",
        type=str,
        help="Filter string for listing logs",
        dest="filter_string",
    )
    list_parser.add_argument(
        "--order-by",
        type=str,
        help="Order by string for listing logs",
        dest="order_by",
    )
    list_parser.set_defaults(func=handle_job_instance_logs_list_command)

    # get command
    get_parser = lvl1.add_parser("get", help="Get a specific job instance log")
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
        help="ID of the job instance",
        dest="job_instance_id",
        required=True,
    )
    get_parser.add_argument(
        "--log-id",
        type=str,
        help="ID of the log to get",
        dest="log_id",
        required=True,
    )
    get_parser.set_defaults(func=handle_job_instance_logs_get_command)


def handle_job_instance_logs_list_command(args, chronicle):
    """Handle job instance logs list command"""
    try:
        out = chronicle.list_job_instance_logs(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
            page_size=args.page_size,
            page_token=args.page_token,
            filter_string=args.filter_string,
            order_by=args.order_by,
            as_list=args.as_list,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing job instance logs: {e}", file=sys.stderr)
        sys.exit(1)


def handle_job_instance_logs_get_command(args, chronicle):
    """Handle job instance log get command"""
    try:
        out = chronicle.get_job_instance_log(
            integration_name=args.integration_name,
            job_id=args.job_id,
            job_instance_id=args.job_instance_id,
            job_instance_log_id=args.log_id,
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting job instance log: {e}", file=sys.stderr)
        sys.exit(1)
