# Quick Start Guide

## Prerequisites

Before you begin, make sure you have:
1. Installed the SDK (see [Installation](installation.md))
2. Set up authentication (see [Authentication](authentication.md))
3. Access to a Google Chronicle/SecOps instance

## Initializing the Client

First, import the SecOpsClient and initialize it:

```python
from secops import SecOpsClient

# Initialize with default credentials
client = SecOpsClient()

# Initialize Chronicle client
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",  # Your Chronicle instance ID
    project_id="your-project-id",             # Your GCP project ID
    region="us"                               # Chronicle API region
)
```

For available regions, see the [Regions documentation](advanced/regions.md).

## Basic Operations

### Performing a UDM Search

```python
# Simple UDM search for the last 24 hours
results = chronicle.search(
    query="metadata.product_name = \"Okta\"",
    start_time="1d"
)

# Process the results
for event in results:
    print(f"Event time: {event.get('metadata', {}).get('event_timestamp')}")
    print(f"Product: {event.get('metadata', {}).get('product_name')}")
    print("---")
```

### Ingesting Logs

```python
from datetime import datetime, timezone
import json

# Create a sample log (this is an OKTA log)
current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
okta_log = {
    "actor": {
        "displayName": "Joe Doe",
        "alternateId": "jdoe@example.com"
    },
    "client": {
        "ipAddress": "192.168.1.100",
        "userAgent": {
            "os": "Mac OS X",
            "browser": "SAFARI"
        }
    },
    "displayMessage": "User login to Okta",
    "eventType": "user.session.start",
    "outcome": {
        "result": "SUCCESS"
    },
    "published": current_time  # Current time in ISO format
}

# Ingest the log using the default forwarder
result = chronicle.ingest_log(
    log_type="OKTA",  # Chronicle log type
    log_message=json.dumps(okta_log)  # JSON string of the log
)

print(f"Operation: {result.get('operation')}")
```

### Looking Up IoCs

```python
# Look up an IP address
ioc_results = chronicle.ioc_details(
    artifact_value="192.168.1.100",
    artifact_type="IP_ADDRESS"
)

# Process the results
for ioc in ioc_results:
    print(f"IoC: {ioc.get('artifactValue')}")
    print(f"Category: {ioc.get('category')}")
    print(f"First seen: {ioc.get('firstSeenTime')}")
    print(f"Last seen: {ioc.get('lastSeenTime')}")
    print("---")
```

### Using the CLI

The SDK also provides a command-line interface for common operations:

```bash
# Set up environment variables (optional)
export SECOPS_PROJECT_ID="your-project-id"
export SECOPS_CUSTOMER_ID="your-chronicle-instance-id"
export SECOPS_REGION="us"

# Perform a UDM search
secops chronicle search \
  --query "metadata.log_type = \"OKTA\"" \
  --start-time "1d"

# Perform a natural language search
secops chronicle nl-search \
  --query "Show me all failed login attempts in the last 24 hours" \
  --start-time "1d"
```

## Next Steps

Now that you've learned the basics, you can explore more advanced features:
- [Chronicle Client](chronicle/index.md) - Detailed documentation for all Chronicle features
- [CLI Reference](cli/index.md) - Complete reference for the command-line interface
- [Advanced Topics](advanced/index.md) - Learn about proxy configuration, pagination, and more
