# Chronicle API Regions

When initializing the Chronicle client, you need to specify the region parameter corresponding to where your Chronicle instance is installed. Use the lowercase version of one of the following values:

| Region Code | Description |
|-------------|-------------|
| `us` | United States - multi-region |
| `europe` | Europe (Default European region) |
| `asia_southeast1` | Singapore |
| `europe_west2` | London |
| `australia_southeast1` | Sydney |
| `me_west1` | Israel |
| `europe_west6` | Zurich |
| `europe_west3` | Frankfurt |
| `me_central2` | Dammam |
| `asia_south1` | Mumbai |
| `asia_northeast1` | Tokyo |
| `northamerica_northeast2` | Toronto |
| `europe_west12` | Turin |
| `me_central1` | Doha |
| `southamerica_east1` | Sao Paulo |
| `europe_west9` | Paris |

## Usage Example

```python
# Initialize Chronicle client with the appropriate region
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"  # Use lowercase region code from the table above
)
```

Always use the lowercase version of the region code when configuring your Chronicle client.
