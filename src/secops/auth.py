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
#
"""Authentication handling for Google SecOps SDK."""
from typing import Optional, Dict, Any, List
from google.auth.credentials import Credentials
from google.oauth2 import service_account
import google.auth
import google.auth.transport.requests
from secops.exceptions import AuthenticationError

# Define default scopes needed for Chronicle API
CHRONICLE_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


class SecOpsAuth:
    """Handles authentication for the Google SecOps SDK."""

    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        service_account_path: Optional[str] = None,
        service_account_info: Optional[Dict[str, Any]] = None,
        scopes: Optional[List[str]] = None,
    ):
        """Initialize authentication for SecOps.

        Args:
            credentials: Optional pre-existing Google Auth credentials
            service_account_path: Optional path to service account JSON key file
            service_account_info: Optional service account JSON key data as dict
            scopes: Optional list of OAuth scopes to request
        """
        self.scopes = scopes or CHRONICLE_SCOPES
        self.credentials = self._get_credentials(
            credentials, service_account_path, service_account_info
        )
        self._session = None

    def _get_credentials(
        self,
        credentials: Optional[Credentials],
        service_account_path: Optional[str],
        service_account_info: Optional[Dict[str, Any]],
    ) -> Credentials:
        """Get credentials from various sources."""
        try:
            if credentials:
                return credentials.with_scopes(self.scopes)

            if service_account_info:
                return service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=self.scopes
                )

            if service_account_path:
                return service_account.Credentials.from_service_account_file(
                    service_account_path, scopes=self.scopes
                )

            # Try to get default credentials
            credentials, project = google.auth.default(scopes=self.scopes)
            return credentials
        except Exception as e:
            raise AuthenticationError(f"Failed to get credentials: {str(e)}")

    @property
    def session(self):
        """Get an authorized session using the credentials.

        Returns:
            Authorized session for API requests
        """
        if self._session is None:
            self._session = google.auth.transport.requests.AuthorizedSession(
                self.credentials
            )
        return self._session
