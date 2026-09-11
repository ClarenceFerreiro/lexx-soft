"""Shared fixtures for LexxSoft API tests."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from lexxsoft_client import LexxClient

load_dotenv()


@pytest.fixture(scope="session")
def public_client():
    """Always-unauthenticated client pointing to the primary API host."""
    with LexxClient() as client:
        yield client


@pytest.fixture(scope="session")
def auth_client():
    """Authenticated client created only from an explicitly supplied test token."""
    token = os.getenv("LEXX_ACCESS_TOKEN")
    if not token:
        pytest.skip("LEXX_ACCESS_TOKEN is not set")
    with LexxClient(access_token=token) as client:
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
