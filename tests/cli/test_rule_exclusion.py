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
"""Tests for the SecOps CLI rule exclusion commands."""

import argparse
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from secops.cli.commands.rule_exclusion import (
    handle_rule_exclusion_test_command,
)


@patch("secops.cli.commands.rule_exclusion.output_formatter")
def test_handle_rule_exclusion_test_command(mock_output_formatter):
    """Test the rule-exclusion test command handler."""
    chronicle = Mock()
    chronicle.test_rule_exclusion.return_value = {"activity": {"count": 1}}
    args = argparse.Namespace(
        refinement_type="DETECTION_EXCLUSION",
        query='ip = "8.8.8.8"',
        start_time="2026-01-29T15:28:13.975619Z",
        end_time="2026-04-29T15:28:13.975619Z",
        time_window=24,
        detection_exclusion_application='{"curatedRules": ["curatedRules/ur_123"]}',
        outcome_filters='[{"field": "principal.ip"}]',
        output="json",
    )

    handle_rule_exclusion_test_command(args, chronicle)

    chronicle.test_rule_exclusion.assert_called_once_with(
        refinement_type="DETECTION_EXCLUSION",
        query='ip = "8.8.8.8"',
        start_time=datetime(2026, 1, 29, 15, 28, 13, 975619, tzinfo=timezone.utc),
        end_time=datetime(2026, 4, 29, 15, 28, 13, 975619, tzinfo=timezone.utc),
        detection_exclusion_application={"curatedRules": ["curatedRules/ur_123"]},
        outcome_filters=[{"field": "principal.ip"}],
    )
    mock_output_formatter.assert_called_once_with({"activity": {"count": 1}}, "json")
