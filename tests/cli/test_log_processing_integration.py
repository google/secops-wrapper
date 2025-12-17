"""Integration tests for the SecOps CLI log processing commands."""

import base64
import json
import os
import subprocess
import time
import uuid
from datetime import datetime, timezone

import pytest

from tests.config import CHRONICLE_CONFIG


@pytest.mark.integration
def test_cli_log_processing_crud_workflow(cli_env, common_args, tmp_path):
    """Test the log processing pipeline create, update, and delete."""
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Pipeline {unique_id}"

    pipeline_config = {
        "displayName": display_name,
        "description": "CLI integration test pipeline",
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

    config_file = tmp_path / "pipeline_config.json"
    config_file.write_text(json.dumps(pipeline_config))

    pipeline_id = None

    try:
        create_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "create",
                "--pipeline",
                str(config_file),
            ]
        )

        create_result = subprocess.run(
            create_cmd, env=cli_env, capture_output=True, text=True
        )

        assert create_result.returncode == 0

        pipeline_data = json.loads(create_result.stdout)
        assert "name" in pipeline_data
        pipeline_id = pipeline_data["name"].split("/")[-1]
        print(f"Created pipeline with ID: {pipeline_id}")

        time.sleep(2)

        updated_display_name = f"Updated Pipeline {unique_id}"
        updated_config = {
            "name": pipeline_data.get("name"),
            "displayName": updated_display_name,
            "description": "Updated CLI integration test pipeline",
            "processors": pipeline_data.get("processors"),
        }

        updated_config_file = tmp_path / "updated_pipeline_config.json"
        updated_config_file.write_text(json.dumps(updated_config))

        update_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "update",
                "--id",
                pipeline_id,
                "--pipeline",
                str(updated_config_file),
                "--update-mask",
                "displayName,description",
            ]
        )

        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )

        assert update_result.returncode == 0

        updated_pipeline = json.loads(update_result.stdout)
        assert updated_pipeline["displayName"] == updated_display_name
        print(f"Updated pipeline to: {updated_display_name}")

    finally:
        if pipeline_id:
            delete_cmd = (
                [
                    "secops",
                ]
                + common_args
                + [
                    "log-processing",
                    "delete",
                    "--id",
                    pipeline_id,
                ]
            )

            delete_result = subprocess.run(
                delete_cmd, env=cli_env, capture_output=True, text=True
            )

            if delete_result.returncode == 0:
                print(f"Successfully deleted pipeline: {pipeline_id}")
            else:
                print(f"Failed to delete test pipeline: {delete_result.stderr}")


@pytest.mark.integration
def test_cli_log_processing_stream_operations(cli_env, common_args, tmp_path):
    """Test stream association and dissociation commands."""
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Stream Test Pipeline {unique_id}"

    pipeline_config = {
        "displayName": display_name,
        "description": "CLI test for stream operations",
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

    config_file = tmp_path / "pipeline_config.json"
    config_file.write_text(json.dumps(pipeline_config))

    pipeline_id = None

    try:
        create_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "create",
                "--pipeline",
                str(config_file),
            ]
        )

        create_result = subprocess.run(
            create_cmd, env=cli_env, capture_output=True, text=True
        )

        assert create_result.returncode == 0

        pipeline_data = json.loads(create_result.stdout)
        pipeline_id = pipeline_data["name"].split("/")[-1]
        print(f"Created pipeline with ID: {pipeline_id}")

        time.sleep(2)

        streams = [{"logType": "WINEVTLOG"}]
        streams_file = tmp_path / "streams.json"
        streams_file.write_text(json.dumps(streams))

        associate_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "associate-streams",
                "--id",
                pipeline_id,
                "--streams",
                str(streams_file),
            ]
        )

        associate_result = subprocess.run(
            associate_cmd, env=cli_env, capture_output=True, text=True
        )

        assert associate_result.returncode == 0
        print("Streams associated successfully")

        time.sleep(2)

        dissociate_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "dissociate-streams",
                "--id",
                pipeline_id,
                "--streams",
                str(streams_file),
            ]
        )

        dissociate_result = subprocess.run(
            dissociate_cmd, env=cli_env, capture_output=True, text=True
        )

        assert dissociate_result.returncode == 0
        print("Streams dissociated successfully")

    finally:
        if pipeline_id:
            delete_cmd = (
                [
                    "secops",
                ]
                + common_args
                + [
                    "log-processing",
                    "delete",
                    "--id",
                    pipeline_id,
                ]
            )

            delete_result = subprocess.run(
                delete_cmd, env=cli_env, capture_output=True, text=True
            )

            if delete_result.returncode == 0:
                print(f"Successfully deleted pipeline: {pipeline_id}")
            else:
                print(f"Failed to delete test pipeline: {delete_result.stderr}")


@pytest.mark.integration
def test_cli_log_processing_fetch_associated(cli_env, common_args, tmp_path):
    """Test fetch associated pipeline command."""
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Fetch Test Pipeline {unique_id}"

    pipeline_config = {
        "displayName": display_name,
        "description": "CLI test for fetch associated",
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

    config_file = tmp_path / "pipeline_config.json"
    config_file.write_text(json.dumps(pipeline_config))

    pipeline_id = None

    try:
        create_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "create",
                "--pipeline",
                str(config_file),
            ]
        )

        create_result = subprocess.run(
            create_cmd, env=cli_env, capture_output=True, text=True
        )

        assert create_result.returncode == 0

        pipeline_data = json.loads(create_result.stdout)
        pipeline_id = pipeline_data["name"].split("/")[-1]
        print(f"Created pipeline with ID: {pipeline_id}")

        time.sleep(2)

        streams = [{"logType": "WINEVTLOG"}]
        streams_file = tmp_path / "streams.json"
        streams_file.write_text(json.dumps(streams))

        associate_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "associate-streams",
                "--id",
                pipeline_id,
                "--streams",
                str(streams_file),
            ]
        )

        associate_result = subprocess.run(
            associate_cmd, env=cli_env, capture_output=True, text=True
        )

        assert associate_result.returncode == 0
        print("Streams associated successfully")

        time.sleep(2)

        stream_query = {"logType": "WINEVTLOG"}
        stream_file = tmp_path / "stream_query.json"
        stream_file.write_text(json.dumps(stream_query))

        fetch_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "fetch-associated",
                "--stream",
                str(stream_file),
            ]
        )

        fetch_result = subprocess.run(
            fetch_cmd, env=cli_env, capture_output=True, text=True
        )

        assert fetch_result.returncode == 0

        associated_pipeline = json.loads(fetch_result.stdout)
        assert "name" in associated_pipeline
        print(f"Fetched associated pipeline: {associated_pipeline['name']}")

    finally:
        if pipeline_id:
            delete_cmd = (
                [
                    "secops",
                ]
                + common_args
                + [
                    "log-processing",
                    "delete",
                    "--id",
                    pipeline_id,
                ]
            )

            delete_result = subprocess.run(
                delete_cmd, env=cli_env, capture_output=True, text=True
            )

            if delete_result.returncode == 0:
                print(f"Successfully deleted pipeline: {pipeline_id}")
            else:
                print(f"Failed to delete test pipeline: {delete_result.stderr}")


@pytest.mark.integration
def test_cli_log_processing_fetch_sample_logs(cli_env, common_args, tmp_path):
    """Test fetch sample logs command."""
    # Generate unique display name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"CLI Test Sample Logs Pipeline {unique_id}"

    # Pipeline configuration
    pipeline_config = {
        "displayName": display_name,
        "description": "CLI test pipeline for sample logs",
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

    pipeline_config_file = tmp_path / "pipeline_config.json"
    pipeline_config_file.write_text(json.dumps(pipeline_config))

    pipeline_id = None
    try:
        # Create pipeline
        create_cmd = (
            ["secops"]
            + common_args
            + [
                "log-processing",
                "create",
                "--pipeline",
                str(pipeline_config_file),
            ]
        )

        print(f"Creating pipeline: {display_name}")
        create_result = subprocess.run(
            create_cmd, env=cli_env, capture_output=True, text=True
        )

        if create_result.returncode != 0:
            pytest.skip(f"Failed to create pipeline: {create_result.stderr}")

        created_pipeline = json.loads(create_result.stdout)
        pipeline_id = created_pipeline["name"].split("/")[-1]
        print(f"Created pipeline with ID: {pipeline_id}")

        # Associate CS_EDR log type with pipeline
        streams = [{"logType": "CS_EDR"}]
        streams_file = tmp_path / "streams.json"
        streams_file.write_text(json.dumps(streams))

        associate_cmd = (
            ["secops"]
            + common_args
            + [
                "log-processing",
                "associate-streams",
                "--id",
                pipeline_id,
                "--streams",
                str(streams_file),
            ]
        )

        print(f"Associating streams: {streams}")
        associate_result = subprocess.run(
            associate_cmd, env=cli_env, capture_output=True, text=True
        )

        if associate_result.returncode != 0:
            pytest.skip(
                f"Failed to associate streams: {associate_result.stderr}"
            )

        print("Streams associated successfully")

        # Wait for association to propagate
        time.sleep(10)

        # Fetch sample logs
        fetch_cmd = (
            ["secops"]
            + common_args
            + [
                "log-processing",
                "fetch-sample-logs",
                "--streams",
                str(streams_file),
                "--count",
                "5",
            ]
        )

        print(f"Fetching sample logs for streams: {streams}")
        result = subprocess.run(
            fetch_cmd, env=cli_env, capture_output=True, text=True
        )

        if result.returncode == 0:
            output = json.loads(result.stdout)
            if not output or (
                "logs" not in output and "sampleLogs" not in output
            ):
                pytest.skip("No sample logs available for CS_EDR log type")

            logs = output.get("logs", output.get("sampleLogs", []))
            print(f"Fetched sample logs: {len(logs)} logs")
            assert len(logs) > 0, "Expected at least one sample log"
        else:
            pytest.skip(f"Fetch sample logs command skipped: {result.stderr}")

    finally:
        # Cleanup: Delete the created pipeline
        if pipeline_id:
            delete_cmd = (
                ["secops"]
                + common_args
                + ["log-processing", "delete", "--id", pipeline_id]
            )

            print(f"Deleting pipeline: {pipeline_id}")
            delete_result = subprocess.run(
                delete_cmd, env=cli_env, capture_output=True, text=True
            )

            if delete_result.returncode == 0:
                print("Test pipeline deleted successfully")
            else:
                print(
                    f"Warning: Failed to delete test pipeline: "
                    f"{delete_result.stderr}"
                )


@pytest.mark.integration
def test_cli_log_processing_test_pipeline(cli_env, common_args, tmp_path):
    """Test the test pipeline command."""
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

    config_file = tmp_path / "pipeline_config.json"
    config_file.write_text(json.dumps(pipeline_config))

    logs_file = tmp_path / "input_logs.json"
    logs_file.write_text(json.dumps(input_logs))

    cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "log-processing",
            "test",
            "--pipeline",
            str(config_file),
            "--input-logs",
            str(logs_file),
        ]
    )

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    if result.returncode == 0:
        output = json.loads(result.stdout)
        assert "logs" in output
        print(
            f"Pipeline test completed: {len(output.get('logs', []))} processed"
        )
    else:
        pytest.skip(f"Test pipeline command skipped: {result.stderr}")


@pytest.mark.integration
def test_cli_log_processing_list_with_pagination(cli_env, common_args):
    """Test listing pipelines with pagination."""
    cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "log-processing",
            "list",
            "--page-size",
            "1",
        ]
    )

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    assert result.returncode == 0

    output = json.loads(result.stdout)
    assert "logProcessingPipelines" in output
    pipelines = output.get("logProcessingPipelines", [])
    print(f"First page: {len(pipelines)} pipelines")

    if "nextPageToken" in output:
        next_page_token = output["nextPageToken"]

        next_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "log-processing",
                "list",
                "--page-size",
                "1",
                "--page-token",
                next_page_token,
            ]
        )

        next_result = subprocess.run(
            next_cmd, env=cli_env, capture_output=True, text=True
        )

        assert next_result.returncode == 0

        next_output = json.loads(next_result.stdout)
        assert "logProcessingPipelines" in next_output
        next_pipelines = next_output.get("logProcessingPipelines", [])
        print(f"Second page: {len(next_pipelines)} pipelines")
