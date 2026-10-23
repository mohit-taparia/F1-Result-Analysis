# Legacy notebooks

This directory contains the original notebook-based implementation of the Formula 1 project.

## Execution flow

```text
scrape.ipynb
      |
      v
source CSV files
      |
      v
cleaning&processing.ipynb
      |
      v
model-ready dataset
      |
      v
Final_code.ipynb
      |
      v
predictions / model artifact / evaluation plots
```

### `scrape.ipynb`

Collects historical race, result, driver-standing, and constructor-standing data. The notebook also contains logic for shifting standings so a race uses information from the previous round.

The notebook was written against the historical Ergast API host and contains local output paths that need to be replaced during modernization.

### `cleaning&processing.ipynb`

Combines race, result, weather, qualifying, driver-standing, and constructor-standing datasets. It also handles missing values and creates modeling features such as driver age and relative qualifying time.

### `Final_code.ipynb`

Creates the winner target, one-hot encodes categorical variables, explores correlations, trains Random Forest models, performs hyperparameter experiments, saves a model artifact, and generates race-level predictions.

## Known limitations

These notebooks are retained as the original implementation rather than presented as production-ready code.

The main issues to address in the rebuild are:

- notebook-only pipeline structure
- hard-coded local paths
- retired/changed upstream API assumptions
- inconsistent scaling/model-evaluation flow
- random splitting of time-dependent data in part of the evaluation
- hyperparameter selection that references the evaluation season
- class imbalance making raw accuracy a poor success metric
- generated data and model artifacts committed alongside source code
- limited automated testing and dependency pinning

The modernization work will move reusable logic into Python modules and SQL/dbt models while keeping these notebooks as historical reference.
