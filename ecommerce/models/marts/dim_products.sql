SELECT
    product_key,
    product_category,
    product_weight_gram,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    product_photo_count
FROM {{ ref('stg_products') }}