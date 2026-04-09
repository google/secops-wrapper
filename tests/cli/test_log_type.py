"""Unit tests for Log Type CLI commands."""

from unittest.mock import MagicMock
from argparse import Namespace
import pytest

from secops.cli.commands.log_type import (
    handle_trigger_checks_command,
    handle_get_analysis_report_command,
)
from secops.exceptions import APIError, SecOpsError


def test_handle_trigger_checks_command_success():
    """Test successful trigger_checks command execution."""
    args = Namespace(
        associated_pr="owner/repo/pull/123",
        log_type="DUMMY_LOGTYPE",
        output="json",
    )
    mock_chronicle = MagicMock()
    mock_chronicle.trigger_github_checks.return_value = {
        "message": "Success",
        "details": "Details",
    }

    try:
        handle_trigger_checks_command(args, mock_chronicle)
    except SystemExit:
        pytest.fail("Command exited unexpectedly")

    mock_chronicle.trigger_github_checks.assert_called_once_with(
        associated_pr="owner/repo/pull/123",
        log_type="DUMMY_LOGTYPE",
    )


def test_handle_trigger_checks_command_api_error(capsys):
    """Test trigger_checks command with APIError."""
    args = Namespace(
        associated_pr="owner/repo/pull/123",
        log_type="BRO_DNS",
        output="json",
    )
    mock_chronicle = MagicMock()
    mock_chronicle.trigger_github_checks.side_effect = APIError("API fault")

    with pytest.raises(SystemExit) as exc:
        handle_trigger_checks_command(args, mock_chronicle)

    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error: API fault" in err


def test_handle_get_analysis_report_command_success():
    """Test successful get_analysis_report command execution."""
    args = Namespace(
        log_type="DEF",
        parser_id="XYZ",
        report_id="123",
        output="json",
    )
    mock_chronicle = MagicMock()
    mock_chronicle.get_analysis_report.return_value = {
        "reportId": "123",
        "status": "COMPLETED",
    }

    try:
        handle_get_analysis_report_command(args, mock_chronicle)
    except SystemExit:
        pytest.fail("Command exited unexpectedly")

    mock_chronicle.get_analysis_report.assert_called_once_with(
        log_type="DEF",
        parser_id="XYZ",
        report_id="123",
    )


def test_handle_get_analysis_report_command_secops_error(capsys):
    """Test get_analysis_report command with SecOpsError."""
    args = Namespace(
        log_type="DEF",
        parser_id="XYZ",
        report_id="123",
        output="json",
    )
    mock_chronicle = MagicMock()
    mock_chronicle.get_analysis_report.side_effect = SecOpsError("Invalid input")

    with pytest.raises(SystemExit) as exc:
        handle_get_analysis_report_command(args, mock_chronicle)

    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error: Invalid input" in err
