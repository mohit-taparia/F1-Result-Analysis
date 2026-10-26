# Phase 3 — dbt Transformation Layer

## Purpose

Phase 3 converts validated Snowflake RAW data into tested, reusable SQL models and a leakage-aware machine-learning feature mart.

## Model flow

```text
F1_ANALYTICS.RAW
       |
       v
dbt STAGING (views)
       |
       v
dbt CORE (views)
       |
       v
dbt MART (tables)
       |
       v
mart_race_features
```

### STAGING

- `stg_races`
- `stg_results`
- `stg_qualifying`
- `stg_driver_standings`
- `stg_constructor_standings`

Staging performs source cleanup, type normalization, stable grain keys, and lap-time conversion. It does not apply predictive business logic.

### CORE

Dimensions:

- `dim_driver`
- `dim_constructor`
- `dim_circuit`
- `dim_race`

Facts:

- `fct_race_results`
- `fct_qualifying`
- `fct_driver_standings`
- `fct_constructor_standings`

CORE exposes reusable business entities and facts. Race results and standings remain historically truthful; post-race information is not disguised as a pre-race feature.

### MART

`mart_race_features` is one row per driver/race after qualifying.

Current-race inputs include qualifying position/time. Championship features use round N-1. Driver form uses only prior race results. Historical outcome columns are labels only and must never enter the model feature matrix.

## Automated tests

dbt schema tests validate:

- unique grains
- required keys
- relationships between dimensions/facts/marts

Singular leakage/business-rule tests validate:

- standings used for a prediction are always earlier than the predicted round
- round 1 does not accidentally receive current-season standings
- qualifying gaps cannot be negative

## Local installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,snowflake,dbt]"
```

Configure Snowflake environment variables using `.env.example` as the variable-name reference. Do not commit credentials.

## Structural validation without Snowflake

```bash
dbt parse --project-dir dbt --profiles-dir .github/dbt --no-partial-parse
```

This validates dbt project structure/Jinja/model dependencies only. It does **not** execute models in Snowflake.

## Real Snowflake validation

Create a local dbt profile that points to the same Snowflake account/database containing the validated RAW tables. The target schema is the developer schema used for this validation; dbt will create its configured STAGING/CORE/MART derived schemas according to `dbt_project.yml`.

Run:

```bash
dbt debug --project-dir dbt --profiles-dir <your-local-profile-directory>
dbt build --project-dir dbt --profiles-dir <your-local-profile-directory> --full-refresh
```

Do not use `.github/dbt/profiles.yml` for the real build; that profile intentionally contains non-secret CI placeholders.

## Acceptance checks

Phase 3 has passed its real Snowflake acceptance gate:

1. `dbt debug` confirmed the Snowflake connection.
2. STAGING, CORE, and MART builds completed successfully.
3. Applicable dbt schema and singular tests passed.
4. `mart_race_features` contains 479 rows and 479 unique driver/race keys.
5. Explicit standings leakage checks returned zero violations.
6. Historical labels reconcile to 24 races and exactly 24 winners.
7. Prior-race finish validation checked 479 rows with zero mismatches.
8. An unchanged MART rebuild again passed all 13 checks.

Useful reconciliation queries:

```sql
-- One feature row per qualifying row.
SELECT COUNT(*) FROM <mart_schema>.MART_RACE_FEATURES;

-- No duplicate driver/race grain.
SELECT DRIVER_RACE_KEY, COUNT(*)
FROM <mart_schema>.MART_RACE_FEATURES
GROUP BY 1
HAVING COUNT(*) > 1;

-- Exactly one historical winner per completed race represented in the mart.
SELECT RACE_KEY, COUNT_IF(IS_WINNER)
FROM <mart_schema>.MART_RACE_FEATURES
WHERE IS_WINNER IS NOT NULL
GROUP BY 1
HAVING COUNT_IF(IS_WINNER) <> 1;

-- Temporal leakage guard should return zero.
SELECT *
FROM <mart_schema>.MART_RACE_FEATURES
WHERE DRIVER_STANDINGS_THROUGH_ROUND >= ROUND
   OR CONSTRUCTOR_STANDINGS_THROUGH_ROUND >= ROUND;
```

## Gate to later phases

The real Snowflake `dbt build` gate has passed. Before meaningful ML training/backtesting, the modern warehouse still needs a multi-season historical backfill; current real-warehouse validation uses 2024 data.
