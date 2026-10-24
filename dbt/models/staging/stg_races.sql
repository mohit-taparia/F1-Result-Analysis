with source as (
    select * from {{ source('raw', 'races') }}
)

select
    season::number(4, 0) as season,
    round::number(3, 0) as round,
    concat(season, '-', round) as race_key,
    race_name,
    race_date::date as race_date,
    race_time_utc,
    circuit_id,
    circuit_name,
    locality,
    country,
    latitude::float as latitude,
    longitude::float as longitude,
    source_url,
    load_id as _load_id,
    source as _source,
    loaded_at as _loaded_at
from source
