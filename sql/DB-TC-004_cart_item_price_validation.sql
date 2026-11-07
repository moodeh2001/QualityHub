
-- Test Case: DB-TC-004
-- Objective: Calculate line totals for all cart items.
-- Expected: Each calculated total should match
-- the corresponding API line_total.
-- Verified example: Cart 13 - PASSED

-- Current verification: supply API cart JSON through psql api_cart variable.
-- Historical example above is not a fresh execution result. Expected: zero rows.
WITH expected AS (SELECT :'api_cart'::jsonb AS doc), items AS (
 SELECT value AS item FROM expected, jsonb_array_elements(doc->'items')
)
SELECT ci.cart_id,ci.variant_id,ci.qty*ci.unit_price_snapshot AS calculated_total
FROM public.cart_items ci, expected e, items a
WHERE ci.cart_id=(e.doc->'cart'->>'id')::bigint
AND ci.variant_id=(a.item->>'variant_id')::bigint
AND (ci.unit_price_snapshot IS DISTINCT FROM (a.item->>'unit_price')::numeric
 OR round(ci.qty*ci.unit_price_snapshot,2) IS DISTINCT FROM (a.item->>'line_total')::numeric);
