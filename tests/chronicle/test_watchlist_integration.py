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
"""Integration tests for Chronicle watchlist."""
import pytest
from datetime import datetime, timezone
from secops import SecOpsClient
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.fixture(scope="module")
def chronicle():
    """Fixture to create a Chronicle client."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    return client.chronicle(**CHRONICLE_CONFIG)


@pytest.mark.integration
def test_watchlist_crud_workflow(chronicle):
    """Test complete watchlist CRUD workflow including update."""

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    watchlist_name = f"secops-test-watchlist-{ts}"
    display_name = f"SecOps Test Watchlist {ts}"
    description = (
        "Integration test watchlist - created by test_watchlist_integration.py"
    )
    multiplying_factor = 1.0

    created_watchlist = None
    watchlist_id = None

    try:
        # 1. Create watchlist
        print("\n1. Creating watchlist...")
        created_watchlist = chronicle.create_watchlist(
            name=watchlist_name,
            display_name=display_name,
            multiplying_factor=multiplying_factor,
            description=description,
        )

        assert isinstance(created_watchlist, dict)
        assert "name" in created_watchlist
        assert created_watchlist.get("displayName") == display_name
        assert created_watchlist.get("description") == description

        watchlist_id = created_watchlist["name"].split("/")[-1]
        print(f"   Created watchlist: {display_name} (ID: {watchlist_id})")

        # 2. Get watchlist
        print("\n2. Getting watchlist...")
        fetched_watchlist = chronicle.get_watchlist(watchlist_id)

        assert isinstance(fetched_watchlist, dict)
        assert fetched_watchlist.get("name") == created_watchlist["name"]
        assert fetched_watchlist.get("displayName") == display_name
        print(f"   Fetched watchlist: {fetched_watchlist.get('displayName')}")

        # 3. Update watchlist - change display_name, description, multiplying_factor
        print("\n3. Updating watchlist fields...")
        updated_display_name = f"Updated Watchlist {ts}"
        updated_description = "Updated description - integration test"
        updated_multiplying_factor = 2.5

        updated_watchlist = chronicle.update_watchlist(
            watchlist_id=watchlist_id,
            display_name=updated_display_name,
            description=updated_description,
            multiplying_factor=updated_multiplying_factor,
        )

        assert isinstance(updated_watchlist, dict)
        assert updated_watchlist.get("displayName") == updated_display_name
        assert updated_watchlist.get("description") == updated_description
        assert (
            updated_watchlist.get("multiplyingFactor")
            == updated_multiplying_factor
        )
        print(
            f"   Updated display_name: {updated_watchlist.get('displayName')}"
        )
        print(f"   Updated description: {updated_watchlist.get('description')}")
        print(
            f"   Updated multiplying_factor: "
            f"{updated_watchlist.get('multiplyingFactor')}"
        )

        # 4. Update watchlist user preferences (pinned)
        print("\n4. Updating watchlist user preferences (pinned=True)...")
        pinned_watchlist = chronicle.update_watchlist(
            watchlist_id=watchlist_id,
            watchlist_user_preferences={"pinned": True},
        )

        assert isinstance(pinned_watchlist, dict)
        user_prefs = pinned_watchlist.get("watchlistUserPreferences", {})
        assert user_prefs.get("pinned") is True
        print(f"   Pinned: {user_prefs.get('pinned')}")

        # 5. List watchlists and verify our watchlist is present
        print("\n5. Listing watchlists...")
        watchlists_response = chronicle.list_watchlists(page_size=100)

        assert isinstance(watchlists_response, dict)
        watchlists = watchlists_response.get("watchlists", [])
        watchlist_names = [w.get("name") for w in watchlists]
        assert created_watchlist["name"] in watchlist_names
        print(
            f"   Found {len(watchlists)} watchlists, "
            f"verified test watchlist is present"
        )

        # 6. Delete watchlist (cleanup)
        print("\n6. Deleting watchlist...")
        delete_result = chronicle.delete_watchlist(watchlist_id)

        assert isinstance(delete_result, dict)
        print(f"   Successfully deleted watchlist {watchlist_id}")

        # Verify deletion
        print("\n7. Verifying deletion...")
        try:
            chronicle.get_watchlist(watchlist_id)
            pytest.fail("Watchlist should have been deleted")
        except Exception:
            print("   Watchlist successfully deleted (get returned error)")

    except Exception as e:
        # Cleanup on failure
        if watchlist_id:
            try:
                print(
                    f"\nCleanup: Attempting to delete watchlist {watchlist_id}"
                )
                chronicle.delete_watchlist(watchlist_id, force=True)
                print("Cleanup: Successfully deleted watchlist")
            except Exception as cleanup_error:
                print(f"Cleanup failed: {cleanup_error}")
        raise e


@pytest.mark.integration
def test_watchlist_list(chronicle):
    """Test listing watchlists with pagination."""
    print("\nTesting watchlist list with pagination...")

    # List with small page size
    result = chronicle.list_watchlists(page_size=1)

    assert isinstance(result, dict)
    watchlists = result.get("watchlists", [])
    assert isinstance(watchlists, list)
    print(f"Listed {len(watchlists)} watchlist(s) with page_size=1")

    # If there's more data, verify pagination token exists
    if len(watchlists) == 1:
        # List all to check total count
        all_result = chronicle.list_watchlists()
        all_watchlists = all_result.get("watchlists", [])
        print(f"Total watchlists available: {len(all_watchlists)}")
