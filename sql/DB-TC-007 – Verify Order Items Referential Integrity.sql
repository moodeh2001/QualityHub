
SELECT
    oi.id AS order_item_id,
    oi.order_id
FROM public.order_items oi
LEFT JOIN public.orders o
    ON oi.order_id = o.id
WHERE o.id IS NULL;
