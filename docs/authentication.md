# Authentication

## 1. Application Default Credentials (ADC)

### a. Using gcloud CLI (Recommended for Local Development)

```
# Login and set up application-default credentials
gcloud auth application-default login
```

Then in your code:

```python
from secops import SecOpsClient

# Initialize with default credentials - no explicit configuration needed
client = SecOpsClient()
```

### b. Using Environment Variable

Set the environment variable pointing to your service account key:

```
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

Then in your code:

```python
from secops import SecOpsClient

# Initialize with default credentials - will automatically use the credentials file
client = SecOpsClient()
```

### c. Google Cloud Environment (Automatic)

When running on Google Cloud services (Compute Engine, Cloud Functions, Cloud Run, etc.), ADC works automatically without any configuration:

```python
from secops import SecOpsClient

# Initialize with default credentials - will automatically use the service account
# assigned to your Google Cloud resource
client = SecOpsClient()
```

ADC will automatically try these authentication methods in order:
1. Environment variable `GOOGLE_APPLICATION_CREDENTIALS`
2. Google Cloud SDK credentials (set by `gcloud auth application-default login`)
3. Google Cloud-provided service account credentials
4. Local service account impersonation credentials

## 2. Service Account Authentication

### a. Using a Service Account JSON File

```python
from secops import SecOpsClient

# Initialize with service account JSON file
client = SecOpsClient(service_account_path="/path/to/service-account.json")
```

### b. Using Service Account Info Dictionary

```python
from secops import SecOpsClient

# Service account details as a dictionary
service_account_info = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN...",
    "client_email": "service-account@project.iam.gserviceaccount.com",
    "client_id": "client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}

# Initialize with service account info
client = SecOpsClient(service_account_info=service_account_info)
```

## Next Steps

After authenticating, you'll need to initialize the Chronicle client. See the [Quick Start Guide](quickstart.md) for more information.
