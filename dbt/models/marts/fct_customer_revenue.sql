select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.country,
    count(distinct o.order_id) as order_count,
    sum(s.total_amount) as total_revenue
from {{ ref('stg_customers') }} c
join {{ ref('stg_orders') }} o
  on c.customer_id = o.customer_id
join {{ ref('stg_sales') }} s
  on o.order_id = s.order_id
group by
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.country
