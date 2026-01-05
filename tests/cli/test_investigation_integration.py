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
"""Integration tests for the SecOps CLI investigation commands."""

import json
import subprocess
from datetime import datetime, timedelta

import pytest

from tests.config import CHRONICLE_CONFIG


@pytest.mark.integration
def test_cli_investigation_list_and_get(cli_env, common_args):
    """Test investigation list and get commands in a workflow."""
    # Step 1: List investigations
    list_cmd = ["secops"] + common_args + ["investigation", "list"]

    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )
    assert list_result.returncode == 0

    try:
        list_output = json.loads(list_result.stdout)
        assert isinstance(list_output, dict)
        assert "investigations" in list_output
        assert isinstance(list_output["investigations"], list)
        print(f"Found {len(list_output['investigations'])} investigations")

        if not list_output.get("investigations"):
            pytest.skip("No investigations found to test get command")

        # Step 2: Get a specific investigation
        investigation_id = list_output["investigations"][0]["name"].split("/")[
            -1
        ]
        print(f"Testing get for investigation: {investigation_id}")

        get_cmd = (
            [
                "secops",
            ]
            + common_args
            + [
                "investigation",
                "get",
                "--id",
                investigation_id,
            ]
        )

        get_result = subprocess.run(
            get_cmd, env=cli_env, capture_output=True, text=True
        )
        assert get_result.returncode == 0

        get_output = json.loads(get_result.stdout)
        assert isinstance(get_output, dict)
        assert "name" in get_output
        assert investigation_id in get_output["name"]
        print(f"Successfully retrieved investigation: {get_output['name']}")

    except json.JSONDecodeError:
        pytest.fail("Failed to parse JSON output")


@pytest.mark.integration
def test_cli_investigation_list_with_pagination(cli_env, common_args):
    """Test the investigation list command with page size."""
    cmd = (
        [
            "secops",
        ]
        + common_args
        + ["investigation", "list", "--page-size", "5"]
    )

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    assert result.returncode == 0

    try:
        output = json.loads(result.stdout)
        assert isinstance(output, dict)
        assert "investigations" in output
        assert len(output["investigations"]) <= 5
        print(
            f"Retrieved {len(output['investigations'])} "
            f"investigations with page_size=5"
        )
    except json.JSONDecodeError:
        assert "Error:" not in result.stdout


@pytest.mark.integration
def test_cli_investigation_trigger_and_fetch_workflow(cli_env, common_args):
    """Test triggering and fetching associated investigations workflow."""
    # Step 1: Get an alert ID
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    alert_cmd = (
        ["secops"]
        + common_args
        + [
            "alert",
            "--start-time",
            start_time.isoformat(),
            "--end-time",
            end_time.isoformat(),
            "--max-alerts",
            "5",
        ]
    )

    alert_result = subprocess.run(
        alert_cmd, env=cli_env, capture_output=True, text=True
    )

    if alert_result.returncode != 0:
        pytest.skip("Could not fetch alerts to test trigger operation")

    try:
        alerts_data = json.loads(alert_result.stdout)
        if not alerts_data or "alerts" not in alerts_data:
            pytest.skip("No alerts available to test trigger operation")

        nested_alerts = alerts_data["alerts"].get("alerts", [])
        if not nested_alerts:
            pytest.skip("No alerts available to test trigger operation")

        alert_id = nested_alerts[0]["id"]
        print(f"Using alert ID: {alert_id}")

    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse alerts response")

    # Step 2: Trigger investigation
    trigger_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "investigation",
            "trigger",
            "--alert-id",
            alert_id,
        ]
    )

    trigger_result = subprocess.run(
        trigger_cmd, env=cli_env, capture_output=True, text=True
    )

    assert trigger_result.returncode == 0

    try:
        trigger_output = json.loads(trigger_result.stdout)
        assert isinstance(trigger_output, dict)
        assert "name" in trigger_output
        print(
            f"Investigation triggered successfully: "
            f"{trigger_output['name']}"
        )
    except json.JSONDecodeError:
        pytest.fail("Failed to parse trigger response")

    # Step 3: Fetch associated investigations
    fetch_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "investigation",
            "fetch-associated",
            "--detection-type",
            "ALERT",
            "--alert-ids",
            alert_id,
            "--association-limit",
            "5",
        ]
    )

    fetch_result = subprocess.run(
        fetch_cmd, env=cli_env, capture_output=True, text=True
    )

    assert fetch_result.returncode == 0

    try:
        fetch_output = json.loads(fetch_result.stdout)
        assert isinstance(fetch_output, dict)
        print(f"Fetch associated result keys: {fetch_output.keys()}")

        if "associationsList" in fetch_output:
            print(
                f"Found associations for "
                f"{len(fetch_output['associationsList'])} detections"
            )
    except json.JSONDecodeError:
        pytest.fail("Failed to parse fetch response")


@pytest.mark.integration
def test_cli_investigation_fetch_associated_with_multiple_alerts(
    cli_env, common_args
):
    """Test fetching associated investigations with multiple alert IDs."""
    # Get multiple alert IDs
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    alert_cmd = (
        ["secops"]
        + common_args
        + [
            "alert",
            "--start-time",
            start_time.isoformat(),
            "--end-time",
            end_time.isoformat(),
            "--max-alerts",
            "10",
        ]
    )

    alert_result = subprocess.run(
        alert_cmd, env=cli_env, capture_output=True, text=True
    )

    if alert_result.returncode != 0:
        pytest.skip("Could not fetch alerts")

    try:
        alerts_data = json.loads(alert_result.stdout)
        if not alerts_data or "alerts" not in alerts_data:
            pytest.skip("No alerts available for this test")

        nested_alerts = alerts_data["alerts"].get("alerts", [])
        if not nested_alerts or len(nested_alerts) < 2:
            pytest.skip("Need at least 2 alerts for this test")

        alert_ids = [alert["id"] for alert in nested_alerts[:3]]
        alert_ids_str = ",".join(alert_ids)
        print(f"Using alert IDs: {alert_ids_str}")

    except (json.JSONDecodeError, KeyError):
        pytest.skip("Could not parse alerts response")

    # Fetch associated investigations for multiple alerts
    fetch_cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "investigation",
            "fetch-associated",
            "--detection-type",
            "ALERT",
            "--alert-ids",
            alert_ids_str,
        ]
    )

    fetch_result = subprocess.run(
        fetch_cmd, env=cli_env, capture_output=True, text=True
    )

    assert fetch_result.returncode == 0

    try:
        fetch_output = json.loads(fetch_result.stdout)
        assert isinstance(fetch_output, dict)
        print(
            f"Successfully fetched associations for " f"{len(alert_ids)} alerts"
        )
    except json.JSONDecodeError:
        pytest.fail("Failed to parse fetch response")
