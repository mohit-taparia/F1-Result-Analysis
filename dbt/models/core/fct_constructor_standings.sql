select
    constructor_standing_key,
    race_key,
    season,
    round,
    constructor_id,
    position,
    position_text,
    points,
    wins
from {{ ref('stg_constructor_standings') }}
