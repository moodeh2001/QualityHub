# QualityHub backend roadmap

Current scope: Python/pytest API, SQL and PostgreSQL integration, manual Postman testing, Docker Compose, sanitized reporting and Python GitHub Actions. UI automation is out of scope because no reliable frontend is available. Newman and JMeter were removed at the owner's request and are not pending deliverables.

| Deliverable | Fresh verification on 2026-11-08 |
| --- | --- |
| API automation | 32 cases passed |
| Read-only database/catalog checks | 11 cases passed |
| API/database integration | 3 cases passed |
| Python regression/configuration checks | 12 cases passed |
| SQL cases DB-TC-001–012 | Exercised by database/integration tests |
| Complete pytest suite | 58 passed, zero failures/errors/skips |
| Clean source with default report root | 12 regressions passed |
| Clean source with custom report root | 12 regressions passed; no project-local reports created |
| Manual Postman collection | 21 requests preserved byte-for-byte; no new manual run |
| Python CI workflow | Local configuration checks passed; remote execution not observed |

Remaining steps:
1. Configure CI secrets, verify image pulls and observe a real GitHub Actions run.
2. Verify dependency installation on a newly provisioned environment; source-only verification reused installed dependencies.
3. Exercise exact shipping-boundary and expiration scenarios in a dedicated sandbox.
4. Verify constraint rejection with controlled writes in a disposable database; inspect wider tenant relationships.
5. Recreate existing containers with private Compose configuration to apply loopback bindings when operationally appropriate.
6. Review and stage only intended source files. The owner controls commits and pushes.
