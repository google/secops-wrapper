"""Data table functionality for Chronicle."""

import ipaddress
import re
import sys
from itertools import islice
from typing import Any

from secops.exceptions import APIError, SecOpsError

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


# Regular expression for validating reference list and data table IDs
REF_LIST_DATA_TABLE_ID_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{0,254}$")


def validate_cidr_entries(entries: list[str]) -> None:
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
        except ValueError as e:
            raise SecOpsError(f"Invalid CIDR entry: {entry}") from e


class DataTableColumnType(StrEnum):
    """
    DataTableColumnType denotes the type of the column to be referenced in
    the rule.
    """

    STRING = "STRING"
    """Denotes the type of the column as STRING."""

    REGEX = "REGEX"
    """Denotes the type of the column as REGEX."""

    CIDR = "CIDR"
    """Denotes the type of the column as CIDR."""

    NUMBER = "NUMBER"
    """Denotes the type of the column as NUMBER."""


def create_data_table(
    client: "Any",
    name: str,
    description: str,
    header: dict[str, DataTableColumnType | str],
    column_options: dict[str, dict[str, Any]] | None = None,
    rows: list[list[str]] | None = None,
    scopes: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new data table.

    Args:
        client: ChronicleClient instance
        name: The name for the new data table
        description: A user-provided description of the data table
        header: A dictionary mapping column names to column types or
                entity proto field mappings
        column_options: Optional dictionary of column options
                        syntax: {column_name:{option:value}}
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
            "Ensure the name starts with a letter, contains only letters, "
            "numbers, and underscores, and has length < 256 characters."
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
        "columnInfo": [],
    }
    # Create columnInfo section of request body
    for i, (column_name, v) in enumerate(header.items()):
        column = {"columnIndex": i, "originalColumn": column_name}

        # columnType and mappedColumnPath are mutually exclusive
        if isinstance(v, DataTableColumnType):
            column["columnType"] = v.value
        else:  # Assume it is an entity mapping (passed as string).
            column["mappedColumnPath"] = v

        # Merge additional options into column dictionary
        if column_options:
            if column_name in column_options:
                column = column | column_options[column_name]

        # Finally, add column to list of columns
        body_payload["columnInfo"].append(column)

    if scopes:
        body_payload["scopeInfo"] = {"dataAccessScopes": scopes}

    # Create the data table
    response = client.session.post(
        f"{client.base_url}/{client.instance_id}/dataTables",
        params={"dataTableId": name},
        json=body_payload,
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to create data table '{name}': {response.status_code} "
            f"{response.text}"
        )

    created_table_data = response.json()

    # Add rows if provided
    if rows:
        try:
            row_creation_responses = create_data_table_rows(client, name, rows)
            created_table_data["rowCreationResponses"] = row_creation_responses
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Report the error but don't fail the whole operation
            created_table_data["rowCreationError"] = str(e)

    return created_table_data


def create_data_table_rows(
    client: "Any", name: str, rows: list[list[str]]
) -> list[dict[str, Any]]:
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
            current_chunk_size_bytes = sum(
                sys.getsizeof("".join(r)) for r in chunk
            )

        if not chunk:  # If chunk became empty
            continue

        # If a single row is too large
        if current_chunk_size_bytes > 4000000 and len(chunk) == 1:
            raise SecOpsError(
                "Single row is too large to process "
                f"(>{current_chunk_size_bytes} bytes): {chunk[0][:100]}..."
            )

        responses.append(_create_data_table_rows(client, name, chunk))

    return responses


def _create_data_table_rows(
    client: "Any", name: str, rows: list[list[str]]
) -> dict[str, Any]:
    """Create a batch of data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table
        rows: Data table rows to create. A maximum of 1000 rows can be created
              in a single request. Total size of the rows should be
              less than 4MB.

    Returns:
        Dictionary containing the created data table rows

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/dataTables/{name}"
        "/dataTableRows:bulkCreate"
    )
    response = client.session.post(
        url,
        json={"requests": [{"data_table_row": {"values": x}} for x in rows]},
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to create data table rows for '{name}': "
            f"{response.status_code} {response.text}"
        )

    return response.json()


def delete_data_table(
    client: "Any",
    name: str,
    force: bool = False,
) -> dict[str, Any]:
    """Delete a data table.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to delete
        force: If set to true, any rows under this data table will also be
            deleted. (Otherwise, the request will only work if
            the data table has no rows).

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
            except Exception:  # pylint: disable=broad-exception-caught
                return {"status": "success", "statusCode": response.status_code}
        return {}

    raise APIError(
        f"Failed to delete data table '{name}': {response.status_code} "
        f"{response.text}"
    )


def delete_data_table_rows(
    client: "Any",
    name: str,
    row_ids: list[str],
) -> list[dict[str, Any]]:
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
) -> dict[str, Any]:
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
        f"{client.base_url}/{client.instance_id}/dataTables/{table_id}"
        f"/dataTableRows/{row_guid}"
    )

    if response.status_code == 200 or response.status_code == 204:
        if response.text:
            try:
                return response.json()
            except Exception:  # pylint: disable=broad-exception-caught
                return {"status": "success", "statusCode": response.status_code}
        return {"status": "success", "statusCode": response.status_code}

    raise APIError(
        f"Failed to delete data table row '{row_guid}' from '{table_id}': "
        f"{response.status_code} {response.text}"
    )


def get_data_table(
    client: "Any",
    name: str,
) -> dict[str, Any]:
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
            f"Failed to get data table '{name}': {response.status_code} "
            f"{response.text}"
        )

    return response.json()


def list_data_tables(
    client: "Any",
    order_by: str | None = None,
) -> list[dict[str, Any]]:
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
                f"Failed to list data tables: {response.status_code} "
                f"{response.text}"
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
    order_by: str | None = None,
) -> list[dict[str, Any]]:
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
            f"{client.base_url}/{client.instance_id}/dataTables"
            f"/{name}/dataTableRows",
            params=params,
        )

        if response.status_code != 200:
            raise APIError(
                f"Failed to list data table rows for '{name}': "
                f"{response.status_code} {response.text}"
            )

        resp_json = response.json()
        all_rows.extend(resp_json.get("dataTableRows", []))

        page_token = resp_json.get("nextPageToken")
        if page_token:
            params["pageToken"] = page_token
        else:
            break

    return all_rows


def update_data_table(
    client: "Any",
    name: str,
    description: str | None = None,
    row_time_to_live: str | None = None,
    update_mask: list[str] | None = None,
) -> dict[str, Any]:
    """Update a existing data table.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to update
        description: Description for the data table
        row_time_to_live: TTL for the data table rows
        update_mask: List of fields to update. When no field mask is supplied,
                     all non-empty fields will be updated.
                     Supported fields include:
                     'description', 'row_time_to_live'.

    Returns:
        Dictionary containing the updated data table

    Raises:
        APIError: If the API request fails
        SecOpsError: If validation fails
    """
    if not REF_LIST_DATA_TABLE_ID_REGEX.match(name):
        raise SecOpsError(
            f"Invalid data table name: {name}.\n"
            "Ensure the name starts with a letter, contains only letters, "
            "numbers, and underscores, and has length < 256 characters."
        )

    # Prepare request body
    body_payload = {}
    if description is not None:
        body_payload["description"] = description
    if row_time_to_live is not None:
        body_payload["row_time_to_live"] = row_time_to_live

    # Prepare query parameters
    params = {}
    if update_mask:
        params["updateMask"] = ",".join(update_mask)

    # Make the PATCH request
    response = client.session.patch(
        f"{client.base_url}/{client.instance_id}/dataTables/{name}",
        params=params,
        json=body_payload,
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to update data table '{name}': {response.status_code} "
            f"{response.text}"
        )

    return response.json()


def _estimate_row_json_size(row: list[str]) -> int:
    """Estimate the size of a row when formatted as JSON.

    Args:
        row: A list of string values representing a row

    Returns:
        Estimated size in bytes of the row when formatted as JSON
    """
    # Basic size for JSON structure: {"data_table_row":{"values":[...]}}
    base_size = 30

    # Add size for each string value in the row
    # Account for quotes, commas, and possible escaping
    for value in row:
        # String length + quotes + possible escaping (estimate ~10% overhead)
        base_size += len(value) + 3 + int(len(value) * 0.1)

    return base_size


def replace_data_table_rows(
    client: "Any", name: str, rows: list[list[str]]
) -> list[dict[str, Any]]:
    """Replace all rows in a data table with new rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table
        rows: A list of new rows to replace all existing rows in the table

    Returns:
        List of responses from the API calls

    Raises:
        APIError: If any API request fails
        SecOpsError: If a row is too large to process
    """

    url = (
        f"{client.base_url}/{client.instance_id}/dataTables/{name}"
        "/dataTableRows:bulkReplace"
    )

    # Check for empty input
    if not rows:
        return []

    row_sizes = []

    # Validate each row isn't too large before processing
    for i, row in enumerate(rows):
        # Validate row structure to prevent IndexError
        if not isinstance(row, list):
            raise SecOpsError(
                f"Invalid row format at index {i}: "
                f"expected list but got {type(row)}"
            )

        row_size = _estimate_row_json_size(row)
        row_sizes.append(row_size)  # Store calculated size

        if row_size > 4000000:
            row_preview = repr(row[:50])
            raise SecOpsError(
                f"Single row is too large to process (>{row_size} bytes): "
                f"{row_preview}..."
            )

    all_responses = []

    # Use bulkReplace for the first batch (up to 1000 rows)
    # This replaces all existing rows in the table
    first_batch_size = min(1000, len(rows))
    first_batch = rows[:first_batch_size]
    first_batch_sizes = row_sizes[:first_batch_size]

    print(f"Replacing all existing rows with first {first_batch_size} rows")

    first_api_batch = []
    first_api_batch_size = 0
    first_batch_max_size = 4000000  # 4MB in bytes

    # First, determine how many rows we can include in the first API call
    # (max 4MB)
    for i, row in enumerate(first_batch):
        # If adding this row would exceed 4MB,
        # stop adding rows to first API call
        if first_api_batch_size + first_batch_sizes[i] > first_batch_max_size:
            break

        first_api_batch.append(row)
        first_api_batch_size += first_batch_sizes[i]

    if first_api_batch:
        replace_requests = [
            {"data_table_row": {"values": r}} for r in first_api_batch
        ]

        response = client.session.post(
            url,
            json={"requests": replace_requests},
        )

        if response.status_code != 200:
            raise APIError(
                f"Failed to replace data table rows for '{name}': "
                f"{response.status_code} {response.text}"
            )

        all_responses.append(response.json())

    # Handle any remaining rows from the first 1000 using bulkCreate
    remaining_first_batch = first_batch[len(first_api_batch) :]

    # Add remaining rows using bulkCreate (if any)
    if remaining_first_batch or len(rows) > 1000:
        print(f"Adding remaining {len(rows) - len(first_api_batch)} rows")

        remaining_rows = remaining_first_batch + rows[1000:]
        create_responses = create_data_table_rows(client, name, remaining_rows)
        all_responses.extend(create_responses)

    return all_responses


def update_data_table_rows(
    client: "Any",
    name: str,
    row_updates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Update data table rows in bulk, chunking if necessary.

    Args:
        client: ChronicleClient instance
        name: The name of the data table
        row_updates: List of row update specifications. Each dict must contain:
            - 'name': str - Full resource name of the row to update
            - 'values': List[str] - The new values for the row
            - 'update_mask': str (optional) - Comma-separated field mask

    Returns:
        List of responses containing the updated data table rows

    Raises:
        APIError: If the API request fails
        SecOpsError: If a row is too large to process or validation fails
    """
    responses = []
    row_iter = iter(row_updates)

    # Process rows in chunks of up to 1000 rows or 2MB
    while chunk := list(islice(row_iter, 1000)):
        # Estimate chunk size
        current_chunk_size_bytes = sum(
            _estimate_row_json_size(row.get("values", [])) for row in chunk
        )

        # If chunk is too large, split it
        while current_chunk_size_bytes > 2000000 and len(chunk) > 1:
            half_len = len(chunk) // 2
            if half_len == 0:  # Should not happen if len(chunk) > 1
                break

            temp_chunk_for_next_iter = chunk[half_len:]
            chunk = chunk[:half_len]
            row_iter = iter(temp_chunk_for_next_iter + list(row_iter))
            current_chunk_size_bytes = sum(
                _estimate_row_json_size(row.get("values", [])) for row in chunk
            )

        if not chunk:  # If chunk became empty
            continue

        # If a single row is too large
        if current_chunk_size_bytes > 2000000 and len(chunk) == 1:
            row_preview = repr(chunk[0].get("values", [])[:50])
            raise SecOpsError(
                "Single row is too large to process "
                f"(>{current_chunk_size_bytes} bytes): {row_preview}..."
            )

        responses.append(_update_data_table_rows(client, name, chunk))

    return responses


def _update_data_table_rows(
    client: "Any",
    name: str,
    row_updates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Update a batch of data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table
        row_updates: List of row update specifications. Each dict must contain:
            - 'name': str - Full resource name of the row to update
            - 'values': List[str] - The new values for the row
            - 'update_mask': str (optional) - Comma-separated field mask

    Returns:
        Dictionary containing the updated data table rows

    Raises:
        APIError: If the API request fails
        SecOpsError: If validation fails
    """
    url = (
        f"{client.base_url}/{client.instance_id}/dataTables/{name}"
        "/dataTableRows:bulkUpdate"
    )

    # Build request payload
    requests = []
    for row_update in row_updates:
        if "name" not in row_update:
            raise SecOpsError("Each row update must contain 'name'")
        if "values" not in row_update:
            raise SecOpsError("Each row update must contain 'values'")

        request_item = {
            "dataTableRow": {
                "name": row_update["name"],
                "values": row_update["values"],
            }
        }

        # Add update mask if provided
        if row_update.get("update_mask"):
            request_item["updateMask"] = row_update["update_mask"]

        requests.append(request_item)

    response = client.session.post(
        url,
        json={"requests": requests},
    )

    if response.status_code != 200:
        raise APIError(
            f"Failed to update data table rows for '{name}': "
            f"{response.status_code} {response.text}"
        )

    return response.json()
