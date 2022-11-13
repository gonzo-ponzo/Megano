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
           o.error_type_id,
           pe.name as error_name,
           SUM(oo.price * oo.amount) AS sum_price,
           SUM(oo.discount * oo.amount) AS sum_discount,
           CASE
             WHEN o.delivery_type = 2 THEN od.price + od.express_price
             WHEN COUNT(DISTINCT pf.shop_id) > 1 THEN od.price
             WHEN SUM(oo.price * oo.amount) < od.sum_order THEN od.price
             ELSE 0
           END AS price_delivery
    FROM order_order o
        JOIN order_orderoffer oo ON o.id = oo.order_id
        JOIN order_delivery od ON o.delivery_id = od.id
        JOIN product_offer pf ON oo.offer_id = pf.id
        LEFT JOIN  order_paymenterror pe ON o.error_type_id = pe.id
    WHERE o.deleted_at IS NULL AND {}
    GROUP BY o.id, o.created_at, o.user_id, o.city, o.address, o.comment, o.delivery_type, o.payment_type,
             o.status_type, o.error_type_id, od.price, od.express_price, od.sum_order, pe.name
)
SELECT ho.id,
       ho.created_at,
       ho.user_id,
       ho.city,
       ho.address,
       ho.comment,
       ho.delivery_type,
       ho.payment_type,
       ho.status_type,
       ho.error_type_id,
       ho.error_name,
       ho.sum_price + ho.price_delivery AS full_price,
       ho.price_delivery,
       ho.sum_discount,
       ho.sum_price + ho.price_delivery - ho.sum_discount AS total_full_price
FROM history_order ho
ORDER BY ho.created_at DESC
"""

USER_ORDERS_SQL = __order_history_sql.format("user_id = %s")
USER_LAST_ORDER_SQL = f"{USER_ORDERS_SQL}LIMIT 1"
ORDER_SQL = __order_history_sql.format("order_id = %s AND user_id = %s")
