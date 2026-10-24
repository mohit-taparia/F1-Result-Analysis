with source as (
    select * from {{ source('raw', 'constructor_standings') }}
)

select
    season::number(4, 0) as season,
    round::number(3, 0) as round,
    concat(season, '-', round) as race_key,
    concat(season, '-', round, '-', constructor_id) as constructor_standing_key,
    constructor_id,
    constructor_name,
    position::number(3, 0) as position,
    position_text,
    points::float as points,
    wins::number(3, 0) as wins,
    load_id as _load_id,
    source as _source,
    loaded_at as _loaded_at
from source
