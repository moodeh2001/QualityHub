
-- Test Case: DB-TC-001
-- Objective: Verify that all cart items
-- reference existing product variants.
-- Expected Result: 0 rows
-- Observed Result: 0 rows
-- Status: PASSED (2026-11-06)

SELECT
    ci.id,
    ci.cart_id,
    ci.variant_id
FROM public.cart_items ci
LEFT JOIN public.product_variants pv
    ON ci.variant_id = pv.id
WHERE pv.id IS NULL;
