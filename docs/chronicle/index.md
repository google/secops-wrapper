# Chronicle Client

## Initializing the Chronicle Client

After creating a SecOpsClient, you need to initialize the Chronicle-specific client:

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

For available regions, see the [Regions documentation](../advanced/regions.md).

## Features

The Chronicle client provides access to the following features:

### Data Ingestion and Search

- Log Ingestion - Ingest raw logs directly into Chronicle
- UDM Search - Search for events in the Universal Data Model (UDM)
- Natural Language Search - Search using natural language queries

### Security Intelligence

- IoCs Management - Manage Indicators of Compromise
- Entity Graph - Get detailed information about specific entities

### Alert and Case Management

- Alert Management - Retrieve and manage alerts
- Case Management - Create and manage cases

### Detection Rules

- Detection Rules - Manage detection rules
- Retrohunts - Run retroactive hunts against historical data

## Examples

Here's a simple example of using the Chronicle client to search for events:

```python
# Search for events in the last 24 hours
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

## Next Steps

Explore the specific features of the Chronicle client in the following pages:
