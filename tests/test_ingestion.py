import pytest

from f1_pipeline.ingestion.qualifying import fetch_qualifying
from f1_pipeline.ingestion.races import fetch_races
from f1_pipeline.ingestion.results import fetch_results
from f1_pipeline.ingestion.standings import fetch_constructor_standings, fetch_driver_standings
from f1_pipeline.validation import DataValidationError, validate_records


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.paths = []

    def iter_pages(self, path):
        self.paths.append(path)
        yield self.payload


def test_fetch_races_normalizes_types():
    payload = {"MRData": {"RaceTable": {"Races": [{
        "season": "2025", "round": "1", "raceName": "Example GP", "date": "2025-03-01",
        "Circuit": {"circuitId": "example", "circuitName": "Example Circuit", "Location": {
            "lat": "1.5", "long": "2.5", "locality": "City", "country": "Country"
        }}
    }]}}}
    records = fetch_races(FakeClient(payload), 2025)
    assert records[0]["season"] == 2025
    assert records[0]["round"] == 1
    assert records[0]["latitude"] == 1.5


def test_fetch_results_flattens_nested_race_results():
    payload = {"MRData": {"RaceTable": {"Races": [{
        "season": "2025", "round": "1", "raceName": "Example GP", "date": "2025-03-01",
        "Circuit": {"circuitId": "example"},
        "Results": [{
            "number": "1", "position": "1", "points": "25", "grid": "2", "laps": "57", "status": "Finished",
            "Driver": {"driverId": "driver_a", "code": "AAA", "givenName": "A", "familyName": "Driver"},
            "Constructor": {"constructorId": "team_a", "name": "Team A"}
        }]
    }]}}}
    record = fetch_results(FakeClient(payload), 2025)[0]
    assert record["driver_id"] == "driver_a"
    assert record["finish_position"] == 1
    assert record["points"] == 25.0


def test_fetch_qualifying_preserves_session_times():
    payload = {"MRData": {"RaceTable": {"Races": [{
        "season": "2025", "round": "1", "Circuit": {"circuitId": "example"},
        "QualifyingResults": [{
            "number": "4", "position": "1", "Q1": "1:20.000", "Q2": "1:19.500", "Q3": "1:19.000",
            "Driver": {"driverId": "driver_a"}, "Constructor": {"constructorId": "team_a", "name": "Team A"}
        }]
    }]}}}
    record = fetch_qualifying(FakeClient(payload), 2025)[0]
    assert record["qualifying_position"] == 1
    assert record["q3"] == "1:19.000"


def test_driver_standings_are_round_specific():
    payload = {"MRData": {"StandingsTable": {"StandingsLists": [{
        "season": "2025", "round": "3", "DriverStandings": [{
            "position": "1", "points": "62", "wins": "2",
            "Driver": {"driverId": "driver_a", "code": "AAA"},
            "Constructors": [{"constructorId": "team_a"}]
        }]
    }]}}}
    client = FakeClient(payload)
    record = fetch_driver_standings(client, 2025, 3)[0]
    assert client.paths == ["2025/3/driverstandings/"]
    assert record["round"] == 3
    assert record["wins"] == 2


def test_validation_rejects_duplicate_business_keys():
    records = [
        {"season": 2025, "round": 1, "driver_id": "a"},
        {"season": 2025, "round": 1, "driver_id": "a"},
    ]
    with pytest.raises(DataValidationError, match="duplicate key"):
        validate_records(
            records,
            dataset="results",
            required_fields=("season", "round", "driver_id"),
            unique_key=("season", "round", "driver_id"),
        )


def test_constructor_standings_are_round_specific():
    payload = {"MRData": {"StandingsTable": {"StandingsLists": [{
        "season": "2025", "round": "3", "ConstructorStandings": [{
            "position": "1", "points": "110", "wins": "4",
            "Constructor": {"constructorId": "team_a", "name": "Team A"}
        }]
    }]}}}
    client = FakeClient(payload)
    record = fetch_constructor_standings(client, 2025, 3)[0]
    assert client.paths == ["2025/3/constructorstandings/"]
    assert record["constructor_id"] == "team_a"
    assert record["points"] == 110.0
