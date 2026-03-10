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
"""Top level arguments for integration commands"""

from secops.cli.commands.integration import (
    jobs,
    job_revisions,
    job_context_properties,
    job_instance_logs,
    job_instances,
)


def setup_integrations_command(subparsers):
    """Setup integration command"""
    integrations_parser = subparsers.add_parser(
        "integration", help="Manage SecOps integrations"
    )
    lvl1 = integrations_parser.add_subparsers(
        dest="integrations_command", help="Integrations command"
    )

    # Setup all subcommands under `integration`
    jobs.setup_jobs_command(lvl1)
    job_revisions.setup_job_revisions_command(lvl1)
    job_context_properties.setup_job_context_properties_command(lvl1)
    job_instance_logs.setup_job_instance_logs_command(lvl1)
    job_instances.setup_job_instances_command(lvl1)
