"""Smoke tests for Binance public market-data endpoints used by LexxSoft terminal.

These endpoints are known to block GitHub Actions IP ranges (HTTP 451).
Run them locally; CI skips them via the `binance` marker.
"""

from __future__ import annotations

import pytest
import requests

pytestmark = [pytest.mark.public, pytest.mark.smoke, pytest.mark.binance]


class TestBinanceMarketData:
    """Smoke tests for Binance Spot public market-data endpoints."""

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
