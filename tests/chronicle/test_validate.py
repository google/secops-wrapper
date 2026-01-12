from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.models import APIVersion
from secops.chronicle.validate import validate_query


@pytest.fixture
def chronicle_client() -> Mock:
    # validate_query only needs a client object to pass through to chronicle_request
    return Mock()


def test_validate_query_calls_chronicle_request_with_expected_params(chronicle_client: Mock) -> None:
    expected = {"queryType": "QUERY_TYPE_UDM_QUERY", "isValid": True}

    with patch("secops.chronicle.validate.chronicle_request", return_value=expected) as req:
        result = validate_query(
            chronicle_client, 'metadata.event_type = "NETWORK_CONNECTION"'
        )

    assert result == expected

    req.assert_called_once()
    kwargs = req.call_args.kwargs

    assert req.call_args.args[0] is chronicle_client  # client passed positionally
    assert kwargs["method"] == "GET"
    assert kwargs["endpoint_path"] == ":validateQuery"
    assert kwargs["api_version"] == APIVersion.V1ALPHA

    # Check params are correct for dialect + placeholders behaviour
    assert kwargs["params"]["dialect"] == "DIALECT_UDM_SEARCH"
    assert kwargs["params"]["allowUnreplacedPlaceholders"] == "false"
    assert kwargs["params"]["rawQuery"] == 'metadata.event_type = "NETWORK_CONNECTION"'


def test_validate_query_encodes_exclamation_marks(chronicle_client: Mock) -> None:
    expected = {"isValid": True}

    with patch("secops.chronicle.validate.chronicle_request", return_value=expected) as req:
        validate_query(chronicle_client, 'field = "a!b"')

    raw_query = req.call_args.kwargs["params"]["rawQuery"]
    assert raw_query == 'field = "a\\u0021b"'
