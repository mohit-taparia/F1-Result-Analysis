from collections.abc import Iterable
from typing import Any


class DataValidationError(ValueError):
    """Raised when source data does not satisfy minimum ingestion guarantees."""


def validate_records(
    records: list[dict[str, Any]],
    *,
    dataset: str,
    required_fields: Iterable[str],
    unique_key: Iterable[str],
    allow_empty: bool = False,
) -> None:
    if not records and not allow_empty:
        raise DataValidationError(f"{dataset}: source returned no records")

    required_fields = tuple(required_fields)
    unique_key = tuple(unique_key)
    seen: set[tuple[Any, ...]] = set()

    for index, record in enumerate(records):
        missing = [field for field in required_fields if record.get(field) in (None, "")]
        if missing:
            raise DataValidationError(f"{dataset}: record {index} missing required fields {missing}")

        key = tuple(record.get(field) for field in unique_key)
        if key in seen:
            raise DataValidationError(f"{dataset}: duplicate key {key}")
        seen.add(key)
