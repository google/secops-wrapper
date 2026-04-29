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
"""Integration tests for Chronicle integration actions.

These tests require valid credentials and API access.
"""

import time
import uuid

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from tests.config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


_ACTION_SCRIPT = (
    "from SiemplifyAction import SiemplifyAction\n"
    "siemplify = SiemplifyAction()\n"
    "siemplify.end('Test action', True)\n"
)


@pytest.mark.integration
def test_integration_actions_workflow():
    """Test full action lifecycle: template, create, get, list, update, delete.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    integration_name = None
    action_id = None

    try:
        print("\n1. Finding a target integration")
        integrations_resp = chronicle.soar.list_integrations(page_size=5)
        integrations = integrations_resp.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available to test action workflow.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")

        print("\n2. Getting action template")
        template_resp = chronicle.soar.get_integration_action_template(
            integration_name=integration_name,
        )
        assert template_resp is not None
        print("Retrieved sync action template successfully")

        print("\n2a. Getting async action template")
        async_template_resp = chronicle.soar.get_integration_action_template(
            integration_name=integration_name,
            is_async=True,
        )
        assert async_template_resp is not None
        print("Retrieved async action template successfully")

        print("\n3. Creating a custom action")
        unique_id = str(uuid.uuid4())[:8]
        display_name = f"SDK Test Action {unique_id}"

        create_resp = chronicle.soar.create_integration_action(
            integration_name=integration_name,
            display_name=display_name,
            script=_ACTION_SCRIPT,
            timeout_seconds=60,
            enabled=True,
            script_result_name="result",
            is_async=False,
            description="Temporary action created by integration test",
        )

        assert create_resp is not None
        assert "name" in create_resp
        action_id = create_resp["name"].split("/")[-1]
        print(f"Created action with ID: {action_id}")

        time.sleep(2)

        print("\n4. Getting action details")
        get_resp = chronicle.soar.get_integration_action(
            integration_name=integration_name,
            action_id=action_id,
        )
        assert get_resp is not None
        assert "name" in get_resp
        assert get_resp.get("displayName") == display_name
        print(f"Retrieved action: {get_resp.get('displayName')}")

        print("\n5. Listing actions and verifying created action appears")
        list_resp = chronicle.soar.list_integration_actions(
            integration_name=integration_name,
        )
        actions = list_resp.get("actions", [])
        assert isinstance(actions, list)
        found = any(a.get("name", "").endswith(action_id) for a in actions)
        assert found, f"Created action {action_id} not found in list."
        print(f"Found action in list ({len(actions)} total)")

        print("\n5a. Listing actions with as_list=True")
        actions_list = chronicle.soar.list_integration_actions(
            integration_name=integration_name,
            as_list=True,
        )
        assert isinstance(actions_list, list)
        print(f"as_list returned {len(actions_list)} actions")

        print("\n6. Updating the action")
        updated_description = f"Updated by integration test {unique_id}"
        update_resp = chronicle.soar.update_integration_action(
            integration_name=integration_name,
            action_id=action_id,
            description=updated_description,
        )
        assert update_resp is not None
        assert "name" in update_resp
        print("Updated action description successfully")

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        raise
    finally:
        print("\n7. Cleaning up")
        if integration_name and action_id:
            try:
                chronicle.soar.delete_integration_action(
                    integration_name=integration_name,
                    action_id=action_id,
                )
                print(f"Cleaned up action: {action_id}")
            except Exception as cleanup_error:
                print(f"Warning: Failed to delete test action: {cleanup_error}")
