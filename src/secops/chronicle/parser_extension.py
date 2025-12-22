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
"""Parser extension management functionality for Chronicle."""

import base64
import json
from dataclasses import dataclass, field
from typing import Any

from secops.exceptions import APIError


@dataclass
class ParserExtensionConfig:
    """Parser extension configuration."""

    log: str | None = None
    parser_config: str | None = None
    field_extractors: dict | str | None = None
    dynamic_parsing: dict | str | None = None
    encoded_log: str | None = field(init=False, default=None)
    encoded_cbn_snippet: str | None = field(init=False, default=None)

    @staticmethod
    def encode_base64(text: str) -> str:
        """Encode a string to base64.

        Args:
            log: Raw string

        Returns:
            Base64 encoded string
        """
        if not text:
            raise ValueError("Value cannot be empty for encoding")

        # Check if the string is already base64 encoded
        try:
            decoded = base64.b64decode(text)
            decoded.decode("utf-8")  # Validate it's valid UTF-8 when decoded
            return text  # Return valid base64 string
        except Exception:  # pylint: disable=broad-except
            # If not base64 encoded, encode it
            return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    def __post_init__(self) -> None:
        """Post initialization hook for field processing."""
        if self.log:
            self.encoded_log = self.encode_base64(self.log)
        if self.parser_config:
            self.encoded_cbn_snippet = self.encode_base64(self.parser_config)

        if self.field_extractors and isinstance(self.field_extractors, str):
            try:
                self.field_extractors = json.loads(self.field_extractors)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON for field_extractors: {e}"
                ) from e

        if self.dynamic_parsing and isinstance(self.dynamic_parsing, str):
            try:
                self.dynamic_parsing = json.loads(self.dynamic_parsing)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON for dynamic_parsing: {e}"
                ) from e

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        # Count number of non-None config fields
        config_count = sum(
            1
            for x in [
                self.parser_config,
                self.field_extractors,
                self.dynamic_parsing,
            ]
            if x is not None
        )

        if config_count != 1:
            raise ValueError(
                "Exactly one of parser_config, field_extractors, or "
                "dynamic_parsing must be specified"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary format for API request.

        Returns:
            Dict containing the configuration in API format

        Raises:
            ValueError: If configuration is invalid
        """
        self.validate()
        config = {}

        if self.encoded_log is not None:
            config["log"] = self.encoded_log
        if self.parser_config is not None:
            config["cbn_snippet"] = self.encoded_cbn_snippet
        elif self.field_extractors is not None:
            config["field_extractors"] = self.field_extractors
        elif self.dynamic_parsing is not None:
            config["dynamic_parsing"] = self.dynamic_parsing

        return config


def create_parser_extension(
    client,
    log_type: str,
    extension_config: ParserExtensionConfig | dict[str, Any],
) -> dict[str, Any]:
    """Create a parser extension.

    Args:
        client: ChronicleClient instance
        log_type: The log type for which the parser extension is being created
        extension_config: Configuration for the parser extension, can be either
            a ParserExtensionConfig instance or a dictionary with configuration

    Returns:
        Dict containing the created parser extension details

    Raises:
        APIError: If the API request fails
        ValueError: If configuration is invalid
    """
    # Convert dictionary input to ParserExtensionConfig if needed
    if isinstance(extension_config, dict):
        try:
            extension_config = ParserExtensionConfig(**extension_config)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid extension configuration: {e}") from e

    url = (
        f"{client.base_url}/{client.instance_id}/logTypes/"
        f"{log_type}/parserExtensions"
    )
    response = client.session.post(url, json=extension_config.to_dict())
    if not response.ok:
        raise APIError(f"Failed to create parser extension: {response.text}")
    return response.json()


def get_parser_extension(
    client, log_type: str, extension_id: str
) -> dict[str, Any]:
    """Get a parser extension.

    Args:
        client: ChronicleClient instance
        log_type: The log type of the parser extension
        extension_id: The ID of the parser extension

    Returns:
        Dict containing the parser extension details

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/logTypes/"
        f"{log_type}/parserExtensions/{extension_id}"
    )
    response = client.session.get(url)
    if not response.ok:
        raise APIError(f"Failed to get parser extension: {response.text}")
    return response.json()


def list_parser_extensions(
    client,
    log_type: str,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    """List parser extensions.

    Args:
        client: ChronicleClient instance
        log_type: The log type to list parser extensions for
        page_size: Maximum number of parser extensions to return
        page_token: Token for pagination

    Returns:
        Dict containing list of parser extensions and next page token if any

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/logTypes/"
        f"{log_type}/parserExtensions"
    )
    params = {}
    if page_size is not None:
        params["pageSize"] = page_size
    if page_token is not None:
        params["pageToken"] = page_token

    response = client.session.get(url, params=params)
    if not response.ok:
        raise APIError(f"Failed to list parser extensions: {response.text}")
    return response.json()


def activate_parser_extension(client, log_type: str, extension_id: str) -> None:
    """Activate a parser extension.

    Args:
        client: ChronicleClient instance
        log_type: The log type of the parser extension
        extension_id: The ID of the parser extension to activate

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/logTypes/"
        f"{log_type}/parserExtensions/{extension_id}:activate"
    )
    response = client.session.post(url)
    if not response.ok:
        raise APIError(f"Failed to activate parser extension: {response.text}")


def delete_parser_extension(client, log_type: str, extension_id: str) -> None:
    """Delete a parser extension.

    Args:
        client: ChronicleClient instance
        log_type: The log type of the parser extension
        extension_id: The ID of the parser extension to delete

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/logTypes/"
        f"{log_type}/parserExtensions/{extension_id}"
    )
    response = client.session.delete(url)
    if not response.ok:
        raise APIError(f"Failed to delete parser extension: {response.text}")
