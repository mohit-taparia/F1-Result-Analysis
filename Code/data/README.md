# Data

This directory contains CSV files used by the original Formula 1 analysis.

The repository currently stores both source-like datasets and generated modeling outputs together. That was convenient for the original academic project but is not the intended structure for the modernized pipeline.

## Current datasets

Examples include:

- `races.csv`
- `results.csv`
- `qualifying.csv`
- `driver_standings.csv`
- `constructor_standings.csv`
- `weather.csv`
- `dummies_removed.csv`
- grid-search and prediction outputs

## Planned data layout

The rebuild will separate data by lifecycle rather than mixing inputs and generated outputs:

```text
RAW       -> API payloads / minimally transformed source data
STAGING   -> typed, standardized, deduplicated records
MART      -> race, driver, constructor, and ML feature models
PREDICT   -> model scores and race-level predictions
```

For a warehouse-backed version, these layers should live in the data platform rather than as large generated CSV files committed to Git.
