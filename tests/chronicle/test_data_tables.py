"""Unit tests for Chronicle API data table and reference list functionality."""

from datetime import datetime, timezone
import pytest
from unittest.mock import (
    Mock,
    patch,
    call,
)  # Added call for checking multiple calls if needed

from secops.chronicle.client import ChronicleClient  # This will be the actual client

# We'll need to import the enums and functions once they are in their final place
# For now, let's assume they might be in a module like secops.chronicle.data_table
# from secops.chronicle.data_table import (
#     DataTableColumnType, create_data_table, get_data_table, list_data_tables,
#     delete_data_table, create_data_table_rows, list_data_table_rows, delete_data_table_rows,
#     ReferenceListSyntaxType, ReferenceListView, create_reference_list, get_reference_list,
#     list_reference_lists, update_reference_list
# )
# Placeholder for where these will live, adjust import path as SDK develops
from secops.chronicle.data_table import *  # Temp, will be specific
from secops.chronicle.reference_list import *  # Temp, will be specific

from secops.exceptions import APIError, SecOpsError


@pytest.fixture
def mock_chronicle_client() -> Mock:
    """Provides a mock ChronicleClient with a mock session."""
    client = Mock(spec=ChronicleClient)
    client.session = Mock()
    client.base_url = "https://test-chronicle.googleapis.com/v1alpha"
    client.instance_id = "projects/test-project/locations/us/instances/test-customer"
    return client


# ---- Test Data Tables ----


class TestDataTables:
    """Unit tests for data table functions."""

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_create_data_table_success(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful creation of a data table without rows."""
        mock_regex_check.match.return_value = True  # Assume name is valid
        mock_response = Mock()
        mock_response.status_code = 200
        expected_dt_name = "projects/test-project/locations/us/instances/test-customer/dataTables/test_dt_123"
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "displayName": "test_dt_123",
            "description": "Test Description",
            "createTime": "2025-06-17T10:00:00Z",
            "columnInfo": [{"originalColumn": "col1", "columnType": "STRING"}],
            "dataTableUuid": "some-uuid",
        }
        mock_chronicle_client.session.post.return_value = mock_response

        dt_name = "test_dt_123"
        description = "Test Description"
        header = {"col1": DataTableColumnType.STRING}

        result = create_data_table(mock_chronicle_client, dt_name, description, header)

        assert result["name"] == expected_dt_name
        assert result["description"] == description
        mock_chronicle_client.session.post.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables",
            params={"dataTableId": dt_name},
            json={
                "description": description,
                "columnInfo": [
                    {"columnIndex": 0, "originalColumn": "col1", "columnType": "STRING"}
                ],
            },
        )

    @patch("secops.chronicle.data_table.create_data_table_rows")
    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_create_data_table_with_rows_success(
        self,
        mock_regex_check: Mock,
        mock_create_rows: Mock,
        mock_chronicle_client: Mock,
    ) -> None:
        """Test successful creation of a data table with rows."""
        mock_regex_check.match.return_value = True
        mock_dt_response = Mock()
        mock_dt_response.status_code = 200
        expected_dt_name = "projects/test-project/locations/us/instances/test-customer/dataTables/test_dt_with_rows"
        mock_dt_response.json.return_value = {
            "name": expected_dt_name,
            "displayName": "test_dt_with_rows",
            "description": "Test With Rows",
            # ... other fields
        }
        mock_chronicle_client.session.post.return_value = mock_dt_response

        mock_create_rows.return_value = [
            {"dataTableRows": [{"name": "row1_full_name"}]}
        ]  # Simulate response from create_data_table_rows

        dt_name = "test_dt_with_rows"
        description = "Test With Rows"
        header = {"host": DataTableColumnType.STRING}
        rows_data = [["server1"], ["server2"]]

        result = create_data_table(
            mock_chronicle_client, dt_name, description, header, rows=rows_data
        )

        assert result["name"] == expected_dt_name
        mock_create_rows.assert_called_once_with(
            mock_chronicle_client, dt_name, rows_data
        )
        assert "rowCreationResponses" in result

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_create_data_table_invalid_name(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test create_data_table with an invalid name."""
        mock_regex_check.match.return_value = False  # Simulate invalid name
        with pytest.raises(
            SecOpsError, match="Invalid data table name: invalid_name!."
        ):
            create_data_table(
                mock_chronicle_client,
                "invalid_name!",
                "desc",
                {"col": DataTableColumnType.STRING},
            )

    def test_get_data_table_success(self, mock_chronicle_client: Mock) -> None:
        """Test successful retrieval of a data table."""
        mock_response = Mock()
        mock_response.status_code = 200
        dt_name = "existing_dt"
        expected_response = {
            "name": f"projects/test-project/locations/us/instances/test-customer/dataTables/{dt_name}",
            "displayName": dt_name,
            # ... other fields based on logs
        }
        mock_response.json.return_value = expected_response
        mock_chronicle_client.session.get.return_value = mock_response

        result = get_data_table(mock_chronicle_client, dt_name)
        assert result == expected_response
        mock_chronicle_client.session.get.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}"
        )

    def test_list_data_tables_success(self, mock_chronicle_client: Mock) -> None:
        """Test successful listing of data tables without pagination."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTables": [
                {"name": "dt1", "displayName": "DT One"},
                {"name": "dt2", "displayName": "DT Two"},
            ]
            # No nextPageToken means single page
        }
        mock_chronicle_client.session.get.return_value = mock_response

        result = list_data_tables(mock_chronicle_client, order_by="createTime asc")

        assert len(result) == 2
        assert result[0]["displayName"] == "DT One"
        mock_chronicle_client.session.get.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables",
            params={"pageSize": 1000, "orderBy": "createTime asc"},
        )

    def test_list_data_tables_api_error_invalid_orderby(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test list_data_tables when API returns error for invalid orderBy."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = (
            "invalid order by field: ordering is only supported by create time asc"
        )
        # No .json() method will be called if status is not 200 in the actual code
        mock_chronicle_client.session.get.return_value = mock_response

        with pytest.raises(
            APIError, match="Failed to list data tables: 400 invalid order by field"
        ):
            list_data_tables(mock_chronicle_client, order_by="createTime desc")

    def test_delete_data_table_success(self, mock_chronicle_client: Mock) -> None:
        """Test successful deletion of a data table."""
        mock_response = Mock()
        mock_response.status_code = 200  # API might return 200 with empty body or LRO
        mock_response.json.return_value = {}  # Based on your logs
        mock_chronicle_client.session.delete.return_value = mock_response

        dt_name = "dt_to_delete"
        result = delete_data_table(mock_chronicle_client, dt_name, force=True)

        assert result == {}
        mock_chronicle_client.session.delete.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}",
            params={"force": "true"},
        )

    @patch("secops.chronicle.data_table._create_data_table_rows")
    def test_create_data_table_rows_chunking(
        self, mock_internal_create_rows: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test that create_data_table_rows chunks large inputs."""
        # This test is more complex as it involves mocking sys.getsizeof and islice behavior
        # For simplicity, we'll test if _create_data_table_rows is called multiple times for oversized list

        # Assume each row is small, but we provide more than 1000 rows
        rows_data = [[f"value{i}"] for i in range(1500)]  # 1500 rows
        mock_internal_create_rows.return_value = {
            "dataTableRows": [{"name": "row_chunk_resp"}]
        }

        dt_name = "dt_for_chunking"
        responses = create_data_table_rows(mock_chronicle_client, dt_name, rows_data)

        # Expect two calls: one for 1000 rows, one for 500 rows
        assert mock_internal_create_rows.call_count == 2
        # First call with the first 1000 rows
        call_args_1 = mock_internal_create_rows.call_args_list[0]
        assert call_args_1[0][1] == dt_name  # name
        assert len(call_args_1[0][2]) == 1000  # rows in first chunk
        # Second call with the remaining 500 rows
        call_args_2 = mock_internal_create_rows.call_args_list[1]
        assert call_args_2[0][1] == dt_name
        assert len(call_args_2[0][2]) == 500

        assert len(responses) == 2

    def test_list_data_table_rows_success(self, mock_chronicle_client: Mock) -> None:
        """Test successful listing of data table rows."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [
                {"name": "row1_full", "values": ["a", "b"]},
                {"name": "row2_full", "values": ["c", "d"]},
            ]
        }
        mock_chronicle_client.session.get.return_value = mock_response
        dt_name = "my_table_with_rows"

        result = list_data_table_rows(
            mock_chronicle_client, dt_name, order_by="createTime asc"
        )

        assert len(result) == 2
        assert result[0]["values"] == ["a", "b"]
        mock_chronicle_client.session.get.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}/dataTableRows",
            params={"pageSize": 1000, "orderBy": "createTime asc"},
        )

    @patch("secops.chronicle.data_table._delete_data_table_row")
    def test_delete_data_table_rows_multiple(
        self, mock_internal_delete: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test deleting multiple data table rows."""
        dt_name = "test_table_for_row_delete"
        row_guids_to_delete = ["guid1", "guid2", "guid3"]

        # Mock the internal delete function to return simple success
        mock_internal_delete.side_effect = lambda client, table_id, row_guid: {
            "status": "success",
            "deleted_row_guid": row_guid,
        }

        results = delete_data_table_rows(
            mock_chronicle_client, dt_name, row_guids_to_delete
        )

        assert mock_internal_delete.call_count == 3
        expected_calls = [
            call(mock_chronicle_client, dt_name, "guid1"),
            call(mock_chronicle_client, dt_name, "guid2"),
            call(mock_chronicle_client, dt_name, "guid3"),
        ]
        mock_internal_delete.assert_has_calls(expected_calls, any_order=False)

        assert len(results) == 3
        assert results[0]["deleted_row_guid"] == "guid1"


# ---- Test Reference Lists ----


class TestReferenceLists:
    """Unit tests for reference list functions."""

    @patch("secops.chronicle.reference_list.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_create_reference_list_success(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful creation of a reference list."""
        mock_regex_check.match.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        rl_name = "test_rl_123"
        description = "My Test RL"
        entries = ["entryA", "entryB"]
        syntax_type = ReferenceListSyntaxType.STRING

        # Based on your logs for create_reference_list
        expected_response_json = {
            "name": f"projects/test-project/locations/us/instances/test-customer/referenceLists/{rl_name}",
            "displayName": rl_name,
            "revisionCreateTime": "2025-06-17T12:00:00Z",  # Mocked time
            "description": description,
            "entries": [{"value": "entryA"}, {"value": "entryB"}],
            "syntaxType": "REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING",
        }
        mock_response.json.return_value = expected_response_json
        mock_chronicle_client.session.post.return_value = mock_response

        result = create_reference_list(
            mock_chronicle_client, rl_name, description, entries, syntax_type
        )

        assert result["displayName"] == rl_name
        assert result["description"] == description
        assert len(result["entries"]) == 2
        mock_chronicle_client.session.post.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/referenceLists",
            params={"referenceListId": rl_name},
            json={
                "description": description,
                "entries": [{"value": "entryA"}, {"value": "entryB"}],
                "syntaxType": syntax_type.value,
            },
        )

    @patch("secops.chronicle.reference_list.REF_LIST_DATA_TABLE_ID_REGEX")
    @patch("secops.chronicle.reference_list._validate_cidr_entries")
    def test_create_reference_list_cidr_success(
        self,
        mock_validate_cidr: Mock,
        mock_regex_check: Mock,
        mock_chronicle_client: Mock,
    ) -> None:
        """Test successful creation of a CIDR reference list."""
        mock_regex_check.match.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        rl_name = "cidr_rl_test"
        entries = ["192.168.1.0/24"]

        mock_response.json.return_value = {
            "name": f"projects/test-project/locations/us/instances/test-customer/referenceLists/{rl_name}",
            "displayName": rl_name,
            "syntaxType": "REFERENCE_LIST_SYNTAX_TYPE_CIDR",
            "entries": [{"value": "192.168.1.0/24"}],
        }
        mock_chronicle_client.session.post.return_value = mock_response

        create_reference_list(
            mock_chronicle_client,
            name=rl_name,
            description="CIDR RL",
            entries=entries,
            syntax_type=ReferenceListSyntaxType.CIDR,
        )
        mock_validate_cidr.assert_called_once_with(entries)

    def test_get_reference_list_full_view_success(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test successful retrieval of a reference list (FULL view)."""
        mock_response = Mock()
        mock_response.status_code = 200
        rl_name = "my_full_rl"
        # Based on your logs for get_reference_list (FULL view)
        expected_response_json = {
            "name": f"projects/test-project/locations/us/instances/test-customer/referenceLists/{rl_name}",
            "displayName": rl_name,
            "revisionCreateTime": "2025-06-17T12:05:00Z",
            "description": "Full RL details",
            "entries": [{"value": "full_entry1"}],
            "syntaxType": "REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING",
            "scopeInfo": {"referenceListScope": {}},
        }
        mock_response.json.return_value = expected_response_json
        mock_chronicle_client.session.get.return_value = mock_response

        result = get_reference_list(
            mock_chronicle_client, rl_name, view=ReferenceListView.FULL
        )

        assert result["description"] == "Full RL details"
        assert len(result["entries"]) == 1
        mock_chronicle_client.session.get.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/referenceLists/{rl_name}",
            params={"view": ReferenceListView.FULL.value},
        )

    def test_list_reference_lists_basic_view_success(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test successful listing of reference lists (BASIC view, default)."""
        mock_response = Mock()
        mock_response.status_code = 200
        # Based on your logs for list_reference_lists
        mock_response.json.return_value = {
            "referenceLists": [
                {
                    "name": "projects/test-project/locations/us/instances/test-customer/referenceLists/rl_basic1",
                    "displayName": "rl_basic1",
                    "syntaxType": "REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING",
                    # Basic view has fewer fields
                }
            ]
        }
        mock_chronicle_client.session.get.return_value = mock_response

        results = list_reference_lists(mock_chronicle_client)  # Defaults to BASIC

        assert len(results) == 1
        assert results[0]["displayName"] == "rl_basic1"
        assert "entries" not in results[0]  # Entries are not in BASIC view
        mock_chronicle_client.session.get.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/referenceLists",
            params={"pageSize": 1000, "view": ReferenceListView.BASIC.value},
        )

    @patch("secops.chronicle.reference_list.get_reference_list")
    def test_update_reference_list_success(
        self, mock_get_reference_list: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful update of a reference list's description and entries."""
        mock_response = Mock()
        mock_response.status_code = 200
        rl_name = "rl_to_update"
        new_description = "Updated RL Description"
        new_entries = ["updated_entryX", "new_entryY"]

        # Mock the get_reference_list call inside update_reference_list
        mock_get_reference_list.return_value = {
            "name": f"projects/test-project/locations/us/instances/test-customer/referenceLists/{rl_name}",
            "syntaxType": ReferenceListSyntaxType.STRING.value,
        }

        # Based on your logs for update_reference_list
        expected_response_json = {
            "name": f"projects/test-project/locations/us/instances/test-customer/referenceLists/{rl_name}",
            "displayName": rl_name,
            "revisionCreateTime": "2025-06-17T12:10:00Z",
            "description": new_description,
            "entries": [{"value": "updated_entryX"}, {"value": "new_entryY"}],
            "syntaxType": "REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING",
            # other fields like scopeInfo might be present
        }
        mock_response.json.return_value = expected_response_json
        mock_chronicle_client.session.patch.return_value = mock_response

        result = update_reference_list(
            mock_chronicle_client,
            rl_name,
            description=new_description,
            entries=new_entries,
        )

        assert result["description"] == new_description
        assert len(result["entries"]) == 2
        assert result["entries"][0]["value"] == "updated_entryX"

        mock_chronicle_client.session.patch.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/referenceLists/{rl_name}",
            json={
                "description": new_description,
                "entries": [{"value": "updated_entryX"}, {"value": "new_entryY"}],
            },
            params={"updateMask": "description,entries"},
        )

    def test_update_reference_list_no_changes_error(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test update_reference_list raises error if no fields are provided for update."""
        with pytest.raises(
            SecOpsError,
            match=r"Either description or entries \(or both\) must be provided for update.",
        ):
            update_reference_list(mock_chronicle_client, "some_rl_name")

    # TODO: Add more unit tests for:
    # - APIError scenarios for each function (e.g., 404 Not Found, 500 Server Error)
    # - Pagination in list_data_tables and list_data_table_rows, list_reference_lists
    # - create_data_table with CIDR validation failure (_validate_cidr_entries raises SecOpsError)
    # - create_reference_list with CIDR validation failure
    # - _validate_cidr_entries itself
    # - REF_LIST_DATA_TABLE_ID_REGEX utility if used directly by other parts (though it's tested via create methods)
    # - Edge cases for row chunking in create_data_table_rows (e.g. single massive row)
    # - delete_data_table_row specific tests (if _delete_data_table_row is complex enough)
