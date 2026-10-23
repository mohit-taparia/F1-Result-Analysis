import argparse
import logging

from f1_pipeline.ingestion import (
    fetch_constructor_standings,
    fetch_driver_standings,
    fetch_qualifying,
    fetch_races,
    fetch_results,
)
from f1_pipeline.ingestion.client import JolpicaClient
from f1_pipeline.validation import validate_records
from f1_pipeline.warehouse import SnowflakeSettings, bootstrap_raw_schema, connect, load_records

LOGGER = logging.getLogger(__name__)


def _validate(dataset: str, records: list[dict]) -> None:
    keys = {
        "races": ("season", "round"),
        "results": ("season", "round", "driver_id"),
        "qualifying": ("season", "round", "driver_id"),
        "driver_standings": ("season", "round", "driver_id"),
        "constructor_standings": ("season", "round", "constructor_id"),
    }
    validate_records(records, dataset=dataset, required_fields=keys[dataset], unique_key=keys[dataset])


def collect_season(client: JolpicaClient, season: int) -> dict[str, list[dict]]:
    races = fetch_races(client, season)
    results = fetch_results(client, season)
    qualifying = fetch_qualifying(client, season)

    driver_standings: list[dict] = []
    constructor_standings: list[dict] = []
    for race in races:
        round_number = race["round"]
        driver_standings.extend(fetch_driver_standings(client, season, round_number))
        constructor_standings.extend(fetch_constructor_standings(client, season, round_number))

    datasets = {
        "races": races,
        "results": results,
        "qualifying": qualifying,
        "driver_standings": driver_standings,
        "constructor_standings": constructor_standings,
    }
    for name, records in datasets.items():
        _validate(name, records)
    return datasets


def main() -> None:
    parser = argparse.ArgumentParser(description="Load a Formula 1 season into Snowflake RAW")
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--bootstrap", action="store_true", help="Create the five RAW tables if they do not exist")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    settings = SnowflakeSettings.from_env()
    datasets = collect_season(JolpicaClient(), args.season)

    with connect(settings) as connection:
        if args.bootstrap:
            bootstrap_raw_schema(connection, settings)
        for dataset, records in datasets.items():
            load_id = load_records(connection, settings, dataset, records)
            LOGGER.info("Loaded %s records into RAW.%s (load_id=%s)", len(records), dataset.upper(), load_id)


if __name__ == "__main__":
    main()
