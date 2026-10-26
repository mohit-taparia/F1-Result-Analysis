# F1 Modern Data Platform — Implementation Plan

This document tracks the modernization of the original Formula 1 ML project into an end-to-end data engineering, machine learning, and AI analytics platform.

> Development branch: `feature/f1-modern-data-platform`
>
> Rule: changes remain off `main` until the implementation is validated end to end and explicitly approved for merge.

## Target architecture

```text
Jolpica F1 API
      |
      v
Python ingestion
      |
      v
Snowflake RAW
      |
      v
dbt STAGING / CORE / MART
      |
      +--------------------+
      |                    |
      v                    v
Analytics marts       ML feature mart
                           |
                           v
                 time-aware backtesting
                           |
                           v
                    race predictions
                           |
                           v
                 Snowflake predictions
                           |
                           v
                  AI analytics layer
```

## Engineering principles

The rebuild will follow these rules:

1. Do not claim a technology in the README until working code exists.
2. Separate ingestion, transformation, orchestration, ML, and AI concerns.
3. Prefer incremental and reproducible pipelines over notebook-only workflows.
4. Keep credentials outside source control.
5. Validate source data before loading downstream models.
6. Use time-aware ML validation to prevent future-data leakage.
7. Make each phase independently testable.
8. Preserve the original notebooks as historical reference.

---

## Phase 1 — Python ingestion foundation

**Goal:** replace notebook-based API collection with reusable Python ingestion code.

Planned structure:

```text
src/
├── ingestion/
│   ├── client.py
│   ├── races.py
│   ├── results.py
│   ├── qualifying.py
│   └── standings.py
├── config.py
└── main.py

tests/
├── test_client.py
├── test_ingestion.py
└── fixtures/
```

Capabilities:

- reusable F1 API client
- request timeout and retry handling
- pagination where required
- typed/normalized records
- configurable season/race ranges
- structured logging
- basic source-data validation
- unit tests using mocked API responses

**Validation gate**

- tests pass locally/CI
- a known season can be fetched reproducibly
- record counts and required keys are validated
- failed API calls do not silently create incomplete data
- no secrets or machine-specific paths are committed

Status: **COMPLETE**

Implemented in the first Phase 1 increment:

- reusable Jolpica API client
- custom User-Agent
- timeout + retry/backoff handling
- limit/offset pagination
- normalized races, results, qualifying, driver standings, and constructor standings
- JSON Lines local RAW output for pre-Snowflake validation
- duplicate/required-field validation
- CLI entry point
- mocked unit tests

Current local validation: **7 tests passing**

Validation completed:

- GitHub Actions unit-test job passes
- live Jolpica API smoke test passes against the completed 2024 season
- the 2024 schedule contract returns all 24 race rounds
- results and qualifying cover the expected completed-season rounds
- driver and constructor standings validate against real API responses
- constructor-standings normalization has dedicated unit-test coverage
- request pacing, retry/backoff, pagination, required-field checks, and duplicate-key validation are active
- generated RAW files remain outside source control

Phase 1 is considered stable enough to become the source layer for the Snowflake RAW implementation.

---

## Phase 2 — Snowflake RAW layer

**Goal:** persist source data in a warehouse rather than generated CSV files.

Initial RAW entities:

- races
- results
- qualifying
- driver standings
- constructor standings

Capabilities:

- Snowflake connection through environment variables
- explicit schemas and table definitions
- ingestion metadata such as load timestamp and source
- incremental/upsert strategy
- duplicate protection
- rerunnable loads

**Validation gate**

- repeated loads do not create unintended duplicates
- source-to-target record counts reconcile
- required fields and data types are validated
- historical reload can be performed safely

Status: **COMPLETE**

Implemented:

- explicit Snowflake RAW table specifications for five source datasets
- configurable `F1_ANALYTICS.RAW` database/schema naming
- environment-based Snowflake connection settings
- temporary staging tables + bound batch inserts
- business-key `MERGE` upserts for rerunnable season loads
- `LOAD_ID`, `SOURCE`, and `LOADED_AT` lineage metadata
- transaction rollback on failed loads
- dedicated Snowflake loader CLI
- unit tests for DDL, merge SQL, metadata, commit/rollback, and empty-load protection
- RAW-layer architecture/runbook documentation

Local warehouse-layer validation: **8/8 tests passing**

Real-warehouse validation completed against Snowflake:

- least-privilege `F1_PIPELINE_ROLE` connected successfully to `F1_ANALYTICS.RAW`
- all five RAW tables bootstrapped from the Python table specifications
- 2024 source-to-target counts reconciled: 24 races, 479 results, 479 qualifying records, 519 driver-standing records, and 240 constructor-standing records
- all five datasets cover rounds 1–24
- duplicate business-key checks returned zero across all five tables
- null business-key checks returned zero across all five tables
- `constructor_ids` verified as a Snowflake `VARIANT` containing an `ARRAY`
- lineage metadata verified on real rows
- a complete 2024 reload preserved the exact same table counts, proving full-season MERGE idempotency
- failed warehouse writes roll back rather than committing partial data

Phase 2 is complete. The RAW layer is now the validated source boundary for dbt transformations.

---

## Phase 3 — dbt transformation layer

**Goal:** move business transformations from Pandas notebooks into tested SQL models.

Proposed layers:

```text
RAW
 |
 v
STAGING
 |
 v
CORE
 |
 v
MART
```

Candidate models:

- `stg_races`
- `stg_results`
- `stg_qualifying`
- `stg_driver_standings`
- `stg_constructor_standings`
- `dim_driver`
- `dim_constructor`
- `dim_circuit`
- `dim_race`
- `fct_race_results`
- `fct_qualifying`
- `mart_race_features`

dbt tests will cover relationships, uniqueness, nullability, accepted values, and selected business rules.

**Validation gate**

- dbt build succeeds
- dbt tests pass
- transformed outputs reconcile with source data
- pre-race features contain no post-race information

Status: **COMPLETE — REAL SNOWFLAKE VALIDATED**

Implemented:

- five STAGING models with normalized keys/types and lap-time conversion
- four dimensions and four CORE fact models
- `mart_race_features` at driver/race grain
- prior-round championship features and prior-race driver form
- explicit separation of historical outcome labels from model inputs
- schema tests for uniqueness, nullability, and relationships
- singular tests for temporal leakage and qualifying-gap business rules
- CI `dbt parse` validation
- Phase 3 Snowflake validation runbook

Real Snowflake validation completed:

- STAGING: 5 models built successfully with 24 applicable tests passing; row counts exactly reconcile to RAW (24 races, 479 results, 479 qualifying, 519 driver standings, 240 constructor standings)
- CORE: 8 models built successfully with 43 applicable tests passing; fact row counts exactly reconcile to STAGING
- CORE winner-label validation confirmed 24 races, 24 winners, and exactly one winner per race
- MART: `mart_race_features` built successfully with 13 applicable tests passing
- MART grain validation confirmed 479 rows and 479 unique driver/race keys across 24 races
- historical labels reconcile to 24 winners and 479 populated finish positions
- explicit temporal-leakage checks returned zero violations for current-round standings, incorrect prior-round standings, and round-1 same-season standings
- prior-race form validation checked all 479 rows with zero `previous_finish_position` mismatches
- an unchanged MART rebuild again passed all 13 checks, confirming reproducible logical output

Phase 3 is complete. The next data prerequisite for meaningful time-aware ML is a multi-season historical backfill; the currently validated modern warehouse contains the 2024 season.

---

## Phase 4 — Orchestration

**Goal:** coordinate ingestion, warehouse loading, dbt transformations, tests, and prediction jobs.

Target: Apache Airflow.

Expected workflow:

```text
ingest
  -> validate raw data
  -> load Snowflake
  -> dbt build
  -> dbt test
  -> build ML features
  -> predict
  -> validate predictions
```

The workflow will be designed around dependencies and reruns rather than simply scheduling independent scripts.

**Validation gate**

- dependency order is enforced
- failed tasks prevent invalid downstream execution
- reruns are safe
- logs make failures diagnosable

Status: **PLANNED**

---

## Phase 5 — ML redesign and backtesting

**Goal:** replace misleading binary-accuracy evaluation with race-level prediction and time-aware evaluation.

Changes:

- eliminate random time-series train/test splitting
- eliminate tuning against the final evaluation season
- train only on information available before the predicted race
- rank drivers by win probability within each race
- implement rolling/season-based backtesting

Candidate metrics:

- race winner accuracy
- Top-3 hit rate
- Mean Reciprocal Rank
- log loss
- Brier score
- calibration metrics

Baseline models will be compared before choosing a more complex model.

**Validation gate**

- automated leakage checks
- reproducible backtest
- baseline comparison
- metrics calculated at race level
- model artifact tied to training data/version

Status: **PLANNED**

---

## Phase 6 — CI/CD and engineering quality

**Goal:** make repository changes testable before merge.

Planned GitHub Actions checks:

- Python lint/format validation
- unit tests
- dbt validation where practical
- configuration/security checks

Pull requests should fail validation when core tests fail.

Status: **PLANNED**

---

## Phase 7 — AI analytics layer

**Goal:** allow natural-language analysis of trusted F1 data and model outputs.

Example questions:

- Which drivers outperform their normal results in wet races?
- How has a constructor performed at Monaco over the last ten seasons?
- Why did the prediction model rank a particular driver first?
- Which features contributed most to a race prediction?

The AI layer will query curated data/model outputs rather than treating an LLM as the source of truth.

Possible implementation:

- Snowflake Cortex or an application LLM
- governed SQL/query tools
- semantic definitions for metrics
- retrieval of model metadata/explanations
- guardrails against unsupported answers

**Validation gate**

- generated answers can be traced to query results
- AI cannot access credentials
- unsupported questions are handled explicitly
- numeric answers reconcile with warehouse queries

Status: **PLANNED**

---

## Final release gate

Nothing is merged to `main` until:

- Python tests pass
- data-quality tests pass
- dbt build/tests pass
- orchestration path is validated
- backtesting is reproducible
- documentation matches the implemented system
- secrets and generated local files are excluded
- the branch is reviewed as a complete portfolio project
- merge is explicitly approved

## Progress

| Phase | Status |
| --- | --- |
| Repository cleanup | Complete on cleanup branch |
| 1. Python ingestion | Complete |
| 2. Snowflake RAW | Complete |
| 3. dbt transformations | Complete — real Snowflake validated |
| 4. Airflow orchestration | Planned |
| 5. ML redesign | Planned |
| 6. CI/CD | In progress |
| 7. AI analytics | Planned |
| Final validation | Pending |
