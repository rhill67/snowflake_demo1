select
    p.product_id,
    p.product_name,
    p.category,
    p.active,
    sum(s.quantity) as units_sold,
    sum(s.total_amount) as revenue
from {{ ref('stg_sales') }} s
join {{ ref('stg_products') }} p
  on s.product_id = p.product_id
group by
    p.product_id,
    p.product_name,
    p.category,
    p.active
