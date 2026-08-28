{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

select
    order_id,
    customer_id,
    order_date,
    {{ clean_text('status') }} as status
from {{ source('bronze', 'orders') }}
where order_id is not null
  and customer_id is not null

{% if is_incremental() %}
  and order_id not in (select order_id from {{ this }})
{% endif %}
