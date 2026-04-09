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
"""Chronicle SOAR API specific functionality."""

from secops.chronicle.soar.service import SOARService

from secops.chronicle.soar.integration.integrations import (
    list_integrations,
    get_integration,
    delete_integration,
    create_integration,
    transition_integration,
    update_integration,
    update_custom_integration,
    get_integration_affected_items,
    get_integration_dependencies,
    get_integration_diff,
    get_integration_restricted_agents,
)
from secops.chronicle.soar.integration.integration_instances import (
    list_integration_instances,
    get_integration_instance,
    delete_integration_instance,
    create_integration_instance,
    update_integration_instance,
)
from secops.chronicle.soar.integration.marketplace_integrations import (
    list_marketplace_integrations,
    get_marketplace_integration,
    get_marketplace_integration_diff,
    install_marketplace_integration,
    uninstall_marketplace_integration,
)

__all__ = [
    # client
    "SOARService",
    # Integrations
    "list_integrations",
    "get_integration",
    "delete_integration",
    "create_integration",
    "transition_integration",
    "update_integration",
    "update_custom_integration",
    "get_integration_affected_items",
    "get_integration_dependencies",
    "get_integration_diff",
    "get_integration_restricted_agents",
    # Marketplace Integrations
    "list_marketplace_integrations",
    "get_marketplace_integration",
    "get_marketplace_integration_diff",
    "install_marketplace_integration",
    "uninstall_marketplace_integration",
    # Integration Instances
    "list_integration_instances",
    "get_integration_instance",
    "delete_integration_instance",
    "create_integration_instance",
    "update_integration_instance",
]
