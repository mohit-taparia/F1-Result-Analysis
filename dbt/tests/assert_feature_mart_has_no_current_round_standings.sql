-- Any returned row is a temporal-leakage failure.
select *
from {{ ref('mart_race_features') }}
where
    (driver_standings_through_round is not null
        and driver_standings_through_round >= round)
    or
    (constructor_standings_through_round is not null
        and constructor_standings_through_round >= round)
