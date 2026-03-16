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
"""Provides log processing pipeline management for Chronicle."""

from typing import Any

from secops.chronicle.utils.format_utils import format_resource_id
from secops.chronicle.utils.request_utils import (
    chronicle_request,
    chronicle_paginated_request,
)


def list_log_processing_pipelines(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
    filter_expr: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """Lists log processing pipelines.

    Args:
        client: ChronicleClient instance.
        page_size: Maximum number of pipelines to return. If not
            specified, server determines the number.
        page_token: Page token from a previous list call to retrieve
            the next page.
        filter_expr: Filter expression (AIP-160) to restrict results.
        as_list: If True, return only the list of pipelines.
            If False, return dict with metadata and pagination tokens.

    Returns:
        If as_list is True: List of log processing pipelines.
        If as_list is False: Dict with logProcessingPipelines list and
            pagination metadata.

    Raises:
        APIError: If the API request fails.
    """
    extra_params = {}
    if filter_expr:
        extra_params["filter"] = filter_expr

    return chronicle_paginated_request(
        client,
        path="logProcessingPipelines",
        items_key="logProcessingPipelines",
        page_size=page_size,
        page_token=page_token,
        extra_params=extra_params if extra_params else None,
        as_list=as_list,
    )


def get_log_processing_pipeline(
    client: "ChronicleClient", pipeline_id: str
) -> dict[str, Any]:
    """Gets a log processing pipeline by ID.

    Args:
        client: ChronicleClient instance.
        pipeline_id: ID of the pipeline to retrieve.

    Returns:
        Dictionary containing pipeline information.

    Raises:
        APIError: If the API request fails.
    """

    extracted_pipeline_id = format_resource_id(pipeline_id)
    endpoint_path = f"logProcessingPipelines/{extracted_pipeline_id}"

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=endpoint_path,
        error_message="Failed to get log processing pipeline",
    )


def create_log_processing_pipeline(
    client: "ChronicleClient",
    pipeline: dict[str, Any],
    pipeline_id: str | None = None,
) -> dict[str, Any]:
    """Creates a new log processing pipeline.

    Args:
        client: ChronicleClient instance.
        pipeline: LogProcessingPipeline configuration dict containing:
            - displayName: Display name for the pipeline
            - description: Optional description
            - processors: List of processor configurations
            - customMetadata: Optional custom metadata list
        pipeline_id: Optional ID for the pipeline. If omitted, server
            assigns a unique ID.

    Returns:
        Dictionary containing the created pipeline.

    Raises:
        APIError: If the API request fails.
    """
    params: dict[str, Any] = {}
    if pipeline_id:
        params["logProcessingPipelineId"] = pipeline_id

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="logProcessingPipelines",
        params=params if params else None,
        json=pipeline,
        error_message="Failed to create log processing pipeline",
    )


def update_log_processing_pipeline(
    client: "ChronicleClient",
    pipeline_id: str,
    pipeline: dict[str, Any],
    update_mask: str | None = None,
) -> dict[str, Any]:
    """Updates a log processing pipeline.

    Args:
        client: ChronicleClient instance.
        pipeline_id: ID of the pipeline to update.
        pipeline: LogProcessingPipeline configuration dict with fields
            to update.
        update_mask: Optional comma-separated list of fields to update
            (e.g., "displayName,description"). If not included, all
            fields with default/non-default values will be overwritten.

    Returns:
        Dictionary containing the updated pipeline.

    Raises:
        APIError: If the API request fails.
    """
    extracted_pipeline_id = format_resource_id(pipeline_id)
    endpoint_path = f"logProcessingPipelines/{extracted_pipeline_id}"

    params: dict[str, Any] = {}
    if update_mask:
        params["updateMask"] = update_mask

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=endpoint_path,
        params=params if params else None,
        json=pipeline,
        error_message="Failed to patch log processing pipeline",
    )


def delete_log_processing_pipeline(
    client: "ChronicleClient", pipeline_id: str, etag: str | None = None
) -> dict[str, Any]:
    """Deletes a log processing pipeline.

    Args:
        client: ChronicleClient instance.
        pipeline_id: ID of the pipeline to delete.
        etag: Optional etag value. If provided, deletion only succeeds
            if the resource's current etag matches this value.

    Returns:
        Empty dictionary on successful deletion.

    Raises:
        APIError: If the API request fails.
    """

    extracted_pipeline_id = format_resource_id(pipeline_id)
    endpoint_path = f"logProcessingPipelines/{extracted_pipeline_id}"

    params: dict[str, Any] = {}
    if etag:
        params["etag"] = etag

    return chronicle_request(
        client,
        method="DELETE",
        endpoint_path=endpoint_path,
        params=params if params else None,
        error_message="Failed to delete log processing pipeline",
    )


def associate_streams(
    client: "ChronicleClient", pipeline_id: str, streams: list[dict[str, Any]]
) -> dict[str, Any]:
    """Associates streams with a log processing pipeline.

    Args:
        client: ChronicleClient instance.
        pipeline_id: ID of the pipeline to associate streams with.
        streams: List of stream dicts. Each stream can be:
            - {"logType": "LOG_TYPE_NAME"} or
            - {"feedId": "FEED_ID"}

    Returns:
        Empty dictionary on success.

    Raises:
        APIError: If the API request fails.
    """
    extracted_pipeline_id = format_resource_id(pipeline_id)
    endpoint_path = (
        f"logProcessingPipelines/{extracted_pipeline_id}:associateStreams"
    )

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=endpoint_path,
        json={"streams": streams},
        error_message="Failed to associate streams",
    )


def dissociate_streams(
    client: "ChronicleClient", pipeline_id: str, streams: list[dict[str, Any]]
) -> dict[str, Any]:
    """Dissociates streams from a log processing pipeline.

    Args:
        client: ChronicleClient instance.
        pipeline_id: ID of the pipeline to dissociate streams from.
        streams: List of stream dicts. Each stream can be:
            - {"logType": "LOG_TYPE_NAME"} or
            - {"feedId": "FEED_ID"}

    Returns:
        Empty dictionary on success.

    Raises:
        APIError: If the API request fails.
    """

    extracted_pipeline_id = format_resource_id(pipeline_id)
    endpoint_path = (
        f"logProcessingPipelines/{extracted_pipeline_id}:dissociateStreams"
    )

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=endpoint_path,
        json={"streams": streams},
        error_message="Failed to dissociate streams",
    )


def fetch_associated_pipeline(
    client: "ChronicleClient", stream: dict[str, Any]
) -> dict[str, Any]:
    """Fetches the pipeline associated with a specific stream.

    Args:
        client: ChronicleClient instance.
        stream: Stream dict, can be:
            - {"logType": "LOG_TYPE_NAME"} or
            - {"feedId": "FEED_ID"}

    Returns:
        Dictionary containing the associated pipeline.

    Raises:
        APIError: If the API request fails.
    """
    params = {}
    for key, value in stream.items():
        params[f"stream.{key}"] = value

    return chronicle_request(
        client,
        method="GET",
        endpoint_path="logProcessingPipelines:fetchAssociatedPipeline",
        params=params,
        error_message="Failed to fetch associated pipeline",
    )


def fetch_sample_logs_by_streams(
    client: "ChronicleClient",
    streams: list[dict[str, Any]],
    sample_logs_count: int | None = None,
) -> dict[str, Any]:
    """Fetches sample logs for specified streams.

    Args:
        client: ChronicleClient instance.
        streams: List of stream dicts. Each stream can be:
            - {"logType": "LOG_TYPE_NAME"} or
            - {"feedId": "FEED_ID"}
        sample_logs_count: Number of sample logs to fetch per stream.
            Default is 100. Max is 1000 or 4MB per stream.

    Returns:
        Dictionary containing:
            - logs: List of log objects
            - sampleLogs: List of base64-encoded log strings (deprecated)

    Raises:
        APIError: If the API request fails.
    """
    body = {"streams": streams}
    if sample_logs_count is not None:
        body["sampleLogsCount"] = sample_logs_count

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="logProcessingPipelines:fetchSampleLogsByStreams",
        json=body,
        error_message="Failed to fetch sample logs by streams",
    )


def test_pipeline(
    client: "ChronicleClient",
    pipeline: dict[str, Any],
    input_logs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Tests a log processing pipeline with input logs.

    Args:
        client: ChronicleClient instance.
        pipeline: LogProcessingPipeline configuration to test.
        input_logs: List of log objects to process through the pipeline.

    Returns:
        Dictionary containing:
            - logs: List of processed log objects

    Raises:
        APIError: If the API request fails.
    """
    body = {"logProcessingPipeline": pipeline, "inputLogs": input_logs}

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="logProcessingPipelines:testPipeline",
        json=body,
        error_message="Failed to test pipeline",
    )
