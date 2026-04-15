SELECT
    OrderID AS order_key,
    CustID AS customer_key,
    Zip AS zip,
    Status as order_status,
    OrderPurchaseTime::DATE AS order_purchase_date,
    OrderPurchaseTime::TIME AS order_purchase_time,
    OrderApprovalTime::DATE AS order_approval_date,
    OrderApprovalTime::TIME AS order_approval_time,
    OrderDeliverCarrier::DATE AS order_deliver_carrier_date,
    OrderDeliverCustomer::DATE AS order_deliver_customer_date,
    OrderDeliverEstimate::DATE AS order_deliver_estimate_date
FROM commerce.orders