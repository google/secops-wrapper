# Log Ingestion

The Chronicle client provides capabilities for ingesting logs and events into Chronicle.

## Log Ingestion

You can ingest raw logs in various formats (JSON, XML, text) into Chronicle:

```python
from secops import SecOpsClient
import json
from datetime import datetime, timezone

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

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

## UDM Ingestion

For more control, you can ingest structured UDM events directly:

```python
from secops import SecOpsClient
import uuid
from datetime import datetime, timezone

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

# Create a UDM event
current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
udm_event = {
    "metadata": {
        "event_timestamp": current_time,
        "event_type": "USER_LOGIN",
        "product_name": "Custom Application",
        "vendor_name": "My Company",
        "event_id": str(uuid.uuid4())
    },
    "principal": {
        "user": {
            "userid": "jdoe@example.com",
            "user_display_name": "John Doe"
        },
        "ip": "192.168.1.100"
    },
    "target": {
        "application": "My Application"
    },
    "security_result": {
        "action": "ALLOW",
        "summary": "Successful login"
    }
}

# Ingest the UDM event
result = chronicle.ingest_udm(udm_event)

print(f"Operation: {result.get('operation')}")
```

## Batch Ingestion

You can also ingest multiple logs or UDM events in a single request:

```python
# Batch log ingestion
log_batch = [
    {
        "log_type": "OKTA",
        "log_message": json.dumps(okta_log1)
    },
    {
        "log_type": "OKTA",
        "log_message": json.dumps(okta_log2)
    }
]

batch_result = chronicle.ingest_logs_batch(log_batch)

# Batch UDM ingestion
udm_batch = [udm_event1, udm_event2, udm_event3]
udm_batch_result = chronicle.ingest_udm_batch(udm_batch)
```

## Forwarder Management

Chronicle uses forwarders to ingest logs. You can manage forwarders programmatically:

```python
# List all forwarders
forwarders = chronicle.list_forwarders()
for forwarder in forwarders:
    print(f"Forwarder: {forwarder.get('name')}")

# Create a new forwarder
new_forwarder = chronicle.create_forwarder(
    display_name="My Custom Forwarder",
    log_type="CUSTOM_LOG_TYPE"
)

# Get or create a forwarder (creates if it doesn't exist)
forwarder = chronicle.get_or_create_forwarder(
    log_type="WINDOWS_EVENT_LOG"
)
```

## Log Types

Chronicle supports many log types. You can list available log types:

```python
# List all supported log types
log_types = chronicle.list_log_types()
for log_type in log_types:
    print(f"Log Type: {log_type.get('name')}")
    print(f"Description: {log_type.get('description')}")
    print("---")
```

## Custom Timestamps

You can specify custom timestamps for your logs:

```python
# Ingest with custom timestamp
result = chronicle.ingest_log(
    log_type="OKTA",
    log_message=json.dumps(okta_log),
    entry_timestamp="2023-01-01T12:00:00Z",  # When the event occurred
    collection_timestamp="2023-01-01T12:05:00Z"  # When the log was collected
)
```

## Error Handling

```python
try:
    result = chronicle.ingest_log(
        log_type="OKTA",
        log_message=json.dumps(okta_log)
    )
except Exception as e:
    print(f"Ingestion failed: {e}")
```
