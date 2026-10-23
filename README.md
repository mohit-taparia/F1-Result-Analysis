# Formula 1 Race Result Analysis & Winner Prediction

A Formula 1 analytics and machine-learning project built from historical race, qualifying, weather, driver-standing, and constructor-standing data.

This repository began as an academic machine-learning project. The current version is being refactored into a more production-oriented data project with clearer ingestion, transformation, validation, modeling, and evaluation stages.

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

## Modernization roadmap

The next version is intended to evolve this project from a notebook-based ML exercise into an end-to-end data engineering and analytics system.

Planned areas of improvement:

- replace the retired Ergast host with the maintained Jolpica F1 API
- separate ingestion, transformation, feature engineering, training, and inference into reusable Python modules
- introduce a warehouse-oriented RAW / STAGING / MART data model
- implement SQL/dbt transformations and automated data-quality tests
- use incremental ingestion instead of rebuilding historical datasets
- orchestrate ingestion, transformation, testing, and model runs
- implement season-based and rolling-window backtesting to prevent temporal leakage
- evaluate ranking metrics and race-winner accuracy rather than relying on imbalanced binary accuracy
- add CI checks for Python, SQL, and data-model changes
- expose curated F1 data through an analytics or AI interface

See the project roadmap in this README for proposed architecture options before those components are implemented.

## Proposed target architecture

One possible modernization path is:

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

This architecture is a **target design**, not a description of the current implementation.

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
**Repository cleanup:** in progress  
**Modern data-engineering rebuild:** planned

The goal of the rebuild is not simply to increase a model accuracy number. It is to create a reproducible data platform that demonstrates ingestion, transformation, data quality, orchestration, ML evaluation, and AI-enabled analytics on Formula 1 data.
