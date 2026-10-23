import json
import uuid
from datetime import datetime, timezone
from typing import Any

from .config import SnowflakeSettings
from .specs import TABLE_SPECS, TableSpec
from .sql import create_table_sql, create_temp_table_sql, merge_sql, quote_identifier

SOURCE_NAME = "jolpica_ergast_compatible_api"


def connect(settings: SnowflakeSettings):
    try:
        import snowflake.connector
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the 'snowflake' project extra to load data into Snowflake") from exc

    kwargs = {
        "account": settings.account,
        "user": settings.user,
        "warehouse": settings.warehouse,
        "autocommit": False,
    }
    if settings.role:
        kwargs["role"] = settings.role
    if settings.password:
        kwargs["password"] = settings.password
    return snowflake.connector.connect(**kwargs)


def bootstrap_raw_schema(connection, settings: SnowflakeSettings) -> None:
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {quote_identifier(settings.database)}")
        cursor.execute(
            f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(settings.database)}.{quote_identifier(settings.schema)}"
        )
        for spec in TABLE_SPECS.values():
            cursor.execute(create_table_sql(settings.database, settings.schema, spec))
    connection.commit()


def _serialize_value(column_type: str, value: Any) -> Any:
    if value is None:
        return None
    if column_type == "VARIANT":
        return json.dumps(value, separators=(",", ":"))
    return value


def _rows_for_load(spec: TableSpec, records: list[dict[str, Any]], load_id: str, loaded_at: datetime):
    rows = []
    for record in records:
        enriched = {**record, "load_id": load_id, "source": SOURCE_NAME, "loaded_at": loaded_at}
        rows.append(
            tuple(_serialize_value(column.snowflake_type, enriched.get(column.name)) for column in spec.columns)
        )
    return rows


def load_records(
    connection,
    settings: SnowflakeSettings,
    dataset: str,
    records: list[dict[str, Any]],
    *,
    load_id: str | None = None,
) -> str:
    if dataset not in TABLE_SPECS:
        raise ValueError(f"Unknown RAW dataset: {dataset}")
    if not records:
        raise ValueError(f"Refusing to load empty dataset: {dataset}")

    spec = TABLE_SPECS[dataset]
    load_id = load_id or str(uuid.uuid4())
    loaded_at = datetime.now(timezone.utc)
    temp_name = f"tmp_{dataset}_{load_id.replace('-', '')[:12]}"
    columns = ", ".join(quote_identifier(column.name) for column in spec.columns)
    placeholders = ", ".join(
        "PARSE_JSON(?)" if column.snowflake_type == "VARIANT" else "?" for column in spec.columns
    )
    insert_sql = f'INSERT INTO {quote_identifier(temp_name)} ({columns}) VALUES ({placeholders})'
    rows = _rows_for_load(spec, records, load_id, loaded_at)

    try:
        with connection.cursor() as cursor:
            cursor.execute(create_temp_table_sql(settings.database, settings.schema, spec, temp_name))
            cursor.executemany(insert_sql, rows)
            cursor.execute(merge_sql(settings.database, settings.schema, spec, temp_name))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return load_id
