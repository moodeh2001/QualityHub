
-- Test Case: DB-TC-008
-- Objective: Validate order subtotal and grand total.
-- Expected Result: 0 rows
-- Actual Result: 0 rows
-- Status: PASSED
-- Execution Date: 2026-11-07
-- Verified: 1800 order items across 900 orders.

SELECT
    o.id AS order_id,
    o.subtotal AS stored_subtotal,
    COALESCE(SUM(oi.line_total), 0) AS calculated_subtotal,
    o.grand_total AS stored_grand_total,
    o.subtotal - o.discount_total
        + o.shipping_total AS calculated_grand_total
FROM public.orders o
LEFT JOIN public.order_items oi
    ON o.id = oi.order_id
GROUP BY
    o.id,
    o.subtotal,
    o.discount_total,
    o.shipping_total,
    o.grand_total
HAVING
    o.subtotal IS DISTINCT FROM
        COALESCE(SUM(oi.line_total), 0)
    OR
    o.grand_total IS DISTINCT FROM
        (o.subtotal - o.discount_total + o.shipping_total);
