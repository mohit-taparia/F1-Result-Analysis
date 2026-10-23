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

Status: **IN PROGRESS**

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

Remaining before Phase 1 is complete:

- live API smoke test against a known completed season
- verify endpoint record counts against real Jolpica responses
- add constructor-standings coverage and incomplete/current-season handling
- tighten failure/partial-load behavior after live testing
- add CI execution of the unit test suite

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

Status: **PLANNED**

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

Status: **PLANNED**

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
| 1. Python ingestion | Next |
| 2. Snowflake RAW | Planned |
| 3. dbt transformations | Planned |
| 4. Airflow orchestration | Planned |
| 5. ML redesign | Planned |
| 6. CI/CD | Planned |
| 7. AI analytics | Planned |
| Final validation | Pending |
