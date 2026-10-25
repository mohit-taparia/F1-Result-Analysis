with ranked as (
    select
        circuit_id,
        circuit_name,
        locality,
        country,
        latitude,
        longitude,
        row_number() over (
            partition by circuit_id
            order by race_date desc, season desc, round desc
        ) as recency_rank
    from {{ ref('stg_races') }}
)

select
    circuit_id,
    circuit_name,
    locality,
    country,
    latitude,
    longitude
from ranked
where recency_rank = 1
