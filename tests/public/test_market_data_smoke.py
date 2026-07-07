"""Smoke tests for public market-data endpoints used by LexxSoft terminal.

LexxSoft terminal does not proxy public market data through its own backend.
Instead, it fetches data directly from exchange APIs. This suite verifies that
those upstream endpoints are reachable and return the expected shape.

Additionally, it includes a smoke test for the LexxSoft authentication endpoint
(`/api/auth/login`) to confirm the backend is alive.
"""

from __future__ import annotations

import pytest
import requests

pytestmark = [pytest.mark.public, pytest.mark.smoke]


class TestBinanceMarketData:
    """Smoke tests for Binance public market-data endpoints."""

    BASE_URL = "https://api.binance.com/api/v3"

    def test_binance_exchangeinfo_returns_200(self):
        response = requests.get(f"{self.BASE_URL}/exchangeInfo", timeout=30)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_binance_depth_returns_orderbook(self):
        response = requests.get(
            f"{self.BASE_URL}/depth",
            params={"symbol": "BTCUSDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "bids" in data
        assert "asks" in data

    def test_binance_ticker_24hr_returns_data(self):
        response = requests.get(
            f"{self.BASE_URL}/ticker/24hr",
            params={"symbol": "BTCUSDT"},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("symbol") == "BTCUSDT"

    def test_binance_trades_returns_list(self):
        response = requests.get(
            f"{self.BASE_URL}/trades",
            params={"symbol": "BTCUSDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


class TestBinanceFuturesMarketData:
    """Smoke tests for Binance USDⓈ-M futures market-data endpoints."""

    BASE_URL = "https://fapi.binance.com/fapi/v1"

    def test_binance_futures_depth_returns_orderbook(self):
        response = requests.get(
            f"{self.BASE_URL}/depth",
            params={"symbol": "BTCUSDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert "bids" in data and "asks" in data

    def test_binance_futures_ticker_24hr_returns_data(self):
        response = requests.get(
            f"{self.BASE_URL}/ticker/24hr",
            params={"symbol": "BTCUSDT"},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("symbol") == "BTCUSDT"


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
