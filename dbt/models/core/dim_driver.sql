with ranked as (
    select
        driver_id,
        driver_code,
        driver_given_name,
        driver_family_name,
        driver_date_of_birth,
        driver_nationality,
        row_number() over (
            partition by driver_id
            order by race_date desc, season desc, round desc
        ) as recency_rank
    from {{ ref('stg_results') }}
)

select
    driver_id,
    driver_code,
    driver_given_name,
    driver_family_name,
    trim(concat(coalesce(driver_given_name, ''), ' ', coalesce(driver_family_name, ''))) as driver_name,
    driver_date_of_birth,
    driver_nationality
from ranked
where recency_rank = 1
