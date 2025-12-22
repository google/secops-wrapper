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
"""Example usage of the Google SecOps SDK for Log Processing Pipelines."""

import argparse
import base64
import json
import time
import uuid
from datetime import datetime, timezone

from secops import SecOpsClient


def get_client(project_id, customer_id, region):
    """Initialize and return the Chronicle client.

    Args:
        project_id: Google Cloud Project ID.
        customer_id: Chronicle Customer ID (UUID).
        region: Chronicle region (us or eu).

    Returns:
        Chronicle client instance.
    """
    client = SecOpsClient()
    chronicle = client.chronicle(
        customer_id=customer_id, project_id=project_id, region=region
    )
    return chronicle


def example_list_pipelines(chronicle):
    """Example 1: List Log Processing Pipelines."""
    print("\n=== Example 1: List Log Processing Pipelines ===")

    try:
        # List all pipelines
        response = chronicle.list_log_processing_pipelines()
        pipelines = response.get("logProcessingPipelines", [])

        print(f"\nFound {len(pipelines)} pipeline(s)")

        if pipelines:
            print("\nSample pipeline details:")
            sample_pipeline = pipelines[0]
            print(f"Name: {sample_pipeline.get('name')}")
            print(f"Display Name: {sample_pipeline.get('displayName')}")
            print(f"Description: {sample_pipeline.get('description', 'N/A')}")

            # Extract pipeline ID from the name
            pipeline_id = sample_pipeline.get("name", "").split("/")[-1]
            print(f"Pipeline ID: {pipeline_id}")

            # Print processor count
            processors = sample_pipeline.get("processors", [])
            print(f"Number of processors: {len(processors)}")
        else:
            print("No pipelines found in your Chronicle instance.")

    except Exception as e:
        print(f"Error listing pipelines: {e}")


def example_create_and_get_pipeline(chronicle):
    """Example 2: Create and Get Pipeline."""
    print("\n=== Example 2: Create and Get Pipeline ===")

    # Generate unique pipeline name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Pipeline {unique_id}"

    # Define a simple filter processor pipeline
    pipeline_config = {
        "displayName": display_name,
        "description": "Example pipeline created by SDK",
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
        "customMetadata": [
            {"key": "environment", "value": "test"},
            {"key": "created_by", "value": "sdk_example"},
        ],
    }

    created_pipeline = None

    try:
        # Create the pipeline
        print(f"\nCreating pipeline: {display_name}")
        created_pipeline = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config
        )

        # Extract pipeline ID from the name
        pipeline_id = created_pipeline.get("name", "").split("/")[-1]

        print(f"Pipeline created successfully!")
        print(f"Pipeline ID: {pipeline_id}")
        print(f"Display Name: {created_pipeline.get('displayName')}")

        # Wait for pipeline to be fully created
        time.sleep(2)

        # Get the pipeline to verify it was created
        print(f"\nRetrieving pipeline details for ID: {pipeline_id}")
        retrieved_pipeline = chronicle.get_log_processing_pipeline(pipeline_id)

        print("Pipeline details retrieved:")
        print(f"Name: {retrieved_pipeline.get('name')}")
        print(f"Display Name: {retrieved_pipeline.get('displayName')}")
        print(f"Description: {retrieved_pipeline.get('description', 'N/A')}")

    except Exception as e:
        print(f"Error creating or getting pipeline: {e}")

    finally:
        # Clean up: delete the pipeline if it was created
        if created_pipeline:
            try:
                pipeline_id = created_pipeline.get("name", "").split("/")[-1]
                print(f"\nCleaning up: Deleting pipeline ID: {pipeline_id}")
                chronicle.delete_log_processing_pipeline(pipeline_id)
                print("Pipeline deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test pipeline: {e}")


def example_update_pipeline(chronicle):
    """Example 3: Update (Patch) Pipeline."""
    print("\n=== Example 3: Update Pipeline ===")

    # Generate unique pipeline name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Pipeline {unique_id}"

    # Initial pipeline configuration
    pipeline_config = {
        "displayName": display_name,
        "description": "Original description",
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
        # Create the pipeline
        print(f"\nCreating pipeline to update: {display_name}")
        created_pipeline = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config
        )

        pipeline_id = created_pipeline.get("name", "").split("/")[-1]
        print(f"Pipeline created with ID: {pipeline_id}")

        # Wait for pipeline to be fully created
        time.sleep(2)

        # Update the pipeline with new display name and description
        updated_pipeline_config = {
            "name": created_pipeline.get("name"),
            "displayName": f"Updated {display_name}",
            "description": "Updated description via SDK",
            "processors": created_pipeline.get("processors"),
        }

        print("\nUpdating pipeline...")
        updated_pipeline = chronicle.update_log_processing_pipeline(
            pipeline_id=pipeline_id,
            pipeline=updated_pipeline_config,
            update_mask="displayName,description",
        )

        print("Pipeline updated successfully!")
        print(f"New Display Name: {updated_pipeline.get('displayName')}")
        print(f"New Description: {updated_pipeline.get('description', 'N/A')}")

    except Exception as e:
        print(f"Error updating pipeline: {e}")

    finally:
        # Clean up: delete the pipeline if it was created
        if created_pipeline:
            try:
                pipeline_id = created_pipeline.get("name", "").split("/")[-1]
                print(f"\nCleaning up: Deleting pipeline ID: {pipeline_id}")
                chronicle.delete_log_processing_pipeline(pipeline_id)
                print("Pipeline deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test pipeline: {e}")


def example_stream_association(chronicle):
    """Example 4: Associate and Dissociate Streams."""
    print("\n=== Example 4: Associate and Dissociate Streams ===")

    # Generate unique pipeline name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Pipeline {unique_id}"

    # Pipeline configuration
    pipeline_config = {
        "displayName": display_name,
        "description": "Pipeline for stream association example",
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
        # Create the pipeline
        print(f"\nCreating pipeline: {display_name}")
        created_pipeline = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config
        )

        pipeline_id = created_pipeline.get("name", "").split("/")[-1]
        print(f"Pipeline created with ID: {pipeline_id}")

        # Wait for pipeline to be fully created
        time.sleep(2)

        # Define streams to associate
        # Note: Replace with actual log type or feed ID from environment
        streams = [{"logType": "WINEVTLOG"}]

        print("\nAssociating streams with pipeline...")
        print(f"Streams: {json.dumps(streams, indent=2)}")

        chronicle.associate_streams(pipeline_id=pipeline_id, streams=streams)
        print("Streams associated successfully!")

        # Wait a moment
        time.sleep(2)

        # Dissociate the streams
        print("\nDissociating streams from pipeline...")
        chronicle.dissociate_streams(pipeline_id=pipeline_id, streams=streams)
        print("Streams dissociated successfully!")

    except Exception as e:
        print(f"Error in stream association operations: {e}")
        print(
            "Note: Make sure the log type or feed ID exists "
            "in your environment."
        )

    finally:
        # Clean up: delete the pipeline if it was created
        if created_pipeline:
            try:
                pipeline_id = created_pipeline.get("name", "").split("/")[-1]
                print(f"\nCleaning up: Deleting pipeline ID: {pipeline_id}")
                chronicle.delete_log_processing_pipeline(pipeline_id)
                print("Pipeline deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test pipeline: {e}")


def example_test_pipeline(chronicle):
    """Example 5: Test Pipeline with Sample Logs."""
    print("\n=== Example 5: Test Pipeline ===")

    # Define a pipeline configuration to test
    pipeline_config = {
        "displayName": "Test Pipeline (Not Created)",
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

    # Sample input logs with proper Log resource structure
    current_time = datetime.now(timezone.utc).isoformat()

    input_logs = [
        {
            "data": base64.b64encode(b"Sample log entry 1").decode("utf-8"),
            "logEntryTime": current_time,
            "collectionTime": current_time,
        },
        {
            "data": base64.b64encode(b"Sample log entry 2").decode("utf-8"),
            "logEntryTime": current_time,
            "collectionTime": current_time,
        },
    ]

    try:
        print("\nTesting pipeline configuration...")
        print(f"Pipeline: {pipeline_config['displayName']}")
        print(f"Number of input logs: {len(input_logs)}")

        result = chronicle.test_pipeline(
            pipeline=pipeline_config, input_logs=input_logs
        )

        processed_logs = result.get("logs", [])
        print(f"\nProcessed {len(processed_logs)} log(s)")

        if processed_logs:
            print("\nFirst processed log:")
            print(json.dumps(processed_logs[0], indent=2))

    except Exception as e:
        print(f"Error testing pipeline: {e}")
        print(
            "Note: This example uses simplified log structure. "
            "Actual logs may need more fields."
        )


def example_fetch_associated_pipeline(chronicle):
    """Example 6: Fetch Pipeline Associated with a Stream."""
    print("\n=== Example 6: Fetch Associated Pipeline ===")

    # Define a stream to query
    # Note: Replace with actual log type or feed ID from your environment
    stream = {"logType": "WINEVTLOG"}

    try:
        print(f"\nFetching pipeline for stream: {json.dumps(stream)}")
        result = chronicle.fetch_associated_pipeline(stream=stream)

        if result:
            print("\nAssociated pipeline found:")
            print(f"Name: {result.get('name')}")
            print(f"Display Name: {result.get('displayName')}")
            print(f"Description: {result.get('description', 'N/A')}")
        else:
            print("No pipeline associated with this stream.")

    except Exception as e:
        print(f"Error fetching associated pipeline: {e}")
        print(
            "Note: Make sure the stream exists and has an "
            "associated pipeline."
        )


def example_fetch_sample_logs(chronicle):
    """Example 7: Fetch Sample Logs by Streams."""
    print("\n=== Example 7: Fetch Sample Logs by Streams ===")

    # Define streams to fetch sample logs from
    # Note: Replace with actual log type or feed ID from your environment
    streams = [{"logType": "WINEVTLOG"}]

    try:
        print(f"\nFetching sample logs for streams: {json.dumps(streams)}")
        result = chronicle.fetch_sample_logs_by_streams(
            streams=streams, sample_logs_count=5
        )

        logs = result.get("logs", [])
        print(f"\nFetched {len(logs)} sample log(s)")

        if logs:
            print("\nFirst sample log:")
            print(json.dumps(logs[0], indent=2))
        else:
            print("No sample logs available for the specified streams.")

    except Exception as e:
        print(f"Error fetching sample logs: {e}")
        print("Note: Make sure the streams exist and have ingested logs.")


# Map of example functions
EXAMPLES = {
    "1": example_list_pipelines,
    "2": example_create_and_get_pipeline,
    "3": example_update_pipeline,
    "4": example_stream_association,
    "5": example_test_pipeline,
    "6": example_fetch_associated_pipeline,
    "7": example_fetch_sample_logs,
}


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(
        description="Run Chronicle Log Processing Pipeline examples"
    )
    parser.add_argument(
        "--project_id", required=True, help="Google Cloud Project ID"
    )
    parser.add_argument(
        "--customer_id", required=True, help="Chronicle Customer ID (UUID)"
    )
    parser.add_argument(
        "--region", default="us", help="Chronicle region (us or eu)"
    )
    parser.add_argument(
        "--example",
        "-e",
        help=(
            "Example number to run (1-7). "
            "If not specified, runs all examples."
        ),
    )

    args = parser.parse_args()

    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)

    if args.example:
        if args.example not in EXAMPLES:
            print(
                f"Invalid example number. Available examples: "
                f"{', '.join(EXAMPLES.keys())}"
            )
            return
        EXAMPLES[args.example](chronicle)
    else:
        # Run all examples in order
        for example_num in sorted(EXAMPLES.keys()):
            EXAMPLES[example_num](chronicle)


if __name__ == "__main__":
    main()
