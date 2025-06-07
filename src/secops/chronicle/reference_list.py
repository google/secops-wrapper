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
"""Reference list management functionality for Chronicle."""

from enum import StrEnum
from typing import Any, Dict, List
from secops.chronicle.client import ChronicleClient
from secops.exceptions import APIError, SecOpsError
from secops.utils import REF_LIST_DATA_TABLE_ID_REGEX, _validate_cidr_entries


class ReferenceListSyntaxType(StrEnum):
    """The syntax type indicating how list entries should be validated."""

    STRING = "REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING"
    """List contains plain text patterns."""
    REGEX = "REFERENCE_LIST_SYNTAX_TYPE_REGEX"
    """List contains only Regular Expression patterns."""
    CIDR = "REFERENCE_LIST_SYNTAX_TYPE_CIDR"
    """List contains only CIDR patterns."""


class ReferenceListView(StrEnum):
    """ReferenceListView is a mechanism for viewing partial responses of the ReferenceList resource."""

    UNSPECIFIED = "REFERENCE_LIST_VIEW_UNSPECIFIED"
    """The default / unset value. The API will default to the BASIC view for ListReferenceLists. The API will default to the FULL view for methods that return a single ReferenceList resource."""
    BASIC = "REFERENCE_LIST_VIEW_BASIC"
    """Include metadata about the ReferenceList. This is the default view for ListReferenceLists."""
    FULL = "REFERENCE_LIST_VIEW_FULL"
    """Include all details about the ReferenceList: metadata, content lines, associated rule counts. This is the default view for GetReferenceList."""


def create_reference_list(
    client: ChronicleClient,
    name: str,
    description: str = "",
    entries: List[str] = [],
    syntax_type: ReferenceListSyntaxType = ReferenceListSyntaxType.STRING,
) -> Dict[str, Any]:
    """Creates a new reference list.

    Args:
        client: ChronicleClient instance
        name: The name for the new reference list.
        entries: A list of entries for the reference list.
        description: A user-provided description of the reference list.
        syntax_type: The syntax type of the reference list.

    Returns:
        The created reference list.

    Raises:
        APIError: If the API request fails.
        SecOpsError: If the reference list name is invalid or a CIDR entry is invalid.
    """
    if not REF_LIST_DATA_TABLE_ID_REGEX.match(name):
        raise SecOpsError(
            f"Invalid reference list name: {name}.\n{REF_LIST_DATA_TABLE_ID_REGEX.__doc__.replace("Ensures", "Ensure", 1)}"
        )
    if syntax_type == ReferenceListSyntaxType.CIDR:
        _validate_cidr_entries(entries)
    if (
        response := client.session.post(
            f"{client.base_url}/{client.instance_id}/referenceLists",
            body={
                "description": description,
                "entries": [{"value": x} for x in entries],
                "syntaxType": syntax_type.value,
            },
            params={"referenceListId": name},
        )
    ).status_code != 200:
        raise APIError(f"Failed to create reference list: {response.text}")
    return response.json()


def get_reference_list(
    client: ChronicleClient, name: str, view: ReferenceListView = ReferenceListView.FULL
) -> Dict[str, Any]:
    """Gets a single reference list.

    Args:
        client: ChronicleClient instance
        name: The name of the reference list.
        view (optional): How much of the ReferenceList to view. Defaults to REFERENCE_LIST_VIEW_FULL.

    Returns:
        Dictionary containing the reference list.

    Raises:
        APIError: If the API request fails.
    """
    if (
        response := client.session.get(
            f"{client.base_url}/{client.instance_id}/referenceLists/{name}",
            params={"view": view.value},
        )
    ).status_code != 200:
        raise APIError(f"Failed to get reference list: {response.text}")
    return response.json()


def list_reference_lists(
    client: ChronicleClient,
    view: ReferenceListView = ReferenceListView.BASIC,
) -> List[Dict[str, Any]]:
    """Lists a collection of reference lists.

    Args:
        client: ChronicleClient instance
        view (optional): How much of each ReferenceList to view. Defaults to REFERENCE_LIST_VIEW_BASIC.

    Returns:
        List of reference lists, ordered in ascending alphabetical order by name.

    Raises:
        APIError: If the API request fails.
    """
    ref_lists = []
    params = {"pageSize": 1000, "view": view.value}
    while True:
        if (
            response := client.session.get(
                f"{client.base_url}/{client.instance_id}/referenceLists",
                params=params,
            )
        ).status_code != 200:
            raise APIError(f"Failed to list reference lists: {response.text}")
        ref_lists += response.json().get("referenceLists", [])
        if "nextPageToken" in response.json():
            params["pageToken"] = response.json()["nextPageToken"]
        else:
            break
    return ref_lists


def update_reference_list(
    client: ChronicleClient,
    name: str,
    description: str = "",
    entries: List[str] = [],
    syntax_type: ReferenceListSyntaxType = ReferenceListSyntaxType.STRING,
) -> Dict[str, Any]:
    """Updates a reference list.

    Args:
        client: ChronicleClient instance
        name: The name of the reference list.
        description: A user-provided description of the reference list.
        entries: A list of entries for the reference list.

    Returns:
        The updated reference list.

    Raises:
        APIError: If the API request fails.
        SecOpsError: If no description or entries are provided to be updated,
            or if a CIDR entry is invalid.
    """
    if not all(description, entries):
        raise SecOpsError(
            "One of description or entries must be provided to be updated."
        )
    if syntax_type == ReferenceListSyntaxType.CIDR:
        _validate_cidr_entries(entries)
    if (
        response := client.session.patch(
            f"{client.base_url}/{client.instance_id}/referenceLists/{name}",
            body={
                "description": description,
                "entries": [{"value": x} for x in entries],
            },
        )
    ).status_code != 200:
        raise APIError(f"Failed to update reference list: {response.text}")
    return response.json()
