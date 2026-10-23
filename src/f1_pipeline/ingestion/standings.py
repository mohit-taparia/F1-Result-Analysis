from typing import Any

from .client import JolpicaClient
from .common import as_float, as_int


def fetch_driver_standings(client: JolpicaClient, season: int | str, round_number: int | str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for payload in client.iter_pages(f"{season}/{round_number}/driverstandings/"):
        lists = payload["MRData"].get("StandingsTable", {}).get("StandingsLists", [])
        for standings_list in lists:
            for item in standings_list.get("DriverStandings", []):
                driver = item.get("Driver") or {}
                constructors = item.get("Constructors") or []
                records.append({
                    "season": as_int(standings_list.get("season", season)),
                    "round": as_int(standings_list.get("round", round_number)),
                    "driver_id": driver.get("driverId"),
                    "driver_code": driver.get("code"),
                    "position": as_int(item.get("position")),
                    "position_text": item.get("positionText"),
                    "points": as_float(item.get("points")),
                    "wins": as_int(item.get("wins")),
                    "constructor_ids": [c.get("constructorId") for c in constructors if c.get("constructorId")],
                })
    return records


def fetch_constructor_standings(client: JolpicaClient, season: int | str, round_number: int | str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for payload in client.iter_pages(f"{season}/{round_number}/constructorstandings/"):
        lists = payload["MRData"].get("StandingsTable", {}).get("StandingsLists", [])
        for standings_list in lists:
            for item in standings_list.get("ConstructorStandings", []):
                constructor = item.get("Constructor") or {}
                records.append({
                    "season": as_int(standings_list.get("season", season)),
                    "round": as_int(standings_list.get("round", round_number)),
                    "constructor_id": constructor.get("constructorId"),
                    "constructor_name": constructor.get("name"),
                    "position": as_int(item.get("position")),
                    "position_text": item.get("positionText"),
                    "points": as_float(item.get("points")),
                    "wins": as_int(item.get("wins")),
                })
    return records
