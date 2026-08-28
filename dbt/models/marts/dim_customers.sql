select
    customer_id,
    first_name,
    last_name,
    email,
    signup_date,
    country
from {{ ref('stg_customers') }}
