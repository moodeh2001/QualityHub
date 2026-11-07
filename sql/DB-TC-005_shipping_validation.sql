
-- Test Case: DB-TC-005
-- Objective: Calculate expected shipping fees
-- based on cart subtotal.
--
-- Business Rule:
-- Subtotal >= 500 TL -> Free Shipping
-- Subtotal < 500 TL  -> 29.90 TL
--
-- Compare expected_shipping with
-- shipping_total returned by GET Cart API.
--
-- Tested carts: 13 and 14
-- Observed scenarios: PASSED
-- Exact boundary values: NOT TESTED

-- Current verification: supply API cart JSON via api_cart. Expected: zero rows.
WITH expected AS (SELECT :'api_cart'::jsonb AS doc), subtotal AS (
 SELECT coalesce(sum(ci.qty*ci.unit_price_snapshot),0) AS amount
 FROM public.cart_items ci,expected e WHERE ci.cart_id=(e.doc->'cart'->>'id')::bigint
)
SELECT amount,CASE WHEN amount>=500 THEN 0.00 ELSE 29.90 END AS expected_shipping
FROM subtotal,expected
WHERE (CASE WHEN amount>=500 THEN 0.00 ELSE 29.90 END)
 IS DISTINCT FROM (doc->'totals'->>'shipping_total')::numeric;
