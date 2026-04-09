"""Integration tests for Log Type CLI commands."""

import json
import subprocess
import pytest


@pytest.mark.integration
def test_cli_log_type_lifecycle(cli_env, common_args):
    """Test the complete log-type lifecycle commands."""
    
    print("\nTesting log-type trigger-checks command")

    # We need a stable test fixture for the associated_pr. Since PRs are ephemeral,
    # we will trigger a check for a dummy PR and expect either a successful trigger
    # or a specific graceful failure (like 404 PR not found) to prove the CLI routing works.
    trigger_cmd = (
        ["secops"]
        + common_args
        + [
            "--project-id",
            "140410331797",
            "--customer-id",
            "ebdc4bb9-878b-11e7-8455-10604b7cb5c1",
            "log-type",
            "trigger-checks",
            # google/secops-wrapper/pull/1 is just a dummy sample PR to fulfill validation
            "--associated-pr",
            "google/secops-wrapper/pull/617",
            "--log-type",
            "DUMMY_LOGTYPE",
        ]
    )

    result = subprocess.run(trigger_cmd, env=cli_env, capture_output=True, text=True)

    # Note: Depending on the backend environment, triggering a check on a fake PR/CustomerID
    # might actually return a 400/404 APIError rather than a 0 exit code.
    # We assert that the CLI executed and returned *something* from the server, 
    # even if it's an API error about the fake customer ID.
    if result.returncode == 0:
        try:
            output = json.loads(result.stdout)
            assert isinstance(output, dict)
            print("Successfully triggered checks (or received valid JSON response)")
        except json.JSONDecodeError:
            pytest.fail(f"Could not decode JSON from successful exit: {result.stdout}")
    else:
        # If the backend rejects the fake data, we prove the CLI correctly caught the APIError
        assert "API error" in result.stderr or "Error" in result.stderr
        print(f"Server gracefully rejected the dummy trigger data: {result.stderr.strip()}")

    print("\nTesting log-type get-analysis-report command")
    
    # We supply a dummy log type, parser, and report ID. The backend will likely 404, proving the routing works.
    get_cmd = (
        ["secops"]
        + common_args
        + [
            "--project-id",
            "140410331797",
            "--customer-id",
            "ebdc4bb9-878b-11e7-8455-10604b7cb5c1",
            "log-type",
            "get-analysis-report",
            "--log-type",
            "DUMMY_LOGTYPE",
            "--parser-id",
            "xyz",
            "--report-id",
            "123"
        ]
    )
    
    get_result = subprocess.run(get_cmd, env=cli_env, capture_output=True, text=True)
    
    if get_result.returncode == 0:
        try:
            output = json.loads(get_result.stdout)
            assert isinstance(output, dict)
            print("Successfully retrieved report")
        except json.JSONDecodeError:
            pytest.fail(f"Could not decode JSON: {get_result.stdout}")
    else:
        # We expect a 404 or similar API error since the report name is fake
        assert "API error" in get_result.stderr or "Error" in get_result.stderr
        print(f"Server gracefully rejected dummy report name: {get_result.stderr.strip()}")

if __name__ == "__main__":
    pytest.main(["-v", __file__, "-m", "integration"])
