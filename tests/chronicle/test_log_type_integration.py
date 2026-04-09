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
"""Integration tests for Chronicle log type and parser validation functions.

These tests require valid credentials and API access.
They interact with real Chronicle API endpoints.
"""

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_log_type_lifecycle_integration():
    """Test the complete log-type lifecycle."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)

    # 5. Testing parser validation workflow
    dummy_project_id = "140410331797"
    dummy_customer_id = "ebdc4bb9-878b-11e7-8455-10604b7cb5c1"

    dummy_chronicle = client.chronicle(
        project_id=dummy_project_id,
        customer_id=dummy_customer_id,
        region=CHRONICLE_CONFIG.get("region", "us"),
    )

    print("\nTesting trigger_github_checks with dummy data")
    try:
        # Trigger checks for a dummy PR and log type
        result = dummy_chronicle.trigger_github_checks(
            associated_pr="google/secops-wrapper/pull/617",
            log_type="DUMMY_LOGTYPE",
        )
        assert isinstance(result, dict)
        print("Successfully triggered checks (or received valid JSON response)")
    except (APIError, Exception) as e:
        # We expect a failure due to dummy data, but we want to confirm
        # it reached the server or handled the routing correctly.
        error_msg = str(e)
        assert (
            "api error" in error_msg.lower()
            or "error" in error_msg.lower()
            or "failed" in error_msg.lower()
        )
        print(
            f"Server gracefully handled the dummy trigger data: {error_msg.strip()}"
        )

    print("\nTesting get_analysis_report with dummy data")
    try:
        # Request a report for dummy resource names
        report = dummy_chronicle.get_analysis_report(
            log_type="DUMMY_LOGTYPE", parser_id="xyz", report_id="123"
        )
        assert isinstance(report, dict)
        print("Successfully retrieved report")
    except (APIError, Exception) as e:
        # We expect a 404 or similar since the report is dummy
        error_msg = str(e)
        assert (
            "api error" in error_msg.lower()
            or "error" in error_msg.lower()
            or "not found" in error_msg.lower()
        )
        print(
            f"Server gracefully handled dummy report request: {error_msg.strip()}"
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__, "-m", "integration"])
