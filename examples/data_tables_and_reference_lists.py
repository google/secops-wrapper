"""Example script demonstrating data tables and reference lists in Chronicle."""
import json
import time
from datetime import datetime, timezone, timedelta

from secops import SecOpsClient
from secops.chronicle.data_table import DataTableColumnType
from secops.chronicle.reference_list import ReferenceListSyntaxType, ReferenceListView
from secops.exceptions import APIError, SecOpsError

# Replace these with your actual values
PROJECT_ID = "your-project-id"
CUSTOMER_ID = "your-customer-id"
REGION = "us"  # or "eu", etc.

# Optional: Path to service account key file
# SERVICE_ACCOUNT_PATH = "path/to/service-account.json"


def main():
    """Run the example code."""
    # Initialize the client
    client = SecOpsClient()  # or SecOpsClient(service_account_path=SERVICE_ACCOUNT_PATH)
    chronicle = client.chronicle(
        project_id=PROJECT_ID,
        customer_id=CUSTOMER_ID,
        region=REGION
    )
    
    # Use timestamp for unique names to avoid conflicts
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    
    # ---- Data Table Examples ----
    print("\n=== Data Table Examples ===\n")
    
    # Example 1: Create a data table with string columns
    dt_name = f"example_dt_{timestamp}"
    print(f"Creating data table: {dt_name}")
    
    try:
        # Define the table structure
        dt = chronicle.create_data_table(
            name=dt_name,
            description="Example data table with string columns",
            header={
                "hostname": DataTableColumnType.STRING,
                "ip_address": DataTableColumnType.STRING,
                "description": DataTableColumnType.STRING
            },
            # Initial rows can be provided at creation time
            rows=[
                ["host1.example.com", "192.168.1.10", "Primary server"],
                ["host2.example.com", "192.168.1.11", "Backup server"]
            ]
        )
        print(f"Created data table: {dt['name']}")
        
        # Get the data table details
        dt_details = chronicle.get_data_table(dt_name)
        print(f"Data table has {len(dt_details.get('columnInfo', []))} columns")
        
        # List the rows
        rows = chronicle.list_data_table_rows(dt_name)
        print(f"Data table has {len(rows)} rows")
        
        # Add more rows
        print("Adding more rows...")
        chronicle.create_data_table_rows(
            dt_name,
            [
                ["host3.example.com", "192.168.1.12", "Development server"],
                ["host4.example.com", "192.168.1.13", "Test server"]
            ]
        )
        
        # List the updated rows
        updated_rows = chronicle.list_data_table_rows(dt_name)
        print(f"Data table now has {len(updated_rows)} rows")
        
        # Delete a row (if any rows exist)
        if updated_rows:
            row_to_delete = updated_rows[0]["name"].split("/")[-1]  # Extract the row ID
            print(f"Deleting row: {row_to_delete}")
            chronicle.delete_data_table_rows(dt_name, [row_to_delete])
            
            # Verify deletion
            remaining_rows = chronicle.list_data_table_rows(dt_name)
            print(f"Data table now has {len(remaining_rows)} rows after deletion")
        
    except (APIError, SecOpsError) as e:
        print(f"Error in data table example: {e}")
    finally:
        # Clean up - delete the data table
        try:
            print(f"Cleaning up - deleting data table: {dt_name}")
            chronicle.delete_data_table(dt_name, force=True)
            print("Data table deleted")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")
    
    # Example 2: Create a data table with CIDR column
    dt_cidr_name = f"example_dt_cidr_{timestamp}"
    print(f"\nCreating CIDR data table: {dt_cidr_name}")
    
    try:
        # Define the table with a CIDR column
        dt_cidr = chronicle.create_data_table(
            name=dt_cidr_name,
            description="Example data table with CIDR column",
            header={
                "network": DataTableColumnType.CIDR,
                "location": DataTableColumnType.STRING
            },
            rows=[
                ["10.0.0.0/8", "Corporate HQ"],
                ["192.168.0.0/16", "Branch offices"]
            ]
        )
        print(f"Created CIDR data table: {dt_cidr['name']}")
        
        # Try to add an invalid CIDR (will raise an error)
        try:
            print("Attempting to add invalid CIDR...")
            chronicle.create_data_table_rows(
                dt_cidr_name,
                [["not-a-cidr", "Invalid Network"]]
            )
            print("This should not be printed - expected an error")
        except SecOpsError as e:
            print(f"Expected error for invalid CIDR: {e}")
        
    except (APIError, SecOpsError) as e:
        print(f"Error in CIDR data table example: {e}")
    finally:
        # Clean up
        try:
            print(f"Cleaning up - deleting CIDR data table: {dt_cidr_name}")
            chronicle.delete_data_table(dt_cidr_name, force=True)
            print("CIDR data table deleted")
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")
    
    # ---- Reference List Examples ----
    print("\n=== Reference List Examples ===\n")
    
    # Example 1: Create a reference list with string entries
    rl_name = f"example_rl_{timestamp}"
    print(f"Creating reference list: {rl_name}")
    
    try:
        # Create a reference list with string entries
        rl = chronicle.create_reference_list(
            name=rl_name,
            description="Example reference list with string entries",
            entries=["malicious.example.com", "suspicious.example.org", "evil.example.net"],
            syntax_type=ReferenceListSyntaxType.STRING
        )
        print(f"Created reference list: {rl['name']}")
        
        # Get the reference list with FULL view (includes entries)
        rl_full = chronicle.get_reference_list(rl_name, view=ReferenceListView.FULL)
        print(f"Reference list has {len(rl_full.get('entries', []))} entries")
        
        # Get the reference list with BASIC view (typically doesn't include entries)
        rl_basic = chronicle.get_reference_list(rl_name, view=ReferenceListView.BASIC)
        entries_in_basic = len(rl_basic.get('entries', []))
        print(f"Reference list in BASIC view has {entries_in_basic} entries")
        
        # Update the reference list
        print("Updating reference list...")
        updated_rl = chronicle.update_reference_list(
            name=rl_name,
            description="Updated example reference list",
            entries=["updated.example.com", "new.example.org"]
        )
        print(f"Updated reference list has {len(updated_rl.get('entries', []))} entries")
        
        # List all reference lists
        all_rls = chronicle.list_reference_lists()
        print(f"Total reference lists: {len(all_rls)}")
        
    except (APIError, SecOpsError) as e:
        print(f"Error in reference list example: {e}")
    finally:
        # Note: Reference list deletion is not supported by the API
        print(f"Note: Reference list {rl_name} will remain since deletion is not supported by the API")
    
    # Example 2: Create a reference list with CIDR entries
    rl_cidr_name = f"example_rl_cidr_{timestamp}"
    print(f"\nCreating CIDR reference list: {rl_cidr_name}")
    
    try:
        # Create a reference list with CIDR entries
        rl_cidr = chronicle.create_reference_list(
            name=rl_cidr_name,
            description="Example reference list with CIDR entries",
            entries=["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
            syntax_type=ReferenceListSyntaxType.CIDR
        )
        print(f"Created CIDR reference list: {rl_cidr['name']}")
        
        # Try to update with an invalid CIDR (will raise an error)
        try:
            print("Attempting to update with invalid CIDR...")
            chronicle.update_reference_list(
                name=rl_cidr_name,
                entries=["not-a-cidr", "192.168.1.0/24"]
            )
            print("This should not be printed - expected an error")
        except SecOpsError as e:
            print(f"Expected error for invalid CIDR: {e}")
        
    except (APIError, SecOpsError) as e:
        print(f"Error in CIDR reference list example: {e}")
    finally:
        # Note: Reference list deletion is not supported by the API
        print(f"Note: CIDR reference list {rl_cidr_name} will remain since deletion is not supported by the API")


if __name__ == "__main__":
    main() 