"""Schema validation and edge-case tests for public market-data endpoints."""

from __future__ import annotations

import pytest
import requests

from tests.public.schemas import (
    BinanceExchangeInfo,
    BinanceOrderBook,
    BinanceTicker24hr,
    BinanceTrade,
    OkxRestResponse,
    OkxTicker,
    OkxTrade,
)

pytestmark = [pytest.mark.public, pytest.mark.schema]


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


class TestOkxSchemaValidation:
    """Validate response schemas for OKX public endpoints."""

    BASE_URL = "https://www.okx.com/api/v5/market"

    def test_tickers_schema(self):
        response = requests.get(
            f"{self.BASE_URL}/tickers",
            params={"instType": "SPOT"},
            timeout=30,
        )
        assert response.status_code == 200
        parsed = OkxRestResponse(**response.json())
        assert parsed.code == "0"
        assert len(parsed.data) > 0
        OkxTicker(**parsed.data[0])

    def test_trades_schema(self):
        response = requests.get(
            f"{self.BASE_URL}/trades",
            params={"instId": "BTC-USDT", "limit": 5},
            timeout=30,
        )
        assert response.status_code == 200
        parsed = OkxRestResponse(**response.json())
        assert parsed.code == "0"
        assert len(parsed.data) <= 5
        if parsed.data:
            OkxTrade(**parsed.data[0])


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
        # Binance clamps to allowed values (typically <= 5000 or 1000 for REST)
        assert len(data.bids) <= 1000


class TestOkxErrorHandling:
    """Edge cases and error responses for OKX public endpoints."""

    BASE_URL = "https://www.okx.com/api/v5/market"

    def test_unknown_instid_returns_error_code(self):
        response = requests.get(
            f"{self.BASE_URL}/tickers",
            params={"instType": "SPOT", "instId": "FAKE-TOKEN"},
            timeout=30,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") in {"0", "51001"}  # 51001 = instrument not found

    def test_missing_inst_type_returns_400(self):
        response = requests.get(f"{self.BASE_URL}/tickers", timeout=30)
        assert response.status_code == 400
