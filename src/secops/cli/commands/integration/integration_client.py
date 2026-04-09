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
    marketplace_integration,
    integration,
    actions,
    action_revisions,
    # connectors,
    # connector_revisions,
    # connector_context_properties,
    # connector_instance_logs,
    # connector_instances,
    # jobs,
    # job_revisions,
    # job_context_properties,
    # job_instance_logs,
    # job_instances,
    managers,
    manager_revisions,
    integration_instances,
    # transformers,
    # transformer_revisions,
    # logical_operators,
    # logical_operator_revisions,
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
    integration.setup_integrations_command(lvl1)
    integration_instances.setup_integration_instances_command(lvl1)
    # transformers.setup_transformers_command(lvl1)
    # transformer_revisions.setup_transformer_revisions_command(lvl1)
    # logical_operators.setup_logical_operators_command(lvl1)
    # logical_operator_revisions.setup_logical_operator_revisions_command(lvl1)
    actions.setup_actions_command(lvl1)
    action_revisions.setup_action_revisions_command(lvl1)
    # connectors.setup_connectors_command(lvl1)
    # connector_revisions.setup_connector_revisions_command(lvl1)
    # connector_context_properties.setup_connector_context_properties_command(
    #     lvl1
    # )
    # connector_instance_logs.setup_connector_instance_logs_command(lvl1)
    # connector_instances.setup_connector_instances_command(lvl1)
    # jobs.setup_jobs_command(lvl1)
    # job_revisions.setup_job_revisions_command(lvl1)
    # job_context_properties.setup_job_context_properties_command(lvl1)
    # job_instance_logs.setup_job_instance_logs_command(lvl1)
    # job_instances.setup_job_instances_command(lvl1)
    managers.setup_managers_command(lvl1)
    manager_revisions.setup_manager_revisions_command(lvl1)
    marketplace_integration.setup_marketplace_integrations_command(lvl1)

