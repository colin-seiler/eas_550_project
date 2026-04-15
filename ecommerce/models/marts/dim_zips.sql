SELECT
    zip,
    city,
    state,
    latitude,
    longitude
FROM {{ ref('stg_zips') }}