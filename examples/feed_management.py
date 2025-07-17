#!/usr/bin/env python3
"""Example usage of the Google SecOps SDK for Chronicle Feed Management."""

from datetime import datetime, timedelta, timezone
from secops import SecOpsClient
from pprint import pprint
import json
import argparse
import uuid
import time


def get_client(project_id, customer_id, region):
    """Initialize and return the Chronicle client.

    Args:
        project_id: Google Cloud Project ID
        customer_id: Chronicle Customer ID (UUID)
        region: Chronicle region (us or eu)

    Returns:
        Chronicle client instance
    """
    client = SecOpsClient()
    chronicle = client.chronicle(
        customer_id=customer_id, project_id=project_id, region=region
    )
    return chronicle


def example_feed_list(chronicle):
    """Example 1: List Feeds."""
    print("\n=== Example 1: List Feeds ===")

    try:
        # List all available feeds
        feeds = chronicle.list_feeds()
        print(f"\nFound {len(feeds)} feeds")

        if feeds:
            print("\nSample feed details:")
            sample_feed = feeds[0]
            print(f"Name: {sample_feed.get('name')}")
            print(f"Display Name: {sample_feed.get('displayName')}")
            print(f"State: {sample_feed.get('state')}")
            
            # Extract feed ID from the name
            feed_id = sample_feed.get('name', '').split('/')[-1]
            print(f"Feed ID: {feed_id}")
            
            # Print feed source type if available
            details = sample_feed.get('details', {})
            feed_source_type = details.get('feedSourceType')
            if feed_source_type:
                print(f"Feed Source Type: {feed_source_type}")
        else:
            print("No feeds found in your Chronicle instance.")
    
    except Exception as e:
        print(f"Error listing feeds: {e}")


def example_feed_create_and_get(chronicle):
    """Example 2: Create and Get Feed."""
    print("\n=== Example 2: Create and Get Feed ===")

    # Generate unique feed name for this example
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Feed details for a simple HTTP feed
    feed_details = {
        # Note: You need to use your actual project, region and customer_id values
        "logType": f"projects/{chronicle.project_id}/locations/{chronicle.region}/instances/{chronicle.customer_id}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "sdk_example"},
    }

    created_feed = None
    
    try:
        # Create the feed
        print(f"\nCreating feed: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )
        
        # Extract feed ID from the name
        feed_id = created_feed.get('name', '').split('/')[-1]
        
        print(f"Feed created successfully!")
        print(f"Feed ID: {feed_id}")
        print(f"Display Name: {created_feed.get('displayName')}")
        print(f"State: {created_feed.get('state', 'N/A')}")
        
        # Wait a moment for the feed to be fully created
        time.sleep(2)
        
        # Get the feed to verify it was created
        print(f"\nRetrieving feed details for feed ID: {feed_id}")
        retrieved_feed = chronicle.get_feed(feed_id)
        
        print("Feed details retrieved:")
        print(f"Name: {retrieved_feed.get('name')}")
        print(f"Display Name: {retrieved_feed.get('displayName')}")
        print(f"State: {retrieved_feed.get('state', 'N/A')}")
        
        # Print feed source type from details
        details = retrieved_feed.get('details', {})
        feed_source_type = details.get('feedSourceType')
        if feed_source_type:
            print(f"Feed Source Type: {feed_source_type}")
            
        if 'httpSettings' in details:
            print(f"HTTP URI: {details['httpSettings'].get('uri')}")
            
    except Exception as e:
        print(f"Error creating or getting feed: {e}")
        
    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed.get('name', '').split('/')[-1]
                print(f"\nCleaning up: Deleting feed ID: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test feed: {e}")


def example_feed_update(chronicle):
    """Example 3: Update Feed."""
    print("\n=== Example 3: Update Feed ===")

    # Generate unique feed name for this example
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Feed details for initial creation
    feed_details = {
        "logType": f"projects/{chronicle.project_id}/locations/{chronicle.region}/instances/{chronicle.customer_id}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/original_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "dev", "created_by": "sdk_example"},
    }

    created_feed = None
    
    try:
        # Create the feed
        print(f"\nCreating feed to update: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )
        
        feed_id = created_feed.get('name', '').split('/')[-1]
        print(f"Feed created with ID: {feed_id}")
        
        # Wait a moment for the feed to be fully created
        time.sleep(2)
        
        # Update the feed with new display name and URI
        updated_display_name = f"Updated {display_name}"
        updated_details = {
        "logType": f"projects/{chronicle.project_id}/locations/{chronicle.region}/instances/{chronicle.customer_id}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/updated_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "dev", "created_by": "sdk_example"},
    }
        
        print(f"\nUpdating feed with new display name: {updated_display_name}")
        updated_feed = chronicle.update_feed(
            feed_id, updated_display_name, updated_details
        )
        
        print("Feed updated successfully!")
        print(f"New Display Name: {updated_feed.get('displayName')}")
        
        # Show updated HTTP URI
        details = updated_feed.get('details', {})
        if 'httpSettings' in details:
            print(f"Updated HTTP URI: {details['httpSettings'].get('uri')}")
            
        # Show updated labels
        if 'labels' in details:
            print("Updated Labels:")
            for key, value in details['labels'].items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"Error updating feed: {e}")
        
    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed.get('name', '').split('/')[-1]
                print(f"\nCleaning up: Deleting feed ID: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test feed: {e}")


def example_feed_enable_disable(chronicle):
    """Example 4: Enable and Disable Feed."""
    print("\n=== Example 4: Enable and Disable Feed ===")

    # Generate unique feed name for this example
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Feed details for a simple feed
    feed_details = {
        "logType": f"projects/{chronicle.project_id}/locations/{chronicle.region}/instances/{chronicle.customer_id}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        }
    }

    created_feed = None
    
    try:
        # Create the feed
        print(f"\nCreating feed: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )
        
        feed_id = created_feed.get('name', '').split('/')[-1]
        print(f"Feed created with ID: {feed_id}")
        print(f"Initial State: {created_feed.get('state', 'N/A')}")
        
        # Wait a moment for the feed to be fully created
        time.sleep(2)
        
        # Disable the feed
        print("\nDisabling feed...")
        disabled_feed = chronicle.disable_feed(feed_id)
        print(f"Feed disabled. New State: {disabled_feed.get('state', 'N/A')}")
        
        # Wait a moment before enabling
        time.sleep(2)
        
        # Enable the feed
        print("\nEnabling feed...")
        enabled_feed = chronicle.enable_feed(feed_id)
        print(f"Feed enabled. New State: {enabled_feed.get('state', 'N/A')}")
        
    except Exception as e:
        print(f"Error in feed enable/disable operations: {e}")
        
    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed.get('name', '').split('/')[-1]
                print(f"\nCleaning up: Deleting feed ID: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test feed: {e}")


def example_feed_generate_secret(chronicle):
    """Example 5: Generate Feed Secret."""
    print("\n=== Example 5: Generate Feed Secret ===")
    
    # Generate unique feed name for this example
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"
    
    # Note: This example requires a specific feed type that supports secrets
    # Not all feed types support secret generation
    feed_details = {
        "httpsPushAmazonKinesisFirehoseSettings": {
            "splitDelimiter": ""
        },
        "feedSourceType": "HTTPS_PUSH_AMAZON_KINESIS_FIREHOSE",
        "logType": f"projects/{chronicle.project_id}/locations/{chronicle.region}/instances/{chronicle.customer_id}/logTypes/OKTA"
    }

    created_feed = None
    
    try:
        # Create the feed
        print(f"\nCreating feed with secret capability: {display_name}")
        print("Note: This example will work only if your Chronicle instance supports HTTPS_PUSH_AMAZON_KINESIS_FIREHOSE feed type")
        
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )
        
        feed_id = created_feed.get('name', '').split('/')[-1]
        print(f"Feed created with ID: {feed_id}")
        
        # Wait a moment for the feed to be fully created
        time.sleep(2)
        
        # Generate secret for the feed
        print("\nGenerating secret for feed...")
        secret_result = chronicle.generate_secret(feed_id)
        
        if 'secret' in secret_result:
            print("Secret generated successfully!")
            # Don't print the actual secret in production code - this is just for demonstration
            secret_preview = secret_result['secret'][:5] + '...' if len(secret_result['secret']) > 5 else '...'
            print(f"Secret preview: {secret_preview}")
        else:
            print("Secret generation response did not contain a secret value.")
            
    except Exception as e:
        print(f"Error generating feed secret: {e}")
        print("Note: Feed secret generation is only supported for certain feed types.")
        print("      Make sure your Chronicle instance supports the specified feed type.")
        
    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed.get('name', '').split('/')[-1]
                print(f"\nCleaning up: Deleting feed ID: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except Exception as e:
                print(f"Warning: Failed to delete test feed: {e}")


# Map of example functions
EXAMPLES = {
    "1": example_feed_list,
    "2": example_feed_create_and_get,
    "3": example_feed_update,
    "4": example_feed_enable_disable,
    "5": example_feed_generate_secret,
}


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(description="Run Chronicle Feed API examples")
    parser.add_argument("--project_id", required=True, help="Google Cloud Project ID")
    parser.add_argument(
        "--customer_id", required=True, help="Chronicle Customer ID (UUID)"
    )
    parser.add_argument("--region", default="us", help="Chronicle region (us or eu)")
    parser.add_argument(
        "--example",
        "-e",
        help="Example number to run (1-5). If not specified, runs all examples.",
    )

    args = parser.parse_args()

    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)

    if args.example:
        if args.example not in EXAMPLES:
            print(
                f"Invalid example number. Available examples: {', '.join(EXAMPLES.keys())}"
            )
            return
        EXAMPLES[args.example](chronicle)
    else:
        # Run all examples in order
        for example_num in sorted(EXAMPLES.keys()):
            EXAMPLES[example_num](chronicle)


if __name__ == "__main__":
    main()
