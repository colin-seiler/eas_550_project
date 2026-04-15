SELECT
    OrderID AS order_key,
    OrderItemID AS order_item_num,
    ProductID AS product_key,
    SellerID AS seller_key,
    ShippingLimit::DATE AS order_shipping_limit,
    Price AS order_price,
    Freight AS order_freight
FROM commerce.orderitems