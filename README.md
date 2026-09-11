# LexxSoft API tests

[![Quality](https://github.com/ClarenceFerreiro/lexx-soft/actions/workflows/quality.yml/badge.svg)](https://github.com/ClarenceFerreiro/lexx-soft/actions/workflows/quality.yml)
[![Live API Checks](https://github.com/ClarenceFerreiro/lexx-soft/actions/workflows/public-tests.yml/badge.svg)](https://github.com/ClarenceFerreiro/lexx-soft/actions/workflows/public-tests.yml)

A small black-box test suite for the publicly observable API contracts of the
LexxSoft trading platform and its market-data providers.

This is an independent portfolio project created after my work on the product.
It uses public behaviour and a user-controlled test account; it contains no
company source code, internal documentation, credentials, or customer data.

## What is covered

| Area                       | Checks                                                                            | Where it runs    |
| -------------------------- | --------------------------------------------------------------------------------- | ---------------- |
| LexxSoft backend           | Login error contracts and anonymous access boundaries                             | Live CI          |
| OKX REST                   | Smoke, schema, error handling, modest rate-limit observations                     | Live CI          |
| OKX WebSocket              | Connection and subscription handshake                                             | Live CI          |
| Binance Spot/Futures       | REST smoke, schemas, edge cases, WebSocket                                        | Local            |
| Authenticated LexxSoft API | Endpoint behaviour, RBAC, bot/order/portfolio/settings routes                     | Local with token |
| API client                 | URL construction, explicit Bearer headers, query parameters, credential isolation | Deterministic CI |

The test design and result semantics are described in
[`docs/TEST_STRATEGY.md`](docs/TEST_STRATEGY.md).

## Why there are two workflows

- **Quality** runs `ruff` and unit tests with coverage. It has no network dependency.
- **Live API Checks** exercises public REST/WebSocket contracts and uploads an HTML report.

A green live badge covers only the CI-compatible subset. Binance checks are excluded
because Binance can block GitHub-hosted runner IPs, and authenticated checks are local
because access tokens are not stored in this public repository.

## Quick start

```bash
git clone https://github.com/ClarenceFerreiro/lexx-soft.git
cd lexx-soft
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m pytest tests/unit/ -v
```

Linux/macOS:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest tests/unit/ -v
```

## Test commands

```bash
# Deterministic checks: no credentials or network
ruff check .
pytest tests/unit/ --cov=lexxsoft_client --cov-report=term-missing

# CI-compatible live checks
pytest tests/public/ tests/websocket/ tests/auth/ \
  -m "not binance and (not auth or anonymous)" -v

# Full public REST suite, including Binance
pytest -m public -v

# WebSocket checks
pytest -m websocket -v

# Authenticated checks; requires LEXX_ACCESS_TOKEN
pytest -m "auth and not anonymous" -v

# Generate a self-contained report
pytest --html=reports/report.html --self-contained-html
```

## Authenticated checks

LexxSoft login is protected by reCAPTCHA. The suite does not bypass it. To run
private checks, log in manually with a user-controlled account, copy the temporary
Bearer token from a request in browser DevTools, and place it in a local `.env`:

```dotenv
LEXX_ACCESS_TOKEN=replace-with-a-short-lived-token
```

Then run:

```bash
pytest -m "auth and not anonymous" -v
```

The `.env` file is excluded from Git. Authenticated checks may be skipped or marked
`xfail` when a prerequisite is absent or a documented backend defect is reproduced.

## Project structure

```text
lexx-soft/
├── .github/workflows/
│   ├── quality.yml                # deterministic lint and unit tests
│   └── public-tests.yml           # live CI-compatible API checks
├── docs/
│   └── TEST_STRATEGY.md           # scope, layers, semantics, safety boundaries
├── src/lexxsoft_client/
│   └── client.py                  # thin requests-based API client
├── tests/
│   ├── unit/                      # deterministic client tests
│   ├── public/                    # REST smoke, schema, and rate-limit checks
│   ├── auth/                      # anonymous and token-based access checks
│   └── websocket/                 # public stream checks
├── .env.example
└── pyproject.toml
```

## Current limitations

- The project validates externally observable contracts, not internal implementation.
- Live checks can fail because of upstream changes, regional restrictions, or network issues.
- Authenticated coverage is limited by the permissions and state of the test account.
- Binance tests are not part of GitHub-hosted CI.

These constraints are kept explicit so a passing badge is not presented as broader
coverage than the workflow actually provides.
