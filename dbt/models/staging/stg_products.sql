select
    product_id,
    trim(product_name) as product_name,
    {{ clean_text('category') }} as category,
    price,
    active
from {{ source('bronze', 'products') }}
where product_id is not null
  and price >= 0
