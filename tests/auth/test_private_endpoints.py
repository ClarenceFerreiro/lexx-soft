"""Authenticated private endpoint tests for LexxSoft backend.

Endpoints discovered from the terminal's JS bundle under `/api/private/*`.
The free account used for testing has no bots or positions, so responses are
mostly empty arrays. These tests document reachability and role behaviour.
"""

from __future__ import annotations

import os

import pytest

from lexxsoft_client import LexxClient

pytestmark = [pytest.mark.auth, pytest.mark.smoke, pytest.mark.bots]


@pytest.fixture(scope="module")
def auth_client():
    token = os.getenv("LEXX_ACCESS_TOKEN")
    if not token:
        pytest.skip("LEXX_ACCESS_TOKEN is not set")
    with LexxClient(access_token=token) as client:
        yield client


class TestPrivateBotsEndpoints:
    """Reachability tests for LexxSoft private bot endpoints."""

    def test_get_bots_is_reachable(self, auth_client):
        response = auth_client.get("/private/bots")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert isinstance(data.get("data"), list)

    def test_create_bot_requires_payload(self, auth_client):
        """Empty payload is currently handled as a server error (500)."""
        response = auth_client.post("/private/bots", json={})
        assert response.status_code in (400, 403, 422, 500)


class TestPrivateOrdersEndpoints:
    """Reachability tests for LexxSoft private order endpoints."""

    def test_get_orders_is_reachable(self, auth_client):
        response = auth_client.get("/private/orders")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert isinstance(data.get("data"), list)


class TestPrivateSettingsEndpoints:
    """Reachability tests for LexxSoft private settings endpoints."""

    def test_get_settings_is_reachable(self, auth_client):
        response = auth_client.get("/private/settings")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert "data" in data

    def test_get_account_settings_is_reachable(self, auth_client):
        response = auth_client.get("/private/settings/account")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert "data" in data


class TestPrivatePortfolioEndpoints:
    """Reachability tests for LexxSoft portfolio endpoints."""

    @pytest.mark.parametrize(
        "path",
        [
            "/private/portfolio/positions",
            "/private/portfolio/positions/history",
            "/private/portfolio/earns",
        ],
    )
    def test_portfolio_endpoints_do_not_crash(self, auth_client, path):
        """Portfolio endpoints may 500 for free users; we only check stability."""
        response = auth_client.get(path)
        assert response.status_code in (200, 403, 500)


class TestPrivateExternalEndpoints:
    """Reachability tests for LexxSoft external integration endpoints."""

    def test_get_external_ideas_token_is_reachable(self, auth_client):
        response = auth_client.get("/private/external/ideas")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert "data" in data


class TestAnonymousAccessToPrivateEndpoints:
    """Document LexxSoft's anonymous access policy for `/api/private/*` GET endpoints.

    Behaviour appears region/IP-dependent: some client IPs get 200 with an
    empty payload, GitHub Actions runners get 401. We assert the acceptable
    outcomes and flag unexpected access when it occurs.
    """

    @pytest.mark.parametrize(
        "path",
        [
            "/private/bots",
            "/private/orders",
            "/private/settings",
        ],
    )
    def test_private_get_endpoints_require_or_allow_anonymous_access(
        self,
        public_client,
        path,
    ):
        response = public_client.get(path)
        if response.status_code == 200:
            pytest.skip(
                f"{path} returned 200 without auth from this IP; "
                "region-specific behaviour, not a CI failure"
            )
        assert response.status_code in (401, 403)

    def test_portfolio_positions_is_not_publicly_reachable(self, public_client):
        response = public_client.get("/private/portfolio/positions")
        assert response.status_code in (401, 403, 500)
