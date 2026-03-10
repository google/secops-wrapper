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
    connectors,
    connector_revisions,
    connector_context_properties,
    connector_instance_logs,
    connector_instances,
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
    connectors.setup_connectors_command(lvl1)
    connector_revisions.setup_connector_revisions_command(lvl1)
    connector_context_properties.setup_connector_context_properties_command(
        lvl1
    )
    connector_instance_logs.setup_connector_instance_logs_command(lvl1)
    connector_instances.setup_connector_instances_command(lvl1)
