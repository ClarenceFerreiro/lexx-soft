# LexxSoft API Tests

[![Public API Tests](https://github.com/ClarenceFerreiro/lexx-soft/actions/workflows/public-tests.yml/badge.svg)](https://github.com/ClarenceFerreiro/lexx-soft/actions/workflows/public-tests.yml)

Black-box API test suite for the LexxSoft trading platform (`https://lexx-trade.com`).
Written after leaving the company, so all endpoints are discovered by inspecting
the production web app and confirming behaviour against live APIs.

## What is tested

- **Public market data upstreams** that the LexxSoft terminal consumes directly:
  - **OKX** (`/api/v5/market/*`) — smoke and schema tests, CI-friendly
  - **Binance Spot** (`/api/v3/*`) and **USDⓈ-M Futures** (`/fapi/v1/*`) — smoke and schema tests,
    skipped in GitHub Actions because Binance blocks GitHub Cloud IP ranges
- **LexxSoft backend smoke tests** that require no credentials:
  - `/api/auth/login` existence and reCAPTCHA behaviour
- **WebSocket streams** used by the LexxSoft terminal:
  - Binance Spot (`wss://stream.binance.com`)
  - Binance Futures (`wss://fstream.binance.com`) — connection only, often no data from some regions
  - OKX (`wss://ws.okx.com`)
- **Authenticated endpoints** with a manually-obtained access token:
  - token validity (`/api/user/me`, `/api/user/profile`)
  - RBAC for free-tier accounts (`403 Not supported role` on premium paths)
  - private bot/order/portfolio/settings endpoints discovered in the terminal bundle (`/api/private/*`)
  - security observation: some `/api/private/*` GET endpoints are reachable without auth

## Quick start

```bash
cd lexxsoft-api-tests
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest tests/public/ -v
```

## Run by marker

```bash
# CI-friendly public tests (OKX + LexxSoft auth)
pytest -m "public and not binance" -v

# Local full run including Binance
pytest -m public -v

# WebSocket streams
pytest -m websocket -v

# Rate-limit observation tests
pytest -m rate_limit -v

# Authenticated tests (requires LEXX_ACCESS_TOKEN in .env)
pytest tests/auth/ -v

# Smoke / schema filters
pytest -m smoke -v
pytest -m schema -v
```

## HTML report

```bash
pytest tests/public/ tests/auth/ --html=reports/report.html --self-contained-html
```

Open `reports/report.html` in a browser. GitHub Actions also uploads the report
as an artifact named `pytest-report-py<version>`.

## Authenticated tests

LexxSoft login is protected by reCAPTCHA, so automated login is not supported.
Instead, provide a manually extracted Bearer token:

1. Log in to `https://lexx-trade.com/terminal/login` in your browser.
2. Open DevTools → Network → Fetch/XHR.
3. Find any request to `api.lexx-trade.com` and copy the `Authorization: Bearer ***` header value.
4. Paste the token into `.env` as `LEXX_ACCESS_TOKEN=***`.
5. Run: `pytest tests/auth/ -v`

If the account has a free role, premium endpoints return `403 Not supported role`.
The auth smoke tests document this behaviour.

## CI

GitHub Actions runs public tests that do **not** hit Binance on every push and PR.
Binance tests are marked with `pytest.mark.binance` and excluded from CI because
Binance returns HTTP 451 for GitHub Cloud runners.

## Project structure

```
lexxsoft-api-tests/
├── src/lexxsoft_client/          # Thin API client
├── tests/
│   ├── public/
│   │   ├── schemas.py              # Pydantic response models
│   │   ├── test_binance_smoke.py   # Binance spot/futures smoke tests
│   │   ├── test_binance_schema.py  # Binance schema/edge-case tests
│   │   ├── test_okx_smoke.py       # OKX + LexxSoft auth smoke tests
│   │   ├── test_okx_schema.py      # OKX schema/edge-case tests
│   │   └── test_rate_limits.py     # Rate-limit observation tests
│   ├── auth/
│   │   ├── test_auth_smoke.py     # Authenticated token/RBAC tests
│   │   └── test_private_endpoints.py # Private bot/order/portfolio/settings tests
│   ├── websocket/
│   │   └── test_public_websocket.py # Public exchange WebSocket tests
│   ├── bots/                      # Trading bot tests (reserved)
│   └── conftest.py                # pytest fixtures
├── .github/workflows/            # CI + HTML report artifacts
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Methodology

This is a black-box test suite. Endpoints were discovered by inspecting the
production LexxSoft terminal, and assertions were validated against live
responses from upstream exchanges and the LexxSoft backend.
