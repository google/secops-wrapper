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
"""Integration tests for Chronicle log classification functionality."""
import json
import pytest

from secops import SecOpsClient
from secops.exceptions import APIError, SecOpsError
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_classify_multiple_log_types():
    """Test classifying different log types in a single test workflow.

    This test demonstrates the workflow of classifying various log formats
    and comparing their predictions.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    log_samples = {
        "OKTA": json.dumps(
            {
                "eventType": "user.session.start",
                "displayMessage": "User login to Okta",
                "actor": {"alternateId": "user@example.com"},
                "outcome": {"result": "SUCCESS"},
            }
        ),
        "Windows": "<Event><System><EventID>4624</EventID></System></Event>",
        "AWS_CloudTrail": json.dumps(
            {
                "eventName": "GetObject",
                "eventSource": "s3.amazonaws.com",
                "userIdentity": {"type": "IAMUser"},
            }
        ),
    }

    try:
        results = {}

        for log_name, log_data in log_samples.items():
            print(f"\nClassifying {log_name} log...")
            result = chronicle.classify_logs(log_data=log_data)

            assert isinstance(result, list)
            results[log_name] = result

            if len(result) > 0:
                print(f"Top prediction: {result[0]['logType']}")
                print(f"Score: {result[0]['score']}")

        print(f"\nSuccessfully classified {len(results)} log types")
        assert len(results) == 3

    except APIError as e:
        print(f"\nAPI Error details: {str(e)}")
        if "permission" in str(e).lower():
            pytest.skip("Insufficient permissions to classify logs")
        raise
