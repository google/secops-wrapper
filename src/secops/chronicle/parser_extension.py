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

from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_request,
    chronicle_paginated_request,
)


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

    return chronicle_request(
        client,
        method="POST",
        endpoint_path=f"logTypes/{log_type}/parserExtensions",
        json=extension_config.to_dict(),
        error_message="Failed to create parser extension",
    )


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
    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"logTypes/{log_type}/parserExtensions/{extension_id}",
        error_message="Failed to get parser extension",
    )


def list_parser_extensions(
    client,
    log_type: str,
    page_size: int | None = None,
    page_token: str | None = None,
    as_list: bool = False,
) -> dict[str, Any] | list[Any]:
    """List parser extensions.

    Args:
        client: ChronicleClient instance
        log_type: The log type to list parser extensions for
        page_size: Maximum number of parser extensions to return
        page_token: Token for pagination
        as_list: If True, return only the list of parser extensions.
            If False, return dict with metadata and pagination tokens.

    Returns:
        If as_list is True: List of parser extensions.
        If as_list is False: Dict with parserExtensions list and
            pagination metadata.

    Raises:
        APIError: If the API request fails
    """
    return chronicle_paginated_request(
        client,
        path=f"logTypes/{log_type}/parserExtensions",
        items_key="parserExtensions",
        page_size=page_size,
        page_token=page_token,
        as_list=as_list,
    )


def activate_parser_extension(client, log_type: str, extension_id: str) -> None:
    """Activate a parser extension.

    Args:
        client: ChronicleClient instance
        log_type: The log type of the parser extension
        extension_id: The ID of the parser extension to activate

    Raises:
        APIError: If the API request fails
    """
    chronicle_request(
        client,
        method="POST",
        endpoint_path=(
            f"logTypes/{log_type}/parserExtensions/{extension_id}:activate"
        ),
        error_message="Failed to activate parser extension",
    )


def delete_parser_extension(client, log_type: str, extension_id: str) -> None:
    """Delete a parser extension.

    Args:
        client: ChronicleClient instance
        log_type: The log type of the parser extension
        extension_id: The ID of the parser extension to delete

    Raises:
        APIError: If the API request fails
    """
    chronicle_request(
        client,
        method="DELETE",
        endpoint_path=f"logTypes/{log_type}/parserExtensions/{extension_id}",
        error_message="Failed to delete parser extension",
    )
