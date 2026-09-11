"""Deterministic unit tests for the LexxSoft API client."""

from __future__ import annotations

import pytest
import requests
import responses
from pydantic import ValidationError

from lexxsoft_client import LexxClient
from tests.public.schemas import BinanceOrderBook, OkxRestResponse

pytestmark = pytest.mark.unit
FAKE_CREDENTIAL = "unit-test-credential"


def test_builds_url_for_nested_api_route_used_by_user_endpoints():
    """The backend intentionally exposes user routes below ``/api/api``."""
    with LexxClient(base_url="https://example.test/api") as client:
        assert client._url("/api/user/me") == "https://example.test/api/api/user/me"


def test_environment_token_is_not_implicitly_attached(monkeypatch):
    monkeypatch.setenv("LEXX_ACCESS_TOKEN", "real-looking-environment-token")

    with LexxClient(base_url="https://example.test/api") as client:
        assert "Authorization" not in client.session.headers


def test_netrc_credentials_are_not_attached_to_prepared_request(monkeypatch, tmp_path):
    netrc_file = tmp_path / "netrc"
    netrc_file.write_text(
        "machine example.test login unintended-user password unintended-password\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("NETRC", str(netrc_file))

    with LexxClient(base_url="https://example.test/api") as client:
        request = requests.Request("GET", client._url("/health"))
        prepared = client.session.prepare_request(request)

    assert "Authorization" not in prepared.headers


def test_access_token_is_added_to_prepared_request():
    with LexxClient(base_url="https://example.test/api", access_token=FAKE_CREDENTIAL) as client:
        request = requests.Request("GET", client._url("/private/orders"))
        prepared = client.session.prepare_request(request)

    assert prepared.headers["Authorization"] == f"Bearer {FAKE_CREDENTIAL}"


@responses.activate
def test_get_forwards_query_parameters():
    responses.get(
        "https://example.test/api/private/orders",
        json={"status": "success", "data": []},
        status=200,
    )

    with LexxClient(base_url="https://example.test/api", timeout=7) as client:
        response = client.get("/private/orders", params={"page": 2})

    assert response.status_code == 200
    assert responses.calls[0].request.url == "https://example.test/api/private/orders?page=2"


@responses.activate
def test_login_stores_token_returned_by_backend():
    responses.post(
        "https://example.test/api/auth/login",
        json={"access_token": "issued-token"},
        status=200,
    )

    with LexxClient(
        base_url="https://example.test/api",
        email="qa@example.test",
        password=FAKE_CREDENTIAL,
    ) as client:
        response = client.login()

        assert response.status_code == 200
        assert client.access_token == "issued-token"
        assert client.session.headers["Authorization"] == "Bearer issued-token"


def test_okx_response_wraps_invalid_data_type_as_validation_error():
    with pytest.raises(ValidationError):
        OkxRestResponse(code="0", data={})


def test_binance_order_book_wraps_invalid_side_as_validation_error():
    with pytest.raises(ValidationError):
        BinanceOrderBook(lastUpdateId=1, bids={}, asks=[])
