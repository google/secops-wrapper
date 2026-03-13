"""Reference list management functionality for Chronicle."""

import sys
from enum import Enum
from typing import Any

from secops.chronicle.data_table import (
    REF_LIST_DATA_TABLE_ID_REGEX,
    validate_cidr_entries,
)
from secops.chronicle.models import APIVersion
from secops.chronicle.utils.request_utils import (
    chronicle_paginated_request,
    chronicle_request,
)
from secops.exceptions import SecOpsError

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


# Add a local reference to the imported function for backward compatibility
# with tests
validate_cidr_entries_local = validate_cidr_entries


class ReferenceListSyntaxType(StrEnum):
    """The syntax type indicating how list entries should be validated."""

    STRING = "REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING"
    """List contains plain text patterns."""

    REGEX = "REFERENCE_LIST_SYNTAX_TYPE_REGEX"
    """List contains only Regular Expression patterns."""

    CIDR = "REFERENCE_LIST_SYNTAX_TYPE_CIDR"
    """List contains only CIDR patterns."""


class ReferenceListView(StrEnum):
    """
    ReferenceListView is a mechanism for viewing partial responses of
    the ReferenceList resource.
    """

    UNSPECIFIED = "REFERENCE_LIST_VIEW_UNSPECIFIED"
    """The default / unset value. The API will default to the BASIC view for 
    ListReferenceLists. The API will default to the FULL view for methods that 
    return a single ReferenceList resource."""

    BASIC = "REFERENCE_LIST_VIEW_BASIC"
    """Include metadata about the ReferenceList. This is the default view for 
    ListReferenceLists."""

    FULL = "REFERENCE_LIST_VIEW_FULL"
    """Include all details about the ReferenceList: metadata, content lines, 
    associated rule counts. This is the default view for GetReferenceList."""


def create_reference_list(
    client: "Any",
    name: str,
    description: str = "",
    entries: list[str] = None,
    syntax_type: ReferenceListSyntaxType = ReferenceListSyntaxType.STRING,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Create a new reference list.

    Args:
        client: ChronicleClient instance
        name: The name for the new reference list
        description: A user-provided description of the reference list
        entries: A list of entries for the reference list
        syntax_type: The syntax type of the reference list
        api_version: Preferred API version to use. Defaults to V1

    Returns:
        Dictionary containing the created reference list

    Raises:
        APIError: If the API request fails
        SecOpsError: If the reference list name is invalid or
            a CIDR entry is invalid
    """
    # Defaulting to empty entries
    if entries is None:
        entries = []

    if not REF_LIST_DATA_TABLE_ID_REGEX.match(name):
        raise SecOpsError(
            f"Invalid reference list name: {name}.\n"
            "Ensure the name starts with a letter, contains only letters, "
            "numbers, and underscores, and has length < 256 characters."
        )

    # Validate CIDR entries if using CIDR syntax type
    if syntax_type == ReferenceListSyntaxType.CIDR:
        validate_cidr_entries_local(entries)

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="referenceLists",
        api_version=api_version,
        params={"referenceListId": name},
        json={
            "description": description,
            "entries": [{"value": x} for x in entries],
            "syntaxType": syntax_type.value,
        },
        error_message=f"Failed to create reference list '{name}'",
    )


def get_reference_list(
    client: "Any",
    name: str,
    view: ReferenceListView = ReferenceListView.FULL,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Get a single reference list.

    Args:
        client: ChronicleClient instance
        name: The name of the reference list
        view: How much of the ReferenceList to view.
            Defaults to REFERENCE_LIST_VIEW_FULL.
        api_version: Preferred API version to use. Defaults to V1

    Returns:
        Dictionary containing the reference list

    Raises:
        APIError: If the API request fails
    """
    params = {}
    if view != ReferenceListView.UNSPECIFIED:
        params["view"] = view.value

    return chronicle_request(
        client,
        method="GET",
        endpoint_path=f"referenceLists/{name}",
        api_version=api_version,
        params=params if params else None,
        error_message=f"Failed to get reference list '{name}'",
    )


def list_reference_lists(
    client: "Any",
    view: ReferenceListView = ReferenceListView.BASIC,
    api_version: APIVersion | None = APIVersion.V1,
    as_list: bool = True,
) -> dict[str, Any] | list[Any]:
    """List reference lists.

    Args:
        client: ChronicleClient instance
        view: How much of each ReferenceList to view. Defaults to
            REFERENCE_LIST_VIEW_BASIC.
        api_version: Preferred API version to use. Defaults to V1
        as_list: If True, return only the list of reference lists.
            If False, return dict with metadata and pagination tokens.
            Defaults to True for backward compatibility.

    Returns:
        If as_list is True: List of reference lists, ordered in ascending
            alphabetical order by name.
        If as_list is False: Dict with referenceLists list and
            pagination metadata.

    Raises:
        APIError: If the API request fails
    """
    extra_params = {}
    if view != ReferenceListView.UNSPECIFIED:
        extra_params["view"] = view.value

    return chronicle_paginated_request(
        client,
        path="referenceLists",
        items_key="referenceLists",
        api_version=api_version,
        extra_params=extra_params if extra_params else None,
        as_list=as_list,
    )


def update_reference_list(
    client: "Any",
    name: str,
    description: str | None = None,
    entries: list[str] | None = None,
    api_version: APIVersion | None = APIVersion.V1,
) -> dict[str, Any]:
    """Update a reference list.

    Args:
        client: ChronicleClient instance
        name: The name of the reference list
        description: A user-provided description of the reference list
        entries: A list of entries for the reference list
        api_version: Preferred API version to use. Defaults to V1

    Returns:
        Dictionary containing the updated reference list

    Raises:
        APIError: If the API request fails
        SecOpsError: If no description or entries are provided to be updated
    """
    if description is None and entries is None:
        raise SecOpsError(
            "Either description or entries (or both) must be "
            "provided for update."
        )

    # Get the reference list to check its syntax type for CIDR validation
    if entries is not None:
        ref_list = get_reference_list(client, name)
        syntax_type = ref_list.get("syntaxType", "")

        # Validate CIDR entries if the reference list has CIDR syntax type
        if syntax_type == ReferenceListSyntaxType.CIDR.value:
            validate_cidr_entries(entries)

    # Prepare request body and update mask
    payload = {}
    update_paths = []

    if description is not None:
        payload["description"] = description
        update_paths.append("description")

    if entries is not None:
        payload["entries"] = [{"value": x} for x in entries]
        update_paths.append("entries")

    params = {"updateMask": ",".join(update_paths)}

    return chronicle_request(
        client,
        method="PATCH",
        endpoint_path=f"referenceLists/{name}",
        api_version=api_version,
        params=params,
        json=payload,
        error_message=f"Failed to update reference list '{name}'",
    )


# Note: Reference List deletion is currently not supported by the API
