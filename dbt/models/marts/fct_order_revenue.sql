select
    o.order_id,
    o.order_date,
    o.status,
    o.customer_id,
    c.first_name,
    c.last_name,
    c.country,
    sum(s.total_amount) as order_revenue
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c
  on o.customer_id = c.customer_id
join {{ ref('stg_sales') }} s
  on o.order_id = s.order_id
group by
    o.order_id,
    o.order_date,
    o.status,
    o.customer_id,
    c.first_name,
    c.last_name,
    c.country
