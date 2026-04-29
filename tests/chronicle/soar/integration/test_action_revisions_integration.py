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
"""Integration tests for Chronicle integration action revisions.

These tests require valid credentials and API access.
"""

import time
import uuid

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from tests.config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_action_revisions_workflow():
    """Test full action revision lifecycle: create, list, rollback, delete.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    integration_name = None
    action_id = None
    revision_id = None

    try:
        print("\n1. Finding a target integration")
        integrations_resp = chronicle.soar.list_integrations(page_size=5)
        integrations = integrations_resp.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available to test action revisions.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")

        print("\n2. Creating a temporary custom action")
        unique_id = str(uuid.uuid4())[:8]
        display_name = f"SDK Test Action {unique_id}"
        script = (
            "from SiemplifyAction import SiemplifyAction\n"
            "siemplify = SiemplifyAction()\n"
            "siemplify.end('Test action', True)\n"
        )

        create_action_resp = chronicle.soar.create_integration_action(
            integration_name=integration_name,
            display_name=display_name,
            script=script,
            timeout_seconds=60,
            enabled=True,
            script_result_name="result",
            is_async=False,
            description="Temporary action created by integration test",
        )

        assert create_action_resp is not None
        assert "name" in create_action_resp
        action_id = create_action_resp["name"].split("/")[-1]
        print(f"Created action with ID: {action_id}")

        time.sleep(2)

        print("\n3. Getting action details for snapshotting")
        action = chronicle.soar.get_integration_action(
            integration_name=integration_name,
            action_id=action_id,
        )
        assert action is not None
        assert "name" in action
        print(f"Retrieved action: {action.get('displayName')}")

        print("\n4. Creating a revision of the action")
        revision_comment = f"SDK test revision {unique_id}"
        create_rev_resp = chronicle.soar.create_integration_action_revision(
            integration_name=integration_name,
            action_id=action_id,
            action=action,
            comment=revision_comment,
        )

        assert create_rev_resp is not None
        assert "name" in create_rev_resp
        revision_id = create_rev_resp["name"].split("/")[-1]
        print(f"Created revision with ID: {revision_id}")

        time.sleep(1)

        print("\n5. Listing revisions and verifying the new revision appears")
        list_resp = chronicle.soar.list_integration_action_revisions(
            integration_name=integration_name,
            action_id=action_id,
        )

        revisions = list_resp.get("revisions", [])
        assert isinstance(revisions, list)
        found = any(r.get("name", "").endswith(revision_id) for r in revisions)
        assert found, f"Created revision {revision_id} not found in list."
        print(f"Found revision in list ({len(revisions)} total)")

        print("\n5a. Listing revisions as_list=True")
        revisions_list = chronicle.soar.list_integration_action_revisions(
            integration_name=integration_name,
            action_id=action_id,
            as_list=True,
        )
        assert isinstance(revisions_list, list)
        print(f"as_list returned {len(revisions_list)} revisions")

        print("\n6. Rolling back action to the created revision")
        rollback_resp = chronicle.soar.rollback_integration_action_revision(
            integration_name=integration_name,
            action_id=action_id,
            revision_id=revision_id,
        )
        assert rollback_resp is not None
        print(f"Rollback successful: {rollback_resp.get('name')}")

        time.sleep(1)

        print("\n7. Deleting the revision")
        chronicle.soar.delete_integration_action_revision(
            integration_name=integration_name,
            action_id=action_id,
            revision_id=revision_id,
        )
        revision_id = None
        print("Revision deleted successfully")

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        raise
    finally:
        print("\n8. Cleaning up")
        if integration_name and revision_id:
            try:
                chronicle.soar.delete_integration_action_revision(
                    integration_name=integration_name,
                    action_id=action_id,
                    revision_id=revision_id,
                )
                print(f"Cleaned up revision: {revision_id}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to delete test revision: {cleanup_error}"
                )
        if integration_name and action_id:
            try:
                chronicle.soar.delete_integration_action(
                    integration_name=integration_name,
                    action_id=action_id,
                )
                print(f"Cleaned up action: {action_id}")
            except Exception as cleanup_error:
                print(f"Warning: Failed to delete test action: {cleanup_error}")
