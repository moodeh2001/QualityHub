
SELECT
    id,
    cart_id,
    variant_id,
    qty
FROM public.cart_items
WHERE qty <= 0;
