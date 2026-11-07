
SELECT
    pv.id AS variant_id,
    pv.product_id
FROM public.product_variants pv
LEFT JOIN public.products p
    ON pv.product_id = p.id
WHERE p.id IS NULL;
