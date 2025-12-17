#!/usr/bin/env python3
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
"""Integration tests for log processing pipeline endpoints.

These tests require valid credentials and API access.
"""
import pytest
import time
import uuid
import base64
from datetime import datetime, timezone
from secops import SecOpsClient
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON
from secops.exceptions import APIError


@pytest.mark.integration
def test_log_processing_pipeline_crud_workflow():
    """Test CRUD workflow for log processing pipelines."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique display name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Pipeline {unique_id}"

    # Pipeline configuration
    pipeline_config = {
        "displayName": display_name,
        "description": "Integration test pipeline",
        "processors": [
            {
                "filterProcessor": {
                    "include": {
                        "logMatchType": "REGEXP",
                        "logBodies": [".*"],
                    },
                    "errorMode": "IGNORE",
                }
            }
        ],
    }

    created_pipeline = None

    try:
        # Test CREATE
        print(f"Creating pipeline: {display_name}")
        created_pipeline = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config
        )

        # Extract pipeline ID from the name
        pipeline_id = created_pipeline.get("name", "").split("/")[-1]

        assert created_pipeline is not None
        assert "name" in created_pipeline
        assert created_pipeline.get("displayName") == display_name
        print(f"Pipeline created: {created_pipeline['name']}")

        # Wait for pipeline to be fully created
        time.sleep(2)

        # Test GET
        print(f"Getting pipeline: {pipeline_id}")
        retrieved_pipeline = chronicle.get_log_processing_pipeline(pipeline_id)
        assert retrieved_pipeline is not None
        assert retrieved_pipeline.get("displayName") == display_name
        print(f"Pipeline retrieved: {retrieved_pipeline['name']}")

        # Test LIST
        print("Listing pipelines")
        list_result = chronicle.list_log_processing_pipelines(page_size=10)
        assert "logProcessingPipelines" in list_result
        pipelines = list_result["logProcessingPipelines"]
        pipeline_ids = [p["name"].split("/")[-1] for p in pipelines]
        assert pipeline_id in pipeline_ids
        print(f"Found {len(pipelines)} pipelines")

        # Test PATCH
        updated_display_name = f"Updated Pipeline {unique_id}"
        updated_config = {
            "name": created_pipeline.get("name"),
            "displayName": updated_display_name,
            "description": "Updated description",
            "processors": created_pipeline.get("processors"),
        }
        print(f"Updating pipeline: {pipeline_id}")
        updated_pipeline = chronicle.update_log_processing_pipeline(
            pipeline_id=pipeline_id,
            pipeline=updated_config,
            update_mask="displayName,description",
        )
        assert updated_pipeline is not None
        assert updated_pipeline.get("displayName") == updated_display_name
        print(f"Pipeline updated: {updated_pipeline['displayName']}")

        # Verify update
        time.sleep(2)
        verified_pipeline = chronicle.get_log_processing_pipeline(pipeline_id)
        assert verified_pipeline.get("displayName") == updated_display_name
        print("Pipeline update verified")

    except APIError as e:
        print(f"Pipeline CRUD test failed: {str(e)}")
        pytest.fail(f"Pipeline CRUD test failed due to API error: {str(e)}")

    finally:
        # Test DELETE - cleanup
        if created_pipeline:
            try:
                print(f"Deleting pipeline: {pipeline_id}")
                chronicle.delete_log_processing_pipeline(pipeline_id)
                print("Pipeline deleted successfully")

                # Verify deletion
                time.sleep(2)
                try:
                    chronicle.get_log_processing_pipeline(pipeline_id)
                    pytest.fail("Pipeline still exists after deletion")
                except APIError:
                    print("Pipeline deletion verified")

            except APIError as e:
                print(f"Warning: Failed to delete test pipeline: {str(e)}")


@pytest.mark.integration
def test_log_processing_pipeline_stream_operations():
    """Test stream association and dissociation workflow."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique display name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Stream Test Pipeline {unique_id}"

    # Pipeline configuration
    pipeline_config = {
        "displayName": display_name,
        "description": "Integration test for stream operations",
        "processors": [
            {
                "filterProcessor": {
                    "include": {
                        "logMatchType": "REGEXP",
                        "logBodies": [".*"],
                    },
                    "errorMode": "IGNORE",
                }
            }
        ],
    }

    created_pipeline = None

    try:
        # Create pipeline
        print(f"Creating pipeline for stream test: {display_name}")
        created_pipeline = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config
        )

        # Extract pipeline ID from the name
        pipeline_id = created_pipeline.get("name", "").split("/")[-1]
        assert created_pipeline is not None
        print(f"Pipeline created: {created_pipeline['name']}")
        time.sleep(2)

        # Test ASSOCIATE STREAMS
        streams = [{"logType": "WINEVTLOG"}]
        print(f"Associating streams to pipeline: {pipeline_id}")
        associate_result = chronicle.associate_streams(
            pipeline_id=pipeline_id, streams=streams
        )
        assert associate_result is not None
        print("Streams associated successfully")
        time.sleep(2)

        # Test FETCH ASSOCIATED PIPELINE
        print("Fetching associated pipeline by stream")
        stream_query = {"logType": "WINEVTLOG"}
        associated_pipeline = chronicle.fetch_associated_pipeline(
            stream=stream_query
        )
        assert associated_pipeline is not None
        print(f"Associated pipeline: {associated_pipeline.get('name', 'N/A')}")

        # Test DISSOCIATE STREAMS
        print(f"Dissociating streams from pipeline: {pipeline_id}")
        dissociate_result = chronicle.dissociate_streams(
            pipeline_id=pipeline_id, streams=streams
        )
        assert dissociate_result is not None
        print("Streams dissociated successfully")

    except APIError as e:
        print(f"Stream operations test failed: {str(e)}")
        pytest.fail(f"Stream operations test failed due to API error: {str(e)}")

    finally:
        # Cleanup
        if created_pipeline:
            try:
                print(f"Deleting pipeline: {pipeline_id}")
                chronicle.delete_log_processing_pipeline(pipeline_id)
                print("Pipeline deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test pipeline: {str(e)}")


@pytest.mark.integration
def test_fetch_sample_logs_by_streams():
    """Test fetching sample logs by streams."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique display name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Sample Logs Pipeline {unique_id}"

    # Pipeline configuration
    pipeline_config = {
        "displayName": display_name,
        "description": "Pipeline for testing sample logs",
        "processors": [
            {
                "filterProcessor": {
                    "include": {
                        "logMatchType": "REGEXP",
                        "logBodies": [".*"],
                    },
                    "errorMode": "IGNORE",
                }
            }
        ],
    }

    pipeline_id = None
    try:
        # Create the pipeline
        print(f"Creating pipeline: {display_name}")
        created_pipeline = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config
        )
        pipeline_id = created_pipeline["name"].split("/")[-1]
        print(f"Created pipeline with ID: {pipeline_id}")

        # Associate CS_EDR log type with the pipeline
        streams = [{"logType": "CS_EDR"}]
        print(f"Associating streams: {streams}")
        chronicle.associate_streams(pipeline_id=pipeline_id, streams=streams)
        print("Streams associated successfully")

        # Wait briefly for association to propagate
        time.sleep(10)

        # Fetch sample logs for the log type
        print(f"Fetching sample logs for streams: {streams}")
        result = chronicle.fetch_sample_logs_by_streams(
            streams=streams, sample_logs_count=5
        )

        assert result is not None
        if not result or ("logs" not in result and "sampleLogs" not in result):
            pytest.skip("No sample logs found for CS_EDR log type")

        logs = result.get("logs", result.get("sampleLogs", []))
        print(f"Fetched sample logs: {len(logs)} logs")
        assert len(logs) > 0, "Expected at least one sample log"

    except APIError as e:
        print(f"Fetch sample logs test failed: {str(e)}")
        pytest.skip(
            f"Fetch sample logs test skipped due to API error: {str(e)}"
        )

    finally:
        # Cleanup: Delete the created pipeline
        if pipeline_id:
            try:
                print(f"Deleting pipeline: {pipeline_id}")
                chronicle.delete_log_processing_pipeline(pipeline_id)
                print("Test pipeline deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test pipeline: {str(e)}")


@pytest.mark.integration
def test_pipeline_testing_functionality():
    """Test the test_pipeline functionality."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Pipeline configuration for testing
    pipeline_config = {
        "displayName": "Test Pipeline Config",
        "processors": [
            {
                "filterProcessor": {
                    "include": {
                        "logMatchType": "REGEXP",
                        "logBodies": [".*"],
                    },
                    "errorMode": "IGNORE",
                }
            }
        ],
    }

    # Create test input logs
    current_time = datetime.now(timezone.utc).isoformat()
    log_data_1 = base64.b64encode(b"Sample log line 1").decode("utf-8")
    log_data_2 = base64.b64encode(b"Sample log line 2").decode("utf-8")

    input_logs = [
        {
            "data": log_data_1,
            "logEntryTime": current_time,
            "collectionTime": current_time,
        },
        {
            "data": log_data_2,
            "logEntryTime": current_time,
            "collectionTime": current_time,
        },
    ]

    try:
        print("Testing pipeline with input logs")
        print(f"Pipeline: {pipeline_config['displayName']}")
        print(f"Number of input logs: {len(input_logs)}")

        result = chronicle.test_pipeline(
            pipeline=pipeline_config, input_logs=input_logs
        )

        assert result is not None
        assert "logs" in result

        processed_logs = result.get("logs", [])
        print(f"Pipeline test completed: {len(processed_logs)} logs processed")

        if processed_logs:
            print("First processed log data present")
            assert len(processed_logs) > 0

    except APIError as e:
        print(f"Test pipeline functionality failed: {str(e)}")
        pytest.skip(
            f"Test pipeline functionality skipped due to API error: {str(e)}"
        )


@pytest.mark.integration
def test_list_pipelines_with_pagination():
    """Test listing pipelines with pagination."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        # Get first page with small page size
        print("Fetching first page of pipelines")
        first_page = chronicle.list_log_processing_pipelines(page_size=1)

        assert first_page is not None
        assert "logProcessingPipelines" in first_page
        pipelines = first_page.get("logProcessingPipelines", [])
        print(f"First page: {len(pipelines)} pipelines")

        # If there's a next page token, fetch next page
        next_token = first_page.get("nextPageToken")
        if next_token:
            print("Fetching second page of pipelines")
            second_page = chronicle.list_log_processing_pipelines(
                page_size=1, page_token=next_token
            )
            assert second_page is not None
            pipelines_2 = second_page.get("logProcessingPipelines", [])
            print(f"Second page: {len(pipelines_2)} pipelines")

            # Verify pagination works correctly
            if pipelines and pipelines_2:
                assert pipelines[0].get("name") != pipelines_2[0].get("name")
                print("Pagination verified successfully")
        else:
            print("No second page available for pagination test")

    except APIError as e:
        print(f"List pipelines pagination test failed: {str(e)}")
        pytest.skip(
            f"List pipelines pagination test skipped due to API error: {str(e)}"
        )
