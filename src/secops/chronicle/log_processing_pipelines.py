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

from secops.exceptions import APIError


def list_log_processing_pipelines(
    client: "ChronicleClient",
    page_size: int | None = None,
    page_token: str | None = None,
    filter_expr: str | None = None,
) -> dict[str, Any]:
    """Lists log processing pipelines.

    Args:
        client: ChronicleClient instance.
        page_size: Maximum number of pipelines to return. If not
            specified, server determines the number.
        page_token: Page token from a previous list call to retrieve
            the next page.
        filter_expr: Filter expression (AIP-160) to restrict results.

    Returns:
        Dictionary containing:
            - logProcessingPipelines: List of pipeline dicts
            - nextPageToken: Token for next page (if more results exist)

    Raises:
        APIError: If the API request fails.
    """
    url = f"{client.base_url}/{client.instance_id}/logProcessingPipelines"

    params: dict[str, Any] = {}
    if page_size is not None:
        params["pageSize"] = page_size
    if page_token:
        params["pageToken"] = page_token
    if filter_expr:
        params["filter"] = filter_expr

    response = client.session.get(url, params=params)
    if response.status_code != 200:
        raise APIError(
            f"Failed to list log processing pipelines: {response.text}"
        )

    return response.json()


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
    if not pipeline_id.startswith("projects/"):
        url = (
            f"{client.base_url}/{client.instance_id}/"
            f"logProcessingPipelines/{pipeline_id}"
        )
    else:
        url = f"{client.base_url}/{pipeline_id}"

    response = client.session.get(url)
    if response.status_code != 200:
        raise APIError(
            f"Failed to get log processing pipeline: {response.text}"
        )

    return response.json()


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
    url = f"{client.base_url}/{client.instance_id}/logProcessingPipelines"

    params: dict[str, Any] = {}
    if pipeline_id:
        params["logProcessingPipelineId"] = pipeline_id

    response = client.session.post(url, json=pipeline, params=params)
    if response.status_code != 200:
        raise APIError(
            f"Failed to create log processing pipeline: {response.text}"
        )

    return response.json()


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
    if not pipeline_id.startswith("projects/"):
        url = (
            f"{client.base_url}/{client.instance_id}/"
            f"logProcessingPipelines/{pipeline_id}"
        )
    else:
        url = f"{client.base_url}/{pipeline_id}"

    params: dict[str, Any] = {}
    if update_mask:
        params["updateMask"] = update_mask

    response = client.session.patch(url, json=pipeline, params=params)
    if response.status_code != 200:
        raise APIError(
            f"Failed to patch log processing pipeline: {response.text}"
        )

    return response.json()


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
    if not pipeline_id.startswith("projects/"):
        url = (
            f"{client.base_url}/{client.instance_id}/"
            f"logProcessingPipelines/{pipeline_id}"
        )
    else:
        url = f"{client.base_url}/{pipeline_id}"

    params: dict[str, Any] = {}
    if etag:
        params["etag"] = etag

    response = client.session.delete(url, params=params)
    if response.status_code != 200:
        raise APIError(
            f"Failed to delete log processing pipeline: {response.text}"
        )

    return response.json()


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
    if not pipeline_id.startswith("projects/"):
        url = (
            f"{client.base_url}/{client.instance_id}/"
            f"logProcessingPipelines/{pipeline_id}:associateStreams"
        )
    else:
        url = f"{client.base_url}/{pipeline_id}:associateStreams"
    body = {"streams": streams}

    response = client.session.post(url, json=body)
    if response.status_code != 200:
        raise APIError(f"Failed to associate streams: {response.text}")

    return response.json()


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
    if not pipeline_id.startswith("projects/"):
        url = (
            f"{client.base_url}/{client.instance_id}/"
            f"logProcessingPipelines/{pipeline_id}:dissociateStreams"
        )
    else:
        url = f"{client.base_url}/{pipeline_id}:dissociateStreams"

    body = {"streams": streams}

    response = client.session.post(url, json=body)
    if response.status_code != 200:
        raise APIError(f"Failed to dissociate streams: {response.text}")

    return response.json()


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
    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"logProcessingPipelines:fetchAssociatedPipeline"
    )

    # Pass stream fields as separate query parameters with stream. prefix
    params = {}
    for key, value in stream.items():
        params[f"stream.{key}"] = value

    response = client.session.get(url, params=params)
    if response.status_code != 200:
        raise APIError(f"Failed to fetch associated pipeline: {response.text}")

    return response.json()


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
    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"logProcessingPipelines:fetchSampleLogsByStreams"
    )

    body = {"streams": streams}
    if sample_logs_count is not None:
        body["sampleLogsCount"] = sample_logs_count

    response = client.session.post(url, json=body)
    if response.status_code != 200:
        raise APIError(
            f"Failed to fetch sample logs by streams: {response.text}"
        )

    return response.json()


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
    url = (
        f"{client.base_url}/{client.instance_id}/"
        f"logProcessingPipelines:testPipeline"
    )

    body = {"logProcessingPipeline": pipeline, "inputLogs": input_logs}

    response = client.session.post(url, json=body)
    if response.status_code != 200:
        raise APIError(f"Failed to test pipeline: {response.text}")

    return response.json()
