select
    date_trunc('month', o.order_date) as revenue_month,
    count(distinct o.order_id) as order_count,
    sum(s.total_amount) as total_revenue
from {{ ref('stg_orders') }} o
join {{ ref('stg_sales') }} s
  on o.order_id = s.order_id
group by date_trunc('month', o.order_date)
