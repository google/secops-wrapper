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
"""Integration connector instance logs functionality for Chronicle."""

from typing import Any, TYPE_CHECKING

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.format_utils import format_resource_id
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)

if TYPE_CHECKING:
    from secops.chronicle.client import ChronicleClient


def list_connector_instance_logs(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter_string: str | None = None,
    order_by: str | None = None,
    api_version: APIVersion | None = APIVersion.V1BETA,
    as_list: bool = False,
) -> dict[str, Any] | list[dict[str, Any]]:
    """List all logs for a specific connector instance.

    Use this method to browse the execution history and diagnostic output of
    a connector. Supports filtering and pagination to efficiently navigate
    large volumes of log data.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance to list logs for.
        page_size: Maximum number of logs to return.
        page_token: Page token from a previous call to retrieve the next page.
        filter_string: Filter expression to filter logs.
        order_by: Field to sort the logs by.
        api_version: API version to use for the request. Default is V1BETA.
        as_list: If True, return a list of logs instead of a dict with logs
            list and nextPageToken.

    Returns:
        If as_list is True: List of logs.
        If as_list is False: Dict with logs list and nextPageToken.

    Raises:
        APIError: If the API request fails.
    """
    extra_params = {
        "filter": filter_string,
        "orderBy": order_by,
    }

    # Remove keys with None values
    extra_params = {k: v for k, v in extra_params.items() if v is not None}

    return chronicle_paginated_request(
        client,
        api_version=api_version,
        path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}/logs"
        ),
        items_key="logs",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params,
        as_list=as_list,
    )


def get_connector_instance_log(
    client: "ChronicleClient",
    integration_name: str,
    connector_id: str,
    connector_instance_id: str,
    log_id: str,
    api_version: APIVersion | None = APIVersion.V1BETA,
) -> dict[str, Any]:
    """Get a single log entry for a specific connector instance.

    Use this method to retrieve a specific log entry from a connector
    instance's execution, including its message, timestamp, and severity
    level. Useful for auditing and detailed troubleshooting of a specific
    connector run.

    Args:
        client: ChronicleClient instance.
        integration_name: Name of the integration the connector belongs to.
        connector_id: ID of the connector the instance belongs to.
        connector_instance_id: ID of the connector instance the log belongs to.
        log_id: ID of the log entry to retrieve.
        api_version: API version to use for the request. Default is V1BETA.

    Returns:
        Dict containing details of the specified ConnectorLog.

    Raises:
        APIError: If the API request fails.
    """
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=(
            f"integrations/{format_resource_id(integration_name)}/"
            f"connectors/{connector_id}/connectorInstances/"
            f"{connector_instance_id}/logs/{log_id}"
        ),
        api_version=api_version,
    )
