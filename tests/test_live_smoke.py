"""Optional live integration smoke test.

Run manually with:
    RUN_LIVE_F1_TESTS=1 pytest -m live

It intentionally exercises a small slice of a completed season so normal CI
does not depend on an external API.
"""
import os

import pytest

from f1_pipeline.ingestion import (
    fetch_constructor_standings,
    fetch_driver_standings,
    fetch_qualifying,
    fetch_races,
    fetch_results,
)
from f1_pipeline.ingestion.client import JolpicaClient
from f1_pipeline.validation import validate_records

pytestmark = pytest.mark.live


@pytest.mark.skipif(os.getenv("RUN_LIVE_F1_TESTS") != "1", reason="live API smoke test is opt-in")
def test_completed_2024_season_api_contract():
    client = JolpicaClient()

    races = fetch_races(client, 2024)
    results = fetch_results(client, 2024)
    qualifying = fetch_qualifying(client, 2024)
    driver_standings = fetch_driver_standings(client, 2024, 1)
    constructor_standings = fetch_constructor_standings(client, 2024, 1)

    # 2024 is a fixed, completed season and therefore a useful contract fixture.
    assert len(races) == 24

    validate_records(
        races,
        dataset="races",
        required_fields=("season", "round", "circuit_id"),
        unique_key=("season", "round"),
    )
    validate_records(
        results,
        dataset="results",
        required_fields=("season", "round", "driver_id"),
        unique_key=("season", "round", "driver_id"),
    )
    validate_records(
        qualifying,
        dataset="qualifying",
        required_fields=("season", "round", "driver_id"),
        unique_key=("season", "round", "driver_id"),
    )
    validate_records(
        driver_standings,
        dataset="driver_standings",
        required_fields=("season", "round", "driver_id"),
        unique_key=("season", "round", "driver_id"),
    )
    validate_records(
        constructor_standings,
        dataset="constructor_standings",
        required_fields=("season", "round", "constructor_id"),
        unique_key=("season", "round", "constructor_id"),
    )

    assert {row["round"] for row in results} == set(range(1, 25))
    assert {row["round"] for row in qualifying} == set(range(1, 25))
