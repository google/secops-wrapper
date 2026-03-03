# Copyright 2026 Google LLC
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
"""Integration tests for SecOps CLI log search commands."""

import json
import subprocess
from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.integration
def test_cli_search_raw_logs(cli_env, common_args):
    """Test the search raw-logs command."""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    cmd = (
        [
            "secops",
        ]
        + common_args
        + [
            "search",
            "raw-logs",
            "--query",
            'raw = "test"',
            "--start-time",
            start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--end-time",
            end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "--page-size",
            "5",
        ]
    )

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    assert result.returncode == 0

    try:
        output = json.loads(result.stdout)
        assert output

        if isinstance(output, dict):
            assert "matches" in output
        elif isinstance(output, list):
            assert len(output) > 0
    except json.JSONDecodeError:
        assert "Error:" not in result.stdout
