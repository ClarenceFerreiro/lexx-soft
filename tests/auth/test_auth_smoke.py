"""Authenticated endpoint tests for LexxSoft backend.

These tests require a valid access token. Set LEXX_ACCESS_TOKEN in .env.
The token can be obtained from the browser after manual login (see README).
"""

from __future__ import annotations

import os

import pytest

from lexxsoft_client import LexxClient

pytestmark = [pytest.mark.auth, pytest.mark.smoke]


@pytest.fixture(scope="module")
def auth_client():
    token = os.getenv("LEXX_ACCESS_TOKEN")
    if not token:
        pytest.skip("LEXX_ACCESS_TOKEN is not set")
    with LexxClient(access_token=token) as client:
        yield client


class TestAuthTokenValidity:
    """Verify that the provided access token is accepted by the backend."""

    def test_user_me_is_authenticated(self, auth_client):
        """A valid token should reach the endpoint (role check is separate)."""
        response = auth_client.get("/api/user/me")
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            data = response.json()
            assert "id" in data or "email" in data or "role" in data
        else:
            data = response.json()
            assert data.get("status") == "failed"
            assert "role" in data.get("msg", "").lower()

    def test_user_profile_is_authenticated(self, auth_client):
        response = auth_client.get("/api/user/profile")
        assert response.status_code in (200, 403)


class TestFreeRoleRestrictions:
    """Document RBAC restrictions for the free role."""

    @pytest.mark.parametrize(
        "path",
        [
            "/api/referrals",
            "/api/statistics",
            "/api/billing",
            "/api/api-keys",
        ],
    )
    def test_premium_endpoints_require_paid_role(self, auth_client, path):
        """Free-role accounts should be rejected from premium endpoints."""
        response = auth_client.get(path)
        assert response.status_code in (403, 404)
        if response.status_code == 403:
            data = response.json()
            assert data.get("status") == "failed"


class TestAuthenticatedVsAnonymous:
    """Verify that authenticated requests differ from anonymous ones."""

    def test_user_me_requires_auth(self, public_client):
        """Anonymous requests to user endpoints should be rejected."""
        response = public_client.get("/api/user/me")
        assert response.status_code in (401, 403)
