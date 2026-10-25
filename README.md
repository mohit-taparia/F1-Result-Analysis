# Formula 1 Race Result Analysis & Winner Prediction

A Formula 1 analytics and machine-learning project built from historical race, qualifying, weather, driver-standing, and constructor-standing data.

This repository began as an academic machine-learning project. The active modernization branch now contains a reusable Python ingestion layer, a validated Snowflake RAW loader, dbt STAGING/CORE models, and a leakage-aware ML feature mart. Airflow orchestration, time-aware model backtesting, and AI analytics remain later phases.

## What the current project does

The existing implementation:

1. Collects historical Formula 1 data from the Ergast-compatible API.
2. Combines race results, qualifying data, weather data, driver standings, and constructor standings.
3. Engineers pre-race features such as grid position, prior standings, prior wins, qualifying-time differences, and driver age.
4. Trains a Random Forest classifier to rank drivers by predicted win probability.
5. Produces race-level winner predictions and model evaluation outputs.

Historical data in the original project covers Formula 1 seasons from 1950 through 2023, depending on source availability.

## Current architecture

```text
Formula 1 API / source CSVs
            |
            v
     Data ingestion
     scrape.ipynb
            |
            v
 Cleaning + integration
 cleaning&processing.ipynb
            |
            v
   Feature engineering
            |
            v
 Random Forest modeling
   Final_code.ipynb
            |
            v
 Predictions + evaluation
```

## Repository structure

```text
.
├── Code/
│   ├── scrape.ipynb
│   ├── cleaning&processing.ipynb
│   ├── Final_code.ipynb
│   ├── data/
│   ├── Images/
│   └── Prediction/
├── final_project.tex
├── final_project.pdf
├── bibliography.bib
└── README.md
```

### Main notebooks

| Notebook | Purpose |
| --- | --- |
| `Code/scrape.ipynb` | Collects race, result, driver-standing, and constructor-standing data |
| `Code/cleaning&processing.ipynb` | Joins source datasets, handles missing values, and engineers modeling features |
| `Code/Final_code.ipynb` | Performs analysis, model selection, Random Forest training, evaluation, and race-level predictions |

## Data pipeline

The project integrates multiple datasets around season, round, circuit, driver, and constructor identifiers.

Key inputs include:

- race schedule and circuit information
- race results
- qualifying results
- driver standings
- constructor standings
- weather information

An important part of the original ingestion logic shifts championship standings by one race so that a prediction uses information available **before** the race rather than post-race standings.

## Machine-learning approach

The original project treats race winning as a binary classification problem:

- `1` — driver wins the race
- `0` — driver does not win

A Random Forest classifier is trained on historical features, and predicted probabilities are used to rank the drivers in each race. The driver with the highest predicted win probability is selected as the race prediction.

### Important evaluation note

The original report emphasized overall classification accuracy. That metric is misleading for this problem because only one driver wins each race, creating a heavily imbalanced target.

The stored report shows high overall accuracy while also showing zero precision and recall for the positive winner class in one evaluation. The current modeling workflow also contains evaluation choices that should be improved, including random train/test splitting of time-dependent race data and model selection against a season later used for evaluation.

These limitations are retained in the legacy notebooks for transparency and will be addressed in the modernization work.

## Modern platform status

The next version is intended to evolve this project from a notebook-based ML exercise into an end-Implemented on the active modernization branch:

- Jolpica API ingestion with retries, pagination, validation, and live-contract testing
- Snowflake RAW loading for races, results, qualifying, driver standings, and constructor standings
- rerunnable business-key MERGE loads with lineage metadata and rollback protection
- dbt STAGING models for source cleanup and type normalization
- dbt CORE dimensions/facts for reusable Formula 1 entities
- `mart_race_features` with prior-round standings and prior-race form to reduce temporal leakage
- automated Python tests, live API smoke tests, dbt parsing, and Python linting in CI

Still pending:

- real Snowflake `dbt build` validation of the Phase 3 models
- Airflow orchestration
- time-aware ML training/backtesting and race-level evaluation
- prediction persistence
- governed AI/natural-language analytics

See `docs/IMPLEMENTATION_PLAN.md` and `docs/DBT_TRANSFORMATIONS.md` for the detailed architecture and validation gates.

 |
      v
Python ingestion
      |
      v
Snowflake RAW
      |
      v
dbt STAGING / MART models
      |
      +------> analytics / dashboards
      |
      v
ML feature tables
      |
      v
time-aware model training + backtesting
      |
      v
prediction table
      |
      v
AI / natural-language analytics layer
```

The ingestion, Snowflake RAW, and dbt layers shown above are implemented on the active modernization branch; downstream orchestration, ML backtesting, predictions, and AI analytics remain target components.

## Running the legacy project

The existing project is notebook-based.

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
jupyter notebook
```

Run the notebooks in this general order:

1. `Code/scrape.ipynb` — only if rebuilding source data
2. `Code/cleaning&processing.ipynb`
3. `Code/Final_code.ipynb`

> **Note:** The legacy notebooks contain some historical local paths and API assumptions. Full reproducibility is part of the modernization work rather than something the current repository guarantees.

## Original report

The academic write-up is retained in `final_project.pdf` and `final_project.tex` as a record of the original project.

## Status

**Legacy implementation:** preserved  
**Repository cleanup:** complete on the modernization branch  
**Python ingestion:** implemented and CI-validated  
**Snowflake RAW:** implemented and warehouse-validated  
**dbt transformations:** implemented; real Snowflake build pending  
**Airflow / ML redesign / AI analytics:** pending

The goal of the rebuild is not simply to increase a model accuracy number. It is to create a reproducible data platform that demonstrates ingestion, transformation, data quality, orchestration, ML evaluation, and AI-enabled analytics on Formula 1 data.
