# Detection Rules

The Chronicle client provides capabilities for managing detection rules, which are used to identify suspicious or malicious activity in your data.

## Rule Formats

Chronicle supports detection rules in YARA-L2 format, a specialized language for writing detection rules.

## Listing Rules

You can list and filter detection rules:

```python
from secops import SecOpsClient

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

# List all rules
rules = chronicle.list_rules()

# Process the results
for rule in rules:
    print(f"Rule ID: {rule.get('ruleId')}")
    print(f"Name: {rule.get('ruleName')}")
    print(f"Severity: {rule.get('severity')}")
    print(f"Created: {rule.get('createTime')}")
    print("---")
```

## Getting Rule Details

You can get detailed information about a specific rule:

```python
# Get details of a specific rule
rule_details = chronicle.get_rule(
    rule_id="ru_12345678"
)

print(f"Rule ID: {rule_details.get('ruleId')}")
print(f"Name: {rule_details.get('ruleName')}")
print(f"Description: {rule_details.get('description')}")
print(f"YARA-L2 Content: {rule_details.get('content')}")
print(f"Severity: {rule_details.get('severity')}")
print(f"Created: {rule_details.get('createTime')}")
print(f"Updated: {rule_details.get('updateTime')}")
```

## Creating Rules

You can create new detection rules:

```python
# Define a YARA-L2 rule
rule_content = """
rule suspicious_login {
  meta:
    author = "Chronicle Security"
    description = "Detects suspicious login activity"
    severity = "HIGH"
  events:
    $login.metadata.event_type = "USER_LOGIN"
    $login.principal.ip = "192.168.1.100"
    $login.security_result.action = "BLOCK"
  condition:
    $login
}
"""

# Create a new rule
new_rule = chronicle.create_rule(
    rule_name="Suspicious Login Detection",
    description="Detects suspicious login attempts from specific IP",
    content=rule_content,
    severity="HIGH"
)

print(f"Rule ID: {new_rule.get('ruleId')}")
```

## Validating Rules

Before creating or updating a rule, you can validate its syntax:

```python
# Validate a YARA-L2 rule
validation_result = chronicle.validate_rule(
    content=rule_content
)

if validation_result.get('valid'):
    print("Rule is valid!")
else:
    print("Rule validation failed:")
    for error in validation_result.get('errors', []):
        print(f"Line {error.get('line')}: {error.get('message')}")
```

## Updating Rules

You can update existing rules:

```python
# Update an existing rule
update_result = chronicle.update_rule(
    rule_id="ru_12345678",
    rule_name="Updated Suspicious Login Detection",
    description="Updated description with improved detection logic",
    content=updated_rule_content,
    severity="CRITICAL"
)

print(f"Updated: {update_result.get('success')}")
```

## Enabling/Disabling Rules

You can enable or disable rules:

```python
# Disable a rule
disable_result = chronicle.disable_rule(
    rule_id="ru_12345678"
)

print(f"Rule disabled: {disable_result.get('success')}")

# Enable a rule
enable_result = chronicle.enable_rule(
    rule_id="ru_12345678"
)

print(f"Rule enabled: {enable_result.get('success')}")
```

## Deleting Rules

You can delete rules that are no longer needed:

```python
# Delete a rule
delete_result = chronicle.delete_rule(
    rule_id="ru_12345678"
)

print(f"Rule deleted: {delete_result.get('success')}")
```

## Rule Versioning

Chronicle maintains versions of rules. You can list and view rule versions:

```python
# List versions of a rule
versions = chronicle.list_rule_versions(
    rule_id="ru_12345678"
)

for version in versions:
    print(f"Version: {version.get('versionId')}")
    print(f"Created: {version.get('createTime')}")
    print("---")

# Get a specific version of a rule
version_details = chronicle.get_rule_version(
    rule_id="ru_12345678",
    version_id="v1"
)

print(f"Version Content: {version_details.get('content')}")
```

## Rule Severities

Chronicle supports the following rule severities:

| Severity | Description |
|----------|-------------|
| `CRITICAL` | Highest severity, requires immediate attention |
| `HIGH` | High severity, requires prompt attention |
| `MEDIUM` | Medium severity, should be investigated |
| `LOW` | Low severity, may be investigated as resources allow |
| `INFORMATIONAL` | Informational only, no immediate action required |

## Pagination

For large result sets, use pagination:

```python
# First page
results = chronicle.list_rules(
    page_size=25
)

# Get next page if there are more results
if results.next_page_token:
    next_page = chronicle.list_rules(
        page_size=25,
        page_token=results.next_page_token
    )
```

## Error Handling

```python
try:
    rule_details = chronicle.get_rule(
        rule_id="ru_12345678"
    )
except Exception as e:
    print(f"Rule lookup failed: {e}")
```
