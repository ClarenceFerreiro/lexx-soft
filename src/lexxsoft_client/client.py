"""LexxSoft API client used by black-box tests."""

from __future__ import annotations

from typing import Any, Self

import requests

DEFAULT_BASE_URL = "https://api.lexx-trade.com/api"
DEFAULT_BASE_URL_2 = "https://api2.lexx-trade.com/api"
TIMEOUT = 30


class _NoNetrcAuth(requests.auth.AuthBase):
    """Prevent requests from silently applying credentials from ``.netrc``."""

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        return request


class LexxClient:
    """Thin wrapper over requests for LexxSoft public and authenticated APIs."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        email: str | None = None,
        password: str | None = None,
        totp_code: str | None = None,
        access_token: str | None = None,
        timeout: int = TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        # Preserve proxy/CA environment support while disabling implicit .netrc auth.
        self.session.auth = _NoNetrcAuth()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "lexxsoft-api-tests/0.2.0",
            }
        )
        self.email = email
        self.password = password
        self.totp_code = totp_code
        self.access_token = access_token
        if self.access_token:
            self.session.headers.update(self.auth_headers())

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def get(
        self, path: str, params: dict[str, Any] | None = None, **kwargs: Any
    ) -> requests.Response:
        return self.session.get(self._url(path), params=params, timeout=self.timeout, **kwargs)

    def post(
        self, path: str, json: dict[str, Any] | None = None, **kwargs: Any
    ) -> requests.Response:
        return self.session.post(self._url(path), json=json, timeout=self.timeout, **kwargs)

    def auth_headers(self) -> dict[str, str]:
        if not self.access_token:
            raise RuntimeError("Not authenticated. Call login() first.")
        return {"Authorization": f"Bearer {self.access_token}"}

    def login(self) -> requests.Response:
        if not self.email or not self.password:
            raise RuntimeError("Email and password are required for login.")
        payload: dict[str, Any] = {
            "email": self.email,
            "password": self.password,
        }
        if self.totp_code:
            payload["totp_code"] = self.totp_code
        response = self.post("/auth/login", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token") or data.get("token")
            if self.access_token:
                self.session.headers.update(self.auth_headers())
        return response

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.session.close()
