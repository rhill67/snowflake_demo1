select
    product_id,
    product_name,
    category,
    price,
    active
from {{ ref('stg_products') }}
