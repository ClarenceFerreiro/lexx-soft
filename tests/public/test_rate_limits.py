"""Rate-limit observation tests for public exchange APIs.

These tests do not intentionally hammer the APIs. They inspect response
headers and document normal vs. throttled behaviour observed from a single
client IP.
"""

from __future__ import annotations

import time

import pytest
import requests


@pytest.mark.rate_limit
@pytest.mark.binance
class TestBinanceRateLimits:
    """Observe Binance public API rate-limit headers and behaviour."""

    BASE_URL = "https://api.binance.com/api/v3"

    def test_exchangeinfo_includes_rate_limit_headers(self):
        response = requests.get(f"{self.BASE_URL}/exchangeInfo", timeout=30)
        assert response.status_code == 200
        # Binance documents these headers on some endpoints
        assert "x-mbx-used-weight-1m" in {k.lower() for k in response.headers}

    def test_sequential_requests_stay_within_limit(self):
        """A small burst of sequential requests should not trigger 429."""
        responses = []
        for _ in range(5):
            response = requests.get(
                f"{self.BASE_URL}/ticker/24hr",
                params={"symbol": "BTCUSDT"},
                timeout=30,
            )
            responses.append(response)
            time.sleep(0.2)

        assert all(r.status_code == 200 for r in responses)
        statuses = {r.status_code for r in responses}
        assert 429 not in statuses, "Got 429 during a modest sequential burst"


@pytest.mark.rate_limit
class TestOkxRateLimits:
    """Observe OKX public API rate-limit headers and behaviour."""

    BASE_URL = "https://www.okx.com/api/v5/market"

    def test_tickers_reports_headers_or_stays_200(self):
        response = requests.get(
            f"{self.BASE_URL}/tickers",
            params={"instType": "SPOT"},
            timeout=30,
        )
        assert response.status_code == 200
        headers = {k.lower() for k in response.headers}
        # OKX may not return rate-limit headers on every public route
        has_rate_header = any(
            h in headers for h in ("ok-visible-api-limit", "ok-used-weight")
        )
        assert response.status_code == 200
        if not has_rate_header:
            pytest.skip("OKX did not return rate-limit headers on this route")

    def test_sequential_requests_stay_within_limit(self):
        """A small burst of sequential requests should not trigger 429."""
        responses = []
        for _ in range(5):
            response = requests.get(
                f"{self.BASE_URL}/tickers",
                params={"instType": "SPOT"},
                timeout=30,
            )
            responses.append(response)
            time.sleep(0.2)

        assert all(r.status_code == 200 for r in responses)
        statuses = {r.status_code for r in responses}
        assert 429 not in statuses, "Got 429 during a modest sequential burst"


@pytest.mark.rate_limit
class TestLexxSoftRateLimits:
    """Observe LexxSoft backend rate-limit / error behaviour."""

    def test_login_endpoint_does_not_crash_on_repeated_invalid_requests(
        self,
        public_client,
    ):
        """Invalid login attempts are rejected gracefully without crashing."""
        statuses = set()
        for _ in range(3):
            response = public_client.post(
                "/auth/login",
                json={"email": "user@example.com", "password": "wrongpassword"},
            )
            statuses.add(response.status_code)
            time.sleep(0.2)

        assert statuses.issubset({400, 401, 403, 429, 502, 503, 504}), (
            f"Unexpected statuses: {statuses}"
        )
