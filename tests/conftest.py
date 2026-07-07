"""Shared fixtures for LexxSoft API tests."""

from __future__ import annotations

import pytest

from lexxsoft_client import LexxClient


@pytest.fixture(scope="session")
def public_client():
    """Unauthenticated client pointing to the primary API host."""
    with LexxClient() as client:
        yield client


@pytest.fixture(scope="session")
def public_client_2():
    """Unauthenticated client pointing to the secondary API host."""
    with LexxClient(base_url="https://api2.lexx-trade.com/api") as client:
        yield client


@pytest.fixture(scope="session")
def symbol():
    """A liquid pair to use in market-data tests."""
    return "BTCUSDT"
