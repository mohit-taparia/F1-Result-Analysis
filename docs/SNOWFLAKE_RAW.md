# Phase 2 — Snowflake RAW Layer

## Purpose

Phase 2 replaces local generated RAW files as the persistent system of record for the modern pipeline. Python remains responsible for extraction and source validation; Snowflake RAW is responsible for durable, rerunnable storage.

## Objects

Default database and schema:

```text
F1_ANALYTICS
└── RAW
    ├── RACES
    ├── RESULTS
    ├── QUALIFYING
    ├── DRIVER_STANDINGS
    └── CONSTRUCTOR_STANDINGS
```

The names are configurable through environment variables.

## Grain and business keys

| Table | Grain | Merge key |
| --- | --- | --- |
| `RACES` | one Formula 1 race | `season, round` |
| `RESULTS` | one driver's result in a race | `season, round, driver_id` |
| `QUALIFYING` | one driver's qualifying result in a race | `season, round, driver_id` |
| `DRIVER_STANDINGS` | one driver's championship standing after a round | `season, round, driver_id` |
| `CONSTRUCTOR_STANDINGS` | one constructor's championship standing after a round | `season, round, constructor_id` |

## Load metadata

Every RAW row receives:

- `LOAD_ID` — UUID identifying the pipeline load
- `SOURCE` — source system identifier
- `LOADED_AT` — UTC warehouse load timestamp

This is operational lineage for reconciliation and troubleshooting.

## Load strategy

```text
validated Python records
        |
        v
Snowflake TEMP staging table
        |
        v
bound batch INSERT
        |
        v
MERGE on business key
   |              |
matched        not matched
UPDATE            INSERT
        |
        v
COMMIT
```

If staging or merge fails, the transaction is rolled back.

A season may be rerun because the source changed, a pipeline failed, or history is deliberately backfilled. A pure append would duplicate the same race/driver grain. `MERGE` makes reruns safe at the current RAW-table grain.

## Credentials

Credentials are never stored in the repository. The loader reads Snowflake connection settings from environment variables. `.env` remains ignored by Git; `.env.example` documents variable names without containing secrets.

## Run

```bash
pip install -e ".[snowflake,dev]"

f1-load-snowflake --season 2024 --bootstrap
```

After the first successful bootstrap, normal reruns do not require `--bootstrap`.

## Validation queries

After a real Snowflake load, Phase 2 is not complete until we verify:

```sql
SELECT COUNT(*) FROM F1_ANALYTICS.RAW.RACES WHERE SEASON = 2024;

SELECT SEASON, ROUND, DRIVER_ID, COUNT(*)
FROM F1_ANALYTICS.RAW.RESULTS
WHERE SEASON = 2024
GROUP BY 1,2,3
HAVING COUNT(*) > 1;

SELECT LOAD_ID, SOURCE, MIN(LOADED_AT), MAX(LOADED_AT), COUNT(*)
FROM F1_ANALYTICS.RAW.RESULTS
WHERE SEASON = 2024
GROUP BY 1,2;
```

Expected principles:

- 2024 contains 24 race rows.
- business-key duplicate queries return zero rows.
- source counts reconcile with ingestion.
- rerunning the same season does not increase counts through duplication.
- lineage columns are populated.

## Boundary with dbt

RAW intentionally does **not** convert qualifying strings, calculate driver age, shift standings for pre-race features, derive winners, or build analytics metrics. Those transformations belong in Phase 3 so they are versioned, testable SQL/dbt models rather than hidden inside ingestion code.
