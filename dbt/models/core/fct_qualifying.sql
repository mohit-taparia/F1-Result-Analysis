select
    driver_race_key as qualifying_result_key,
    race_key,
    season,
    round,
    race_date,
    circuit_id,
    driver_id,
    constructor_id,
    car_number,
    qualifying_position,
    q1_ms,
    q2_ms,
    q3_ms,
    least_ignore_nulls(q1_ms, q2_ms, q3_ms) as best_qualifying_time_ms
from {{ ref('stg_qualifying') }}
