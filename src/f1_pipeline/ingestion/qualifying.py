from typing import Any

from .client import JolpicaClient
from .common import as_int


def _normalize_qualifying(race: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    driver = result.get("Driver") or {}
    constructor = result.get("Constructor") or {}
    circuit = race.get("Circuit") or {}
    return {
        "season": as_int(race.get("season")),
        "round": as_int(race.get("round")),
        "race_name": race.get("raceName"),
        "race_date": race.get("date"),
        "circuit_id": circuit.get("circuitId"),
        "driver_id": driver.get("driverId"),
        "driver_code": driver.get("code"),
        "constructor_id": constructor.get("constructorId"),
        "constructor_name": constructor.get("name"),
        "car_number": result.get("number"),
        "qualifying_position": as_int(result.get("position")),
        "q1": result.get("Q1"),
        "q2": result.get("Q2"),
        "q3": result.get("Q3"),
    }


def fetch_qualifying(client: JolpicaClient, season: int | str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for payload in client.iter_pages(f"{season}/qualifying/"):
        races = payload["MRData"].get("RaceTable", {}).get("Races", [])
        for race in races:
            records.extend(_normalize_qualifying(race, result) for result in race.get("QualifyingResults", []))
    return records
