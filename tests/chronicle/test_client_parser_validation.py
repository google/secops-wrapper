"""Test parser validation methods on ChronicleClient."""

from unittest.mock import MagicMock
import pytest

from secops.chronicle.client import ChronicleClient


@pytest.fixture
def mock_client():
    """Create a mock ChronicleClient."""
    client = ChronicleClient(
        project_id="test-project",
        customer_id="test-customer",
        auth=MagicMock(),
    )
    # Mock the parser validation service stub
    client.parser_validation_service_stub = MagicMock()
    return client


def test_trigger_github_checks(mock_client, monkeypatch):
    """Test ChronicleClient.trigger_github_checks."""
    # Mock the underlying implementation to avoid REST dependency in tests
    mock_impl = MagicMock(
        return_value={"message": "Success", "details": "Started"}
    )
    monkeypatch.setattr(
        "secops.chronicle.client._trigger_github_checks", mock_impl
    )

    result = mock_client.trigger_github_checks(
        associated_pr="owner/repo/pull/123",
        log_type="DUMMY_LOGTYPE",
    )

    assert result == {"message": "Success", "details": "Started"}
    mock_impl.assert_called_once_with(
        mock_client,
        associated_pr="owner/repo/pull/123",
        log_type="DUMMY_LOGTYPE",
        timeout=60,
    )


def test_get_analysis_report(mock_client, monkeypatch):
    """Test ChronicleClient.get_analysis_report."""
    # Mock the underlying implementation
    mock_impl = MagicMock(return_value={"reportId": "123"})
    monkeypatch.setattr(
        "secops.chronicle.client._get_analysis_report", mock_impl
    )

    result = mock_client.get_analysis_report(
        log_type="DEF", parser_id="XYZ", report_id="123"
    )

    assert result == {"reportId": "123"}
    mock_impl.assert_called_once_with(
        mock_client,
        log_type="DEF",
        parser_id="XYZ",
        report_id="123",
        timeout=60,
    )
