# QualityHub — Backend QA Automation

QualityHub tests the existing LearnQA QA Shop API and PostgreSQL database. The current GitHub version uses Python automation and a preserved Postman collection for manual API testing.

**UI automation is OUT OF SCOPE — No reliable frontend is available.** Performance testing and command-line Postman automation are outside the final scope.

## Verified results — 2026-11-08

The final full run executed **58 pytest cases: 58 passed, 0 failures, 0 errors, 0 skipped**. This consists of 32 API cases, 11 database/catalog cases, 3 API/database integration cases and 12 Python regression/configuration cases.

Evidence: [HTML report](reports/final-python/pytest-xpmyveh2/pytest.html), [JUnit](reports/final-python/pytest-xpmyveh2/junit.xml), [run manifest](reports/final-python/pytest-xpmyveh2/run.json). These are real, ignored local artifacts and will not be included in GitHub source. GitHub Actions publishes current-run artifacts after an actual workflow execution.

Both clean source snapshots started without reports/. Default reporting and custom QH_REPORT_ROOT runs each passed all 12 regressions. The custom run created no project-local reports directory. See [project report](docs/PROJECT_REPORT.md) for exact evidence paths and limitations. The existing virtual environment supplied dependencies; this was not a clean machine installation.

## Scope and technologies

- Python 3.13, pytest, requests, psycopg 3, pytest-html and JUnit XML.
- PostgreSQL data audits, constraint metadata checks and API-to-database reconciliation.
- Docker Compose with digest-pinned QA Shop images.
- GitHub Actions: secret-free Python regressions for fork PRs; full integration for trusted events.
- Existing Postman collection: 21 requests, preserved IDs/order/variables/scripts, manual execution.

## Project structure

```text
clients/api.py                         HTTP client, destination/redirect safety, money assertions
tests/conftest.py                      isolation, read-only DB access, strict/sanitized reporting
tests/api/test_api.py                  API behavior and negative/boundary scenarios
tests/database/test_integrity.py       SQL audits and constraint metadata
tests/integration/test_cart_database.py API writes reconciled with PostgreSQL
tests/unit/                           Python safety, reporting and configuration regressions
sql/                                  DB-TC-001 through DB-TC-012
postman/                              unchanged collection and manual instructions
tools/verify_clean_source.py           isolated source-only regression verification
.github/workflows/backend-qa.yml       Python CI and current-run artifacts
docs/                                 evidence, roadmap, scope and known limits
```

Legacy empty pages/ and tests/ui/ placeholders are unused; they do not represent UI features.

## Setup

Use this repository. For a clean checkout, install Python 3.13 and create a virtual environment:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

No Node or performance tooling is required.

Application server root: `http://localhost:4000`; API prefix: `/api/v1`; health: `/health`. The application serves its bundled contract at `/api/v1/openapi.yaml`.

Configure private process environment variables using [.env.example](.env.example) as a reference. It contains placeholders and is not automatically loaded by Python. Compose can load an ignored private .env file, but does not export it to pytest.

- QH_DATABASE_URL: API database connection using db:5432.
- QH_DATABASE_DSN: pytest database connection using localhost:5433.
- QH_JWT_SECRET: private API signing secret.
- Credentials must match the existing vendor image/volume; never change persistent database credentials merely to make tests pass.

```powershell
docker compose up -d --wait --wait-timeout 120
```

Compose specifies host bindings 127.0.0.1:4000 and 127.0.0.1:5433. Existing containers were not recreated during this delivery; their earlier bindings do not change until recreation.

## Run Python tests

```powershell
# Offline fake-response/configuration regressions; no secrets needed
.venv/Scripts/python.exe -m pytest tests/unit

# Explicit public API subset; no mutation authorization
.venv/Scripts/python.exe -m pytest tests/api -m "not writes"

# Read-only DB audits after setting QH_DATABASE_DSN privately
.venv/Scripts/python.exe -m pytest tests/database

# Full suite: fresh private sandbox, with no existing QH_SANDBOX_KEY set
$env:QH_ALLOW_WRITES='1'
$env:QH_CREATE_SANDBOX='1'
.venv/Scripts/python.exe -m pytest

# Source-only verification, default and custom reporting
.venv/Scripts/python.exe tools/verify_clean_source.py
```

Set QH_DATABASE_DSN privately before the full run. QH_CREATE_SANDBOX=1 plus a nonempty QH_SANDBOX_KEY is rejected. Credentials for new disposable sandboxes stay in memory. For an existing dedicated disposable sandbox, leave QH_CREATE_SANDBOX unset and supply its key/login credentials privately.

Independent tests create fresh carts; repeated addition is an explicit workflow. Test data remains in disposable sandboxes until application expiry. There are no reset/delete cleanup operations. Database connections are read-only. API writes require the exact authorized local root, and automatic redirects are disabled.

Selected skipped tests cause a failing exit by default. Missing setup is not success. `--allow-skips` is for explicitly exploratory partial runs and is not used in CI.

## Reporting and publication safety

Each invocation creates a unique pytest-* directory under reports/ or QH_REPORT_ROOT, with junit.xml, pytest.html and run.json. Raw assertion values, captured output and parameter identifiers are withheld from reports. The redaction regression also respects a custom report root.

Python reports from previous runs are retained locally as historical evidence. Source publication must exclude reports/, .verification/, .venv/, private .env files and exported Postman environments; .gitignore covers these paths. Set a custom report root outside the source tree, or add its path to ignore rules.

## Manual Postman testing

Open the existing collection in Postman and follow [postman/README.md](postman/README.md). This scope change did not modify the collection file or run a new manual Postman session. Historical manual results are not presented as fresh verification.

## GitHub Actions

The regression job runs Python tests without repository secrets, including fork PRs. Trusted events additionally start runner-local Compose services, wait for readiness and run full pytest.

The integration job requires GitHub secrets QH_DATABASE_URL, QH_DATABASE_DSN and QH_JWT_SECRET. A fork-only regression pass is not full integration verification. Each job uploads only its current-run report root. No workflow was pushed or remotely executed in this delivery.

## Known limits

Clean source regression runs were verified using installed dependencies, not a newly provisioned machine. Remote CI/image pull, actual invalid-write constraint enforcement, expired-sandbox behavior and exact shipping-boundary fixtures remain unverified. The historical frontend Service Worker bypass issue remains unresolved and is outside this backend scope.

No commits or pushes were made. See [database cases](docs/DATABASE_TESTS.md), [progress](docs/PROGRESS.md) and [roadmap](docs/ROADMAP.md).
