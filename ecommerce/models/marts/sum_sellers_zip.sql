WITH order_totals AS (
    SELECT
        oi.order_key,
        s.seller_zip,
        SUM(oi.item_price) AS order_total,
        SUM(oi.item_freight) AS order_freight,
        AVG(oi.days_to_deliver_actual) AS avg_delivery_days,
        AVG(oi.days_to_deliver_difference) AS avg_late_days
    FROM {{ ref('fct_order_items') }} oi
    JOIN {{ ref('dim_sellers') }} s ON oi.seller_key = s.seller_key
    GROUP BY oi.order_key, s.seller_zip
)
SELECT
    seller_zip,
    COUNT(DISTINCT order_key) AS total_orders,
    AVG(order_total) AS avg_order_price,
    AVG(order_freight) AS avg_order_freight,
    AVG(avg_delivery_days) AS avg_delivery_days,
    AVG(avg_late_days) AS avg_late_days
FROM order_totals
WHERE seller_zip IS NOT NULL
GROUP BY seller_zip