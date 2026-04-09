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
