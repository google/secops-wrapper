# IoCs Management

The Chronicle client provides capabilities for managing and querying Indicators of Compromise (IoCs).

## Querying IoCs

You can query IoCs by various attributes:

```python
from secops import SecOpsClient

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

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

## Supported IoC Types

Chronicle supports various IoC types:

| Type | Description | Example |
|------|-------------|---------|
| `IP_ADDRESS` | IPv4 or IPv6 address | `"192.168.1.100"` |
| `DOMAIN_NAME` | Domain name | `"example.com"` |
| `HASH_MD5` | MD5 hash | `"d41d8cd98f00b204e9800998ecf8427e"` |
| `HASH_SHA1` | SHA1 hash | `"da39a3ee5e6b4b0d3255bfef95601890afd80709"` |
| `HASH_SHA256` | SHA256 hash | `"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"` |
| `URL` | URL | `"https://example.com/path"` |
| `EMAIL_ADDRESS` | Email address | `"user@example.com"` |

## Listing IoCs

You can list all IoCs or filter by various criteria:

```python
# List all IoCs from the last 7 days
all_iocs = chronicle.list_iocs(
    start_time="7d"
)

# List IoCs with filtering
filtered_iocs = chronicle.list_iocs(
    start_time="30d",
    artifact_type="DOMAIN_NAME",
    limit=100
)

# Process the results
for ioc in filtered_iocs:
    print(f"IoC: {ioc.get('artifactValue')}")
    print(f"Type: {ioc.get('artifactType')}")
    print("---")
```

## IoC Reputation

You can check the reputation of an IoC:

```python
# Check reputation of a domain
reputation = chronicle.ioc_reputation(
    artifact_value="example.com",
    artifact_type="DOMAIN_NAME"
)

print(f"Reputation score: {reputation.get('score')}")
print(f"Category: {reputation.get('category')}")
print(f"Source: {reputation.get('source')}")
```

## IoC Enrichment

Get additional context about an IoC:

```python
# Get enrichment for an IP address
enrichment = chronicle.ioc_enrichment(
    artifact_value="8.8.8.8",
    artifact_type="IP_ADDRESS"
)

print(f"ASN: {enrichment.get('asn')}")
print(f"Country: {enrichment.get('country')}")
print(f"Owner: {enrichment.get('owner')}")
```

## IoC Relationships

Discover relationships between IoCs and other entities:

```python
# Get relationships for a domain
relationships = chronicle.ioc_relationships(
    artifact_value="example.com",
    artifact_type="DOMAIN_NAME",
    relationship_type="RESOLVES_TO"
)

for relationship in relationships:
    print(f"Related to: {relationship.get('relatedArtifact')}")
    print(f"Relationship: {relationship.get('relationshipType')}")
    print(f"First seen: {relationship.get('firstSeenTime')}")
    print("---")
```

## Time Formats

The IoC API supports multiple time formats:

- **Relative time**: `"1h"`, `"6h"`, `"1d"`, `"7d"`, `"30d"`
- **ISO 8601**: `"2023-01-01T00:00:00Z"`
- **RFC 3339**: `"2023-01-01T00:00:00+00:00"`

## Pagination

For large result sets, use pagination:

```python
# First page
results = chronicle.list_iocs(
    start_time="30d",
    page_size=25
)

# Get next page if there are more results
if results.next_page_token:
    next_page = chronicle.list_iocs(
        start_time="30d",
        page_size=25,
        page_token=results.next_page_token
    )
```

## Error Handling

```python
try:
    ioc_results = chronicle.ioc_details(
        artifact_value="192.168.1.100",
        artifact_type="IP_ADDRESS"
    )
except Exception as e:
    print(f"IoC lookup failed: {e}")
```
