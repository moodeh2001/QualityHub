# QualityHub progress — final backend scope

## Current delivery: 2026-11-08

Removed Newman runner/regressions/npm configuration and JMeter plan/scripts/docs/configuration test. Removed only their generated reports; existing Python reports remain preserved locally. The existing Postman collection is unchanged, including request IDs/order/variables/scripts.

Fixed the report-redaction regression to create its workspace under QH_REPORT_ROOT, creating the parent when necessary. It no longer assumes project-local reports/ exists. Python CI retains fork-safe secret-free regressions, trusted-event full integration and current-run uploads.

Fresh full execution: **58 passed, zero failures/errors/skips**: 32 API, 11 DB, 3 integration and 12 regression/configuration cases. All writes used newly created local private sandboxes; DB connections were read-only.

Default and custom-root clean source snapshots each passed 12 regressions. Both began without reports/; custom-root execution created no reports/ in its source snapshot. These checks used the existing virtual environment, not a fresh dependency install.

Reports and exact commands are recorded in PROJECT_REPORT.md. No commits, pushes, application migrations, owner-sandbox resets or destructive DB operations were performed. UI automation is out of scope.

## Historical evidence

Earlier 48-case and 59-case Python runs are historical; their ignored local reports were retained. They are not current test counts. Earlier command-line API/performance tooling has been removed from the final scope.

The owner previously reported successful manual Postman health/product/authentication/variant/cart checks. Those observations were preserved and were not reclassified as fresh manual execution.

## Pending

Remote GitHub Actions, clean-machine dependency/image setup, expiration/exact shipping-boundary scenarios, and constraint-enforcement writes in a disposable database remain unverified. Existing container port bindings require recreation to apply the Compose loopback configuration. The old frontend Service Worker limitation remains unresolved; UI is out of scope.
