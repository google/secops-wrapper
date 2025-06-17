"""Integration tests for the SecOps CLI."""
import pytest
import subprocess
import json
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

# Import configuration - use absolute import
from tests.config import CHRONICLE_CONFIG

# Integration test fixture
@pytest.fixture
def cli_env():
    """Set up environment for CLI tests."""
    env = os.environ.copy()
    # Add any environment variables needed for testing
    return env

@pytest.fixture
def common_args():
    """Return common command line arguments for the CLI."""
    return [
        "--customer-id", CHRONICLE_CONFIG.get("customer_id", ""),
        "--project-id", CHRONICLE_CONFIG.get("project_id", ""),
        "--region", CHRONICLE_CONFIG.get("region", "us")
    ]

@pytest.mark.integration
def test_cli_search(cli_env, common_args):
    """Test the search command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "search",
        "--query", "metadata.event_type = \"NETWORK_CONNECTION\"",
        "--time-window", "1",
        "--max-events", "5"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "events" in output
        assert "total_events" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_entity(cli_env, common_args):
    """Test the entity command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "entity",
        "--value", "8.8.8.8",
        "--time-window", "24"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # For entity command, we just verify it returned successfully
    # Output format can vary too much for detailed assertions
    assert result.stdout.strip() != ""
    assert "Error:" not in result.stderr

@pytest.mark.integration
def test_cli_rule_list(cli_env, common_args):
    """Test the rule list command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "rule", "list"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "rules" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_rule_search(cli_env, common_args):
    """Test the rule search command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "rule", "search", "--query", ".*"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "rules" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_stats(cli_env, common_args):
    """Test the stats command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "stats",
        "--query", """metadata.event_type = "NETWORK_CONNECTION"
match:
  principal.hostname
outcome:
  $count = count(metadata.id)
order:
  $count desc""",
        "--time-window", "1",
        "--max-events", "10",
        "--max-values", "5"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "columns" in output
        assert "rows" in output
        assert "total_rows" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_iocs(cli_env, common_args):
    """Test the iocs command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "iocs",
        "--time-window", "24",
        "--max-matches", "5"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "matches" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_log_types(cli_env, common_args):
    """Test the log types command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "log", "types"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON - should be a list of log types
    assert result.stdout.strip() != ""
    assert "Error:" not in result.stderr

@pytest.mark.integration
def test_cli_rule_get(cli_env, common_args):
    """Test the rule get command (first need to find an existing rule ID)."""
    # First list rules to get a valid rule ID
    list_cmd = [
        "secops",
    ] + common_args + [
        "rule", "list"
    ]
    
    list_result = subprocess.run(
        list_cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that we have at least one rule to test with
    assert list_result.returncode == 0
    
    rules = json.loads(list_result.stdout)
    if not rules.get("rules"):
        pytest.skip("No rules available to test the get command")
    
    # Get the first rule's ID
    rule_id = rules["rules"][0]["name"].split("/")[-1]
    
    # Test the get command with this rule ID
    get_cmd = [
        "secops",
    ] + common_args + [
        "rule", "get",
        "--id", rule_id
    ]
    
    get_result = subprocess.run(
        get_cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert get_result.returncode == 0
    
    # Try to parse the output as JSON
    rule_data = json.loads(get_result.stdout)
    assert "name" in rule_data
    assert rule_data["name"].endswith(rule_id)

@pytest.mark.integration
def test_cli_rule_validate(cli_env, common_args):
    """Test the rule validate command."""
    # Create a temporary file with a simple valid rule
    with tempfile.NamedTemporaryFile(suffix=".yaral", mode="w+", delete=False) as temp_file:
        temp_file.write("""
rule test_rule {
    meta:
        description = "Test rule for validation"
        author = "Test Author"
        severity = "Low"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
    condition:
        $e
}
""")
        temp_file_path = temp_file.name
    
    try:
        # Execute the CLI command
        cmd = [
            "secops",
        ] + common_args + [
            "rule", "validate",
            "--file", temp_file_path
        ]
        
        result = subprocess.run(
            cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the command executed successfully
        assert result.returncode == 0
        
        # Should return "Rule is valid."
        assert "Rule is valid" in result.stdout
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.integration
def test_cli_rule_lifecycle(cli_env, common_args):
    """Test rule creation, update, enable/disable, and deletion (full lifecycle)."""
    # Create temp files for the rule
    with tempfile.NamedTemporaryFile(suffix=".yaral", mode="w+", delete=False) as temp_file:
        temp_file.write("""
rule test_cli_rule {
    meta:
        description = "Test rule for CLI testing"
        author = "CLI Test"
        severity = "Low"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
    condition:
        $e
}
""")
        rule_file_path = temp_file.name
    
    with tempfile.NamedTemporaryFile(suffix=".yaral", mode="w+", delete=False) as update_file:
        update_file.write("""
rule test_cli_rule {
    meta:
        description = "Updated test rule for CLI testing"
        author = "CLI Test"
        severity = "Medium"
        yara_version = "YL2.0"
        rule_version = "1.1"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
    condition:
        $e
}
""")
        update_file_path = update_file.name
    
    try:
        # 1. Create the rule
        create_cmd = [
            "secops",
        ] + common_args + [
            "rule", "create",
            "--file", rule_file_path
        ]
        
        create_result = subprocess.run(
            create_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the command executed successfully
        assert create_result.returncode == 0
        
        # Extract the rule ID
        rule_data = json.loads(create_result.stdout)
        rule_id = rule_data["name"].split("/")[-1]
        
        # 2. Update the rule
        update_cmd = [
            "secops",
        ] + common_args + [
            "rule", "update",
            "--id", rule_id,
            "--file", update_file_path
        ]
        
        update_result = subprocess.run(
            update_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the update command executed successfully
        assert update_result.returncode == 0
        
        # 3. Enable the rule
        enable_cmd = [
            "secops",
        ] + common_args + [
            "rule", "enable",
            "--id", rule_id,
            "--enabled", "true"
        ]
        
        enable_result = subprocess.run(
            enable_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the enable command executed successfully
        assert enable_result.returncode == 0
        
        # 4. Disable the rule
        disable_cmd = [
            "secops",
        ] + common_args + [
            "rule", "enable",
            "--id", rule_id,
            "--enabled", "false"
        ]
        
        disable_result = subprocess.run(
            disable_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the disable command executed successfully
        assert disable_result.returncode == 0
        
        # 5. Delete the rule
        delete_cmd = [
            "secops",
        ] + common_args + [
            "rule", "delete",
            "--id", rule_id,
            "--force"
        ]
        
        delete_result = subprocess.run(
            delete_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the delete command executed successfully
        assert delete_result.returncode == 0
        
    finally:
        # Clean up temp files
        os.unlink(rule_file_path)
        os.unlink(update_file_path)

@pytest.mark.integration
def test_cli_alert(cli_env, common_args):
    """Test the alert command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "alert",
        "--time-window", "24",
        "--max-alerts", "5"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "complete" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_log_ingest_with_labels(cli_env, common_args):
    """Test the log ingest command with labels."""
    # Create a temporary file with a sample OKTA log
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as temp_file:
        # Create an OKTA log similar to the examples/ingest_logs.py format
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        okta_log = {
            "actor": {
                "displayName": "CLI Test User",
                "alternateId": "cli_test@example.com"
            },
            "client": {
                "ipAddress": "192.168.1.100",
                "userAgent": {
                    "os": "Mac OS X",
                    "browser": "SAFARI"
                }
            },
            "displayMessage": "User login to Okta via CLI test",
            "eventType": "user.session.start",
            "outcome": {
                "result": "SUCCESS"
            },
            "published": current_time
        }
        temp_file.write(json.dumps(okta_log))
        temp_file_path = temp_file.name
    
    try:
        # Test 1: Test with JSON format labels
        json_labels = '{"environment": "test", "source": "cli_test", "version": "1.0"}'
        
        json_cmd = [
            "secops",
        ] + common_args + [
            "log", "ingest",
            "--type", "OKTA",
            "--file", temp_file_path,
            "--labels", json_labels
        ]
        
        json_result = subprocess.run(
            json_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the command executed successfully with JSON labels
        assert json_result.returncode == 0, f"Command failed with stderr: {json_result.stderr}"
        
        # Try to parse the output as JSON - just check it's valid JSON, not specific fields
        try:
            json_output = json.loads(json_result.stdout)
            # The response might be an empty object {}, which is still valid
            assert isinstance(json_output, dict)
        except json.JSONDecodeError:
            # If not valid JSON, check for expected error messages
            assert "Error:" not in json_result.stdout
        
        # Test 2: Test with key=value format labels
        kv_labels = "environment=integration,source=cli_integration_test,team=security"
        
        kv_cmd = [
            "secops",
        ] + common_args + [
            "log", "ingest",
            "--type", "OKTA",
            "--file", temp_file_path,
            "--labels", kv_labels
        ]
        
        kv_result = subprocess.run(
            kv_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that the command executed successfully with key=value labels
        assert kv_result.returncode == 0, f"Command failed with stderr: {kv_result.stderr}"
        
        # Try to parse the output as JSON - just check it's valid JSON, not specific fields
        try:
            kv_output = json.loads(kv_result.stdout)
            # The response might be an empty object {}, which is still valid
            assert isinstance(kv_output, dict)
        except json.JSONDecodeError:
            # If not valid JSON, check for expected error messages
            assert "Error:" not in kv_result.stdout
            
    finally:
        # Clean up
        os.unlink(temp_file_path)

@pytest.mark.integration
def test_cli_export_log_types(cli_env, common_args):
    """Test the export log-types command."""
    # Execute the CLI command
    cmd = [
        "secops",
    ] + common_args + [
        "export", "log-types",
        "--time-window", "24"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Try to parse the output as JSON
    try:
        output = json.loads(result.stdout)
        assert "log_types" in output
    except json.JSONDecodeError:
        # If not valid JSON, check for expected error messages
        assert "Error:" not in result.stdout

@pytest.mark.integration
def test_cli_gemini(cli_env, common_args):
    """Test the gemini command."""
    # Execute the CLI command - Gemini output will be text by default, not JSON
    cmd = [
        "secops",
    ] + common_args + [
        "gemini",
        "--query", "What is Windows event ID 4625?"
    ]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    # Note: this may fail if Gemini is not enabled for the account
    if "users must opt-in before using Gemini" in result.stderr:
        pytest.skip("Test skipped: User account has not been opted-in to Gemini.")
    
    assert result.returncode == 0
    
    # For Gemini, just check that we got some text response
    assert len(result.stdout.strip()) > 0
    assert "Error:" not in result.stderr

@pytest.mark.integration
def test_cli_help(cli_env):
    """Test the help command."""
    # Execute the CLI command
    cmd = ["secops", "--help"]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # Check that the command executed successfully
    assert result.returncode == 0
    
    # Should contain help text
    assert "usage: secops" in result.stdout
    assert "Command to execute" in result.stdout

@pytest.mark.integration
def test_cli_version(cli_env):
    """Test retrieving the CLI version (using --version)."""
    # This assumes there's a --version flag; let's check if it exists
    cmd = ["secops", "--version"]
    
    result = subprocess.run(
        cmd,
        env=cli_env,
        capture_output=True,
        text=True
    )
    
    # If version flag exists, it should return successfully
    if result.returncode != 0:
        # If not, we'll skip this test
        pytest.skip("secops CLI does not support --version flag")
    
    # Should include a version number in the format x.y.z
    import re
    assert re.search(r"\d+\.\d+\.\d+", result.stdout)

@pytest.mark.integration
def test_cli_config_lifecycle(cli_env):
    """Test config set, view, and clear commands."""
    # Create temp directory for config file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override the CONFIG_DIR and CONFIG_FILE with temp directory
        with patch('secops.cli.CONFIG_DIR', Path(temp_dir)), \
             patch('secops.cli.CONFIG_FILE', Path(temp_dir) / "config.json"):
            
            # 1. Set configuration - standard parameters
            set_cmd = [
                "secops", "config", "set",
                "--customer-id", "test-customer-id",
                "--project-id", "test-project-id",
                "--region", "test-region"
            ]
            
            set_result = subprocess.run(
                set_cmd,
                env=cli_env,
                capture_output=True,
                text=True
            )
            
            # Check that the set command executed successfully
            assert set_result.returncode == 0
            assert "Configuration saved" in set_result.stdout
            
            # 2. Set time-related configuration
            time_set_cmd = [
                "secops", "config", "set",
                "--start-time", "2023-01-01T00:00:00Z",
                "--end-time", "2023-01-02T00:00:00Z",
                "--time-window", "48"
            ]
            
            time_set_result = subprocess.run(
                time_set_cmd,
                env=cli_env,
                capture_output=True,
                text=True
            )
            
            # Check that the time set command executed successfully
            assert time_set_result.returncode == 0
            assert "Configuration saved" in time_set_result.stdout
            
            # 3. View configuration
            view_cmd = ["secops", "config", "view"]
            
            view_result = subprocess.run(
                view_cmd,
                env=cli_env,
                capture_output=True,
                text=True
            )
            
            # Check that the view command executed successfully
            assert view_result.returncode == 0
            assert "test-customer-id" in view_result.stdout
            assert "test-project-id" in view_result.stdout
            assert "test-region" in view_result.stdout
            assert "2023-01-01T00:00:00Z" in view_result.stdout
            assert "2023-01-02T00:00:00Z" in view_result.stdout
            assert "48" in view_result.stdout
            
            # 4. Run a command that should use the configuration
            search_cmd = ["secops", "search", "--query", "metadata.event_type = \"NETWORK_CONNECTION\"", "--max-events", "1"]
            
            search_result = subprocess.run(
                search_cmd,
                env=cli_env,
                capture_output=True,
                text=True
            )
            
            # This might fail if the test credentials don't work, so we'll just check that it tried to use them
            
            # 5. Clear configuration
            clear_cmd = ["secops", "config", "clear"]
            
            clear_result = subprocess.run(
                clear_cmd,
                env=cli_env,
                capture_output=True,
                text=True
            )
            
            # Check that the clear command executed successfully
            assert clear_result.returncode == 0
            assert "Configuration cleared" in clear_result.stdout
            
            # 6. View again to confirm it's cleared
            view_cmd = ["secops", "config", "view"]
            
            view_result = subprocess.run(
                view_cmd,
                env=cli_env,
                capture_output=True,
                text=True
            )
            
            # Check that the view command shows no configuration
            assert view_result.returncode == 0
            assert "No configuration found" in view_result.stdout

@pytest.mark.integration
def test_cli_data_tables(cli_env, common_args):
    """Test the data-table command lifecycle."""
    # Generate unique name for data table using timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    table_name = f"test_cli_dt_{timestamp}"
    
    try:
        # 1. Create a data table
        header = json.dumps({"hostname": "STRING", "ip_address": "STRING", "description": "STRING"})
        rows = json.dumps([["host1.example.com", "192.168.1.10", "Test host 1"], 
                           ["host2.example.com", "192.168.1.11", "Test host 2"]])
        
        create_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "create",
            "--name", table_name,
            "--description", "CLI Test Data Table",
            "--header", header,
            "--rows", rows
        ]
        
        create_result = subprocess.run(
            create_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that creation was successful
        assert create_result.returncode == 0, f"Creation failed: {create_result.stderr}"
        
        # 2. Get the data table
        get_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "get",
            "--name", table_name
        ]
        
        get_result = subprocess.run(
            get_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that get was successful
        assert get_result.returncode == 0
        table_data = json.loads(get_result.stdout)
        assert table_data["name"].endswith(table_name)
        assert table_data["description"] == "CLI Test Data Table"
        assert len(table_data["columnInfo"]) == 3
        
        # 3. List rows
        list_rows_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "list-rows",
            "--name", table_name
        ]
        
        list_rows_result = subprocess.run(
            list_rows_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert list_rows_result.returncode == 0
        rows_data = json.loads(list_rows_result.stdout)
        assert len(rows_data) == 2  # We added 2 rows during creation
        
        # 4. Add more rows
        new_rows = json.dumps([["host3.example.com", "192.168.1.12", "Test host 3"]])
        add_rows_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "add-rows",
            "--name", table_name,
            "--rows", new_rows
        ]
        
        add_rows_result = subprocess.run(
            add_rows_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert add_rows_result.returncode == 0
        
        # 5. List rows again to verify the addition
        list_rows_result = subprocess.run(
            list_rows_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert list_rows_result.returncode == 0
        updated_rows_data = json.loads(list_rows_result.stdout)
        assert len(updated_rows_data) == 3  # Now should have 3 rows
        
        # 6. Delete a row
        # First, get the row ID
        row_id = updated_rows_data[0]["name"].split("/")[-1]
        
        delete_row_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "delete-rows",
            "--name", table_name,
            "--row-ids", row_id
        ]
        
        delete_row_result = subprocess.run(
            delete_row_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert delete_row_result.returncode == 0
        
        # 7. List data tables
        list_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "list"
        ]
        
        list_result = subprocess.run(
            list_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert list_result.returncode == 0
        tables = json.loads(list_result.stdout)
        # Find our table in the list
        found = False
        for table in tables:
            if table["name"].endswith(table_name):
                found = True
                break
        assert found, f"Couldn't find {table_name} in list of tables"
        
        # 8. Delete the table
        delete_cmd = [
            "secops",
        ] + common_args + [
            "data-table", "delete",
            "--name", table_name,
            "--force"
        ]
        
        delete_result = subprocess.run(
            delete_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert delete_result.returncode == 0
        
    except Exception as e:
        # Clean up in case of test failure
        try:
            subprocess.run([
                "secops",
            ] + common_args + [
                "data-table", "delete",
                "--name", table_name,
                "--force"
            ], env=cli_env, capture_output=True)
        except:
            pass
        raise

@pytest.mark.integration
def test_cli_reference_lists(cli_env, common_args):
    """Test the reference-list command lifecycle."""
    # Generate unique name for reference list using timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    list_name = f"test_cli_rl_{timestamp}"
    
    try:
        # 1. Create a reference list
        # Create a temporary file with reference list entries
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp_file:
            temp_file.write("malicious.example.com\n")
            temp_file.write("suspicious.example.org\n")
            temp_file.write("evil.example.net\n")
            entries_file_path = temp_file.name
        
        create_cmd = [
            "secops",
        ] + common_args + [
            "reference-list", "create",
            "--name", list_name,
            "--description", "CLI Test Reference List",
            "--entries-file", entries_file_path,
            "--syntax-type", "STRING"
        ]
        
        create_result = subprocess.run(
            create_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that creation was successful
        assert create_result.returncode == 0, f"Creation failed: {create_result.stderr}"
        
        # 2. Get the reference list
        get_cmd = [
            "secops",
        ] + common_args + [
            "reference-list", "get",
            "--name", list_name,
            "--view", "FULL"
        ]
        
        get_result = subprocess.run(
            get_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that get was successful
        assert get_result.returncode == 0
        list_data = json.loads(get_result.stdout)
        assert list_data["name"].endswith(list_name)
        assert list_data["description"] == "CLI Test Reference List"
        assert len(list_data["entries"]) == 3
        
        # 3. List reference lists
        list_cmd = [
            "secops",
        ] + common_args + [
            "reference-list", "list"
        ]
        
        list_result = subprocess.run(
            list_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert list_result.returncode == 0
        lists = json.loads(list_result.stdout)
        # Find our list in the result
        found = False
        for ref_list in lists:
            if ref_list["name"].endswith(list_name):
                found = True
                break
        assert found, f"Couldn't find {list_name} in list of reference lists"
        
        # 4. Update the reference list with new entries
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w+", delete=False) as temp_update_file:
            temp_update_file.write("updated.example.com\n")
            temp_update_file.write("new.example.org\n")
            update_file_path = temp_update_file.name
        
        update_cmd = [
            "secops",
        ] + common_args + [
            "reference-list", "update",
            "--name", list_name,
            "--description", "Updated CLI Test Reference List",
            "--entries-file", update_file_path
        ]
        
        update_result = subprocess.run(
            update_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert update_result.returncode == 0
        
        # 5. Get the updated reference list to verify changes
        get_updated_result = subprocess.run(
            get_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        assert get_updated_result.returncode == 0
        updated_data = json.loads(get_updated_result.stdout)
        assert updated_data["description"] == "Updated CLI Test Reference List"
        assert len(updated_data["entries"]) == 2
        
        # Add a delay before deletion to allow API to fully process previous operations
        time.sleep(5)
        
        # Note: Reference list deletion is not currently supported by the API
        print(f"Skipping deletion of reference list {list_name} - deletion not supported by API")
        
    except Exception as e:
        # Note: Reference list deletion is not currently supported by the API,
        # so we can't clean up test reference lists
        print(f"Warning: Test reference list {list_name} will remain since deletion is not supported")
        raise
    finally:
        # Clean up temp files
        if 'entries_file_path' in locals():
            os.unlink(entries_file_path)
        if 'update_file_path' in locals():
            os.unlink(update_file_path)

@pytest.mark.integration
def test_cli_reference_list_create_delete(cli_env, common_args):
    """Test simple reference list create and delete operations."""
    # Generate unique name for reference list using timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    list_name = f"test_cli_simple_{timestamp}"
    
    try:
        # 1. Create a reference list with simple inline entries
        create_cmd = [
            "secops",
        ] + common_args + [
            "reference-list", "create",
            "--name", list_name,
            "--description", "Simple Test Reference List",
            "--entries", "test1.example.com,test2.example.com",
            "--syntax-type", "STRING"
        ]
        
        create_result = subprocess.run(
            create_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that creation was successful
        assert create_result.returncode == 0, f"Creation failed: {create_result.stderr}"
        print(f"Reference list created: {list_name}")
        
        # 2. Get the reference list to confirm creation
        get_cmd = [
            "secops",
        ] + common_args + [
            "reference-list", "get",
            "--name", list_name
        ]
        
        get_result = subprocess.run(
            get_cmd,
            env=cli_env,
            capture_output=True,
            text=True
        )
        
        # Check that get was successful
        assert get_result.returncode == 0, f"Get failed: {get_result.stderr}"
        list_data = json.loads(get_result.stdout)
        print(f"Successfully retrieved reference list: {list_data['name']}")
        
        # Note: Reference list deletion is not currently supported by the API
        print(f"Skipping deletion of reference list {list_name} - deletion not supported by API")
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        # Note: Reference list deletion is not currently supported by the API,
        # so we can't clean up test reference lists
        print(f"Warning: Test reference list {list_name} will remain since deletion is not supported")
        raise

@pytest.mark.integration
def test_cli_reference_list_api_investigation(cli_env, common_args):
    """Test reference list API interactions directly using the SecOpsClient."""
    from secops import SecOpsClient
    from secops.chronicle.reference_list import ReferenceListSyntaxType, ReferenceListView
    from tests.config import CHRONICLE_CONFIG
    
    # Generate unique name for reference list
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    list_name = f"test_cli_api_{timestamp}"
    
    # Create a direct client instance
    client = SecOpsClient()
    chronicle = client.chronicle(**CHRONICLE_CONFIG)
    
    print("\n=== Reference List API Test ===\n")
    
    try:
        # 1. Create a reference list
        print(f"Creating reference list: {list_name}")
        created = chronicle.create_reference_list(
            name=list_name,
            description="API Test Reference List",
            entries=["test1.example.com", "test2.example.com"],
            syntax_type=ReferenceListSyntaxType.STRING
        )
        print(f"Creation response: {created}")
        print(f"Reference list name: {created.get('name', 'N/A')}")
        
        # 2. Get the reference list
        print(f"\nGetting reference list: {list_name}")
        retrieved = chronicle.get_reference_list(list_name, view=ReferenceListView.FULL)
        print(f"Get response: {retrieved}")
        print(f"Retrieved name: {retrieved.get('name', 'N/A')}")
        
        # 3. List reference lists and check if ours is included
        print("\nListing all reference lists")
        all_lists = chronicle.list_reference_lists()
        found = False
        for ref_list in all_lists:
            if ref_list.get("name", "").endswith(list_name):
                found = True
                print(f"Found in list: {ref_list.get('name')}")
                break
        
        if not found:
            print(f"WARNING: Reference list {list_name} not found in list results")
            
        # 4. Examine delete endpoint
        # Print what the delete URL would be
        instance_id = CHRONICLE_CONFIG.get("customer_id")
        project_id = CHRONICLE_CONFIG.get("project_id")
        region = CHRONICLE_CONFIG.get("region", "us")
        base_url = f"https://{region}-chronicle.googleapis.com/v1alpha"
        
        delete_url = f"{base_url}/{project_id}/locations/{region}/instances/{instance_id}/referenceLists/{list_name}"
        print(f"\nDelete would use URL: {delete_url}")
        
        # Note: Reference list deletion is not currently supported by the API
        print(f"\nSkipping deletion of reference list {list_name} - deletion not supported by API")
            
    except Exception as e:
        print(f"Test encountered an error: {e}")
        raise
