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

import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from http import HTTPStatus
from types import TracebackType
from typing import Any

import google.auth
import google.auth.transport.requests
from google.auth import impersonated_credentials
from google.auth.credentials import Credentials
from google.oauth2 import service_account
from requests.adapters import HTTPAdapter, Retry
from urllib3 import BaseHTTPResponse
from urllib3.connectionpool import ConnectionPool

from secops.exceptions import AuthenticationError

# Use built-in HTTPMethod from http if Python 3.11+,
# otherwise create a compatible version
if sys.version_info >= (3, 11):
    from http import HTTPMethod
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value

    class HTTPMethod(StrEnum):
        """HTTP method names."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"


# Define default scopes needed for Chronicle API
CHRONICLE_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


@dataclass
class RetryConfig:
    """Configuration for HTTP request retry behavior.

    Attributes:
        total: Maximum number of retries to attempt.
        retry_status_codes: List of HTTP status codes that should trigger
            a retry.
        allowed_methods: List of HTTP methods that are allowed to be retried.
        backoff_factor: A backoff factor to apply between retry attempts.
    """

    total: int = 5
    retry_status_codes: Sequence[int] = field(
        default_factory=lambda: [
            HTTPStatus.TOO_MANY_REQUESTS.value,  # 429
            HTTPStatus.INTERNAL_SERVER_ERROR.value,  # 500
            HTTPStatus.BAD_GATEWAY.value,  # 502
            HTTPStatus.SERVICE_UNAVAILABLE.value,  # 503
            HTTPStatus.GATEWAY_TIMEOUT.value,  # 504
        ]
    )
    allowed_methods: Sequence[str] = field(
        default_factory=lambda: [
            HTTPMethod.GET.value,
            HTTPMethod.PUT.value,
            HTTPMethod.DELETE.value,
            HTTPMethod.POST.value,
            HTTPMethod.PATCH.value,
        ]
    )
    backoff_factor: float = 0.3

    def to_dict(self) -> dict[str, Any]:
        """Convert the config to a dictionary for urllib3.Retry."""
        return asdict(self)


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig()


class LogRetry(Retry):
    """Retry strategy configuration with logging."""

    def increment(
        self,
        method: str | None = None,
        url: str | None = None,
        response: BaseHTTPResponse | None = None,
        error: Exception | None = None,
        _pool: ConnectionPool | None = None,
        _stacktrace: TracebackType | None = None,
    ) -> Retry:
        """Return a new Retry object with incremented retry counters and logs
        retry attempt.

        Args:
            method: HTTP method used in the request.
            url: URL of the request.
            response: A response object, or None, if the server did not
                return a response.
            error: An error encountered during the request, or
                None if the response was received successfully.

        Returns:
            Retry object with incremented retry counters.
        """
        if response:
            print(
                f"Retrying {method} {url} for {response.status} "
                f"status code....",
                file=sys.stderr,
            )
        else:
            print(
                f"Retrying {method} {url} due to error: {error}",
                file=sys.stderr,
            )

        return super().increment(
            method, url, response, error, _pool, _stacktrace
        )


class SecOpsAuth:
    """Handles authentication for the Google SecOps SDK."""

    def __init__(
        self,
        credentials: Credentials | None = None,
        service_account_path: str | None = None,
        service_account_info: dict[str, Any] | None = None,
        impersonate_service_account: str | None = None,
        scopes: list[str] | None = None,
        retry_config: RetryConfig | dict[str, Any] | bool | None = None,
    ):
        """Initialize authentication for SecOps.

        Args:
            credentials: Optional pre-existing Google Auth credentials
            service_account_path: Optional path to service account JSON key file
            service_account_info: Optional service account JSON key data as dict
            impersonate_service_account: Optional service account to impersonate
            scopes: Optional list of OAuth scopes to request
            retry_config: Request retry configurations.
                If set to false, retry will be disabled.
        """
        self.scopes = scopes or CHRONICLE_SCOPES
        self.credentials = self._get_credentials(
            credentials,
            service_account_path,
            service_account_info,
            impersonate_service_account,
        )
        self._session = None

        self.retry_config = retry_config

    def _get_credentials(
        self,
        credentials: Credentials | None,
        service_account_path: str | None,
        service_account_info: dict[str, Any] | None,
        impersonate_service_account: str | None,
    ) -> Credentials:
        """Get credentials from various sources."""
        try:
            if credentials:
                google_credentials = credentials.with_scopes(self.scopes)

            elif service_account_info:
                google_credentials = (
                    service_account.Credentials.from_service_account_info(
                        service_account_info, scopes=self.scopes
                    )
                )

            elif service_account_path:
                google_credentials = (
                    service_account.Credentials.from_service_account_file(
                        service_account_path, scopes=self.scopes
                    )
                )

            else:
                # Try to get default credentials
                google_credentials, _ = google.auth.default(scopes=self.scopes)

            if impersonate_service_account:
                target_credentials = impersonated_credentials.Credentials(
                    source_credentials=google_credentials,
                    target_principal=impersonate_service_account,
                    target_scopes=self.scopes,
                    lifetime=600,
                )
                return target_credentials
            return google_credentials
        except Exception as e:
            raise AuthenticationError(
                f"Failed to get credentials: {str(e)}"
            ) from e

    @property
    def session(self):
        """Get an authorized session with retry mechanism using the credentials.

        Returns:
            Authorized session for API requests
        """
        if self._session is None:
            self._session = google.auth.transport.requests.AuthorizedSession(
                self.credentials
            )
            # Set custom user agent
            self._session.headers["User-Agent"] = "secops-wrapper-sdk"

        # Configure retry mechanism unless set false.
        if self.retry_config is not False and self._session:
            self._configure_retry()

        return self._session

    def _configure_retry(self):
        """Configure retry mechanism for the session."""

        # The default configuration
        config = DEFAULT_RETRY_CONFIG

        if isinstance(self.retry_config, RetryConfig):
            config = self.retry_config
        elif isinstance(self.retry_config, dict):
            updated_config = RetryConfig(
                **{**config.to_dict(), **self.retry_config}
            )
            config = updated_config

        # Retry strategy from configuration
        retry_strategy = LogRetry(
            total=config.total,
            status_forcelist=config.retry_status_codes,
            allowed_methods=config.allowed_methods,
            backoff_factor=config.backoff_factor,
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        # Adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)

        # Mount adapter to session for both http and https
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
