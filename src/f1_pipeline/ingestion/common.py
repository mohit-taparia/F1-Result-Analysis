from typing import Any


def as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def circuit_fields(race: dict[str, Any]) -> dict[str, Any]:
    circuit = race.get("Circuit") or {}
    location = circuit.get("Location") or {}
    return {
        "circuit_id": circuit.get("circuitId"),
        "circuit_name": circuit.get("circuitName"),
        "locality": location.get("locality"),
        "country": location.get("country"),
        "latitude": as_float(location.get("lat")),
        "longitude": as_float(location.get("long")),
    }
