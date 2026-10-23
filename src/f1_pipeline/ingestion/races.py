from typing import Any

from .client import JolpicaClient
from .common import as_int, circuit_fields


def _normalize_race(race: dict[str, Any]) -> dict[str, Any]:
    return {
        "season": as_int(race.get("season")),
        "round": as_int(race.get("round")),
        "race_name": race.get("raceName"),
        "race_date": race.get("date"),
        "race_time_utc": race.get("time"),
        "source_url": race.get("url"),
        **circuit_fields(race),
    }


def fetch_races(client: JolpicaClient, season: int | str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for payload in client.iter_pages(f"{season}/races/"):
        races = payload["MRData"].get("RaceTable", {}).get("Races", [])
        records.extend(_normalize_race(race) for race in races)
    return records
