import argparse
import logging

from f1_pipeline.ingestion.client import JolpicaClient
from f1_pipeline.warehouse import SnowflakeSettings, bootstrap_raw_schema, connect, load_records
from f1_pipeline.warehouse_main import collect_season

LOGGER = logging.getLogger(__name__)
FIRST_F1_SEASON = 1950


def validate_season_range(start_season: int, end_season: int) -> None:
    if start_season < FIRST_F1_SEASON:
        raise ValueError(f"start season must be >= {FIRST_F1_SEASON}")
    if end_season < start_season:
        raise ValueError("end season must be greater than or equal to start season")


def backfill_seasons(
    connection,
    settings: SnowflakeSettings,
    client: JolpicaClient,
    start_season: int,
    end_season: int,
) -> None:
    """Collect, validate, and MERGE seasons into Snowflake RAW in ascending order."""
    validate_season_range(start_season, end_season)

    for season in range(start_season, end_season + 1):
        LOGGER.info("Backfill season %s: collecting and validating source data", season)
        datasets = collect_season(client, season)

        for dataset, records in datasets.items():
            load_id = load_records(connection, settings, dataset, records)
            LOGGER.info(
                "Backfill season %s: loaded %s %s records (load_id=%s)",
                season,
                len(records),
                dataset,
                load_id,
            )

        LOGGER.info("Backfill season %s: complete", season)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill an inclusive Formula 1 season range into Snowflake RAW"
    )
    parser.add_argument("--start-season", type=int, required=True)
    parser.add_argument("--end-season", type=int, required=True)
    parser.add_argument(
        "--bootstrap",
        action="store_true",
        help="Create the five RAW tables if they do not exist",
    )
    args = parser.parse_args()

    try:
        validate_season_range(args.start_season, args.end_season)
    except ValueError as exc:
        parser.error(str(exc))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    settings = SnowflakeSettings.from_env()
    client = JolpicaClient()

    with connect(settings) as connection:
        if args.bootstrap:
            bootstrap_raw_schema(connection, settings)
        backfill_seasons(
            connection,
            settings,
            client,
            args.start_season,
            args.end_season,
        )


if __name__ == "__main__":
    main()
