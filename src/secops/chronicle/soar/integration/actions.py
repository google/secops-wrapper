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
"""Integration actions functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion, ActionParameter
from secops.chronicle.utils.format_utils import (
    format_resource_id,
    build_patch_body,
    remove_none_values,
)
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def list_integration_actions(
    client: "ChronicleClient",
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
        client: ChronicleClient instance
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
    field_map = remove_none_values({
        "filter": filter_string,
        "orderBy": order_by,
        "expand": expand,
    })

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path=f"integrations/{format_resource_id(integration_name)}/actions",
        items_key="actions",
        page_size=page_size,
        page_token=page_token,
        extra_params=field_map,
        as_list=as_list,
    )


def get_integration_action(
    client: "ChronicleClient",
    integration_name: str,
    action_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get details of a specific action for a given integration.

    Args:
        client: ChronicleClient instance
        integration_name: Name of the integration the action belongs to
        action_id: ID of the action to retrieve
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified action.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions/{action_id}",
        api_version=api_version,
    )


def delete_integration_action(
    client: "ChronicleClient",
    integration_name: str,
    action_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> None:
    """Delete a specific action from a given integration.

    Args:
        client: ChronicleClient instance
        integration_name: Name of the integration the action belongs to
        action_id: ID of the action to delete
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        None

    Raises:
        APIError: If the API request fails
    """
    chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions/{action_id}",
        api_version=api_version,
    )


def create_integration_action(
    client: "ChronicleClient",
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
    parameters: list[dict[str, Any] | ActionParameter] | None = None,
    ai_generated: bool | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Create a new custom action for a given integration.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to create the action for.
        display_name: Action's display name. Maximum 150 characters. Required.
        script: Action's Python script. Maximum size 5MB. Required.
        timeout_seconds: Action timeout in seconds. Maximum 1200. Required.
        enabled: Whether the action is enabled or disabled. Required.
        script_result_name: Field name that holds the script result.
            Maximum 100 characters. Required.
        is_async: Whether the action is asynchronous. Required.
        description: Action's description. Maximum 400 characters. Optional.
        default_result_value: Action's default result value.
            Maximum 1000 characters. Optional.
        async_polling_interval_seconds: Polling interval in seconds for async
            actions. Cannot exceed total timeout. Optional.
        async_total_timeout_seconds: Total async timeout in seconds.
            Maximum 1209600 (14 days). Optional.
        dynamic_results: List of dynamic result metadata dicts.
            Max 50. Optional.
        parameters: List of ActionParameter instances or dicts.
            Max 50. Optional.
        ai_generated: Whether the action was generated by AI. Optional.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the newly created IntegrationAction resource.

    Raises:
        APIError: If the API request fails.
    """
    resolved_parameters = (
        [
            p.to_dict() if isinstance(p, ActionParameter) else p
            for p in parameters
        ]
        if parameters is not None
        else None
    )

    body = remove_none_values({
        "displayName": display_name,
        "script": script,
        "timeoutSeconds": timeout_seconds,
        "enabled": enabled,
        "scriptResultName": script_result_name,
        "async": is_async,
        "description": description,
        "defaultResultValue": default_result_value,
        "asyncPollingIntervalSeconds": async_polling_interval_seconds,
        "asyncTotalTimeoutSeconds": async_total_timeout_seconds,
        "dynamicResults": dynamic_results,
        "parameters": resolved_parameters,
        "aiGenerated": ai_generated,
    })

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions",
        api_version=api_version,
        json=body,
    )


def update_integration_action(
    client: "ChronicleClient",
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
    parameters: list[dict[str, Any] | ActionParameter] | None = None,
    ai_generated: bool | None = None,
    update_mask: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Update an existing custom action for a given integration.

    Only custom actions can be updated; predefined commercial actions are
    immutable.

    Args:
        client: ChronicleClient instance.
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
        async_polling_interval_seconds: Polling interval in seconds for async
            actions. Cannot exceed total timeout.
        async_total_timeout_seconds: Total async timeout in seconds. Maximum
            1209600 (14 days).
        dynamic_results: List of dynamic result metadata dicts. Max 50.
        parameters: List of ActionParameter instances or dicts.
            Max 50. Optional.
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
    body, params = build_patch_body(
        field_map=[
            ("displayName", "displayName", display_name),
            ("script", "script", script),
            ("timeoutSeconds", "timeoutSeconds", timeout_seconds),
            ("enabled", "enabled", enabled),
            ("scriptResultName", "scriptResultName", script_result_name),
            ("async", "async", is_async),
            ("description", "description", description),
            ("defaultResultValue", "defaultResultValue", default_result_value),
            (
                "asyncPollingIntervalSeconds",
                "asyncPollingIntervalSeconds",
                async_polling_interval_seconds,
            ),
            (
                "asyncTotalTimeoutSeconds",
                "asyncTotalTimeoutSeconds",
                async_total_timeout_seconds,
            ),
            ("dynamicResults", "dynamicResults", dynamic_results),
            ("parameters", "parameters", parameters),
            ("aiGenerated", "aiGenerated", ai_generated),
        ],
        update_mask=update_mask,
    )

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions/{action_id}",
        api_version=api_version,
        json=body,
        params=params,
    )


def execute_integration_action_test(
    client: "ChronicleClient",
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
        client: ChronicleClient instance.
        integration_name: Name of the integration the action belongs to.
        test_case_id: ID of the action test case.
        action: Dict containing the IntegrationAction to test.
        scope: The action test scope.
        integration_instance_id: The integration instance ID to use.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the test execution results with the following fields:
            - output: The script output.
            - debugOutput: The script debug output.
            - resultJson: The result JSON if it exists (optional).
            - resultName: The script result name (optional).

    Raises:
        APIError: If the API request fails.
    """
    body = {
        "testCaseId": test_case_id,
        "action": action,
        "scope": scope,
        "integrationInstanceId": integration_instance_id,
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions:executeTest",
        api_version=api_version,
        json=body,
    )


def get_integration_actions_by_environment(
    client: "ChronicleClient",
    integration_name: str,
    environments: list[str],
    include_widgets: bool,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """List actions executable within specified environments.

    Use this method to discover which automated tasks have active integration
    instances configured for a particular network or organizational context.

    Args:
        client: ChronicleClient instance.
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
    params = {
        "environments": environments,
        "includeWidgets": include_widgets,
    }

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions:fetchActionsByEnvironment",
        api_version=api_version,
        params=params,
    )


def get_integration_action_template(
    client: "ChronicleClient",
    integration_name: str,
    is_async: bool = False,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Retrieve a default Python script template for a new integration action.

    Use this method to jumpstart the development of a custom automated task
    by providing boilerplate code for either synchronous or asynchronous
    operations.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration to fetch the template for.
        is_async: Whether to fetch a template for an async action. Default
            is False.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing the IntegrationAction template.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"integrations/{format_resource_id(integration_name)}"
        f"/actions:fetchTemplate",
        api_version=api_version,
        params={"async": is_async},
    )
