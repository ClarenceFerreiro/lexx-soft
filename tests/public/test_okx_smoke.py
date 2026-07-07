"""Smoke tests for OKX public market-data endpoints and LexxSoft backend.

These tests are CI-friendly: OKX and LexxSoft auth endpoints do not block
GitHub Actions runners.
"""

from __future__ import annotations

import pytest
import requests

pytestmark = [pytest.mark.public, pytest.mark.smoke]


class TestOkxMarketData:
    """Smoke tests for OKX public market-data endpoints."""

    BASE_URL = "https://www.okx.com/api/v5/market"

    def test_okx_tickers_returns_200(self):
        response = requests.get(
            f"{self.BASE_URL}/tickers",
            params={"instType": "SPOT"},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("code") == "0"
        assert "data" in data

    def test_okx_trades_returns_200(self):
        response = requests.get(
            f"{self.BASE_URL}/trades",
            params={"instId": "BTC-USDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("code") == "0"
        assert "data" in data


class TestLexxSoftAuthSmoke:
    """Smoke test for the LexxSoft backend authentication endpoint."""

    def test_auth_login_endpoint_exists_and_requires_recaptcha(self, public_client):
        """The login endpoint must exist and reject requests without recaptcha."""
        response = public_client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("status") == "failed"
        assert "recaptcha" in data.get("msg", "").lower()

    def test_auth_login_rejects_invalid_email_format(self, public_client):
        """The login endpoint must reject malformed email addresses."""
        response = public_client.post(
            "/auth/login",
            json={"email": "not-an-email", "password": "wrongpassword"},
        )
        assert response.status_code in (400, 422)
