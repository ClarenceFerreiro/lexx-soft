# Test strategy

## Purpose

This repository is a portfolio implementation of black-box testing for a trading
web application and the public exchange APIs it depends on. It is not an internal
LexxSoft test repository and contains no proprietary source code, credentials, or
customer data.

## Test layers

| Layer            | Purpose                                                               | Network |       Default CI |
| ---------------- | --------------------------------------------------------------------- | ------: | ---------------: |
| Unit             | Verify URL construction, authentication headers, and client behaviour |      No |              Yes |
| Public REST      | Check availability, response shape, and selected error contracts      |     Yes |              Yes |
| WebSocket        | Verify connection and subscription handshakes                         |     Yes |         OKX only |
| Anonymous access | Check authentication boundaries without credentials                   |     Yes |              Yes |
| Authenticated    | Observe endpoint behaviour, RBAC, and private endpoint contracts      |     Yes |       Local only |
| Rate limit       | Observe headers and a small sequential request series                 |     Yes | Non-Binance only |

## Why CI is split

The `Quality` workflow is deterministic: it runs lint and unit tests without
network access. Its badge answers whether the repository itself is healthy.

The `Live API Checks` workflow depends on third-party services and reports whether
the currently observable contracts still match the tests. A failure can indicate
a product regression, a changed external API, regional blocking, or a transient
network issue, so it should be investigated rather than treated as an automatic
release blocker.

## Result semantics

- `passed`: the observed response satisfied the documented contract;
- `failed`: the response contradicted the contract or the test itself broke;
- `skipped`: a prerequisite such as `LEXX_ACCESS_TOKEN` or a rate-limit header was absent;
- `xfailed`: a known defect in an authenticated, local-only check was reproduced;
- `deselected`: the test was intentionally excluded by a marker expression.

HTTP 500 and anonymous access to a private route fail the live workflow. Security
boundaries are blocking invariants, not observations that can be softened into a
green build.

## Safety boundaries

- Public checks use a small number of sequential requests.
- Tests do not attempt denial-of-service, credential guessing, or CAPTCHA bypass.
- State-changing private tests require a manually supplied token and use invalid or
  empty payloads; they are not enabled in public CI.
- The authenticated fixture loads a token from `.env`, which is excluded from Git,
  and passes it explicitly to the client. Public clients ignore token environment
  variables and `.netrc` credentials while retaining proxy and CA environment support.
- Any unexpected exposure of data should be handled through responsible disclosure,
  not published as sample output in this repository.

## Known constraints

- Binance can return HTTP 451 from GitHub-hosted runners, so Binance checks run locally.
- Authenticated tests require a short-lived token obtained from a user-controlled account.
- Live tests are intentionally less deterministic than unit tests.
- The backend uses nested paths such as `/api/api/user/me`; unit tests document this
  observed routing so it is not accidentally "corrected" to a non-existent endpoint.
