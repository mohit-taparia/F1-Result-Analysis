with ranked as (
    select
        constructor_id,
        constructor_name,
        row_number() over (
            partition by constructor_id
            order by race_date desc, season desc, round desc
        ) as recency_rank
    from {{ ref('stg_results') }}
    where constructor_id is not null
)

select
    constructor_id,
    constructor_name
from ranked
where recency_rank = 1
