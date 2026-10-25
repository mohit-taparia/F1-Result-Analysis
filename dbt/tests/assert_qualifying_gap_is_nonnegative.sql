select *
from {{ ref('mart_race_features') }}
where qualifying_gap_to_fastest_ms < 0
