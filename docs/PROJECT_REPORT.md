# QualityHub final backend project report

**Delivery date: 2026-11-08.** Current automation is Python/pytest. Postman remains for manual API testing. Newman and JMeter have been removed; earlier results for removed tools are not part of this delivery's counts.

## What remains

Reusable requests client, controlled private-sandbox fixtures, API contract checks, read-only psycopg data audits, API/database reconciliation, 12 SQL cases, strict skipped-test handling, redirect safeguards, sanitized reports, Docker Compose and Python-only GitHub Actions.

The existing Postman collection is byte-for-byte preserved: 21 requests, UID 58176932-73c58a92-0a7e-4f3b-99a9-16f1be08f69e. No new manual run or remote sync was necessary because the collection was not changed.

## Fresh executed evidence

| Execution | Command / method | Exact result |
| --- | --- | --- |
| Existing project regressions | .venv/Scripts/python.exe -m pytest tests/unit -p no:cacheprovider -q | 12 passed |
| Clean source, default root | tools/verify_clean_source.py, first source snapshot | 12 passed |
| Clean source, custom root | Same tool, second snapshot with external QH_REPORT_ROOT | 12 passed; no source-local reports/ created |
| Full local backend suite | .venv/Scripts/python.exe -m pytest -p no:cacheprovider -q, authorized local sandbox and read-only DB | 58 passed, zero failures/errors/skips |

Full-suite JUnit breakdown: test_api 32, test_integrity 11, test_cart_database 3, test_configuration 2, test_regressions 7, test_write_safety 3. The full manifest records PASS, exitCode 0, hadSkippedTests false and partialRunAllowed false.

Evidence directories:
- Full suite: reports/final-python/pytest-xpmyveh2/.
- Existing-root regressions: reports/pytest-_fc49_8j/.
- Clean default: .verification/clean-ee3ccfd061b14295ae3e6f22b736354c/default/reports/pytest-adzpm06x/.
- Clean custom: .verification/clean-ee3ccfd061b14295ae3e6f22b736354c/custom-evidence/pytest-cx4xogij/.
- Clean-copy manifest: .verification/clean-ee3ccfd061b14295ae3e6f22b736354c/verification.json.

Each pytest directory contains junit.xml, pytest.html and run.json. Generated reports and snapshots are ignored and excluded from GitHub source. Earlier Python reports remain historical evidence. Copies contain source only: no repository metadata, virtual environment, installed npm tree, historical reports or private .env files. The existing interpreter/dependencies were reused.

## Verification scope

API checks execute health, products, pagination, login/authorization, cart creation/retrieval/addition/repetition, invalid inputs, inventory conflict, pricing and sandbox isolation. Integration tests compare generated cart IDs, quantities, snapshots and totals against PostgreSQL in read-only connections.

Database tests validate existing records plus selected catalog definitions. They do not prove invalid writes are rejected. SQL cases 004/005/011 receive captured fresh cart JSON through safe query parameters.

The redaction regression creates its temporary child runs beneath the configured report root. It verifies failure/skip exit handling and absence of a fake token from terminal/JUnit/HTML output. The two configuration checks retain Compose port binding and fork-safe Python CI coverage. The removed JMeter configuration case is not counted.

## CI and publication

The regression job runs without secrets for fork PRs. The full integration job runs on trusted events after regressions, requires QH_DATABASE_URL/QH_DATABASE_DSN/QH_JWT_SECRET, starts runner-local services, waits for health, runs pytest and uploads only its current-run report root. No Node installation or npm steps remain.

No remote workflow execution, image pull on a clean runner, or clean dependency install was verified. Existing containers were not recreated, so no claim is made that their live port exposure changed. Scope excludes UI automation and performance testing.

Private credentials were not written into source. No commits or pushes were performed. Final source diff inventory is available through the handoff and current Git status; the project was already untracked before these changes.

## CV facts supported by current execution

- Implemented and executed 58 Python backend QA test cases covering HTTP API, PostgreSQL audits, integration and safety regressions.
- Reconciled cart API data with read-only PostgreSQL queries and Decimal monetary checks.
- Used disposable local sandboxes and fresh carts to isolate mutation scenarios.
- Implemented strict completion, no-redirect HTTP handling and sanitized JUnit/HTML reporting.
- Prepared Python CI with fork-safe regression and trusted integration jobs; remote execution remains unverified.

## Remaining work

Observe a real GitHub Actions run after secret configuration; verify a fresh dependency/image setup; test exact shipping boundaries and sandbox expiration; validate actual database write-rejection behavior in a disposable database. Manual Postman verification of the preserved collection is a separate user operation.
