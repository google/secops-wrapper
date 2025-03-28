# Entity Graph

The Chronicle client provides capabilities for querying the Entity Graph, which contains detailed information about entities in your environment.

## Entity Types

Chronicle supports various entity types:

- Users
- Assets (computers, servers, etc.)
- IP addresses
- Domains
- Files
- Applications
- And more

## Getting Entity Details

You can get detailed information about a specific entity:

```python
from secops import SecOpsClient

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

# Get details of a user entity
user_details = chronicle.get_entity(
    entity_type="USER",
    entity_value="jdoe@example.com"
)

print(f"Entity ID: {user_details.get('id')}")
print(f"Type: {user_details.get('type')}")
print(f"First seen: {user_details.get('firstSeenTime')}")
print(f"Last seen: {user_details.get('lastSeenTime')}")

# Get details of an asset entity
asset_details = chronicle.get_entity(
    entity_type="ASSET",
    entity_value="workstation-123"
)

# Get details of an IP address entity
ip_details = chronicle.get_entity(
    entity_type="IP_ADDRESS",
    entity_value="192.168.1.100"
)
```

## Entity Relationships

You can discover relationships between entities:

```python
# Get relationships for a user
relationships = chronicle.get_entity_relationships(
    entity_type="USER",
    entity_value="jdoe@example.com",
    relationship_type="LOGGED_INTO"
)

for relationship in relationships:
    print(f"Related to: {relationship.get('relatedEntity')}")
    print(f"Relationship: {relationship.get('relationshipType')}")
    print(f"First seen: {relationship.get('firstSeenTime')}")
    print(f"Last seen: {relationship.get('lastSeenTime')}")
    print("---")
```

## Entity Timeline

You can get a timeline of events for an entity:

```python
# Get timeline for a user
timeline = chronicle.get_entity_timeline(
    entity_type="USER",
    entity_value="jdoe@example.com",
    start_time="7d"
)

for event in timeline:
    print(f"Event time: {event.get('metadata', {}).get('event_timestamp')}")
    print(f"Event type: {event.get('metadata', {}).get('event_type')}")
    print(f"Product: {event.get('metadata', {}).get('product_name')}")
    print("---")
```

## Entity Risk Score

You can get the risk score for an entity:

```python
# Get risk score for a user
risk_score = chronicle.get_entity_risk_score(
    entity_type="USER",
    entity_value="jdoe@example.com"
)

print(f"Risk score: {risk_score.get('score')}")
print(f"Risk level: {risk_score.get('level')}")
print(f"Last updated: {risk_score.get('updateTime')}")
```

## Entity Alerts

You can get alerts associated with an entity:

```python
# Get alerts for a user
alerts = chronicle.get_entity_alerts(
    entity_type="USER",
    entity_value="jdoe@example.com",
    start_time="30d"
)

for alert in alerts:
    print(f"Alert ID: {alert.get('id')}")
    print(f"Name: {alert.get('name')}")
    print(f"Severity: {alert.get('severity')}")
    print(f"Created: {alert.get('createTime')}")
    print("---")
```

## Entity Assets

You can get assets associated with a user:

```python
# Get assets for a user
assets = chronicle.get_entity_assets(
    entity_type="USER",
    entity_value="jdoe@example.com"
)

for asset in assets:
    print(f"Asset: {asset.get('name')}")
    print(f"Type: {asset.get('type')}")
    print(f"First seen: {asset.get('firstSeenTime')}")
    print(f"Last seen: {asset.get('lastSeenTime')}")
    print("---")
```

## Entity Users

You can get users associated with an asset:

```python
# Get users for an asset
users = chronicle.get_entity_users(
    entity_type="ASSET",
    entity_value="workstation-123"
)

for user in users:
    print(f"User: {user.get('name')}")
    print(f"First seen: {user.get('firstSeenTime')}")
    print(f"Last seen: {user.get('lastSeenTime')}")
    print("---")
```

## Time Formats

The Entity API supports multiple time formats:

- **Relative time**: `"1h"`, `"6h"`, `"1d"`, `"7d"`, `"30d"`
- **ISO 8601**: `"2023-01-01T00:00:00Z"`
- **RFC 3339**: `"2023-01-01T00:00:00+00:00"`

## Pagination

For large result sets, use pagination:

```python
# First page
results = chronicle.get_entity_timeline(
    entity_type="USER",
    entity_value="jdoe@example.com",
    start_time="30d",
    page_size=25
)

# Get next page if there are more results
if results.next_page_token:
    next_page = chronicle.get_entity_timeline(
        entity_type="USER",
        entity_value="jdoe@example.com",
        start_time="30d",
        page_size=25,
        page_token=results.next_page_token
    )
```

## Error Handling

```python
try:
    user_details = chronicle.get_entity(
        entity_type="USER",
        entity_value="jdoe@example.com"
    )
except Exception as e:
    print(f"Entity lookup failed: {e}")
```
