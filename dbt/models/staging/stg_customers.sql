select
    customer_id,
    initcap(trim(first_name)) as first_name,
    initcap(trim(last_name)) as last_name,
    lower(trim(email)) as email,
    signup_date,
    {{ clean_text('country') }} as country
from {{ source('bronze', 'customers') }}
where customer_id is not null
