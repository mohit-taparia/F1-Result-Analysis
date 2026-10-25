-- Round 1 has no previous round in the same season, so standings must be empty/defaulted.
select *
from {{ ref('mart_race_features') }}
where round = 1
  and (
      driver_standings_through_round is not null
      or constructor_standings_through_round is not null
      or prior_driver_points <> 0
      or prior_driver_wins <> 0
      or prior_constructor_points <> 0
      or prior_constructor_wins <> 0
  )
