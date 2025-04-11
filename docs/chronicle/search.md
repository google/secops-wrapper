# UDM Search

The Chronicle client provides powerful search capabilities for querying events in the Universal Data Model (UDM) format.

## Basic Search

```python
from secops import SecOpsClient

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

# Perform a simple search for the last 24 hours
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

## Search Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | UDM search query string | `"metadata.product_name = \"Okta\""` |
| `start_time` | Start time for the search | `"1d"`, `"2023-01-01T00:00:00Z"` |
| `end_time` | End time for the search (optional) | `"2023-01-02T00:00:00Z"` |
| `limit` | Maximum number of results (optional) | `100` |
| `page_size` | Number of results per page (optional) | `25` |
| `page_token` | Token for pagination (optional) | `"token123"` |

## Time Formats

The search API supports multiple time formats:

- **Relative time**: `"1h"`, `"6h"`, `"1d"`, `"7d"`, `"30d"`
- **ISO 8601**: `"2023-01-01T00:00:00Z"`
- **RFC 3339**: `"2023-01-01T00:00:00+00:00"`

## Advanced Queries

```python
# Search with multiple conditions
results = chronicle.search(
    query="""
        metadata.product_name = "Okta" AND
        metadata.event_type = "USER_LOGIN" AND
        principal.user.userid = "jdoe@example.com"
    """,
    start_time="7d"
)
```

## Natural Language Search

Chronicle also supports natural language queries:

```python
# Perform a natural language search
nl_results = chronicle.nl_search(
    query="Show me all failed login attempts in the last 24 hours",
    start_time="1d"
)

# Process the results
for event in nl_results:
    print(f"Event time: {event.get('metadata', {}).get('event_timestamp')}")
    print(f"Product: {event.get('metadata', {}).get('product_name')}")
    print("---")
```

## Translating Natural Language to UDM

You can also translate natural language queries to UDM syntax:

```python
# Translate a natural language query to UDM
udm_query = chronicle.translate_nl_to_udm(
    query="Show me all failed login attempts in the last 24 hours"
)

print(f"UDM Query: {udm_query}")
```

## Pagination

For large result sets, use pagination:

```python
# First page
results = chronicle.search(
    query="metadata.product_name = \"Okta\"",
    start_time="30d",
    page_size=25
)

# Get next page if there are more results
if results.next_page_token:
    next_page = chronicle.search(
        query="metadata.product_name = \"Okta\"",
        start_time="30d",
        page_size=25,
        page_token=results.next_page_token
    )
```

## Error Handling

```python
try:
    results = chronicle.search(
        query="metadata.product_name = \"Okta\"",
        start_time="1d"
    )
except Exception as e:
    print(f"Search failed: {e}")
```
