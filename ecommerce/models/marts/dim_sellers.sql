SELECT
    seller_key,
    seller_zip
FROM {{ ref('stg_sellers') }}