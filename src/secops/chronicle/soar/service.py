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
"""Chronicle SOAR API client."""

from typing import TYPE_CHECKING, Any

# pylint: disable=line-too-long
from secops.chronicle.models import (
    APIVersion,
    DiffType,
    IntegrationInstanceParameter,
    IntegrationType,
    PythonVersion,
    TargetMode,
    IntegrationParam,
)
from secops.chronicle.soar.integration.marketplace_integrations import (
    get_marketplace_integration as _get_marketplace_integration,
    get_marketplace_integration_diff as _get_marketplace_integration_diff,
    install_marketplace_integration as _install_marketplace_integration,
    list_marketplace_integrations as _list_marketplace_integrations,
    uninstall_marketplace_integration as _uninstall_marketplace_integration,
)
from secops.chronicle.soar.integration.integrations import (
    create_integration as _create_integration,
    delete_integration as _delete_integration,
    download_integration as _download_integration,
    download_integration_dependency as _download_integration_dependency,
    export_integration_items as _export_integration_items,
    get_agent_integrations as _get_agent_integrations,
    get_integration as _get_integration,
    get_integration_affected_items as _get_integration_affected_items,
    get_integration_dependencies as _get_integration_dependencies,
    get_integration_diff as _get_integration_diff,
    get_integration_restricted_agents as _get_integration_restricted_agents,
    list_integrations as _list_integrations,
    transition_integration as _transition_integration,
    update_custom_integration as _update_custom_integration,
    update_integration as _update_integration,
)
from secops.chronicle.soar.integration.integration_instances import (
    create_integration_instance as _create_integration_instance,
    delete_integration_instance as _delete_integration_instance,
    execute_integration_instance_test as _execute_integration_instance_test,
    get_default_integration_instance as _get_default_integration_instance,
    get_integration_instance as _get_integration_instance,
    get_integration_instance_affected_items as _get_integration_instance_affected_items,
    list_integration_instances as _list_integration_instances,
    update_integration_instance as _update_integration_instance,
)
from secops.chronicle.soar.integration.actions import (
    create_integration_action as _create_integration_action,
    delete_integration_action as _delete_integration_action,
    execute_integration_action_test as _execute_integration_action_test,
    get_integration_action as _get_integration_action,
    get_integration_action_template as _get_integration_action_template,
    get_integration_actions_by_environment as _get_integration_actions_by_environment,
    list_integration_actions as _list_integration_actions,
    update_integration_action as _update_integration_action,
)
from secops.chronicle.soar.integration.action_revisions import (
    create_integration_action_revision as _create_integration_action_revision,
    delete_integration_action_revision as _delete_integration_action_revision,
    list_integration_action_revisions as _list_integration_action_revisions,
    rollback_integration_action_revision as _rollback_integration_action_revision,
)
from secops.chronicle.soar.integration.managers import (
    create_integration_manager as _create_integration_manager,
    delete_integration_manager as _delete_integration_manager,
    get_integration_manager as _get_integration_manager,
    get_integration_manager_template as _get_integration_manager_template,
    list_integration_managers as _list_integration_managers,
    update_integration_manager as _update_integration_manager,
)
from secops.chronicle.soar.integration.manager_revisions import (
    create_integration_manager_revision as _create_integration_manager_revision,
    delete_integration_manager_revision as _delete_integration_manager_revision,
    get_integration_manager_revision as _get_integration_manager_revision,
    list_integration_manager_revisions as _list_integration_manager_revisions,
    rollback_integration_manager_revision as _rollback_integration_manager_revision,
)

# pylint: enable=line-too-long

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


class SOARService:
    """Namespace for all SOAR-related operations in Google SecOps."""

    def __init__(self, client: "ChronicleClient"):
        self._client = client

    # -------------------------------------------------------------------------
    # Marketplace Integration methods
    # -------------------------------------------------------------------------

    def list_marketplace_integrations(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        filter_string: str | None = None,
        order_by: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
        as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get a list of all marketplace integration.

        Args:
            page_size: Maximum number of integration to return per page
            page_token: Token for the next page of results, if available
            filter_string: Filter expression to filter marketplace integration
            order_by: Field to sort the marketplace integration by
            api_version: API version to use. Defaults to V1BETA
            as_list: If True, return a list of integration instead of a dict
                with integration list and nextPageToken.

        Returns:
            If as_list is True: List of marketplace integration.
            If as_list is False: Dict with marketplace integration list and
                nextPageToken.

        Raises:
            APIError: If the API request fails
        """
        return _list_marketplace_integrations(
            self._client,
            page_size,
            page_token,
            filter_string,
            order_by,
            api_version,
            as_list,
        )

    def get_marketplace_integration(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get a specific marketplace integration by integration name.

        Args:
            integration_name: name of the marketplace integration to retrieve
            api_version: API version to use. Defaults to V1BETA

        Returns:
            Marketplace integration details

        Raises:
            APIError: If the API request fails
        """
        return _get_marketplace_integration(
            self._client, integration_name, api_version
        )

    def get_marketplace_integration_diff(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get the differences between the currently installed version of
            an integration and the commercial version available in the
            marketplace.

        Args:
            integration_name: name of the marketplace integration
            api_version: API version to use. Defaults to V1BETA

        Returns:
            Marketplace integration diff details

        Raises:
            APIError: If the API request fails
        """
        return _get_marketplace_integration_diff(
            self._client, integration_name, api_version
        )

    def install_marketplace_integration(
        self,
        integration_name: str,
        override_mapping: bool | None = None,
        staging: bool | None = None,
        version: str | None = None,
        restore_from_snapshot: bool | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Install a marketplace integration by integration name

        Args:
            integration_name: Name of the marketplace integration to install
            override_mapping: Optional. Determines if the integration should
                override the ontology if already installed, if not provided,
                set to false by default.
            staging: Optional. Determines if the integration should be installed
                as staging or production,
                if not provided, installed as production.
            version: Optional. Determines which version of the integration
                should be installed.
            restore_from_snapshot: Optional. Determines if the integration
                should be installed from existing integration snapshot.
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Installed marketplace integration details

        Raises:
            APIError: If the API request fails
        """
        return _install_marketplace_integration(
            self._client,
            integration_name,
            override_mapping,
            staging,
            version,
            restore_from_snapshot,
            api_version,
        )

    def uninstall_marketplace_integration(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Uninstall a marketplace integration by integration name

        Args:
            integration_name: Name of the marketplace integration to uninstall
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Empty dictionary if uninstallation is successful

        Raises:
            APIError: If the API request fails
        """
        return _uninstall_marketplace_integration(
            self._client, integration_name, api_version
        )

    # -------------------------------------------------------------------------
    # Integration methods
    # -------------------------------------------------------------------------

    def list_integrations(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        filter_string: str | None = None,
        order_by: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
        as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get a list of all integrations.

        Args:
            page_size: Maximum number of integrations to return per page
            page_token: Token for the next page of results, if available
            filter_string: Filter expression to filter integrations.
                Only supports "displayName:" prefix.
            order_by: Field to sort the integrations by
            api_version: API version to use. Defaults to V1BETA
            as_list: If True, return a list of integrations instead of a dict
                with integration list and nextPageToken.

        Returns:
            If as_list is True: List of integrations.
            If as_list is False: Dict with integration list and nextPageToken.

        Raises:
            APIError: If the API request fails
        """
        return _list_integrations(
            self._client,
            page_size,
            page_token,
            filter_string,
            order_by,
            api_version,
            as_list,
        )

    def get_integration(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get a specific integration by integration name.

        Args:
            integration_name: name of the integration to retrieve
            api_version: API version to use. Defaults to V1BETA

        Returns:
            Integration details

        Raises:
            APIError: If the API request fails
        """
        return _get_integration(self._client, integration_name, api_version)

    def delete_integration(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> None:
        """Deletes a specific custom integration. Commercial integrations
        cannot be deleted via this method.

        Args:
            integration_name: Name of the integration to delete
            api_version: API version to use for the request.
                Default is V1BETA.

        Raises:
            APIError: If the API request fails
        """
        _delete_integration(self._client, integration_name, api_version)

    def create_integration(
        self,
        display_name: str,
        staging: bool,
        description: str | None = None,
        image_base64: str | None = None,
        svg_icon: str | None = None,
        python_version: PythonVersion | None = None,
        parameters: list[IntegrationParam | dict[str, Any]] | None = None,
        categories: list[str] | None = None,
        integration_type: IntegrationType | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Creates a new custom SOAR integration.

        Args:
            display_name: Required. The display name of the integration
                (max 150 characters)
            staging: Required. True if the integration is in staging mode
            description: Optional. The integration's description
                (max 1,500 characters)
            image_base64: Optional. The integration's image encoded as a
                base64 string (max 5 MB)
            svg_icon: Optional. The integration's SVG icon (max 1 MB)
            python_version: Optional. The integration's Python version
            parameters: Optional. Integration parameters (max 50).
                Each entry may be an IntegrationParam dataclass instance
                or a plain dict with keys: id, defaultValue,
                displayName, propertyName, type, description, mandatory.
            categories: Optional. Integration categories (max 50)
            integration_type: Optional. The integration's type
                (response/extension)
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the details of the newly created integration

        Raises:
            APIError: If the API request fails
        """
        return _create_integration(
            self._client,
            display_name=display_name,
            staging=staging,
            description=description,
            image_base64=image_base64,
            svg_icon=svg_icon,
            python_version=python_version,
            parameters=parameters,
            categories=categories,
            integration_type=integration_type,
            api_version=api_version,
        )

    def download_integration(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> bytes:
        """Exports the entire integration package as a ZIP file. Includes
        all scripts, definitions, and the manifest file. Use this method
        for backup or sharing.

        Args:
            integration_name: Name of the integration to download
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Bytes of the ZIP file containing the integration package

        Raises:
            APIError: If the API request fails
        """
        return _download_integration(
            self._client, integration_name, api_version
        )

    def download_integration_dependency(
        self,
        integration_name: str,
        dependency_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Initiates the download of a Python dependency (e.g., a library
        from PyPI) for a custom integration.

        Args:
            integration_name: Name of the integration whose dependency
                to download
            dependency_name: The dependency name to download. It can
                contain the version or the repository.
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Empty dict if the download was successful,
                or a dict containing error
            details if the download failed

        Raises:
            APIError: If the API request fails
        """
        return _download_integration_dependency(
            self._client, integration_name, dependency_name, api_version
        )

    def export_integration_items(
        self,
        integration_name: str,
        actions: list[str] | str | None = None,
        jobs: list[str] | str | None = None,
        connectors: list[str] | str | None = None,
        managers: list[str] | str | None = None,
        transformers: list[str] | str | None = None,
        logical_operators: list[str] | str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> bytes:
        """Exports specific items from an integration into a ZIP folder.
        Use this method to extract only a subset of capabilities (e.g.,
        just the connectors) for reuse.

        Args:
            integration_name: Name of the integration to export items from
            actions: Optional. IDs of the actions to export as a list or
                comma-separated string. Format: [1,2,3] or "1,2,3"
            jobs: Optional. IDs of the jobs to export as a list or
                comma-separated string.
            connectors: Optional. IDs of the connectors to export as a
                list or comma-separated string.
            managers: Optional. IDs of the managers to export as a list
                or comma-separated string.
            transformers: Optional. IDs of the transformers to export as
                a list or comma-separated string.
            logical_operators: Optional. IDs of the logical operators to
                export as a list or comma-separated string.
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Bytes of the ZIP file containing the exported items

        Raises:
            APIError: If the API request fails
        """
        return _export_integration_items(
            self._client,
            integration_name,
            actions=actions,
            jobs=jobs,
            connectors=connectors,
            managers=managers,
            transformers=transformers,
            logical_operators=logical_operators,
            api_version=api_version,
        )

    def get_integration_affected_items(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Identifies all system items (e.g., connector instances, job
        instances, playbooks) that would be affected by a change to or
        deletion of this integration. Use this method to conduct impact
        analysis before making breaking changes.

        Args:
            integration_name: Name of the integration to check for
                affected items
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the list of items affected by changes to
                the specified integration

        Raises:
            APIError: If the API request fails
        """
        return _get_integration_affected_items(
            self._client, integration_name, api_version
        )

    def get_agent_integrations(
        self,
        agent_id: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Returns the set of integrations currently installed and
        configured on a specific agent.

        Args:
            agent_id: The agent identifier
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the list of agent-based integrations

        Raises:
            APIError: If the API request fails
        """
        return _get_agent_integrations(self._client, agent_id, api_version)

    def get_integration_dependencies(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Returns the complete list of Python dependencies currently
        associated with a custom integration.

        Args:
            integration_name: Name of the integration to check for
                dependencies
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the list of dependencies for the specified
                integration

        Raises:
            APIError: If the API request fails
        """
        return _get_integration_dependencies(
            self._client, integration_name, api_version
        )

    def get_integration_diff(
        self,
        integration_name: str,
        diff_type: DiffType | None = DiffType.COMMERCIAL,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get the configuration diff of a specific integration.

        Args:
            integration_name: ID of the integration to retrieve the diff for
            diff_type: Type of diff to retrieve (Commercial, Production, or
                Staging). Default is Commercial.
                COMMERCIAL: Diff between the commercial version of the
                    integration and the current version in the environment.
                PRODUCTION: Returns the difference between the staging
                    integration and its matching production version.
                STAGING: Returns the difference between the production
                    integration and its corresponding staging version.
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict containing the configuration diff of the specified integration

        Raises:
            APIError: If the API request fails
        """
        return _get_integration_diff(
            self._client, integration_name, diff_type, api_version
        )

    def get_integration_restricted_agents(
        self,
        integration_name: str,
        required_python_version: PythonVersion,
        push_request: bool = False,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Identifies remote agents that would be restricted from running
        an updated version of the integration, typically due to environment
        incompatibilities like unsupported Python versions.

        Args:
            integration_name: Name of the integration to check for
                restricted agents
            required_python_version: Python version required for the
                updated integration
            push_request: Optional. Indicates whether the integration is
                being pushed to a different mode (production/staging).
                False by default.
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the list of agents that would be restricted
                from running the updated integration

        Raises:
            APIError: If the API request fails
        """
        return _get_integration_restricted_agents(
            self._client,
            integration_name,
            required_python_version=required_python_version,
            push_request=push_request,
            api_version=api_version,
        )

    def transition_integration(
        self,
        integration_name: str,
        target_mode: TargetMode,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Transitions an integration to a different environment
        (e.g. staging to production).

        Args:
            integration_name: Name of the integration to transition
            target_mode: Target mode to transition the integration to.
                PRODUCTION: Transition the integration to production.
                STAGING: Transition the integration to staging.
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the details of the transitioned integration

        Raises:
            APIError: If the API request fails
        """
        return _transition_integration(
            self._client, integration_name, target_mode, api_version
        )

    def update_integration(
        self,
        integration_name: str,
        display_name: str | None = None,
        description: str | None = None,
        image_base64: str | None = None,
        svg_icon: str | None = None,
        python_version: PythonVersion | None = None,
        parameters: list[dict[str, Any]] | None = None,
        categories: list[str] | None = None,
        integration_type: IntegrationType | None = None,
        staging: bool | None = None,
        dependencies_to_remove: list[str] | None = None,
        update_mask: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Updates an existing integration's metadata. Use this method to
        change the description or display image of a custom integration.

        Args:
            integration_name: Name of the integration to update
            display_name: Optional. The display name of the integration
                (max 150 characters)
            description: Optional. The integration's description
                (max 1,500 characters)
            image_base64: Optional. The integration's image encoded as a
                base64 string (max 5 MB)
            svg_icon: Optional. The integration's SVG icon (max 1 MB)
            python_version: Optional. The integration's Python version
            parameters: Optional. Integration parameters (max 50)
            categories: Optional. Integration categories (max 50)
            integration_type: Optional. The integration's type
                (response/extension)
            staging: Optional. True if the integration is in staging mode
            dependencies_to_remove: Optional. List of dependencies to
                remove from the integration
            update_mask: Optional. Comma-separated list of fields to
                update. If not provided, all non-None fields are updated.
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing the details of the updated integration

        Raises:
            APIError: If the API request fails
        """
        return _update_integration(
            self._client,
            integration_name,
            display_name=display_name,
            description=description,
            image_base64=image_base64,
            svg_icon=svg_icon,
            python_version=python_version,
            parameters=parameters,
            categories=categories,
            integration_type=integration_type,
            staging=staging,
            dependencies_to_remove=dependencies_to_remove,
            update_mask=update_mask,
            api_version=api_version,
        )

    def update_custom_integration(
        self,
        integration_name: str,
        display_name: str | None = None,
        description: str | None = None,
        image_base64: str | None = None,
        svg_icon: str | None = None,
        python_version: PythonVersion | None = None,
        parameters: list[dict[str, Any]] | None = None,
        categories: list[str] | None = None,
        integration_type: IntegrationType | None = None,
        staging: bool | None = None,
        dependencies_to_remove: list[str] | None = None,
        update_mask: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Updates a custom integration definition, including its
        parameters and dependencies. Use this method to refine the
        operational behavior of a locally developed integration.

        Args:
            integration_name: Name of the integration to update
            display_name: Optional. The display name of the integration
                (max 150 characters)
            description: Optional. The integration's description
                (max 1,500 characters)
            image_base64: Optional. The integration's image encoded as a
                base64 string (max 5 MB)
            svg_icon: Optional. The integration's SVG icon (max 1 MB)
            python_version: Optional. The integration's Python version
            parameters: Optional. Integration parameters (max 50)
            categories: Optional. Integration categories (max 50)
            integration_type: Optional. The integration's type
                (response/extension)
            staging: Optional. True if the integration is in staging mode
            dependencies_to_remove: Optional. List of dependencies to
                remove from the integration
            update_mask: Optional. Comma-separated list of fields to
                update. If not provided, all non-None fields are updated.
            api_version: API version to use for the request.
                Default is V1BETA.

        Returns:
            Dict containing:
                - successful: Whether the integration was updated
                    successfully
                - integration: The updated integration (if successful)
                - dependencies: Dependency installation statuses
                    (if failed)

        Raises:
            APIError: If the API request fails
        """
        return _update_custom_integration(
            self._client,
            integration_name,
            display_name=display_name,
            description=description,
            image_base64=image_base64,
            svg_icon=svg_icon,
            python_version=python_version,
            parameters=parameters,
            categories=categories,
            integration_type=integration_type,
            staging=staging,
            dependencies_to_remove=dependencies_to_remove,
            update_mask=update_mask,
            api_version=api_version,
        )

    # -------------------------------------------------------------------------
    # Integration Instances methods
    # -------------------------------------------------------------------------

    def list_integration_instances(
        self,
        integration_name: str,
        page_size: int | None = None,
        page_token: str | None = None,
        filter_string: str | None = None,
        order_by: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
        as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """List all instances for a specific integration.

        Use this method to browse the configured integration instances
        available for a custom or third-party product across different
        environments.

        Args:
            integration_name: Name of the integration to list instances
                for.
            page_size: Maximum number of integration instances to
                return.
            page_token: Page token from a previous call to retrieve the
                next page.
            filter_string: Filter expression to filter integration
                instances.
            order_by: Field to sort the integration instances by.
            api_version: API version to use for the request. Default is
                V1BETA.
            as_list: If True, return a list of integration instances
                instead of a dict with integration instances list and
                nextPageToken.

        Returns:
            If as_list is True: List of integration instances.
            If as_list is False: Dict with integration instances list
                and nextPageToken.

        Raises:
            APIError: If the API request fails.
        """
        return _list_integration_instances(
            self._client,
            integration_name,
            page_size=page_size,
            page_token=page_token,
            filter_string=filter_string,
            order_by=order_by,
            api_version=api_version,
            as_list=as_list,
        )

    def get_integration_instance(
        self,
        integration_name: str,
        integration_instance_id: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get a single instance for a specific integration.

        Use this method to retrieve the specific configuration,
        connection status, and environment mapping for an active
        integration.

        Args:
            integration_name: Name of the integration the instance
                belongs to.
            integration_instance_id: ID of the integration instance to
                retrieve.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing details of the specified
                IntegrationInstance.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_instance(
            self._client,
            integration_name,
            integration_instance_id,
            api_version=api_version,
        )

    def delete_integration_instance(
        self,
        integration_name: str,
        integration_instance_id: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> None:
        """Delete a specific integration instance.

        Use this method to permanently remove an integration instance
        and stop all associated automated tasks (connectors or jobs)
        using this instance.

        Args:
            integration_name: Name of the integration the instance
                belongs to.
            integration_instance_id: ID of the integration instance to
                delete.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            None

        Raises:
            APIError: If the API request fails.
        """
        return _delete_integration_instance(
            self._client,
            integration_name,
            integration_instance_id,
            api_version=api_version,
        )

    def create_integration_instance(
        self,
        integration_name: str,
        environment: str,
        display_name: str | None = None,
        description: str | None = None,
        parameters: (
            list[dict[str, Any] | IntegrationInstanceParameter] | None
        ) = None,
        agent: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Create a new integration instance for a specific
        integration.

        Use this method to establish a new integration instance to a
        custom or third-party security product for a specific
        environment. All mandatory parameters required by the
        integration definition must be provided.

        Args:
            integration_name: Name of the integration to create the
                instance for.
            environment: The integration instance environment. Required.
            display_name: The display name of the integration instance.
                Automatically generated if not provided. Maximum 110
                characters.
            description: The integration instance description. Maximum
                1500 characters.
            parameters: List of IntegrationInstanceParameter instances
                or dicts.
            agent: Agent identifier for a remote integration instance.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the newly created IntegrationInstance
                resource.

        Raises:
            APIError: If the API request fails.
        """
        return _create_integration_instance(
            self._client,
            integration_name,
            environment,
            display_name=display_name,
            description=description,
            parameters=parameters,
            agent=agent,
            api_version=api_version,
        )

    def update_integration_instance(
        self,
        integration_name: str,
        integration_instance_id: str,
        environment: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        parameters: (
            list[dict[str, Any] | IntegrationInstanceParameter] | None
        ) = None,
        agent: str | None = None,
        update_mask: str | None = None,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Update an existing integration instance.

        Use this method to modify connection parameters (e.g., rotate
        an API key), change the display name, or update the description
        of a configured integration instance.

        Args:
            integration_name: Name of the integration the instance
                belongs to.
            integration_instance_id: ID of the integration instance to
                update.
            environment: The integration instance environment.
            display_name: The display name of the integration instance.
                Maximum 110 characters.
            description: The integration instance description. Maximum
                1500 characters.
            parameters: List of IntegrationInstanceParameter instances
                or dicts.
            agent: Agent identifier for a remote integration instance.
            update_mask: Comma-separated list of fields to update. If
                omitted, the mask is auto-generated from whichever
                fields are provided. Example:
                "displayName,description".
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the updated IntegrationInstance resource.

        Raises:
            APIError: If the API request fails.
        """
        return _update_integration_instance(
            self._client,
            integration_name,
            integration_instance_id,
            environment=environment,
            display_name=display_name,
            description=description,
            parameters=parameters,
            agent=agent,
            update_mask=update_mask,
            api_version=api_version,
        )

    def execute_integration_instance_test(
        self,
        integration_name: str,
        integration_instance_id: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Execute a connectivity test for a specific integration
        instance.

        Use this method to verify that SecOps can successfully
        communicate with the third-party security product using the
        provided credentials.

        Args:
            integration_name: Name of the integration the instance
                belongs to.
            integration_instance_id: ID of the integration instance to
                test.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the test results with the following fields:
                - successful: Indicates if the test was successful.
                - message: Test result message (optional).

        Raises:
            APIError: If the API request fails.
        """
        return _execute_integration_instance_test(
            self._client,
            integration_name,
            integration_instance_id,
            api_version=api_version,
        )

    def get_integration_instance_affected_items(
        self,
        integration_name: str,
        integration_instance_id: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """List all playbooks that depend on a specific integration
        instance.

        Use this method to perform impact analysis before deleting or
        significantly changing a connection configuration.

        Args:
            integration_name: Name of the integration the instance
                belongs to.
            integration_instance_id: ID of the integration instance to
                fetch affected items for.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing a list of AffectedPlaybookResponse objects
                that depend on the specified integration instance.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_instance_affected_items(
            self._client,
            integration_name,
            integration_instance_id,
            api_version=api_version,
        )

    def get_default_integration_instance(
        self,
        integration_name: str,
        api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get the system default configuration for a specific
        integration.

        Use this method to retrieve the baseline integration instance
        details provided for a commercial product.

        Args:
            integration_name: Name of the integration to fetch the
                default instance for.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the default IntegrationInstance resource.

        Raises:
            APIError: If the API request fails.
        """
        return _get_default_integration_instance(
            self._client,
            integration_name,
            api_version=api_version,
        )

    # -------------------------------------------------------------------------
    # Integration Action methods
    # -------------------------------------------------------------------------

    def list_integration_actions(
            self,
            integration_name: str,
            page_size: int | None = None,
            page_token: str | None = None,
            filter_string: str | None = None,
            order_by: str | None = None,
            expand: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
            as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get a list of actions for a given integration.

        Args:
            integration_name: Name of the integration to get actions for
            page_size: Number of results to return per page
            page_token: Token for the page to retrieve
            filter_string: Filter expression to filter actions
            order_by: Field to sort the actions by
            expand: Comma-separated list of fields to expand in the response
            api_version: API version to use for the request. Default is V1BETA.
            as_list: If True, return a list of actions instead of a dict with
                actions list and nextPageToken.

        Returns:
            If as_list is True: List of actions.
            If as_list is False: Dict with actions list and nextPageToken.

        Raises:
            APIError: If the API request fails
        """
        return _list_integration_actions(
            self,
            integration_name,
            page_size=page_size,
            page_token=page_token,
            filter_string=filter_string,
            order_by=order_by,
            expand=expand,
            api_version=api_version,
            as_list=as_list,
        )

    def get_integration_action(
            self,
            integration_name: str,
            action_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get details of a specific action for a given integration.

        Args:
            integration_name: Name of the integration the action belongs to
            action_id: ID of the action to retrieve
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict containing details of the specified action.

        Raises:
            APIError: If the API request fails
        """
        return _get_integration_action(
            self,
            integration_name,
            action_id,
            api_version=api_version,
        )

    def delete_integration_action(
            self,
            integration_name: str,
            action_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> None:
        """Delete a specific action from a given integration.

        Args:
            integration_name: Name of the integration the action belongs to
            action_id: ID of the action to delete
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            None

        Raises:
            APIError: If the API request fails
        """
        return _delete_integration_action(
            self,
            integration_name,
            action_id,
            api_version=api_version,
        )

    def create_integration_action(
            self,
            integration_name: str,
            display_name: str,
            script: str,
            timeout_seconds: int,
            enabled: bool,
            script_result_name: str,
            is_async: bool,
            description: str | None = None,
            default_result_value: str | None = None,
            async_polling_interval_seconds: int | None = None,
            async_total_timeout_seconds: int | None = None,
            dynamic_results: list[dict[str, Any]] | None = None,
            parameters: list[dict[str, Any]] | None = None,
            ai_generated: bool | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Create a new custom action for a given integration.

        Args:
            integration_name: Name of the integration to
                create the action for.
            display_name: Action's display name.
                Maximum 150 characters. Required.
            script: Action's Python script. Maximum size 5MB. Required.
            timeout_seconds: Action timeout in seconds. Maximum 1200. Required.
            enabled: Whether the action is enabled or disabled. Required.
            script_result_name: Field name that holds the script result.
                Maximum 100 characters. Required.
            is_async: Whether the action is asynchronous. Required.
            description: Action's description. Maximum 400 characters. Optional.
            default_result_value: Action's default result value.
                Maximum 1000 characters. Optional.
            async_polling_interval_seconds: Polling interval
                in seconds for async actions.
                Cannot exceed total timeout. Optional.
            async_total_timeout_seconds: Total async timeout in seconds. Maximum
                1209600 (14 days). Optional.
            dynamic_results: List of dynamic result metadata dicts.
                Max 50. Optional.
            parameters: List of action parameter dicts. Max 50. Optional.
            ai_generated: Whether the action was generated by AI. Optional.
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict containing the newly created IntegrationAction resource.

        Raises:
            APIError: If the API request fails.
        """
        return _create_integration_action(
            self,
            integration_name,
            display_name,
            script,
            timeout_seconds,
            enabled,
            script_result_name,
            is_async,
            description=description,
            default_result_value=default_result_value,
            async_polling_interval_seconds=async_polling_interval_seconds,
            async_total_timeout_seconds=async_total_timeout_seconds,
            dynamic_results=dynamic_results,
            parameters=parameters,
            ai_generated=ai_generated,
            api_version=api_version,
        )

    def update_integration_action(
            self,
            integration_name: str,
            action_id: str,
            display_name: str | None = None,
            script: str | None = None,
            timeout_seconds: int | None = None,
            enabled: bool | None = None,
            script_result_name: str | None = None,
            is_async: bool | None = None,
            description: str | None = None,
            default_result_value: str | None = None,
            async_polling_interval_seconds: int | None = None,
            async_total_timeout_seconds: int | None = None,
            dynamic_results: list[dict[str, Any]] | None = None,
            parameters: list[dict[str, Any]] | None = None,
            ai_generated: bool | None = None,
            update_mask: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Update an existing custom action for a given integration.

        Only custom actions can be updated; predefined commercial actions are
        immutable.

        Args:
            integration_name: Name of the integration the action belongs to.
            action_id: ID of the action to update.
            display_name: Action's display name. Maximum 150 characters.
            script: Action's Python script. Maximum size 5MB.
            timeout_seconds: Action timeout in seconds. Maximum 1200.
            enabled: Whether the action is enabled or disabled.
            script_result_name: Field name that holds the script result.
                Maximum 100 characters.
            is_async: Whether the action is asynchronous.
            description: Action's description. Maximum 400 characters.
            default_result_value: Action's default result value.
                Maximum 1000 characters.
            async_polling_interval_seconds: Polling interval
                in seconds for async actions. Cannot exceed total timeout.
            async_total_timeout_seconds: Total async timeout in seconds. Maximum
                1209600 (14 days).
            dynamic_results: List of dynamic result metadata dicts. Max 50.
            parameters: List of action parameter dicts. Max 50.
            ai_generated: Whether the action was generated by AI.
            update_mask: Comma-separated list of fields to update. If omitted,
                the mask is auto-generated from whichever fields are provided.
                Example: "displayName,script".
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict containing the updated IntegrationAction resource.

        Raises:
            APIError: If the API request fails.
        """
        return _update_integration_action(
            self,
            integration_name,
            action_id,
            display_name=display_name,
            script=script,
            timeout_seconds=timeout_seconds,
            enabled=enabled,
            script_result_name=script_result_name,
            is_async=is_async,
            description=description,
            default_result_value=default_result_value,
            async_polling_interval_seconds=async_polling_interval_seconds,
            async_total_timeout_seconds=async_total_timeout_seconds,
            dynamic_results=dynamic_results,
            parameters=parameters,
            ai_generated=ai_generated,
            update_mask=update_mask,
            api_version=api_version,
        )

    def execute_integration_action_test(
            self,
            integration_name: str,
            test_case_id: int,
            action: dict[str, Any],
            scope: str,
            integration_instance_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Execute a test run of an integration action's script.

        Use this method to verify custom action logic, connectivity, and data
        parsing against a specified integration instance and test case before
        making the action available in playbooks.

        Args:
            integration_name: Name of the integration the action belongs to.
            test_case_id: ID of the action test case.
            action: Dict containing the IntegrationAction to test.
            scope: The action test scope.
            integration_instance_id: The integration instance ID to use.
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict with the test execution results with the following fields:
                - output: The script output.
                - debugOutput: The script debug output.
                - resultJson: The result JSON if it exists (optional).
                - resultName: The script result name (optional).

        Raises:
            APIError: If the API request fails.
        """
        return _execute_integration_action_test(
            self,
            integration_name,
            test_case_id,
            action,
            scope,
            integration_instance_id,
            api_version=api_version,
        )

    def get_integration_actions_by_environment(
            self,
            integration_name: str,
            environments: list[str],
            include_widgets: bool,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """List actions executable within specified environments.

        Use this method to discover which automated tasks have active
        integration instances configured for a particular
        network or organizational context.

        Args:
            integration_name: Name of the integration to fetch actions for.
            environments: List of environments to filter actions by.
            include_widgets: Whether to include widget actions in the response.
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict containing a list of IntegrationAction objects that have
            integration instances in one of the given environments.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_actions_by_environment(
            self,
            integration_name,
            environments,
            include_widgets,
            api_version=api_version,
        )

    def get_integration_action_template(
            self,
            integration_name: str,
            is_async: bool = False,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Retrieve a default Python script template for a new
        integration action.

        Use this method to jumpstart the development of a custom automated task
        by providing boilerplate code for either synchronous or asynchronous
        operations.

        Args:
            integration_name: Name of the integration to fetch the template for.
            is_async: Whether to fetch a template for an async action. Default
                is False.
            api_version: API version to use for the request. Default is V1BETA.

        Returns:
            Dict containing the IntegrationAction template.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_action_template(
            self,
            integration_name,
            is_async=is_async,
            api_version=api_version,
        )

    # -------------------------------------------------------------------------
    # Integration Action Revisions methods
    # -------------------------------------------------------------------------

    def list_integration_action_revisions(
            self,
            integration_name: str,
            action_id: str,
            page_size: int | None = None,
            page_token: str | None = None,
            filter_string: str | None = None,
            order_by: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
            as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """List all revisions for a specific integration action.

        Use this method to view the history of changes to an action,
        enabling version control and the ability to rollback to
        previous configurations.

        Args:
            integration_name: Name of the integration the action
                belongs to.
            action_id: ID of the action to list revisions for.
            page_size: Maximum number of revisions to return.
            page_token: Page token from a previous call to retrieve the
                next page.
            filter_string: Filter expression to filter revisions.
            order_by: Field to sort the revisions by.
            api_version: API version to use for the request. Default is
                V1BETA.
            as_list: If True, return a list of revisions instead of a
                dict with revisions list and nextPageToken.

        Returns:
            If as_list is True: List of action revisions.
            If as_list is False: Dict with action revisions list and
                nextPageToken.

        Raises:
            APIError: If the API request fails.
        """
        return _list_integration_action_revisions(
            self,
            integration_name,
            action_id,
            page_size=page_size,
            page_token=page_token,
            filter_string=filter_string,
            order_by=order_by,
            api_version=api_version,
            as_list=as_list,
        )

    def delete_integration_action_revision(
            self,
            integration_name: str,
            action_id: str,
            revision_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> None:
        """Delete a specific action revision.

        Use this method to permanently remove a revision from the
        action's history.

        Args:
            integration_name: Name of the integration the action
                belongs to.
            action_id: ID of the action the revision belongs to.
            revision_id: ID of the revision to delete.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            None

        Raises:
            APIError: If the API request fails.
        """
        return _delete_integration_action_revision(
            self,
            integration_name,
            action_id,
            revision_id,
            api_version=api_version,
        )

    def create_integration_action_revision(
            self,
            integration_name: str,
            action_id: str,
            action: dict[str, Any],
            comment: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Create a new revision for an integration action.

        Use this method to save a snapshot of the current action
        configuration before making changes, enabling easy rollback if
        needed.

        Args:
            integration_name: Name of the integration the action
                belongs to.
            action_id: ID of the action to create a revision for.
            action: The action object to save as a revision.
            comment: Optional comment describing the revision.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the newly created ActionRevision resource.

        Raises:
            APIError: If the API request fails.
        """
        return _create_integration_action_revision(
            self,
            integration_name,
            action_id,
            action,
            comment=comment,
            api_version=api_version,
        )

    def rollback_integration_action_revision(
            self,
            integration_name: str,
            action_id: str,
            revision_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Rollback an integration action to a previous revision.

        Use this method to restore an action to a previously saved
        state, reverting any changes made since that revision.

        Args:
            integration_name: Name of the integration the action
                belongs to.
            action_id: ID of the action to rollback.
            revision_id: ID of the revision to rollback to.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the rolled back IntegrationAction resource.

        Raises:
            APIError: If the API request fails.
        """
        return _rollback_integration_action_revision(
            self,
            integration_name,
            action_id,
            revision_id,
            api_version=api_version,
        )

    # -------------------------------------------------------------------------
    # Integration Manager methods
    # -------------------------------------------------------------------------

    def list_integration_managers(
            self,
            integration_name: str,
            page_size: int | None = None,
            page_token: str | None = None,
            filter_string: str | None = None,
            order_by: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
            as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """List all managers defined for a specific integration.

        Use this method to discover the library of managers available
        within a particular integration's scope.

        Args:
            integration_name: Name of the integration to list managers
                for.
            page_size: Maximum number of managers to return. Defaults to
                100, maximum is 100.
            page_token: Page token from a previous call to retrieve the
                next page.
            filter_string: Filter expression to filter managers.
            order_by: Field to sort the managers by.
            api_version: API version to use for the request. Default is
                V1BETA.
            as_list: If True, return a list of managers instead of a
                dict with managers list and nextPageToken.

        Returns:
            If as_list is True: List of managers.
            If as_list is False: Dict with managers list and
                nextPageToken.

        Raises:
            APIError: If the API request fails.
        """
        return _list_integration_managers(
            self,
            integration_name,
            page_size=page_size,
            page_token=page_token,
            filter_string=filter_string,
            order_by=order_by,
            api_version=api_version,
            as_list=as_list,
        )

    def get_integration_manager(
            self,
            integration_name: str,
            manager_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get a single manager for a given integration.

        Use this method to retrieve the manager script and its metadata
        for review or reference.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager to retrieve.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing details of the specified IntegrationManager.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_manager(
            self,
            integration_name,
            manager_id,
            api_version=api_version,
        )

    def delete_integration_manager(
            self,
            integration_name: str,
            manager_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> None:
        """Delete a specific custom manager from a given integration.

        Note that deleting a manager may break components (actions,
        jobs) that depend on its code.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager to delete.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            None

        Raises:
            APIError: If the API request fails.
        """
        return _delete_integration_manager(
            self,
            integration_name,
            manager_id,
            api_version=api_version,
        )

    def create_integration_manager(
            self,
            integration_name: str,
            display_name: str,
            script: str,
            description: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Create a new custom manager for a given integration.

        Use this method to add a new shared code utility. Each manager
        must have a unique display name and a script containing valid
        Python logic for reuse across actions, jobs, and connectors.

        Args:
            integration_name: Name of the integration to create the
                manager for.
            display_name: Manager's display name. Maximum 150
                characters. Required.
            script: Manager's Python script. Maximum 5MB. Required.
            description: Manager's description. Maximum 400 characters.
                Optional.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the newly created IntegrationManager
                resource.

        Raises:
            APIError: If the API request fails.
        """
        return _create_integration_manager(
            self,
            integration_name,
            display_name,
            script,
            description=description,
            api_version=api_version,
        )

    def update_integration_manager(
            self,
            integration_name: str,
            manager_id: str,
            display_name: str | None = None,
            script: str | None = None,
            description: str | None = None,
            update_mask: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Update an existing custom manager for a given integration.

        Use this method to modify the shared code, adjust its
        description, or refine its logic across all components that
        import it.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager to update.
            display_name: Manager's display name. Maximum 150
                characters.
            script: Manager's Python script. Maximum 5MB.
            description: Manager's description. Maximum 400 characters.
            update_mask: Comma-separated list of fields to update. If
                omitted, the mask is auto-generated from whichever
                fields are provided. Example: "displayName,script".
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the updated IntegrationManager resource.

        Raises:
            APIError: If the API request fails.
        """
        return _update_integration_manager(
            self,
            integration_name,
            manager_id,
            display_name=display_name,
            script=script,
            description=description,
            update_mask=update_mask,
            api_version=api_version,
        )

    def get_integration_manager_template(
            self,
            integration_name: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Retrieve a default Python script template for a new
        integration manager.

        Use this method to quickly start developing new managers.

        Args:
            integration_name: Name of the integration to fetch the
                template for.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the IntegrationManager template.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_manager_template(
            self,
            integration_name,
            api_version=api_version,
        )

    # -------------------------------------------------------------------------
    # Integration Manager Revisions methods
    # -------------------------------------------------------------------------

    def list_integration_manager_revisions(
            self,
            integration_name: str,
            manager_id: str,
            page_size: int | None = None,
            page_token: str | None = None,
            filter_string: str | None = None,
            order_by: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
            as_list: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """List all revisions for a specific integration manager.

        Use this method to browse the version history and identify
        previous functional states of a manager.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager to list revisions for.
            page_size: Maximum number of revisions to return.
            page_token: Page token from a previous call to retrieve the
                next page.
            filter_string: Filter expression to filter revisions.
            order_by: Field to sort the revisions by.
            api_version: API version to use for the request. Default is
                V1BETA.
            as_list: If True, return a list of revisions instead of a
                dict with revisions list and nextPageToken.

        Returns:
            If as_list is True: List of revisions.
            If as_list is False: Dict with revisions list and
                nextPageToken.

        Raises:
            APIError: If the API request fails.
        """
        return _list_integration_manager_revisions(
            self,
            integration_name,
            manager_id,
            page_size=page_size,
            page_token=page_token,
            filter_string=filter_string,
            order_by=order_by,
            api_version=api_version,
            as_list=as_list,
        )

    def get_integration_manager_revision(
            self,
            integration_name: str,
            manager_id: str,
            revision_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Get a single revision for a specific integration manager.

        Use this method to retrieve a specific snapshot of an
        IntegrationManagerRevision for comparison or review.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager the revision belongs to.
            revision_id: ID of the revision to retrieve.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing details of the specified
                IntegrationManagerRevision.

        Raises:
            APIError: If the API request fails.
        """
        return _get_integration_manager_revision(
            self,
            integration_name,
            manager_id,
            revision_id,
            api_version=api_version,
        )

    def delete_integration_manager_revision(
            self,
            integration_name: str,
            manager_id: str,
            revision_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> None:
        """Delete a specific revision for a given integration manager.

        Use this method to clean up obsolete snapshots and manage the
        historical record of managers.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager the revision belongs to.
            revision_id: ID of the revision to delete.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            None

        Raises:
            APIError: If the API request fails.
        """
        return _delete_integration_manager_revision(
            self,
            integration_name,
            manager_id,
            revision_id,
            api_version=api_version,
        )

    def create_integration_manager_revision(
            self,
            integration_name: str,
            manager_id: str,
            manager: dict[str, Any],
            comment: str | None = None,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Create a new revision snapshot of the current integration
        manager.

        Use this method to establish a recovery point before making
        significant updates to a manager.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager to create a revision for.
            manager: Dict containing the IntegrationManager to snapshot.
            comment: Comment describing the revision. Maximum 400
                characters. Optional.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the newly created
                IntegrationManagerRevision resource.

        Raises:
            APIError: If the API request fails.
        """
        return _create_integration_manager_revision(
            self,
            integration_name,
            manager_id,
            manager,
            comment=comment,
            api_version=api_version,
        )

    def rollback_integration_manager_revision(
            self,
            integration_name: str,
            manager_id: str,
            revision_id: str,
            api_version: APIVersion | None = APIVersion.V1BETA,
    ) -> dict[str, Any]:
        """Revert the current manager definition to a previously saved
        revision.

        Use this method to rapidly recover a functional state for
        common code if an update causes operational issues in dependent
        actions or jobs.

        Args:
            integration_name: Name of the integration the manager
                belongs to.
            manager_id: ID of the manager to rollback.
            revision_id: ID of the revision to rollback to.
            api_version: API version to use for the request. Default is
                V1BETA.

        Returns:
            Dict containing the IntegrationManagerRevision rolled back
                to.

        Raises:
            APIError: If the API request fails.
        """
        return _rollback_integration_manager_revision(
            self,
            integration_name,
            manager_id,
            revision_id,
            api_version=api_version,
        )
