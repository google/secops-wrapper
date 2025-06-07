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
"""Data table functionality for Chronicle."""
import sys
from enum import StrEnum
from itertools import islice
from typing import Any, Dict, List, Optional
from secops.chronicle.client import ChronicleClient
from secops.exceptions import APIError, SecOpsError
from secops.utils import REF_LIST_DATA_TABLE_ID_REGEX, _validate_cidr_entries


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
    client: ChronicleClient,
    name: str,
    description: str,
    header: Dict[str, DataTableColumnType],
    rows: Optional[List[List[str]]] = None,
    scopes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new data table.

    Args:
        client: ChronicleClient instance
        name: The name for the new data table.
        description: A user-provided description of the data table.
        header: A dictionary mapping column names to column types.
        rows (optional): A list of rows for the data table.
        scopes (optional): A list of scopes for the data table.

    Returns:
        Dictionary containing the created data table.

    Raises:
        APIError: If the API request fails.
        SecOpsError: If the data table name is invalid.
    """
    if not REF_LIST_DATA_TABLE_ID_REGEX.match(name):
        raise SecOpsError(
            f"Invalid data table name: {name}.\n{REF_LIST_DATA_TABLE_ID_REGEX.__doc__.replace('Ensures', 'Ensure', 1)}"
        )
    for i, column_type in enumerate(header.values()):
        if column_type == DataTableColumnType.CIDR:
            _validate_cidr_entries([x[i] for x in rows])
    if (
        response := client.session.post(
            f"{client.base_url}/{client.instance_id}/dataTables",
            params={"dataTableId": name},
            body=(
                {
                    "description": description,
                    "columnInfo": [
                        {"columnIndex": i, "originalColumn": k, "columnType": v}
                        for i, (k, v) in enumerate(header.items())
                    ],
                }
                | {"scopes": {"dataAccessScopes": scopes}}
                if scopes
                else {}
            ),
        )
    ).status_code != 200:
        raise APIError(f"Failed to create data table: {response.text}")

    if rows:
        create_data_table_rows(client, name, rows)

    return response.json()


def create_data_table_rows(
    client: ChronicleClient, name: str, rows: List[List[str]]
) -> List[Dict[str, Any]]:
    """Create data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table.
        rows: A list of rows for the data table.

    Returns:
        List of responses containing the created data table rows.
    """
    responses = []
    # Automatically handle chunking/size constraints
    row_iter = iter(rows)
    while chunk := list(islice(row_iter, 1000)):
        while sum(map(lambda r: sys.getsizeof("".join(r)), chunk)) > 4000000:
            row_iter = iter([chunk.pop()] + list(row_iter))
        responses.append(_create_data_table_rows(client, name, chunk))
    return responses


def _create_data_table_rows(
    client: ChronicleClient, name: str, rows: List[List[str]]
) -> Dict[str, Any]:
    """Create data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table.
        rows: Data table rows to create. A maximum of 1000 rows can be created
              in a single request. Total size of the rows should be less than 4MB.

    Returns:
        Dictionary containing the created data table rows.

    Raises:
        APIError: If the API request fails
    """
    if (
        response := client.session.post(
            f"{client.base_url}/{client.instance_id}/dataTables/{name}/dataTableRows:bulkCreate",
            body={"requests": [{"data_table_row": {"values": x}} for x in rows]},
        )
    ).status_code != 200:
        raise APIError(f"Failed to create data table rows: {response.text}")
    return response.json()


def delete_data_table(
    client: ChronicleClient,
    name: str,
    force: bool = False,
) -> Dict[str, Any]:
    """Delete data table

    Args:
        client: ChronicleClient instance
        name: The name of the data table to delete.
        force: If set to true, any rows under this data table will also be deleted.
               (Otherwise, the request will only work if the data table has no rows).

    Returns:
        Dictionary containing the deleted data table.

    Raises:
        APIError: If the API request fails
    """
    if (
        response := client.session.delete(
            f"{client.base_url}/{client.instance_id}/dataTables/{name}",
            params={"force": force},
        )
    ).status_code != 200:
        raise APIError(f"Failed to delete data table: {response.text}")
    return response.json()


def delete_data_table_rows(
    client: ChronicleClient,
    name: str,
    row_ids: List[str],
) -> Dict[str, Any]:
    """Delete data table rows

    Args:
        client: ChronicleClient instance
        name: The name of the data table to delete rows from.
        row_ids: The IDs of the rows to delete.

    Returns:
        Dictionary containing the deleted data table rows.

    Raises:
        APIError: If the API request fails
    """
    return [_delete_data_table_row(client, name, x) for x in row_ids]


def _delete_data_table_row(
    client: ChronicleClient,
    name: str,
    row_id: str,
) -> Dict[str, Any]:
    """Delete data table row

    Args:
        client: ChronicleClient instance
        name: The name of the data table to delete rows from.
        row_id: The ID of the row to delete.

    Returns:
        Dictionary containing the deleted data table row.

    Raises:
        APIError: If the API request fails
    """
    if (
        response := client.session.delete(
            f"{client.base_url}/{client.instance_id}/dataTables/{name}/dataTableRows/{row_id}"
        )
    ).status_code != 200:
        raise APIError(f"Failed to delete data table row: {response.text}")
    return response.json()


def get_data_table(
    client: ChronicleClient,
    name: str,
) -> Dict[str, Any]:
    """Get data table.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to get.

    Returns:
        Dictionary containing the data table.

    Raises:
        APIError: If the API request fails
    """
    if (
        response := client.session.get(
            f"{client.base_url}/{client.instance_id}/dataTables/{name}"
        )
    ).status_code != 200:
        raise APIError(f"Failed to get data table: {response.text}")
    return response.json()


def list_data_tables(
    client: ChronicleClient,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List data tables.

    Args:
        client: ChronicleClient instance
        order_by: Configures ordering of DataTables in the response. Note: Our
                  implementation currently supports order by "create_time asc" only

    Returns:
        Dictionary containing the data tables.

    Raises:
        APIError: If the API request fails
    """
    data_tables = []
    params = {"pageSize": 1000, "orderBy": order_by}
    while True:
        if (
            response := client.session.get(
                f"{client.base_url}/{client.instance_id}/dataTables",
                params=params,
            )
        ).status_code != 200:
            raise APIError(f"Failed to list data tables: {response.text}")
        data_tables += response.json().get("dataTables", [])
        if "nextPageToken" in response.json():
            params["pageToken"] = response.json()["nextPageToken"]
        else:
            break

    return data_tables


def list_data_table_rows(
    client: ChronicleClient,
    name: str,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List data table rows.

    Args:
        client: ChronicleClient instance
        name: The name of the data table to list rows from.
        order_by: Configures ordering of DataTableRows in the response. Note: Our
                  implementation currently supports order by "create_time asc" only

    Returns:
        List of data table rows.

    Raises:
        APIError: If the API request fails
    """
    rows = []
    params = {"pageSize": 1000, "orderBy": order_by}
    while True:
        if (
            response := client.session.get(
                f"{client.base_url}/{client.instance_id}/dataTables/{name}/dataTableRows",
                params={"pageSize": 1000, "orderBy": order_by},
            )
        ).status_code != 200:
            raise APIError(f"Failed to list data table rows: {response.text}")
        rows += response.json().get("dataTableRows", [])
        if "nextPageToken" in response.json():
            params["pageToken"] = response.json()["nextPageToken"]
        else:
            break
    return rows
