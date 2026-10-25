select
    driver_standing_key,
    race_key,
    season,
    round,
    driver_id,
    position,
    position_text,
    points,
    wins,
    constructor_ids
from {{ ref('stg_driver_standings') }}
