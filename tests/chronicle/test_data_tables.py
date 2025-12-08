"""Unit tests for Chronicle API data table and reference list functionality."""

import pytest
from unittest.mock import (
    Mock,
    patch,
    call,
)  # Added call for checking multiple calls if needed

from secops.chronicle.models import APIVersion
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
def mock_chronicle_client():
    """Provides a ChronicleClient with a mock session for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer",
            project_id="test-project",
        )


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

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_create_data_table_with_entity_mapping(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful creation of a data table without rows."""
        mock_regex_check.match.return_value = True  # Assume name is valid
        mock_response = Mock()
        mock_response.status_code = 200
        expected_dt_name = "projects/test-project/locations/us/instances/test-customer/dataTables/test_dt_123"
        entity_mapping = "entity.domain.name" # Sample valid entity mapping
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "displayName": "test_dt_123",
            "description": "Test Description",
            "createTime": "2025-06-17T10:00:00Z",
            "columnInfo": [{"originalColumn": "col1", "mappedColumnPath": entity_mapping}],
            "dataTableUuid": "some-uuid",
        }
        mock_chronicle_client.session.post.return_value = mock_response

        dt_name = "test_dt_123"
        description = "Test Description"
        header = {"col1": entity_mapping}

        result = create_data_table(mock_chronicle_client, dt_name, description, header)

        assert result["name"] == expected_dt_name
        assert result["description"] == description
        mock_chronicle_client.session.post.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables",
            params={"dataTableId": dt_name},
            json={
                "description": description,
                "columnInfo": [
                    {"columnIndex": 0, "originalColumn": "col1", "mappedColumnPath": entity_mapping}
                ],
            },
        )

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_create_data_table_with_column_options(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful creation of a data table without rows, with additional column options."""
        mock_regex_check.match.return_value = True  # Assume name is valid
        mock_response = Mock()
        mock_response.status_code = 200
        expected_dt_name = "projects/test-project/locations/us/instances/test-customer/dataTables/test_dt_123"
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "displayName": "test_dt_123",
            "description": "Test Description",
            "createTime": "2025-06-17T10:00:00Z",
            "columnInfo": [
                {"originalColumn": "key", "columnType": "NUMBER", "keyColumn": True},
                {"originalColumn": "repetitive", "columnType": "STRING", "repeatedValues": True}
            ],
            "dataTableUuid": "some-uuid",
        }
        mock_chronicle_client.session.post.return_value = mock_response

        dt_name = "test_dt_123"
        description = "Test Description"
        header = {
            "key": DataTableColumnType.NUMBER,
            "repetitive": DataTableColumnType.STRING
        }
        column_options = {
            "key": {"keyColumn": True},
            "repetitive": {"repeatedValues": True}
        }

        result = create_data_table(mock_chronicle_client, dt_name, description, header,
            column_options=column_options)

        assert result["name"] == expected_dt_name
        assert result["description"] == description
        mock_chronicle_client.session.post.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables",
            params={"dataTableId": dt_name},
            json={
                "description": description,
                "columnInfo": [
                    {"columnIndex": 0, "originalColumn": "key", "columnType": "NUMBER", "keyColumn": True},
                    {"columnIndex": 1, "originalColumn": "repetitive", "columnType": "STRING", "repeatedValues": True}
                ],
            },
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
            f"{mock_chronicle_client.base_url(APIVersion.V1)}/{mock_chronicle_client.instance_id}/referenceLists",
            params={"referenceListId": rl_name},
            json={
                "description": description,
                "entries": [{"value": "entryA"}, {"value": "entryB"}],
                "syntaxType": syntax_type.value,
            },
        )

    @patch("secops.chronicle.reference_list.REF_LIST_DATA_TABLE_ID_REGEX")
    @patch("secops.chronicle.reference_list.validate_cidr_entries_local")
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
            f"{mock_chronicle_client.base_url(APIVersion.V1)}/{mock_chronicle_client.instance_id}/referenceLists/{rl_name}",
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
            f"{mock_chronicle_client.base_url(APIVersion.V1)}/{mock_chronicle_client.instance_id}/referenceLists",
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
            f"{mock_chronicle_client.base_url(APIVersion.V1)}/{mock_chronicle_client.instance_id}/referenceLists/{rl_name}",
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
            
    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_update_data_table_success_both_params(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful update of a data table with both description and row TTL."""
        mock_regex_check.match.return_value = True  # Assume name is valid
        mock_response = Mock()
        mock_response.status_code = 200
        
        dt_name = "test_dt_update"
        expected_dt_name = f"projects/test-project/locations/us/instances/test-customer/dataTables/{dt_name}"
        new_description = "Updated description"
        new_row_ttl = "48h"
        
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "description": new_description,
            "rowTimeToLive": new_row_ttl,
            "updateTime": "2025-08-25T10:00:00Z",
            "columnInfo": [{"originalColumn": "col1", "columnType": "STRING"}],
            "dataTableUuid": "test-uuid",
        }
        
        mock_chronicle_client.session.patch.return_value = mock_response

        result = update_data_table(
            mock_chronicle_client, 
            dt_name, 
            description=new_description, 
            row_time_to_live=new_row_ttl
        )

        assert result["name"] == expected_dt_name
        assert result["description"] == new_description
        assert result["rowTimeToLive"] == new_row_ttl
        
        mock_chronicle_client.session.patch.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}",
            params={},
            json={
                "description": new_description,
                "row_time_to_live": new_row_ttl,
            },
        )

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_update_data_table_description_only(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful update of a data table with description only."""
        mock_regex_check.match.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        
        dt_name = "test_dt_update"
        expected_dt_name = f"projects/test-project/locations/us/instances/test-customer/dataTables/{dt_name}"
        new_description = "Updated description only"
        
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "description": new_description,
            "updateTime": "2025-08-25T10:05:00Z",
            "dataTableUuid": "test-uuid",
        }
        
        mock_chronicle_client.session.patch.return_value = mock_response

        result = update_data_table(
            mock_chronicle_client, 
            dt_name, 
            description=new_description
        )

        assert result["name"] == expected_dt_name
        assert result["description"] == new_description
        assert "rowTimeToLive" not in result
        
        mock_chronicle_client.session.patch.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}",
            params={},
            json={"description": new_description},
        )

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_update_data_table_row_ttl_only(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test successful update of a data table with row TTL only."""
        mock_regex_check.match.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        
        dt_name = "test_dt_update"
        expected_dt_name = f"projects/test-project/locations/us/instances/test-customer/dataTables/{dt_name}"
        new_row_ttl = "72h"
        
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "rowTimeToLive": new_row_ttl,
            "updateTime": "2025-08-25T10:10:00Z",
            "dataTableUuid": "test-uuid",
        }
        
        mock_chronicle_client.session.patch.return_value = mock_response

        result = update_data_table(
            mock_chronicle_client, 
            dt_name, 
            row_time_to_live=new_row_ttl
        )

        assert result["name"] == expected_dt_name
        assert result["rowTimeToLive"] == new_row_ttl
        assert "description" not in result
        
        mock_chronicle_client.session.patch.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}",
            params={},
            json={"row_time_to_live": new_row_ttl},
        )

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_update_data_table_with_update_mask(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test update of a data table with explicit update mask."""
        mock_regex_check.match.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        
        dt_name = "test_dt_update"
        expected_dt_name = f"projects/test-project/locations/us/instances/test-customer/dataTables/{dt_name}"
        new_description = "Updated with mask"
        new_row_ttl = "96h"
        update_mask = ["description"]
        
        mock_response.json.return_value = {
            "name": expected_dt_name,
            "description": new_description,
            "updateTime": "2025-08-25T10:15:00Z",
            "dataTableUuid": "test-uuid",
        }
        
        mock_chronicle_client.session.patch.return_value = mock_response

        result = update_data_table(
            mock_chronicle_client, 
            dt_name, 
            description=new_description,
            row_time_to_live=new_row_ttl,
            update_mask=update_mask
        )

        assert result["name"] == expected_dt_name
        assert result["description"] == new_description
        
        # Verify that even though row_time_to_live was provided, it wasn't included in the API call
        # due to the update_mask
        mock_chronicle_client.session.patch.assert_called_once_with(
            f"{mock_chronicle_client.base_url}/{mock_chronicle_client.instance_id}/dataTables/{dt_name}",
            params={"updateMask": "description"},
            json={
                "description": new_description,
                "row_time_to_live": new_row_ttl,
            },
        )

    @patch("secops.chronicle.data_table.REF_LIST_DATA_TABLE_ID_REGEX")
    def test_update_data_table_invalid_name(
        self, mock_regex_check: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test update_data_table with an invalid name."""
        mock_regex_check.match.return_value = False  # Simulate invalid name
        with pytest.raises(
            SecOpsError, match="Invalid data table name: invalid_name!."
        ):
            update_data_table(
                mock_chronicle_client,
                "invalid_name!",
                description="New description",
            )
            
        # Verify the API was never called
        mock_chronicle_client.session.patch.assert_not_called()

    def test_update_data_table_api_error(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test update_data_table when API returns an error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid row_time_to_live format"
        
        mock_chronicle_client.session.patch.return_value = mock_response
        
        with pytest.raises(
            APIError, match="Failed to update data table 'test_table': 400 Invalid row_time_to_live format"
        ):
            update_data_table(
                mock_chronicle_client, 
                "test_table", 
                row_time_to_live="invalid"
            )

    @patch('secops.chronicle.data_table._estimate_row_json_size')
    @patch('secops.chronicle.data_table.create_data_table_rows')
    def test_replace_data_table_rows_size_based_batching(
        self, mock_create_rows: Mock, mock_estimate_size: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test that replace_data_table_rows handles size-based batching."""
        # Mock response for API calls
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [{"name": "row_replaced"}]
        }
        mock_chronicle_client.session.post.return_value = mock_response
        
        # Mock create_data_table_rows function for remaining rows
        mock_create_rows.return_value = [{"dataTableRows": [{"name": "row_created"}]}]
        
        # Create test data: first batch will have some rows close to 4MB limit
        # to test size-based batching
        dt_name = "dt_for_replace_batching"
        rows_data = [[f"small_value{i}"] for i in range(950)]  # Under 1000 rows total
        
        # Mock size estimation to force size-based batching
        # First 5 rows are large (close to 1MB each), rest are small
        def estimate_size_side_effect(row):
            if row[0].startswith("small_value") and int(row[0][11:]) < 5:
                return 900000  # Almost 1MB each for first 5 rows
            return 10000  # Small size for other rows
            
        mock_estimate_size.side_effect = estimate_size_side_effect
        
        # Call the function under test
        responses = replace_data_table_rows(mock_chronicle_client, dt_name, rows_data)
        
        # Verify the correct behavior:
        # 1. Single bulkReplace call for the rows that fit in 4MB
        # 2. create_data_table_rows function call for remaining rows
        
        # First call should be bulkReplace with only the rows that fit in 4MB
        mock_chronicle_client.session.post.assert_called_once()
        post_call = mock_chronicle_client.session.post.call_args
        assert "bulkReplace" in post_call[0][0]
        
        # The create_data_table_rows function should be called for remaining rows
        mock_create_rows.assert_called_once()
        create_call_args = mock_create_rows.call_args
        # Verify the function was called with the right parameters
        assert create_call_args[0][0] == mock_chronicle_client  # client
        assert create_call_args[0][1] == dt_name  # name
        
        # Verify we got responses from both operations
        assert len(responses) == 2

    @patch('secops.chronicle.data_table._estimate_row_json_size', return_value=1000)  # Small enough for all rows
    @patch('secops.chronicle.data_table.create_data_table_rows')
    def test_replace_data_table_rows_chunking(
        self, mock_create_rows: Mock, mock_estimate_size: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test that replace_data_table_rows chunks large inputs over 1000 rows."""
        # Mock responses for API calls
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [{"name": "row_replaced_chunk"}]
        }
        mock_chronicle_client.session.post.return_value = mock_response
        
        # Mock create_data_table_rows function for remaining rows
        mock_create_rows.return_value = [{"dataTableRows": [{"name": "row_created_chunk"}]}]
        
        # Create test data with more than 1000 rows
        dt_name = "dt_for_replace_chunking"
        rows_data = [[f"new_value{i}"] for i in range(1500)]  # 1500 rows
        
        # Call the function under test
        responses = replace_data_table_rows(mock_chronicle_client, dt_name, rows_data)
        
        # Verify first call was bulkReplace with first 1000 rows
        assert mock_chronicle_client.session.post.call_count == 1
        post_call = mock_chronicle_client.session.post.call_args
        assert "bulkReplace" in post_call[0][0]
        
        # Verify the remaining rows were sent using create_data_table_rows function
        mock_create_rows.assert_called_once()
        create_call = mock_create_rows.call_args
        
        # Verify function was called with correct parameters
        assert create_call[0][0] == mock_chronicle_client  # client parameter
        assert create_call[0][1] == dt_name  # table name parameter
        
        # We need to include rows 1000-1499 (500 rows total) in the remaining batch
        remaining_rows = create_call[0][2]  # Get the rows passed to create_data_table_rows
        assert len(remaining_rows) == 500  # 500 remaining rows
        
        # Verify we got response correctly
        assert len(responses) == 2

    def test_replace_data_table_rows_few_rows(self, mock_chronicle_client: Mock) -> None:
        """Test direct call to replace_data_table_rows with a small number of rows."""
        # Mock response for API call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [
                {"name": "replaced_row1", "values": ["new1", "new2"]},
                {"name": "replaced_row2", "values": ["new3", "new4"]},
            ]
        }
        mock_chronicle_client.session.post.return_value = mock_response
            
        dt_name = "test_dt_replace"
        rows_to_replace = [["new1", "new2"], ["new3", "new4"]]  # Small set of rows
            
        # Patch row size estimation to return small values and create_data_table_rows
        # since we don't use it in this test case
        with patch('secops.chronicle.data_table._estimate_row_json_size', return_value=1000), \
             patch('secops.chronicle.data_table.create_data_table_rows') as mock_create_rows:
            # Mock doesn't get called in this test but needs to be patched
            # to prevent any unwanted side effects
            mock_create_rows.return_value = []
            
            # Call the function under test
            result = replace_data_table_rows(mock_chronicle_client, dt_name, rows_to_replace)
            
            # Verify API was called correctly
            mock_chronicle_client.session.post.assert_called_once()
            call_args = mock_chronicle_client.session.post.call_args
            assert "bulkReplace" in call_args[0][0]  # URL has bulkReplace
            
            # Verify we have all rows in a single request
            requests = call_args[1]["json"]["requests"]
            assert len(requests) == 2  # Both rows in a single request
            
            # Verify response was processed correctly
            assert len(result) == 1
            assert result[0] == mock_response.json.return_value
            
            # Verify we didn't need to use create_data_table_rows for additional rows
            mock_create_rows.assert_not_called()

    def test_replace_data_table_rows_api_error(self, mock_chronicle_client: Mock) -> None:
        """Test API error handling in replace_data_table_rows."""
        # Mock API error response
        error_response = Mock()
        error_response.status_code = 400
        error_response.text = "Invalid row format"
        mock_chronicle_client.session.post.return_value = error_response
        
        dt_name = "invalid_table"
        rows_to_replace = [["bad_data"]]  # Small test data
        
        # Patch row size estimation to avoid size issues and patch create_data_table_rows
        # as it's not expected to be called in this error case
        with patch('secops.chronicle.data_table._estimate_row_json_size', return_value=1000), \
             patch('secops.chronicle.data_table.create_data_table_rows'):
            with pytest.raises(APIError, match="Failed to replace data table rows for 'invalid_table': 400 Invalid row format"):
                replace_data_table_rows(mock_chronicle_client, dt_name, rows_to_replace)

    def test_replace_data_table_rows_single_oversized_row(self, mock_chronicle_client: Mock) -> None:
        """Test handling of a single oversized row in replace_data_table_rows."""
        dt_name = "dt_with_big_row"
        oversized_row = [["*" * 1000000]]  # Very large row
            
        # Mock _estimate_row_json_size to return a value larger than 4MB for our oversized row
        # Also patch create_data_table_rows as it won't be called in this error case
        with patch('secops.chronicle.data_table._estimate_row_json_size', return_value=5000000), \
             patch('secops.chronicle.data_table.create_data_table_rows'):
            with pytest.raises(SecOpsError, match="Single row is too large to process"):
                replace_data_table_rows(mock_chronicle_client, dt_name, oversized_row)


    def test_update_data_table_rows_success(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test successful update of data table rows."""
        # Mock response for API call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [
                {
                    "name": "projects/test/locations/us/instances/"
                    "test-customer/dataTables/dt1/dataTableRows/row1",
                    "values": ["updated1", "updated2"],
                },
                {
                    "name": "projects/test/locations/us/instances/"
                    "test-customer/dataTables/dt1/dataTableRows/row2",
                    "values": ["updated3", "updated4"],
                },
            ]
        }
        mock_chronicle_client.session.post.return_value = mock_response

        dt_name = "dt1"
        row_updates = [
            {
                "name": "projects/test/locations/us/instances/"
                "test-customer/dataTables/dt1/dataTableRows/row1",
                "values": ["updated1", "updated2"],
            },
            {
                "name": "projects/test/locations/us/instances/"
                "test-customer/dataTables/dt1/dataTableRows/row2",
                "values": ["updated3", "updated4"],
            },
        ]

        # Patch row size estimation to return small values
        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=1000,
        ):
            result = update_data_table_rows(
                mock_chronicle_client, dt_name, row_updates
            )

            # Verify API was called correctly
            mock_chronicle_client.session.post.assert_called_once()
            call_args = mock_chronicle_client.session.post.call_args
            assert "bulkUpdate" in call_args[0][0]

            # Verify payload structure
            requests = call_args[1]["json"]["requests"]
            assert len(requests) == 2
            assert requests[0]["dataTableRow"]["name"] == row_updates[0]["name"]
            assert requests[0]["dataTableRow"]["values"] == row_updates[0][
                "values"
            ]

            # Verify response
            assert len(result) == 1
            assert result[0] == mock_response.json.return_value

    def test_update_data_table_rows_with_update_mask(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test update with update_mask parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [
                {
                    "name": "projects/test/locations/us/instances/"
                    "test-customer/dataTables/dt1/dataTableRows/row1",
                    "values": ["val1", "val2"],
                }
            ]
        }
        mock_chronicle_client.session.post.return_value = mock_response

        dt_name = "dt1"
        row_updates = [
            {
                "name": "projects/test/locations/us/instances/"
                "test-customer/dataTables/dt1/dataTableRows/row1",
                "values": ["val1", "val2"],
                "update_mask": "values",
            }
        ]

        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=1000,
        ):
            result = update_data_table_rows(
                mock_chronicle_client, dt_name, row_updates
            )

            # Verify update mask is included in request
            call_args = mock_chronicle_client.session.post.call_args
            requests = call_args[1]["json"]["requests"]
            assert "updateMask" in requests[0]
            assert requests[0]["updateMask"] == "values"

            # Verify response
            assert len(result) == 1

    @patch("secops.chronicle.data_table._estimate_row_json_size")
    def test_update_data_table_rows_chunking_1000_rows(
        self, mock_estimate_size: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test chunking when updating more than 1000 rows."""
        # Mock response for API calls
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [{"name": "row_updated"}]
        }
        mock_chronicle_client.session.post.return_value = mock_response

        # Mock small row sizes
        mock_estimate_size.return_value = 1000

        dt_name = "dt_chunking"
        # Create 1500 row updates to test chunking
        row_updates = [
            {
                "name": f"projects/test/locations/us/instances/"
                f"test-customer/dataTables/dt_chunking/"
                f"dataTableRows/row{i}",
                "values": [f"val{i}"],
            }
            for i in range(1500)
        ]

        result = update_data_table_rows(
            mock_chronicle_client, dt_name, row_updates
        )

        # Verify API was called twice (1000 + 500)
        assert mock_chronicle_client.session.post.call_count == 2

        # Verify first call has 1000 rows
        first_call = mock_chronicle_client.session.post.call_args_list[0]
        first_requests = first_call[1]["json"]["requests"]
        assert len(first_requests) == 1000

        # Verify second call has 500 rows
        second_call = mock_chronicle_client.session.post.call_args_list[1]
        second_requests = second_call[1]["json"]["requests"]
        assert len(second_requests) == 500

        # Verify we got 2 responses
        assert len(result) == 2

    @patch("secops.chronicle.data_table._estimate_row_json_size")
    def test_update_data_table_rows_size_based_chunking(
        self, mock_estimate_size: Mock, mock_chronicle_client: Mock
    ) -> None:
        """Test size-based chunking when rows approach 2MB limit."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataTableRows": [{"name": "row_updated"}]
        }
        mock_chronicle_client.session.post.return_value = mock_response

        dt_name = "dt_size_chunking"
        # Create test data with varying sizes
        row_updates = [
            {
                "name": f"projects/test/locations/us/instances/"
                f"test-customer/dataTables/dt_size_chunking/"
                f"dataTableRows/row{i}",
                "values": [f"val{i}"],
            }
            for i in range(100)
        ]

        # Mock size estimation: first 10 rows are large
        def estimate_size_side_effect(row):
            if row and len(row) > 0 and row[0].startswith("val"):
                idx = int(row[0][3:])
                if idx < 10:
                    return 250000  # 250KB each (10 rows = 2.5MB)
                return 10000  # Small size for other rows

        mock_estimate_size.side_effect = estimate_size_side_effect

        result = update_data_table_rows(
            mock_chronicle_client, dt_name, row_updates
        )

        # Should have multiple chunks due to size constraints
        assert mock_chronicle_client.session.post.call_count >= 2
        assert len(result) >= 2

    def test_update_data_table_rows_empty_list(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test updating with empty row_updates list."""
        dt_name = "dt_empty"
        row_updates = []

        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=1000,
        ):
            result = update_data_table_rows(
                mock_chronicle_client, dt_name, row_updates
            )

            # Should not make any API calls
            mock_chronicle_client.session.post.assert_not_called()
            # Should return empty list
            assert result == []

    def test_update_data_table_rows_api_error(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test API error handling in update_data_table_rows."""
        # Mock API error response
        error_response = Mock()
        error_response.status_code = 400
        error_response.text = "Invalid row data"
        mock_chronicle_client.session.post.return_value = error_response

        dt_name = "dt_error"
        row_updates = [
            {
                "name": "projects/test/locations/us/instances/"
                "test-customer/dataTables/dt_error/dataTableRows/row1",
                "values": ["bad_data"],
            }
        ]

        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=1000,
        ):
            with pytest.raises(
                APIError,
                match="Failed to update data table rows for 'dt_error': "
                "400 Invalid row data",
            ):
                update_data_table_rows(
                    mock_chronicle_client, dt_name, row_updates
                )

    def test_update_data_table_rows_missing_name_field(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test validation error when 'name' field is missing."""
        dt_name = "dt_missing_name"
        row_updates = [
            {
                # Missing 'name' field
                "values": ["val1", "val2"],
            }
        ]

        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=1000,
        ):
            with pytest.raises(
                SecOpsError, match="Each row update must contain 'name'"
            ):
                update_data_table_rows(
                    mock_chronicle_client, dt_name, row_updates
                )

    def test_update_data_table_rows_missing_values_field(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test validation error when 'values' field is missing."""
        dt_name = "dt_missing_values"
        row_updates = [
            {
                "name": "projects/test/locations/us/instances/"
                "test-customer/dataTables/dt_missing_values/"
                "dataTableRows/row1",
                # Missing 'values' field
            }
        ]

        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=1000,
        ):
            with pytest.raises(
                SecOpsError, match="Each row update must contain 'values'"
            ):
                update_data_table_rows(
                    mock_chronicle_client, dt_name, row_updates
                )

    def test_update_data_table_rows_single_oversized_row(
        self, mock_chronicle_client: Mock
    ) -> None:
        """Test handling of a single oversized row in update operation."""
        dt_name = "dt_oversized"
        row_updates = [
            {
                "name": "projects/test/locations/us/instances/"
                "test-customer/dataTables/dt_oversized/"
                "dataTableRows/row1",
                "values": ["*" * 1000000],  # Very large value
            }
        ]

        # Mock size estimation to return value > 2MB
        with patch(
            "secops.chronicle.data_table._estimate_row_json_size",
            return_value=3000000,
        ):
            with pytest.raises(
                SecOpsError, match="Single row is too large to process"
            ):
                update_data_table_rows(
                    mock_chronicle_client, dt_name, row_updates
                )

    # TODO: Add more unit tests for:
    # - APIError scenarios for each function (e.g., 404 Not Found, 500 Server Error)
    # - Pagination in list_data_tables and list_data_table_rows, list_reference_lists
    # - create_data_table with CIDR validation failure (validate_cidr_entries_local raises SecOpsError)
    # - create_reference_list with CIDR validation failure
    # - validate_cidr_entries_local itself
    # - REF_LIST_DATA_TABLE_ID_REGEX utility if used directly by other parts (though it's tested via create methods)
    # - Edge cases for row chunking in create_data_table_rows (e.g. single massive row)
    # - delete_data_table_row specific tests (if _delete_data_table_row is complex enough)
