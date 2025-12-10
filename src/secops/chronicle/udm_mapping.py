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
"""UDM key/value mapping functionality of Chronicle"""

import base64
import sys
from typing import Any

from secops.exceptions import APIError

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


class RowLogFormat(StrEnum):
    """Enum for log format specification."""

    JSON = "JSON"
    CSV = "CSV"
    XML = "XML"
    LOG_FORMAT_UNSPECIFIED = "LOG_FORMAT_UNSPECIFIED"


def generate_udm_key_value_mappings(
    client,
    log_format: RowLogFormat,
    log: str,
    use_array_bracket_notation: bool | None = None,
    compress_array_fields: bool | None = None,
) -> dict[str, Any]:
    """Generate key-value mappings for a UDM field using Chronicle V1alpha API.

    This function retrieves all unique values for the specified UDM field
    across events within the given time range.

    Args:
        client: ChronicleClient instance
        log_format: Log format (JSON, CSV, XML, or LOG_FORMAT_UNSPECIFIED)
        log: Row log to generate key-value mapping
        use_array_bracket_notation: Flag to format arrays as bracket notation.
        compress_array_fields: Flag to compress array fields.

    Returns:
        Dict containing the generated key-value mapping

    Raises:
        APIError: If the API request fails
    """
    # Endpoint for UDM key-value mappings
    url = f"{client.base_url}/{client.instance_id}:generateUdmKeyValueMappings"

    encoded_log = None
    try:
        decoded = base64.b64decode(log)
        decoded.decode("utf-8")  # Validate it's valid UTF-8 when decoded
        encoded_log = log
    except Exception:  # pylint: disable=broad-except
        # If not base64 encoded, encode it
        encoded_log = base64.b64encode(log.encode("utf-8")).decode("utf-8")

    payload = {"log_format": log_format, "log": encoded_log}

    if use_array_bracket_notation is not None:
        payload["use_array_bracket_notation"] = use_array_bracket_notation
    if compress_array_fields is not None:
        payload["compress_array_fields"] = compress_array_fields

    response = client.session.post(url, json=payload)

    if response.status_code != 200:
        raise APIError(f"Failed to generate key/value mapping: {response.text}")

    # Return field mappings from parsed response
    return response.json().get("fieldMappings")
