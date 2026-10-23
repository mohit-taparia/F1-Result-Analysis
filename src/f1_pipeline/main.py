import argparse
import logging
from pathlib import Path

from f1_pipeline.ingestion import (
    fetch_constructor_standings,
    fetch_driver_standings,
    fetch_qualifying,
    fetch_races,
    fetch_results,
)
from f1_pipeline.ingestion.client import JolpicaClient
from f1_pipeline.io import write_jsonl
from f1_pipeline.validation import validate_records

LOGGER = logging.getLogger(__name__)


def _save(name: str, records: list[dict], output_dir: Path, required: tuple[str, ...], key: tuple[str, ...]) -> None:
    validate_records(records, dataset=name, required_fields=required, unique_key=key)
    path = output_dir / f"{name}.jsonl"
    write_jsonl(records, path)
    LOGGER.info("Wrote %s records to %s", len(records), path)


def ingest_season(season: int, output_dir: Path) -> None:
    client = JolpicaClient()
    races = fetch_races(client, season)
    _save("races", races, output_dir, ("season", "round", "circuit_id"), ("season", "round"))

    results = fetch_results(client, season)
    _save("results", results, output_dir, ("season", "round", "driver_id"), ("season", "round", "driver_id"))

    qualifying = fetch_qualifying(client, season)
    _save("qualifying", qualifying, output_dir, ("season", "round", "driver_id"), ("season", "round", "driver_id"))

    driver_standings: list[dict] = []
    constructor_standings: list[dict] = []
    for race in races:
        round_number = race["round"]
        driver_standings.extend(fetch_driver_standings(client, season, round_number))
        constructor_standings.extend(fetch_constructor_standings(client, season, round_number))

    _save(
        "driver_standings",
        driver_standings,
        output_dir,
        ("season", "round", "driver_id"),
        ("season", "round", "driver_id"),
    )
    _save(
        "constructor_standings",
        constructor_standings,
        output_dir,
        ("season", "round", "constructor_id"),
        ("season", "round", "constructor_id"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Formula 1 season data from Jolpica")
    parser.add_argument("--season", type=int, required=True, help="Season to ingest, e.g. 2025")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    ingest_season(args.season, args.output_dir / str(args.season))


if __name__ == "__main__":
    main()
