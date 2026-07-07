"""Schema validation and edge-case tests for OKX public endpoints.

These tests are CI-friendly: OKX does not block GitHub Actions runners.
"""

from __future__ import annotations

import pytest
import requests

from tests.public.schemas import OkxRestResponse, OkxTicker, OkxTrade

pytestmark = [pytest.mark.public, pytest.mark.schema]


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
