WITH order_totals AS (
    SELECT
        order_key,
        customer_zip,
        SUM(item_price) AS order_total,
        SUM(item_freight) AS order_freight,
        AVG(days_to_ship) AS avg_ship_days,
        AVG(days_to_deliver_actual) AS avg_delivery_days,
        AVG(days_to_deliver_difference) AS avg_late_days
    FROM {{ ref('fct_order_items') }}
    GROUP BY order_key, customer_zip
),
summary AS (
    SELECT
        customer_zip,
        COUNT(DISTINCT order_key) AS total_orders,
        ROUND(AVG(order_total)::numeric, 2) AS avg_order_price,
        ROUND(AVG(order_freight)::numeric, 2) AS avg_order_freight,
        ROUND(AVG(avg_ship_days)::numeric, 2) AS avg_ship_days,
        ROUND(AVG(avg_delivery_days)::numeric, 2) AS avg_delivery_days,
        ROUND(AVG(avg_late_days)::numeric, 2) AS avg_late_days
    FROM order_totals
    GROUP BY customer_zip
)
SELECT
    s.*,
    z.city,
    z.state,
    z.latitude,
    z.longitude
FROM summary s
LEFT JOIN {{ ref('dim_zips') }} z ON s.customer_zip = z.zip