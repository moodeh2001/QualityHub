
SELECT
    cart_id,
    variant_id,
    COUNT(*) AS duplicate_count
FROM public.cart_items
GROUP BY cart_id, variant_id
HAVING COUNT(*) > 1;
