-- Supplementary historical synthetic negative test (not constraint enforcement):
-- Existing order (1): VALID RELATIONSHIP
-- Non-existing order (999999): INVALID ORDER
-- Result: PASSED
-- Note: No database records were modified.



-- Primary audit: actual payments and sandbox relationships. Expected: zero rows.
SELECT p.id, p.order_id FROM public.payments p
LEFT JOIN public.orders o ON o.id=p.order_id
WHERE o.id IS NULL OR p.sandbox_id IS DISTINCT FROM o.sandbox_id;

-- The original synthetic lookup is retained below for manual practice.
WITH test_payments (payment_id, order_id) AS (
    VALUES
        (1, 1),
        (999999, 999999)
)
SELECT
    tp.payment_id,
    tp.order_id,
    CASE
        WHEN o.id IS NULL THEN 'INVALID ORDER'
        ELSE 'VALID RELATIONSHIP'
    END AS validation_result
FROM test_payments tp
LEFT JOIN public.orders o
    ON tp.order_id = o.id;
