"""Tests for Chronicle rule validation functions."""

import pytest
from unittest.mock import Mock, patch
from secops.chronicle.client import ChronicleClient
from secops.chronicle.rule_validation import validate_rule
from secops.exceptions import APIError


@pytest.fixture
def chronicle_client():
    """Create a Chronicle client for testing."""
    with patch("secops.auth.SecOpsAuth") as mock_auth:
        mock_session = Mock()
        mock_session.headers = {}
        mock_auth.return_value.session = mock_session
        return ChronicleClient(
            customer_id="test-customer", project_id="test-project"
        )


@pytest.fixture
def mock_success_response():
    """Create a mock successful API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"success": True}
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "compilationDiagnostics": [
            {
                "message": "semantic analysis: event variable e and its child variables not used in condition section",
                "severity": "ERROR",
            }
        ]
    }
    return mock


@pytest.fixture
def mock_error_with_position():
    """Create a mock error API response with position information."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "compilationDiagnostics": [
            {
                "message": 'parsing: error with token: "+"\nexpected }\nline: 27 \ncolumn: 8-9 ',
                "position": {
                    "startLine": 27,
                    "startColumn": 8,
                    "endLine": 27,
                    "endColumn": 9,
                },
                "severity": "ERROR",
            }
        ]
    }
    return mock


def test_validate_rule_success(chronicle_client, mock_success_response):
    """Test validate_rule function with successful validation."""
    # Arrange
    rule_text = """
    rule test_rule {
        meta:
            author = "test"
            description = "test rule"
            severity = "Low"
        events:
            $e.metadata.event_type = "NETWORK_CONNECTION"
        condition:
            $e
    }
    """

    with patch.object(
        chronicle_client.session, "post", return_value=mock_success_response
    ) as mock_post:
        # Act
        result = validate_rule(chronicle_client, rule_text)

        # Assert
        mock_post.assert_called_once()
        assert result.success is True
        assert result.message is None
        assert result.position is None


def test_validate_rule_error(chronicle_client, mock_error_response):
    """Test validate_rule function with validation error."""
    # Arrange
    rule_text = "invalid rule"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_response
    ) as mock_post:
        # Act
        result = validate_rule(chronicle_client, rule_text)

        # Assert
        mock_post.assert_called_once()
        assert result.success is False
        assert "semantic analysis" in result.message
        assert result.position is None


def test_validate_rule_error_with_position(chronicle_client, mock_error_with_position):
    """Test validate_rule function with validation error including position information."""
    # Arrange
    rule_text = "invalid rule with position"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error_with_position
    ) as mock_post:
        # Act
        result = validate_rule(chronicle_client, rule_text)

        # Assert
        mock_post.assert_called_once()
        assert result.success is False
        assert "parsing: error with token" in result.message
        assert result.position is not None
        assert result.position["startLine"] == 27
        assert result.position["startColumn"] == 8
        assert result.position["endLine"] == 27
        assert result.position["endColumn"] == 9


def test_validate_rule_api_error(chronicle_client):
    """Test validate_rule function with API error."""
    # Arrange
    mock_error = Mock()
    mock_error.status_code = 400
    mock_error.text = "API Error"

    with patch.object(
        chronicle_client.session, "post", return_value=mock_error
    ) as mock_post:
        # Act & Assert
        with pytest.raises(APIError) as exc_info:
            validate_rule(chronicle_client, "rule text")

        assert "Failed to validate rule" in str(exc_info.value)
