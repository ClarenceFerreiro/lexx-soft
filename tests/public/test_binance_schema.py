"""Schema validation and edge-case tests for Binance public endpoints.

These endpoints are known to block GitHub Actions IP ranges (HTTP 451).
Run them locally; CI skips them via the `binance` marker.
"""

from __future__ import annotations

import pytest
import requests

from tests.public.schemas import (
    BinanceExchangeInfo,
    BinanceOrderBook,
    BinanceTicker24hr,
    BinanceTrade,
)

pytestmark = [pytest.mark.public, pytest.mark.schema, pytest.mark.binance]


class TestBinanceSchemaValidation:
    """Validate response schemas for Binance public endpoints."""

    BASE_URL = "https://api.binance.com/api/v3"

    def test_exchangeinfo_schema(self):
        response = requests.get(f"{self.BASE_URL}/exchangeInfo", timeout=30)
        assert response.status_code == 200
        data = BinanceExchangeInfo(**response.json())
        assert len(data.symbols) > 0

    def test_depth_schema(self):
        response = requests.get(
            f"{self.BASE_URL}/depth",
            params={"symbol": "BTCUSDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        data = BinanceOrderBook(**response.json())
        assert len(data.bids) <= 5
        assert len(data.asks) <= 5
        assert all(len(level) == 2 for level in data.bids)
        assert all(len(level) == 2 for level in data.asks)

    def test_ticker_24hr_schema(self):
        response = requests.get(
            f"{self.BASE_URL}/ticker/24hr",
            params={"symbol": "BTCUSDT"},
            timeout=30,
        )
        assert response.status_code == 200
        data = BinanceTicker24hr(**response.json())
        assert data.symbol == "BTCUSDT"

    def test_trades_schema(self):
        response = requests.get(
            f"{self.BASE_URL}/trades",
            params={"symbol": "BTCUSDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        trades = [BinanceTrade(**item) for item in response.json()]
        assert len(trades) <= 5


class TestBinanceErrorHandling:
    """Edge cases and error responses for Binance public endpoints."""

    BASE_URL = "https://api.binance.com/api/v3"

    def test_unknown_symbol_returns_400(self):
        response = requests.get(
            f"{self.BASE_URL}/ticker/24hr",
            params={"symbol": "UNKNOWN_SYMBOL"},
            timeout=30,
        )
        assert response.status_code in (400, 404)

    def test_depth_without_symbol_returns_400(self):
        response = requests.get(f"{self.BASE_URL}/depth", timeout=30)
        assert response.status_code in (400, 404)

    def test_invalid_limit_is_clamped_or_rejected(self):
        """Binance ignores invalid limits and returns the default book size."""
        response = requests.get(
            f"{self.BASE_URL}/depth",
            params={"symbol": "BTCUSDT", "limit": 9999},
            timeout=30,
        )
        assert response.status_code == 200
        data = BinanceOrderBook(**response.json())
        assert len(data.bids) <= 1000
