WITH order_totals AS (
    SELECT
        order_key,
        customer_zip,
        SUM(item_price) AS order_total,
        SUM(item_freight) AS order_freight,
        AVG(days_to_deliver_actual) AS avg_delivery_days,
        AVG(days_to_deliver_difference) AS avg_late_days
    FROM {{ ref('fct_order_items') }}
    GROUP BY order_key, customer_zip
)

SELECT
    customer_zip,
    COUNT(DISTINCT order_key) AS total_orders,
    AVG(order_total) AS avg_order_price,
    AVG(order_freight) AS avg_order_freight,
    AVG(avg_delivery_days) AS avg_delivery_days,
    AVG(avg_late_days) AS avg_late_days
FROM order_totals
GROUP BY customer_zip