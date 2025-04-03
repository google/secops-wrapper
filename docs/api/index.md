# API Reference

## SecOpsClient

The SecOpsClient is the main entry point for the SDK. It provides access to all Google Security Operations products.

```python
from secops import SecOpsClient

# Initialize with default credentials
client = SecOpsClient()
```

## Chronicle Client

The Chronicle client provides access to all Chronicle/SecOps SIEM features.

```python
# Initialize Chronicle client
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)
```

## Module Reference

### Core Modules

- `secops` - Main SDK module
- `secops.chronicle` - Chronicle client module

### Chronicle Feature Modules

- `secops.chronicle.search` - UDM search functionality
- `secops.chronicle.ingestion` - Log ingestion functionality
- `secops.chronicle.iocs` - IoCs management functionality
- `secops.chronicle.alerts` - Alert management functionality
- `secops.chronicle.cases` - Case management functionality
- `secops.chronicle.rules` - Detection rules functionality
- `secops.chronicle.entity` - Entity graph functionality
- `secops.chronicle.retrohunts` - Retrohunts functionality

### Utility Modules

- `secops.auth` - Authentication utilities
- `secops.utils` - General utilities
- `secops.exceptions` - Exception classes
