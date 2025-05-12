"""Integration tests for the SecOps CLI."""
import pytest
import subprocess
import json
import os
import tempfile
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
