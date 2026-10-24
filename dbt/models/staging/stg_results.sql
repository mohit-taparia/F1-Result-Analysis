with source as (
    select * from {{ source('raw', 'results') }}
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
    driver_given_name,
    driver_family_name,
    driver_date_of_birth::date as driver_date_of_birth,
    driver_nationality,
    constructor_id,
    constructor_name,
    car_number,
    grid_position::number(3, 0) as grid_position,
    finish_position::number(3, 0) as finish_position,
    position_text,
    points::float as points,
    laps::number(4, 0) as laps,
    status,
    finish_time_millis::number(18, 0) as finish_time_millis,
    fastest_lap_rank::number(3, 0) as fastest_lap_rank,
    fastest_lap_number::number(4, 0) as fastest_lap_number,
    fastest_lap_time,
    {{ lap_time_to_milliseconds('fastest_lap_time') }} as fastest_lap_time_ms,
    fastest_lap_avg_speed::float as fastest_lap_avg_speed,
    fastest_lap_avg_speed_units,
    load_id as _load_id,
    source as _source,
    loaded_at as _loaded_at
from source
