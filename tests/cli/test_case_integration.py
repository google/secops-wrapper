"""Integration tests for the SecOps CLI case commands.

These tests require valid credentials and API access.
They interact with real Chronicle API endpoints via CLI.
"""

import json
import subprocess

import pytest


@pytest.mark.integration
def test_cli_list_and_get_cases_workflow(cli_env, common_args):
    """Test CLI case list and get workflow."""
    # Test basic list
    list_cmd = ["secops"] + common_args + ["case", "list", "--page-size", "3"]
    list_result = subprocess.run(
        list_cmd, env=cli_env, capture_output=True, text=True
    )
    assert list_result.returncode == 0

    try:
        list_output = json.loads(list_result.stdout)
        assert "cases" in list_output
        assert isinstance(list_output["cases"], list)
        assert "totalSize" in list_output
    except json.JSONDecodeError:
        assert "Error:" not in list_result.stdout

    # Test list with --as-list flag
    as_list_cmd = (
        ["secops"]
        + common_args
        + ["case", "list", "--page-size", "3", "--as-list"]
    )
    as_list_result = subprocess.run(
        as_list_cmd, env=cli_env, capture_output=True, text=True
    )
    assert as_list_result.returncode == 0

    try:
        as_list_output = json.loads(as_list_result.stdout)
        assert isinstance(as_list_output, list)
        if as_list_output:
            assert "name" in as_list_output[0]
    except json.JSONDecodeError:
        assert "Error:" not in as_list_result.stdout

    # Test list with filter
    filter_cmd = (
        ["secops"]
        + common_args
        + ["case", "list", "--page-size", "5", "--filter", 'status = "OPENED"']
    )
    filter_result = subprocess.run(
        filter_cmd, env=cli_env, capture_output=True, text=True
    )
    assert filter_result.returncode == 0

    try:
        filter_output = json.loads(filter_result.stdout)
        assert "cases" in filter_output
    except json.JSONDecodeError:
        assert "Error:" not in filter_result.stdout

    # Test get case by ID
    try:
        if list_output.get("cases"):
            case_name = list_output["cases"][0].get("name", "")
            case_id = case_name.split("/")[-1]

            if case_id:
                get_cmd = (
                    ["secops"] + common_args + ["case", "get", "--id", case_id]
                )
                get_result = subprocess.run(
                    get_cmd, env=cli_env, capture_output=True, text=True
                )

                assert get_result.returncode == 0

                get_output = json.loads(get_result.stdout)
                assert "id" in get_output or "display_name" in get_output
                assert "priority" in get_output
                assert "status" in get_output
    except (json.JSONDecodeError, KeyError):
        pass


@pytest.mark.integration
def test_cli_case_update(cli_env, common_args):
    """Test the case update command."""
    # Use dedicated test case ID
    case_id = "7418669"

    # Get original case state
    get_cmd = ["secops"] + common_args + ["case", "get", "--id", case_id]
    get_result = subprocess.run(
        get_cmd, env=cli_env, capture_output=True, text=True
    )

    if get_result.returncode != 0:
        pytest.skip("Unable to get test case")

    try:
        get_output = json.loads(get_result.stdout)
        original_priority = get_output.get("priority", "PRIORITY_MEDIUM")

        # Determine new priority
        new_priority = (
            "PRIORITY_MEDIUM"
            if original_priority == "PRIORITY_HIGH"
            else "PRIORITY_HIGH"
        )

        # Update the case
        update_cmd = (
            ["secops"]
            + common_args
            + [
                "case",
                "update",
                "--id",
                case_id,
                "--data",
                f'{{"priority": "{new_priority}"}}',
                "--update-mask",
                "priority",
            ]
        )

        update_result = subprocess.run(
            update_cmd, env=cli_env, capture_output=True, text=True
        )

        assert update_result.returncode == 0

        update_output = json.loads(update_result.stdout)
        assert update_output.get("priority") == new_priority

        # Cleanup: Restore original priority
        restore_cmd = (
            ["secops"]
            + common_args
            + [
                "case",
                "update",
                "--id",
                case_id,
                "--data",
                f'{{"priority": "{original_priority}"}}',
                "--update-mask",
                "priority",
            ]
        )
        subprocess.run(restore_cmd, env=cli_env, capture_output=True)

    except (json.JSONDecodeError, KeyError):
        pytest.skip("Unable to parse JSON output or extract data")


@pytest.mark.integration
def test_cli_case_bulk_add_tag(cli_env, common_args):
    """Test the case bulk-add-tag command."""
    # Use dedicated test case ID
    case_ids = ["7418669"]

    # Test bulk add tag
    bulk_cmd = (
        ["secops"]
        + common_args
        + [
            "case",
            "bulk-add-tag",
            "--ids",
            ",".join(case_ids),
            "--tags",
            "cli-integration-test",
        ]
    )

    bulk_result = subprocess.run(
        bulk_cmd, env=cli_env, capture_output=True, text=True
    )

    assert bulk_result.returncode == 0


@pytest.mark.integration
def test_cli_case_bulk_assign(cli_env, common_args):
    """Test the case bulk-assign command.

    Skips test if API returns 500/INTERNAL error.
    """
    # Use dedicated test case ID
    case_ids = ["7418669"]

    bulk_cmd = (
        ["secops"]
        + common_args
        + [
            "case",
            "bulk-assign",
            "--ids",
            ",".join(case_ids),
            "--username",
            "'@Administrator'",
        ]
    )

    bulk_result = subprocess.run(
        bulk_cmd, env=cli_env, capture_output=True, text=True
    )

    # Skip if API returns INTERNAL/500 error
    if bulk_result.returncode != 0:
        if "INTERNAL" in bulk_result.stderr or "500" in bulk_result.stderr:
            pytest.skip(
                f"Bulk assign API returned INTERNAL error: "
                f"{bulk_result.stderr}"
            )

    assert bulk_result.returncode == 0


@pytest.mark.integration
def test_cli_case_bulk_change_priority(cli_env, common_args):
    """Test the case bulk-change-priority command."""
    # Use dedicated test case ID
    case_ids = ["7418669"]

    bulk_cmd = (
        ["secops"]
        + common_args
        + [
            "case",
            "bulk-change-priority",
            "--ids",
            ",".join(case_ids),
            "--priority",
            "MEDIUM",
        ]
    )

    bulk_result = subprocess.run(
        bulk_cmd, env=cli_env, capture_output=True, text=True
    )

    assert bulk_result.returncode == 0


@pytest.mark.integration
def test_cli_case_bulk_change_stage(cli_env, common_args):
    """Test the case bulk-change-stage command."""
    # Use dedicated test case ID
    case_ids = ["7418669"]

    bulk_cmd = (
        ["secops"]
        + common_args
        + [
            "case",
            "bulk-change-stage",
            "--ids",
            ",".join(case_ids),
            "--stage",
            "Triage",
        ]
    )

    bulk_result = subprocess.run(
        bulk_cmd, env=cli_env, capture_output=True, text=True
    )

    assert bulk_result.returncode == 0


@pytest.mark.integration
def test_cli_case_bulk_close_reopen_workflow(cli_env, common_args):
    """Test the case bulk-close and bulk-reopen commands in workflow."""
    # Use dedicated test case ID
    case_ids = ["7418669"]

    try:
        # Test bulk close
        close_cmd = (
            ["secops"]
            + common_args
            + [
                "case",
                "bulk-close",
                "--ids",
                ",".join(case_ids),
                "--close-reason",
                "MAINTENANCE",
                "--root-cause",
                "CLI integration test",
            ]
        )

        close_result = subprocess.run(
            close_cmd, env=cli_env, capture_output=True, text=True
        )

        assert close_result.returncode == 0

    finally:
        # Cleanup: Test bulk reopen
        reopen_cmd = (
            ["secops"]
            + common_args
            + [
                "case",
                "bulk-reopen",
                "--ids",
                ",".join(case_ids),
                "--reopen-comment",
                "CLI integration test cleanup",
            ]
        )

        reopen_result = subprocess.run(
            reopen_cmd, env=cli_env, capture_output=True, text=True
        )

        assert reopen_result.returncode == 0
