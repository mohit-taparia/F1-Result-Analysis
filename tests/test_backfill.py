from unittest.mock import Mock, call

import pytest

from f1_pipeline.backfill_main import backfill_seasons, validate_season_range


def test_validate_season_range_accepts_inclusive_range():
    validate_season_range(2010, 2024)
    validate_season_range(2024, 2024)


@pytest.mark.parametrize(
    ("start_season", "end_season"),
    [
        (1949, 2024),
        (2024, 2023),
    ],
)
def test_validate_season_range_rejects_invalid_ranges(start_season, end_season):
    with pytest.raises(ValueError):
        validate_season_range(start_season, end_season)


def test_backfill_processes_seasons_in_order(monkeypatch):
    connection = Mock()
    settings = Mock()
    client = Mock()

    season_data = {
        2022: {
            "races": [{"season": 2022}],
            "results": [{"season": 2022}],
        },
        2023: {
            "races": [{"season": 2023}],
            "results": [{"season": 2023}],
        },
    }

    collect = Mock(side_effect=lambda _client, season: season_data[season])
    load = Mock(side_effect=["load-1", "load-2", "load-3", "load-4"])
    monkeypatch.setattr("f1_pipeline.backfill_main.collect_season", collect)
    monkeypatch.setattr("f1_pipeline.backfill_main.load_records", load)

    backfill_seasons(connection, settings, client, 2022, 2023)

    assert collect.call_args_list == [call(client, 2022), call(client, 2023)]
    assert load.call_args_list == [
        call(connection, settings, "races", season_data[2022]["races"]),
        call(connection, settings, "results", season_data[2022]["results"]),
        call(connection, settings, "races", season_data[2023]["races"]),
        call(connection, settings, "results", season_data[2023]["results"]),
    ]


def test_backfill_stops_before_loading_failed_season(monkeypatch):
    connection = Mock()
    settings = Mock()
    client = Mock()

    def collect(_client, season):
        if season == 2023:
            raise RuntimeError("source validation failed")
        return {"races": [{"season": season}]}

    load = Mock(return_value="load-id")
    monkeypatch.setattr("f1_pipeline.backfill_main.collect_season", collect)
    monkeypatch.setattr("f1_pipeline.backfill_main.load_records", load)

    with pytest.raises(RuntimeError, match="source validation failed"):
        backfill_seasons(connection, settings, client, 2022, 2024)

    load.assert_called_once_with(connection, settings, "races", [{"season": 2022}])
