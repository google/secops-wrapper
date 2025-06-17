"""Data table functionality for Chronicle."""

import sys
import re
import ipaddress
from itertools import islice
from typing import Any, Dict, List, Optional, Union

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


from secops.exceptions import APIError, SecOpsError

# Regular expression for validating reference list and data table IDs
REF_LIST_DATA_TABLE_ID_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{0,254}$")


def validate_cidr_entries(entries: List[str]) -> None:
    """Check if IP addresses are valid CIDR notation.

    Args:
        entries: A list of CIDR entries

    Raises:
        SecOpsError: If a CIDR entry is invalid
    """
    if not entries:
        return

    for entry in entries:
        try:
            ipaddress.ip_network(entry, strict=False)
        except ValueError:
            raise SecOpsError(f"Invalid CIDR entry: {entry}")


class DataTableColumnType(StrEnum):
    """DataTableColumnType denotes the type of the column to be referenced in the rule."""

    UNSPECIFIED = "DATA_TABLE_COLUMN_TYPE_UNSPECIFIED"
    """The default Data Table Column Type."""

    STRING = "STRING"
    """Denotes the type of the column as STRING."""

    REGEX = "REGEX"
    """Denotes the type of the column as REGEX."""

    CIDR = "CIDR"
    """Denotes the type of the column as CIDR."""


def create_data_table(
    client: "Any",
    name: str,
    description: str,
    header: Dict[str, DataTableColumnType],
    rows: Optional[List[List[str]]] = None,
    scopes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new data table.

    Args:
        client: ChronicleClient instance
        name: The name for the new data table
        description: A user-provided description of the data table
        header: A dictionary mapping column names to column types
        rows: Optional list of rows for the data table
        scopes: Optional list of scopes for the data table

    Returns:
        Dictionary containing the created data table

    Raises:
        APIError: If the API request fails
        SecOpsError: If the data table name is invalid or CIDR validation fails
    """
    if not REF_LIST_DATA_TABLE_ID_REGEX.match(name):
        raise SecOpsError(
            f"Invalid data table name: {name}.\n"
            f"Ensure the name starts with a letter, contains only letters, numbers, and underscores, "
            f"and has length < 256 characters."
        )

    # Validate CIDR entries before creating the table
    if rows:
        for i, column_type in enumerate(header.values()):
            if column_type == DataTableColumnType.CIDR:
                # Extract the i-th element from each row for CIDR validation
                cidr_column_values = [row[i] for row in rows if len(row) > i]
                validate_cidr_entries(cidr_column_values)

    # Prepare request body
    body_payload = {
        "description": description,
        "columnInfo": [
            {"columnIndex": i, "originalColumn": k, "columnType": v.value}
            for i, (k, v) in enumerate(header.items())
        ],
    }

    if scopes:
        body_payload["scopes"] = {"dataAccessScopes": scopes}

    # Create the data table
    response = client.session.post(
        f"{client.base_url}/{client.instance_id}/dataTables",
        params={"dataTableId": name},
        json=body_payload,
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to create data table '{name}': {response.status_code} {response.text}"
        )

    created_table_data = response.json()

    # Add rows if provided
    if rows:
        try:
            row_creation_responses = create_data_table_rows(client, name, rows)
            created_table_data["rowCreationResponses"] = row_creation_responses
        except Exception as e:
            # Report the error but don't fail the whole operation
            created_table_data["rowCreationError"] = str(e)

    return created_table_data


def create_data_table_rows(
    client: "Any", name: str, rows: List[List[str]]
) -> List[Dict[str, Any]]:
    """Create data table rows, chunking if necessary.

    Args:
        client: ChronicleClient instance
        name: The name of the data table
        rows: A list of rows for the data table

    Returns:
        List of responses containing the created data table rows

    Raises:
        APIError: If the API request fails
        SecOpsError: If a row is too large to process
    """
    responses = []
    row_iter = iter(rows)

    # Process rows in chunks of up to 1000 rows or 4MB
    while chunk := list(islice(row_iter, 1000)):
        current_chunk_size_bytes = sum(sys.getsizeof("".join(r)) for r in chunk)

        # If chunk is too large, split it
        while current_chunk_size_bytes > 4000000 and len(chunk) > 1:
            half_len = len(chunk) // 2
            if half_len == 0:  # Should not happen if len(chunk) > 1
                break

            temp_chunk_for_next_iter = chunk[half_len:]
            chunk = chunk[:half_len]
            row_iter = iter(temp_chunk_for_next_iter + list(row_iter))
            current_chunk_size_bytes = sum(sys.getsizeof("".join(r)) for r in chunk)

        if not chunk:  # If chunk became empty
            continue

        # If a single row is too large
        if current_chunk_size_bytes > 4000000 and len(chunk) == 1:
            raise SecOpsError(
                f"Single row is too large to process (>{current_chunk_size_bytes} bytes): {chunk[0][:100]}..."
            )

        responses.append(_create_data_table_rows(client, name, chunk))

    return responses


def _create_data_table_rows(
    client: "Any", name: str, rows: List[List[str]]
) -> Dict[str, Any]:
    """Create a batch of data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table
        rows: Data table rows to create. A maximum of 1000 rows can be created
              in a single request. Total size of the rows should be less than 4MB.

    Returns:
        Dictionary containing the created data table rows

    Raises:
        APIError: If the API request fails
    """
    response = client.session.post(
        f"{client.base_url}/{client.instance_id}/dataTables/{name}/dataTableRows:bulkCreate",
        json={"requests": [{"data_table_row": {"values": x}} for x in rows]},
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to create data table rows for '{name}': {response.status_code} {response.text}"
        )

    return response.json()


def delete_data_table(
    client: "Any",
    name: str,
    force: bool = False,
) -> Dict[str, Any]:
    """Delete a data table.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to delete
        force: If set to true, any rows under this data table will also be deleted.
               (Otherwise, the request will only work if the data table has no rows).

    Returns:
        Dictionary containing the deleted data table or empty dict

    Raises:
        APIError: If the API request fails
    """
    response = client.session.delete(
        f"{client.base_url}/{client.instance_id}/dataTables/{name}",
        params={"force": str(force).lower()},
    )

    # Successful delete returns 200 OK with body or 204 No Content
    if response.status_code == 200 or response.status_code == 204:
        if response.text:
            try:
                return response.json()
            except Exception:
                return {"status": "success", "statusCode": response.status_code}
        return {}

    raise APIError(
        f"Failed to delete data table '{name}': {response.status_code} {response.text}"
    )


def delete_data_table_rows(
    client: "Any",
    name: str,
    row_ids: List[str],
) -> List[Dict[str, Any]]:
    """Delete data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to delete rows from
        row_ids: The IDs of the rows to delete

    Returns:
        List of dictionaries containing the deleted data table rows

    Raises:
        APIError: If the API request fails
    """
    results = []
    for row_guid in row_ids:
        results.append(_delete_data_table_row(client, name, row_guid))
    return results


def _delete_data_table_row(
    client: "Any",
    table_id: str,
    row_guid: str,
) -> Dict[str, Any]:
    """Delete a single data table row.

    Args:
        client: ChronicleClient instance
        table_id: The ID of the data table to delete a row from
        row_guid: The ID of the row to delete

    Returns:
        Dictionary containing the deleted data table row or status information

    Raises:
        APIError: If the API request fails
    """
    response = client.session.delete(
        f"{client.base_url}/{client.instance_id}/dataTables/{table_id}/dataTableRows/{row_guid}"
    )

    if response.status_code == 200 or response.status_code == 204:
        if response.text:
            try:
                return response.json()
            except Exception:
                return {"status": "success", "statusCode": response.status_code}
        return {"status": "success", "statusCode": response.status_code}

    raise APIError(
        f"Failed to delete data table row '{row_guid}' from '{table_id}': {response.status_code} {response.text}"
    )


def get_data_table(
    client: "Any",
    name: str,
) -> Dict[str, Any]:
    """Get data table details.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to get

    Returns:
        Dictionary containing the data table

    Raises:
        APIError: If the API request fails
    """
    response = client.session.get(
        f"{client.base_url}/{client.instance_id}/dataTables/{name}"
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to get data table '{name}': {response.status_code} {response.text}"
        )

    return response.json()


def list_data_tables(
    client: "Any",
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List data tables.

    Args:
        client: ChronicleClient instance
        order_by: Configures ordering of DataTables in the response.
                  Note: The API only supports "createTime asc".

    Returns:
        List of data tables

    Raises:
        APIError: If the API request fails
    """
    all_data_tables = []
    params = {"pageSize": 1000}

    if order_by:
        params["orderBy"] = order_by

    while True:
        response = client.session.get(
            f"{client.base_url}/{client.instance_id}/dataTables",
            params=params,
        )

        if response.status_code != 200:
            raise APIError(
                f"Failed to list data tables: {response.status_code} {response.text}"
            )

        resp_json = response.json()
        all_data_tables.extend(resp_json.get("dataTables", []))

        page_token = resp_json.get("nextPageToken")
        if page_token:
            params["pageToken"] = page_token
        else:
            break

    return all_data_tables


def list_data_table_rows(
    client: "Any",
    name: str,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to list rows from
        order_by: Configures ordering of DataTableRows in the response.
                  Note: The API only supports "createTime asc".

    Returns:
        List of data table rows

    Raises:
        APIError: If the API request fails
    """
    all_rows = []
    params = {"pageSize": 1000}

    if order_by:
        params["orderBy"] = order_by

    while True:
        response = client.session.get(
            f"{client.base_url}/{client.instance_id}/dataTables/{name}/dataTableRows",
            params=params,
        )

        if response.status_code != 200:
            raise APIError(
                f"Failed to list data table rows for '{name}': {response.status_code} {response.text}"
            )

        resp_json = response.json()
        all_rows.extend(resp_json.get("dataTableRows", []))

        page_token = resp_json.get("nextPageToken")
        if page_token:
            params["pageToken"] = page_token
        else:
            break

    return all_rows
