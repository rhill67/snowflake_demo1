select *
from {{ ref('stg_sales') }}
where quantity <= 0
   or unit_price < 0
   or discount < 0
   or discount > 1
   or total_amount < 0
