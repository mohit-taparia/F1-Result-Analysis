with source as (
    select * from {{ source('raw', 'driver_standings') }}
)

select
    season::number(4, 0) as season,
    round::number(3, 0) as round,
    concat(season, '-', round) as race_key,
    concat(season, '-', round, '-', driver_id) as driver_standing_key,
    driver_id,
    driver_code,
    position::number(3, 0) as position,
    position_text,
    points::float as points,
    wins::number(3, 0) as wins,
    constructor_ids,
    load_id as _load_id,
    source as _source,
    loaded_at as _loaded_at
from source
