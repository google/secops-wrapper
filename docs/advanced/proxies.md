# Using Proxies with the SecOps SDK

## Basic Proxy Configuration

### Environment Variables Method (Recommended)

The simplest way to configure a proxy is through environment variables:

```bash
# For HTTP traffic
export HTTP_PROXY="http://proxy.example.com:3128"

# For HTTPS traffic (most common for Chronicle API)
export HTTPS_PROXY="http://proxy.example.com:3128"

# Optional: Bypass proxy for specific hosts
export NO_PROXY="localhost,127.0.0.1,.internal.domain"
```

Then use the SDK normally:

```python
from secops import SecOpsClient

# The client will automatically use the configured proxy
client = SecOpsClient()
chronicle = client.chronicle(region="us")
```

### Programmatic Configuration

You can also set proxy configuration in your code:

```python
import os

# Set proxy before initializing the SDK
os.environ['HTTPS_PROXY'] = 'http://proxy.example.com:3128'
os.environ['HTTP_PROXY'] = 'http://proxy.example.com:3128'

from secops import SecOpsClient
client = SecOpsClient()
```

## Authentication

### Proxy Authentication

If your proxy requires authentication, include the credentials in the proxy URL:

```bash
export HTTPS_PROXY="http://username:password@proxy.example.com:3128"
```

### Google Authentication Through Proxy

The SDK will automatically route Google authentication requests through the configured proxy.

## SSL/TLS Configuration

### Custom Certificates

If your organization uses custom certificates for SSL inspection, you may need to configure the SDK to trust these certificates:

```bash
# Set the path to your organization's CA certificate bundle
export REQUESTS_CA_BUNDLE="/path/to/your/ca-bundle.crt"
```

### Self-signed Certificates (Not Recommended for Production)

For testing environments only, you can disable certificate verification (not recommended for production):

```python
import os
os.environ['SECOPS_VERIFY_SSL'] = 'false'
```

## Required Proxy Access

Ensure your proxy allows access to the following domains:

- `*.googleapis.com` - For all Google API access
- `oauth2.googleapis.com` - For authentication
- `chronicle.security.googleapis.com` - For Chronicle API access

## Troubleshooting

### Common Issues

- **Connection Errors**: Verify proxy URL format and connectivity
- **Authentication Failures**: Check proxy credentials and Google service account permissions
- **SSL/TLS Errors**: Ensure proper certificate configuration

### Debug Logging

Enable debug logging to troubleshoot proxy issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `HTTP_PROXY` | Proxy for HTTP requests |
| `HTTPS_PROXY` | Proxy for HTTPS requests |
| `NO_PROXY` | Comma-separated list of hosts to bypass proxy |
| `REQUESTS_CA_BUNDLE` | Path to custom CA certificate bundle |
| `SECOPS_VERIFY_SSL` | Set to 'false' to disable SSL verification (not recommended) |

## Best Practices

1. Always use environment variables for proxy configuration when possible
2. Use a secure HTTPS proxy for production environments
3. Never disable SSL verification in production
4. Configure proper certificate validation for SSL inspection proxies
5. Use specific NO_PROXY entries to optimize performance for internal resources
