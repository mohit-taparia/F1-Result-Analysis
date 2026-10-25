with qualifying as (
    select * from {{ ref('fct_qualifying') }}
),

driver_history_ranked as (
    select
        q.qualifying_result_key,
        r.finish_position,
        r.points,
        r.is_winner,
        row_number() over (
            partition by q.qualifying_result_key
            order by r.season desc, r.round desc
        ) as recency_rank
    from qualifying q
    left join {{ ref('fct_race_results') }} r
        on q.driver_id = r.driver_id
        and (
            r.season < q.season
            or (r.season = q.season and r.round < q.round)
        )
),

driver_form as (
    select
        qualifying_result_key,
        count_if(finish_position is not null and recency_rank <= 3) as prior_races_used,
        avg(case when recency_rank <= 3 then finish_position end) as avg_finish_last_3,
        sum(case when recency_rank <= 3 and is_winner then 1 else 0 end) as wins_last_3,
        max(case when recency_rank = 1 then finish_position end) as previous_finish_position
    from driver_history_ranked
    group by qualifying_result_key
),

features as (
    select
        q.qualifying_result_key as driver_race_key,
        q.race_key,
        q.season,
        q.round,
        q.race_date,
        q.circuit_id,
        q.driver_id,
        q.constructor_id,

        q.qualifying_position,
        q.best_qualifying_time_ms,
        q.best_qualifying_time_ms
            - min(q.best_qualifying_time_ms) over (partition by q.race_key)
            as qualifying_gap_to_fastest_ms,

        datediff('day', d.driver_date_of_birth, q.race_date) / 365.25
            as driver_age_years,

        ds.round as driver_standings_through_round,
        ds.position as prior_driver_standing_position,
        coalesce(ds.points, 0) as prior_driver_points,
        coalesce(ds.wins, 0) as prior_driver_wins,

        cs.round as constructor_standings_through_round,
        cs.position as prior_constructor_standing_position,
        coalesce(cs.points, 0) as prior_constructor_points,
        coalesce(cs.wins, 0) as prior_constructor_wins,

        coalesce(df.prior_races_used, 0) as prior_races_used,
        df.previous_finish_position,
        df.avg_finish_last_3,
        coalesce(df.wins_last_3, 0) as wins_last_3,

        rr.is_winner,
        rr.finish_position as actual_finish_position
    from qualifying q
    left join {{ ref('dim_driver') }} d
        on q.driver_id = d.driver_id
    left join {{ ref('fct_driver_standings') }} ds
        on q.season = ds.season
        and q.round = ds.round + 1
        and q.driver_id = ds.driver_id
    left join {{ ref('fct_constructor_standings') }} cs
        on q.season = cs.season
        and q.round = cs.round + 1
        and q.constructor_id = cs.constructor_id
    left join driver_form df
        on q.qualifying_result_key = df.qualifying_result_key
    left join {{ ref('fct_race_results') }} rr
        on q.qualifying_result_key = rr.race_result_key
)

select * from features
