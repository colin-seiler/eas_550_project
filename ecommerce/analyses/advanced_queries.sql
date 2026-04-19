
-- who are the top sellers by revenue?
-- joining order items to sellers and pulling in zip for location info
WITH seller_revenue AS (
    SELECT 
        s.SellerID,
        s.Reference AS seller_ref,
        z.City,
        z.State,
        SUM(oi.Price) AS total_revenue,
        COUNT(DISTINCT oi.OrderID) AS total_orders
    FROM commerce.sellers s
    JOIN commerce.orderitems oi ON s.SellerID = oi.SellerID
    JOIN commerce.zips z ON s.Zip = z.Zip
    GROUP BY s.SellerID, s.Reference, z.City, z.State
)
SELECT 
    seller_ref,
    City,
    State,
    total_revenue,
    total_orders,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM seller_revenue
ORDER BY revenue_rank
LIMIT 10;


-- how much are customers spending per order on average?
-- using window functions to rank customers by their avg spend
WITH customer_spend AS (
    SELECT
        c.CustID,
        c.Reference AS cust_ref,
        o.OrderID,
        SUM(oi.Price + oi.Freight) AS order_total
    FROM commerce.customers c
    JOIN commerce.orders o ON c.CustID = o.CustID
    JOIN commerce.orderitems oi ON o.OrderID = oi.OrderID
    GROUP BY c.CustID, c.Reference, o.OrderID
)
SELECT
    cust_ref,
    ROUND(AVG(order_total), 2) AS avg_order_value,
    COUNT(OrderID) AS total_orders,
    SUM(order_total) AS lifetime_value,
    RANK() OVER (ORDER BY SUM(order_total) DESC) AS customer_rank
FROM customer_spend
GROUP BY cust_ref
ORDER BY customer_rank
LIMIT 10;


-- how did order volume and revenue trend month over month?
-- window function to calculate month over month revenue change
WITH monthly_stats AS (
    SELECT
        DATE_TRUNC('month', o.OrderPurchaseTime) AS order_month,
        COUNT(DISTINCT o.OrderID) AS total_orders,
        SUM(oi.Price) AS total_revenue
    FROM commerce.orders o
    JOIN commerce.orderitems oi ON o.OrderID = oi.OrderID
    WHERE o.Status = 'delivered'
    GROUP BY DATE_TRUNC('month', o.OrderPurchaseTime)
)
SELECT
    order_month,
    total_orders,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_revenue - LAG(total_revenue) OVER (ORDER BY order_month), 2) AS revenue_change,
    ROUND(100.0 * (total_revenue - LAG(total_revenue) OVER (ORDER BY order_month)) 
          / LAG(total_revenue) OVER (ORDER BY order_month), 2) AS pct_change
FROM monthly_stats
ORDER BY order_month;