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
"""Integration tests for Chronicle log classification CLI functionality."""
import json
import subprocess
import tempfile
import pytest
from pathlib import Path


@pytest.mark.integration
def test_cli_classify_windows_log_from_file(cli_env, common_args):
    """Test classifying Windows XML log from file."""
    windows_log = """<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
  <System>
    <Provider Name='Microsoft-Windows-Security-Auditing'/>
    <EventID>4624</EventID>
    <Version>2</Version>
    <Level>0</Level>
    <Task>12544</Task>
    <TimeCreated SystemTime='2023-01-15T10:30:00.000000Z'/>
    <EventRecordID>12345</EventRecordID>
    <Channel>Security</Channel>
    <Computer>DESKTOP-TEST</Computer>
  </System>
  <EventData>
    <Data Name='SubjectUserSid'>S-1-5-18</Data>
    <Data Name='SubjectUserName'>SYSTEM</Data>
    <Data Name='TargetUserName'>testuser</Data>
    <Data Name='LogonType'>2</Data>
  </EventData>
</Event>"""

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".xml", delete=False
    ) as tmp_file:
        tmp_file.write(windows_log)
        tmp_file_path = tmp_file.name

    try:
        cmd = (
            ["secops"]
            + common_args
            + ["log", "classify", "--log", tmp_file_path]
        )

        result = subprocess.run(
            cmd, env=cli_env, capture_output=True, text=True
        )

        assert result.returncode == 0
        assert result.stdout.strip(), "Expected non-empty output"

        try:
            output = json.loads(result.stdout.strip())
            assert isinstance(output, list)
            if len(output) > 0:
                assert "logType" in output[0]
                assert "score" in output[0]
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON output, got: {result.stdout}")

        print(f"\nCLI Output:\n{result.stdout}")

    finally:
        Path(tmp_file_path).unlink(missing_ok=True)


@pytest.mark.integration
def test_cli_classify_multiple_logs_workflow(cli_env, common_args):
    """Test workflow of classifying multiple different log types.

    This test demonstrates the complete workflow of classifying various
    log formats using both inline strings and files.
    """
    test_logs = [
        {
            "name": "OKTA",
            "data": json.dumps(
                {
                    "eventType": "user.session.start",
                    "actor": {"alternateId": "user@example.com"},
                }
            ),
            "use_file": False,
        },
        {
            "name": "Windows",
            "data": "<Event><System><EventID>4624</EventID></System></Event>",
            "use_file": True,
        },
    ]

    results = []
    temp_files = []

    try:
        for log_info in test_logs:
            print(f"\nClassifying {log_info['name']} log...")

            if log_info["use_file"]:
                tmp_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".log", delete=False
                )
                tmp_file.write(log_info["data"])
                tmp_file.close()
                temp_files.append(tmp_file.name)
                log_arg = tmp_file.name
            else:
                log_arg = log_info["data"]

            cmd = (
                ["secops"] + common_args + ["log", "classify", "--log", log_arg]
            )

            result = subprocess.run(
                cmd, env=cli_env, capture_output=True, text=True
            )

            assert result.returncode == 0
            results.append({"name": log_info["name"], "output": result.stdout})

        print(f"\nSuccessfully classified {len(results)} log types via CLI")
        assert len(results) == len(test_logs)

        for result in results:
            assert result["output"].strip(), "Expected non-empty output"
            try:
                output = json.loads(result["output"].strip())
                assert isinstance(output, list)
                if len(output) > 0:
                    assert "logType" in output[0]
                    assert "score" in output[0]
            except json.JSONDecodeError:
                pytest.fail(
                    f"Expected JSON output for {result['name']}, "
                    f"got: {result['output']}"
                )

    finally:
        for temp_file in temp_files:
            Path(temp_file).unlink(missing_ok=True)
