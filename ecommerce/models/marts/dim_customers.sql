SELECT
    customer_key
FROM {{ ref('stg_customers') }}