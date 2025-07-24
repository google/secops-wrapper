"""Integration tests for the SecOps CLI feed commands."""

import json
import os
import subprocess
import time
import uuid

import pytest

# Import configuration - use absolute import
from tests.config import CHRONICLE_CONFIG


@pytest.mark.integration
def test_cli_feed_list(cli_env, common_args):
    """Test the feed list command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "feed",
        "list",
    ]

    result = subprocess.run(cmd, env=cli_env, capture_output=True, text=True)

    # Check that the command executed successfully
    assert result.returncode == 0

    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        # Verify it's a list
        assert isinstance(output, list), "Expected a list of feeds"
        # If feeds exist, check the first one has expected fields
        if output:
            assert "name" in output[0]
            assert "displayName" in output[0]
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout


@pytest.mark.integration
def test_cli_feed_get(cli_env, common_args):
    """Test the feed get command."""
    # First, list feeds to get an existing feed ID
    list_cmd = [
        "secops",
    ] + common_args + [
        "feed",
        "list",
    ]

    list_result = subprocess.run(list_cmd, env=cli_env, capture_output=True, text=True)
    assert list_result.returncode == 0

    # Parse the output to get an existing feed ID
    try:
        feeds = json.loads(list_result.stdout)
        if not feeds:
            pytest.skip("No feeds found to test get command")

        # Extract feed ID from the first feed
        feed_id = feeds[0]["name"].split("/")[-1]

        # Now test the get command
        get_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "get",
            "--id",
            feed_id,
        ]

        get_result = subprocess.run(get_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert get_result.returncode == 0

        # Verify the result contains expected data
        feed_data = json.loads(get_result.stdout)
        assert "name" in feed_data
        assert "displayName" in feed_data
        assert feed_data["name"].split("/")[-1] == feed_id

    except (json.JSONDecodeError, IndexError, KeyError):
        pytest.skip("Unable to find a feed ID to test get command")


@pytest.mark.integration
def test_cli_feed_create_update_delete(cli_env, common_args):
    """Test the feed create, update, and delete commands."""
    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Feed details for a simple HTTP feed
    feed_details = {
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "cli_integration_test"},
    }
    
    feed_id = None
    
    try:
        # 1. Create feed
        create_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "create",
            "--display-name",
            display_name,
            "--details",
            json.dumps(feed_details),
        ]
        
        create_result = subprocess.run(create_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert create_result.returncode == 0
        
        # Parse the output to get the feed ID
        feed_data = json.loads(create_result.stdout)
        assert "name" in feed_data
        feed_id = feed_data["name"].split("/")[-1]
        print(f"Created feed with ID: {feed_id}")
        
        # Wait briefly for the feed to be fully created
        time.sleep(2)
        
        # 2. Update feed
        updated_display_name = f"Updated {display_name}"
        update_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "update",
            "--id",
            feed_id,
            "--display-name",
            updated_display_name,
        ]
        
        update_result = subprocess.run(update_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert update_result.returncode == 0
        
        # Verify the update was successful
        updated_feed = json.loads(update_result.stdout)
        assert updated_feed["displayName"] == updated_display_name
        print(f"Successfully updated feed name to: {updated_display_name}")
        
    finally:
        # Clean up: Delete the feed if it was created
        if feed_id:
            delete_cmd = [
                "secops",
            ] + common_args + [
                "feed",
                "delete",
                "--id",
                feed_id,
            ]
            
            delete_result = subprocess.run(delete_cmd, env=cli_env, capture_output=True, text=True)
            
            # Check that the command executed successfully
            if delete_result.returncode == 0:
                print(f"Successfully deleted feed: {feed_id}")
            else:
                print(f"Failed to delete test feed: {delete_result.stderr}")


@pytest.mark.integration
def test_cli_feed_enable_disable(cli_env, common_args):
    """Test the feed enable and disable commands."""
    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Feed details for a simple HTTP feed
    feed_details = {
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "cli_integration_test"},
    }
    
    feed_id = None
    
    try:
        # 1. Create feed
        create_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "create",
            "--display-name",
            display_name,
            "--details",
            json.dumps(feed_details),
        ]
        
        create_result = subprocess.run(create_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert create_result.returncode == 0
        
        # Parse the output to get the feed ID
        feed_data = json.loads(create_result.stdout)
        assert "name" in feed_data
        feed_id = feed_data["name"].split("/")[-1]
        print(f"Created feed with ID: {feed_id}")
        
        # Wait briefly for the feed to be fully created
        time.sleep(2)
        
        # 2. Disable feed
        disable_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "disable",
            "--id",
            feed_id,
        ]
        
        disable_result = subprocess.run(disable_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert disable_result.returncode == 0
        
        # Verify the disable was successful
        disabled_feed = json.loads(disable_result.stdout)
        assert "state" in disabled_feed
        assert disabled_feed["state"] == "INACTIVE" or disabled_feed["state"] == "DISABLED"
        print(f"Successfully disabled feed: {feed_id}")
        
        # Wait briefly
        time.sleep(2)
        
        # 3. Enable feed
        enable_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "enable",
            "--id",
            feed_id,
        ]
        
        enable_result = subprocess.run(enable_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert enable_result.returncode == 0
        
        # Verify the enable was successful
        enabled_feed = json.loads(enable_result.stdout)
        assert "state" in enabled_feed
        assert enabled_feed["state"] == "ACTIVE" or enabled_feed["state"] == "ENABLED"
        print(f"Successfully enabled feed: {feed_id}")
        
    finally:
        # Clean up: Delete the feed if it was created
        if feed_id:
            delete_cmd = [
                "secops",
            ] + common_args + [
                "feed",
                "delete",
                "--id",
                feed_id,
            ]
            
            delete_result = subprocess.run(delete_cmd, env=cli_env, capture_output=True, text=True)
            
            # Check that the command executed successfully
            if delete_result.returncode == 0:
                print(f"Successfully deleted feed: {feed_id}")
            else:
                print(f"Failed to delete test feed: {delete_result.stderr}")


@pytest.mark.integration
def test_cli_feed_generate_secret(cli_env, common_args):
    """Test the feed generate-secret command."""
    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Feed details specifically for a feed type that supports secrets (HTTPS push)
    feed_details = {
        "httpsPushAmazonKinesisFirehoseSettings": {
            "splitDelimiter": ""
        },
        "feedSourceType": "HTTPS_PUSH_AMAZON_KINESIS_FIREHOSE",
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/OKTA"
    }
    
    feed_id = None
    
    try:
        # 1. Create feed
        create_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "create",
            "--display-name",
            display_name,
            "--details",
            json.dumps(feed_details),
        ]
        
        create_result = subprocess.run(create_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check if the command executed successfully
        if create_result.returncode != 0:
            # This could fail if the feed type is not supported in the test environment
            pytest.skip(f"Failed to create feed for secret test: {create_result.stderr}")
            return
        
        # Parse the output to get the feed ID
        feed_data = json.loads(create_result.stdout)
        assert "name" in feed_data
        feed_id = feed_data["name"].split("/")[-1]
        print(f"Created feed with ID: {feed_id}")
        
        # Wait briefly for the feed to be fully created
        time.sleep(2)
        
        # 2. Generate secret
        secret_cmd = [
            "secops",
        ] + common_args + [
            "feed",
            "generate-secret",
            "--id",
            feed_id,
        ]
        
        secret_result = subprocess.run(secret_cmd, env=cli_env, capture_output=True, text=True)
        
        # Check that the command executed successfully
        assert secret_result.returncode == 0
        
        # Verify the secret was generated
        secret_data = json.loads(secret_result.stdout)
        assert "secret" in secret_data
        assert secret_data["secret"]
        print(f"Successfully generated secret for feed: {feed_id}")
        
    finally:
        # Clean up: Delete the feed if it was created
        if feed_id:
            delete_cmd = [
                "secops",
            ] + common_args + [
                "feed",
                "delete",
                "--id",
                feed_id,
            ]
            
            delete_result = subprocess.run(delete_cmd, env=cli_env, capture_output=True, text=True)
            
            # Check that the command executed successfully
            if delete_result.returncode == 0:
                print(f"Successfully deleted feed: {feed_id}")
            else:
                print(f"Failed to delete test feed: {delete_result.stderr}")
