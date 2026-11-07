# Database verification

Current delivery: 2026-11-08. The final Python-only full run passed 58 cases, including all database/integration cases below. Fresh evidence is in reports/final-python/pytest-xpmyveh2/; older counts and fixed report links below are historical. See PROJECT_REPORT.md for current execution details.

Inspected PostgreSQL 16.15, actual public schema and 76 constraint definitions on 2026-11-07. Connections used by pytest set default_transaction_read_only=on. No migrations, DB writes, invalid inserts or resets were performed. API writes were confined to new private local sandboxes.

All cases below were executed successfully on 2026-11-07 against the local QA database. This is a dated observation, not a universal property of future datasets. Zero violating rows is the expected audit result. The primary queries in 004/005/011 require a captured fresh cart API response supplied as the `api_cart` psql variable; Python binds that JSON safely as a query parameter.

| ID | Objective / precondition | Execution and result | Limitation |
| --- | --- | --- | --- |
| DB-TC-001 | cart_items refer to variants; populated schema | pytest database audit: PASS, zero violations | Does not prove FK rejects writes |
| DB-TC-002 | quantities positive | PASS, zero nonpositive rows | NOT NULL is schema-enforced, separately inspected |
| DB-TC-003 | one cart row per variant | PASS, zero duplicate groups | Catalog also shows UNIQUE(cart_id,variant_id) |
| DB-TC-004 | DB snapshot/line arithmetic equals API line values; fresh populated cart | PASS after first and repeated additions | Requires captured API JSON; historical Cart 13 comment remains historical |
| DB-TC-005 | independently compute shipping from DB subtotal and compare API | PASS after first and repeated additions | Exact 499.99/500.00 boundary execution not established |
| DB-TC-006 | variants refer to products | PASS, zero orphans | Not constraint rejection proof |
| DB-TC-007 | order items refer to orders | PASS, zero orphans | Not constraint rejection proof |
| DB-TC-008 | stored order subtotal and grand total reconcile | PASS, zero mismatches | Does not establish every discount policy |
| DB-TC-009 | actual payments refer to same-sandbox orders | PASS, zero orphan/mismatched rows | Retained synthetic lookup is supplementary, not enforcement |
| DB-TC-010 | normalized email uniqueness within sandbox | PASS, zero duplicate groups | DB UNIQUE is case-sensitive; API normalizes email |
| DB-TC-011 | API items equal DB IDs, quantities, snapshots and line totals | PASS after first and repeated additions | Fresh cart prevents vacuous empty comparisons |
| DB-TC-012 | cross-sandbox references across cart/product/order/payment/inventory/user relationships | PASS, zero mismatches | Not exhaustive across addresses/reviews/shipments |

Additional pytest checks verify inventory bounds and selected FK/CHECK/UNIQUE catalog definitions. Current separate payment observation: 1,755 payments, 1,755 distinct orders with payments, zero orphan/sandbox mismatches. Earlier owner counts (810 payments) describe another dataset and are not fixed requirements.

Constraints inspected include cart qty >0, cart+variant uniqueness, per-sandbox email uniqueness, payment/order FK, product/variant FK, and nonnegative inventory fields. Current foreign keys use global parent IDs rather than composite parent+sandbox keys. Existing-data consistency passes; direct SQL rejection of cross-sandbox relationships is NOT VERIFIED. Constraint-enforcement writes were not attempted against the owner's persistent database. A disposable database and separately controlled invalid writes are required for that claim.

Queries are saved in sql/. DB-TC-009 retains its historical synthetic check in the same file, after the primary query; pytest intentionally executes only the primary audit. Historical PASS comments in older files are retained and must not be interpreted as the current execution evidence. Fresh evidence is reports/final-python/pytest-xpmyveh2/junit.xml and pytest.html; older reports/junit.xml and reports/pytest.html are historical, generated and ignored.
