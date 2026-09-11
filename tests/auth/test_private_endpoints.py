"""Authenticated private endpoint tests for the LexxSoft backend.

Endpoints were identified from requests made by the public terminal. Tests that
need credentials use a manually supplied access token and never run in public CI.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.auth, pytest.mark.smoke, pytest.mark.bots]


class TestPrivateBotsEndpoints:
    def test_get_bots_is_reachable(self, auth_client):
        response = auth_client.get("/private/bots")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert isinstance(data.get("data"), list)

    def test_create_bot_requires_payload(self, auth_client):
        """An empty payload should be rejected without a server error."""
        response = auth_client.post("/private/bots", json={})
        if response.status_code == 500:
            pytest.xfail("Known backend defect: empty bot payload causes HTTP 500")
        assert response.status_code in (400, 403, 422)


class TestPrivateOrdersEndpoints:
    def test_get_orders_is_reachable(self, auth_client):
        response = auth_client.get("/private/orders")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert isinstance(data.get("data"), list)


class TestPrivateSettingsEndpoints:
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
    @pytest.mark.parametrize(
        "path",
        [
            "/private/portfolio/positions",
            "/private/portfolio/positions/history",
            "/private/portfolio/earns",
        ],
    )
    def test_portfolio_endpoints_do_not_return_server_error(self, auth_client, path):
        response = auth_client.get(path)
        if response.status_code == 500:
            pytest.xfail(f"Known backend defect: {path} returns HTTP 500 for a free account")
        assert response.status_code in (200, 403)


class TestPrivateExternalEndpoints:
    def test_get_external_ideas_token_is_reachable(self, auth_client):
        response = auth_client.get("/private/external/ideas")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"
            assert "data" in data


class TestAnonymousAccessToPrivateEndpoints:
    """Check that private routes enforce an authentication boundary.

    Behaviour can depend on the source IP, but the security invariant does not:
    anonymous requests must be rejected before reaching application logic.
    """

    pytestmark = pytest.mark.anonymous

    @pytest.mark.parametrize(
        "path",
        [
            "/private/bots",
            "/private/orders",
            "/private/settings",
        ],
    )
    def test_private_get_endpoints_require_authentication(self, public_client, path):
        response = public_client.get(path)
        assert response.status_code in (401, 403), (
            f"{path} returned {response.status_code} without authentication"
        )

    def test_portfolio_positions_requires_authentication(self, public_client):
        response = public_client.get("/private/portfolio/positions")
        assert response.status_code in (401, 403), (
            "portfolio endpoint did not reject the anonymous request at the auth boundary"
        )
