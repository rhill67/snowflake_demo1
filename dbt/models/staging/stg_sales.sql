select
    sale_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount,
    total_amount,
    round(quantity * unit_price * (1 - discount), 2) as calculated_total
from {{ source('bronze', 'sales') }}
where sale_id is not null
  and quantity > 0
  and unit_price >= 0
