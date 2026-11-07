-- DB-TC-011: supply api_cart as JSON via psql -v api_cart=... .
-- Python integration binds it as a parameter. Expected: zero differences.
WITH expected AS (SELECT :'api_cart'::jsonb AS doc), api_items AS (
 SELECT (j->>'variant_id')::bigint AS variant_id, (j->>'qty')::int AS qty,
 (j->>'unit_price')::numeric AS unit_price, (j->>'line_total')::numeric AS line_total
 FROM expected, jsonb_array_elements(doc->'items') j
), actual AS (
 SELECT ci.* FROM public.cart_items ci, expected e WHERE ci.cart_id=(e.doc->'cart'->>'id')::bigint
)
SELECT coalesce(a.variant_id,e.variant_id) AS variant_id FROM actual a FULL JOIN api_items e USING(variant_id)
WHERE a.id IS NULL OR e.variant_id IS NULL OR a.qty IS DISTINCT FROM e.qty
OR a.unit_price_snapshot IS DISTINCT FROM e.unit_price
OR round(a.qty*a.unit_price_snapshot,2) IS DISTINCT FROM e.line_total;
