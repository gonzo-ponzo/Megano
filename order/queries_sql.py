__order_history_sql = """
WITH history_order AS (
    SELECT o.id,
           o.created_at,
           o.user_id,
           o.city,
           o.address,
           o.comment,
           o.delivery_type,
           o.payment_type,
           o.status_type,
           o.error_type,
           SUM(oo.price * oo.amount) AS sum_price,
           SUM(oo.discount)          AS sum_discount,
           CASE
               WHEN o.delivery_type = 2 THEN od.price + od.express_price
               WHEN COUNT(DISTINCT of.shop_id) > 1 THEN od.price
               WHEN SUM(oo.price * oo.amount) < od.sum_order THEN od.price
               ELSE 0 END            AS price_delivery
    FROM order_order o
            JOIN order_orderoffer oo ON o.id = oo.order_id
            JOIN order_delivery od ON o.delivery_id = od.id
            JOIN product_offer of ON oo.offer_id = of.id
    WHERE oo.deleted_at IS NULL AND {}
    GROUP BY o.id, o.created_at, o.user_id, o.city, o.address, o.comment, o.delivery_type,
            o.payment_type,
            o.status_type, o.error_type, od.price, od.express_price, od.sum_order)
SELECT h.id,
       h.created_at,
       h.user_id,
       h.city,
       h.address,
       h.comment,
       h.delivery_type,
       h.payment_type,
       h.status_type,
       h.error_type,
       h.sum_price + h.price_delivery AS full_price,
       h.price_delivery,
       CASE sum_discount
           WHEN 0 THEN NULL
           ELSE h.sum_price + h.price_delivery - h.sum_discount
           END                        AS total_full_price
FROM history_order h
ORDER BY h.created_at DESC
"""

user_orders_sql = __order_history_sql.format("user_id = %s")
user_last_order_sql = f"{__order_history_sql.format('user_id = %s')}LIMIT 1"
order_sql = __order_history_sql.format("order_id = %s")
