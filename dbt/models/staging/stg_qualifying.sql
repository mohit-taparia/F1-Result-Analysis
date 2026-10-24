with source as (
    select * from {{ source('raw', 'qualifying') }}
)

select
    season::number(4, 0) as season,
    round::number(3, 0) as round,
    concat(season, '-', round) as race_key,
    concat(season, '-', round, '-', driver_id) as driver_race_key,
    race_name,
    race_date::date as race_date,
    circuit_id,
    driver_id,
    driver_code,
    constructor_id,
    constructor_name,
    car_number,
    qualifying_position::number(3, 0) as qualifying_position,
    q1,
    q2,
    q3,
    {{ lap_time_to_milliseconds('q1') }} as q1_ms,
    {{ lap_time_to_milliseconds('q2') }} as q2_ms,
    {{ lap_time_to_milliseconds('q3') }} as q3_ms,
    load_id as _load_id,
    source as _source,
    loaded_at as _loaded_at
from source
