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
"""Integration tests for Chronicle raw log search functionality.

These tests require valid credentials and API access.
"""
from datetime import datetime, timedelta, timezone

import pytest

from secops import SecOpsClient

from ..config import CHRONICLE_CONFIG


@pytest.mark.integration
def test_search_raw_logs_basic():
    """Test basic raw log search with real API."""
    client = SecOpsClient()
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)

    result = chronicle.search_raw_logs(
        query='raw = "test"',
        start_time=start_time,
        end_time=end_time,
        page_size=5,
    )

    assert result
    if isinstance(result, dict):
        assert "matches" in result
    elif isinstance(result, list):
        assert len(result) > 0


@pytest.mark.integration
def test_search_raw_logs_with_all_params():
    """Test raw log search with all optional parameters."""
    client = SecOpsClient()
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=2)

    result = chronicle.search_raw_logs(
        query='raw = "test"',
        start_time=start_time,
        end_time=end_time,
        case_sensitive=False,
        page_size=5,
    )

    assert result
    if isinstance(result, dict):
        assert "matches" in result
    elif isinstance(result, list):
        assert len(result) > 0
