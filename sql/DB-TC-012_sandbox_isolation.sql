-- DB-TC-012: detect cross-sandbox parent references in actual records.
SELECT 'cart_items/cart' AS relationship, ci.id FROM public.cart_items ci JOIN public.carts c ON c.id=ci.cart_id WHERE ci.sandbox_id<>c.sandbox_id
UNION ALL SELECT 'cart_items/variant',ci.id FROM public.cart_items ci JOIN public.product_variants v ON v.id=ci.variant_id WHERE ci.sandbox_id<>v.sandbox_id
UNION ALL SELECT 'variants/product',v.id FROM public.product_variants v JOIN public.products p ON p.id=v.product_id WHERE v.sandbox_id<>p.sandbox_id
UNION ALL SELECT 'order_items/order',i.id FROM public.order_items i JOIN public.orders o ON o.id=i.order_id WHERE i.sandbox_id<>o.sandbox_id
UNION ALL SELECT 'payments/order',p.id FROM public.payments p JOIN public.orders o ON o.id=p.order_id WHERE p.sandbox_id<>o.sandbox_id
UNION ALL SELECT 'inventory/variant',i.variant_id FROM public.inventory i JOIN public.product_variants v ON v.id=i.variant_id WHERE i.sandbox_id<>v.sandbox_id
UNION ALL SELECT 'orders/user',o.id FROM public.orders o JOIN public.users u ON u.id=o.user_id WHERE o.sandbox_id<>u.sandbox_id;
