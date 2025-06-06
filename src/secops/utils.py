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
"""Contains any useful (to the SecOps library) things that are reused in different places"""

import ipaddress
import re
from typing import List

from secops.exceptions import SecOpsError

REF_LIST_DATA_TABLE_ID_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{0,254}$")
"""Ensures the reference list/data table id/name matches the following conditions:
    - Starts with letter.
    - Contains only letters, numbers and underscore.
    - Has length < 256
"""


def _validate_cidr_entries(entries: List[str]) -> None:
    """Checks if an IP is valid CIDR.
    
    Args:
        entries: A list of CIDR entries.
        
    Raises:
        SecOpsError: If a CIDR entry is invalid.
    """
    for x in entries:
        try:
            ipaddress.ip_network(x)
        except ValueError:
            raise SecOpsError(f"Invalid CIDR entry: {x}")