from typing import Any

from .client import JolpicaClient
from .common import as_float, as_int


def _normalize_result(race: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    driver = result.get("Driver") or {}
    constructor = result.get("Constructor") or {}
    finish_time = result.get("Time") or {}
    fastest_lap = result.get("FastestLap") or {}
    fastest_time = fastest_lap.get("Time") or {}
    avg_speed = fastest_lap.get("AverageSpeed") or {}
    circuit = race.get("Circuit") or {}

    return {
        "season": as_int(race.get("season")),
        "round": as_int(race.get("round")),
        "race_name": race.get("raceName"),
        "race_date": race.get("date"),
        "circuit_id": circuit.get("circuitId"),
        "driver_id": driver.get("driverId"),
        "driver_code": driver.get("code"),
        "driver_given_name": driver.get("givenName"),
        "driver_family_name": driver.get("familyName"),
        "driver_date_of_birth": driver.get("dateOfBirth"),
        "driver_nationality": driver.get("nationality"),
        "constructor_id": constructor.get("constructorId"),
        "constructor_name": constructor.get("name"),
        "car_number": result.get("number"),
        "grid_position": as_int(result.get("grid")),
        "finish_position": as_int(result.get("position")),
        "position_text": result.get("positionText"),
        "points": as_float(result.get("points")),
        "laps": as_int(result.get("laps")),
        "status": result.get("status"),
        "finish_time_millis": as_int(finish_time.get("millis")),
        "fastest_lap_rank": as_int(fastest_lap.get("rank")),
        "fastest_lap_number": as_int(fastest_lap.get("lap")),
        "fastest_lap_time": fastest_time.get("time"),
        "fastest_lap_avg_speed": as_float(avg_speed.get("speed")),
        "fastest_lap_avg_speed_units": avg_speed.get("units"),
    }


def fetch_results(client: JolpicaClient, season: int | str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for payload in client.iter_pages(f"{season}/results/"):
        races = payload["MRData"].get("RaceTable", {}).get("Races", [])
        for race in races:
            records.extend(_normalize_result(race, result) for result in race.get("Results", []))
    return records
