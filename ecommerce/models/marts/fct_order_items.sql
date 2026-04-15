SELECT
    oi.order_key,
    oi.order_item_num,
    oi.product_key,
    o.customer_key,
    oi.seller_key,
    o.zip AS customer_zip,
    oi.order_price AS item_price,
    oi.order_freight AS item_freight,
    o.order_purchase_date,
    o.order_deliver_carrier_date - oi.order_shipping_limit AS days_to_ship,
    o.order_deliver_customer_date - o.order_purchase_date AS days_to_deliver_actual,
    o.order_deliver_estimate_date - o.order_deliver_customer_date AS days_to_deliver_difference
FROM {{ ref('stg_order_items') }} oi
LEFT JOIN {{ ref('stg_orders' )}} o ON oi.order_key = o.order_key

