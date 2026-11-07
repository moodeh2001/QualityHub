# Python reliability safeguards

Current scope: Python/pytest automation and manual Postman testing. Removed command-line Postman and performance tooling are not current deliverables.

## Strict execution

Selected skipped tests make an otherwise successful pytest run exit 1. Setup failures also fail. Explicit deselection creates a limited run; --allow-skips is only for exploratory partial execution and is not enabled in CI. Every run manifest records completion status and whether partial mode was allowed.

QH_CREATE_SANDBOX=1 plus a nonempty QH_SANDBOX_KEY is rejected before network access. Empty created keys fail setup. Python HTTP calls disable redirects and validate request construction before sending; unauthorized writes are blocked by the local-root safety gate.

## Reports

Each invocation creates a unique pytest-* directory under reports/ or QH_REPORT_ROOT. The redaction regression resolves and creates the configured report root before allocating its child test workspace. Default and custom-root clean-source checks verify this without relying on historical reports.

Failure details, captured output, extra attachments and parameter identifiers are withheld from report records. The fake-token regression checks terminal/JUnit/HTML output and strict skip exit codes. Earlier Python reports remain untouched as historical evidence. Reports and verification snapshots must remain outside published source.

## Assertions and CI

Pagination checks exact expected page size and disjoint first/second pages. The database sandbox check requires the cart to exist exactly once in the intended sandbox.

Compose uses loopback host bindings in source. Running containers need recreation to apply them. Fork PRs execute secret-free Python regressions; full QA Shop integration is a separate trusted job requiring configured secrets. Only current-run report roots are uploaded.

Fresh current results are in [PROJECT_REPORT.md](PROJECT_REPORT.md). Remote CI and database constraint-rejection writes remain unverified. UI automation is out of scope.
