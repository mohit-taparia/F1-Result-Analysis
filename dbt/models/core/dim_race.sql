select
    race_key,
    season,
    round,
    race_name,
    race_date,
    race_time_utc,
    circuit_id
from {{ ref('stg_races') }}
