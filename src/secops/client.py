# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main client for Google SecOps SDK."""

from typing import Any

from google.auth.credentials import Credentials

from secops.auth import RetryConfig, SecOpsAuth
from secops.chronicle import ChronicleClient


class SecOpsClient:
    """Main client class for interacting with Google SecOps."""

    def __init__(
        self,
        credentials: Credentials | None = None,
        service_account_path: str | None = None,
        service_account_info: dict[str, Any] | None = None,
        impersonate_service_account: str | None = None,
        retry_config: RetryConfig | dict[str, Any] | bool | None = None,
    ):
        """Initialize the SecOps client.

        Args:
            credentials: Optional pre-existing Google Auth credentials
            service_account_path: Optional path to service account JSON key file
            service_account_info: Optional service account JSON key data as dict
            impersonate_service_account: Optional service account to impersonate
            retry_config: Request retry configurations.
                If set to false, retry will be disabled.
        """
        self.auth = SecOpsAuth(
            credentials=credentials,
            service_account_path=service_account_path,
            service_account_info=service_account_info,
            impersonate_service_account=impersonate_service_account,
            retry_config=retry_config,
        )
        self._chronicle = None

    def chronicle(
        self,
        customer_id: str,
        project_id: str,
        region: str = "us",
        default_api_version: str | Any = "v1alpha",
    ) -> ChronicleClient:
        """Get Chronicle API client.

        Args:
            customer_id: Chronicle customer ID
            project_id: GCP project ID
            region: Chronicle API region (default: "us")
            default_api_version: Default API version for Chronicle requests.
                Can be "v1", "v1beta", or "v1alpha" (default: "v1alpha").

        Returns:
            ChronicleClient instance
        """
        return ChronicleClient(
            customer_id=customer_id,
            project_id=project_id,
            region=region,
            auth=self.auth,
            default_api_version=default_api_version,
        )
