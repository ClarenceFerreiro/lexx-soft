# LexxSoft API Tests

Black-box API test suite for the LexxSoft trading platform (`https://lexx-trade.com`).

## What is tested

- **Public market data upstreams** that the LexxSoft terminal consumes directly:
  - Binance Spot (`/api/v3/*`) and USDⓈ-M Futures (`/fapi/v1/*`)
  - OKX (`/api/v5/market/*`)
- **LexxSoft backend smoke tests** that require no credentials:
  - `/api/auth/login` existence and recaptcha behaviour
- **Authenticated endpoints** will be added later (profile, portfolio, bots, orders).

## Quick start

```bash
cd lexxsoft-api-tests
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest tests/public/ -v
```

## Run by marker

```bash
# Smoke tests only
pytest -m smoke -v

# Schema validation tests only
pytest -m schema -v

# Public tests only
pytest -m public -v
```

## Authenticated tests

1. Copy `.env.example` to `.env`
2. Fill in `LEXX_EMAIL`, `LEXX_PASSWORD`, and optionally `LEXX_TOTP_CODE`
3. Run: `pytest tests/auth/ -v`

## CI

GitHub Actions workflow runs public tests on every push and PR.

## Project structure

```
lexxsoft-api-tests/
├── src/lexxsoft_client/    # Thin API client
├── tests/
│   ├── public/              # Public / upstream tests
│   ├── auth/                # Authenticated tests (coming soon)
│   └── bots/                # Trading bot tests (coming soon)
├── config/                  # Environment / fixture configs
├── .github/workflows/       # CI
├── pyproject.toml
└── requirements.txt
```

## Methodology

This is a black-box test suite written after leaving LexxSoft. All endpoints
were discovered by inspecting the production web application and confirming
behaviour against live APIs.
