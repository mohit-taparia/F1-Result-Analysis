import re

from .specs import TableSpec

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


def quote_identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe Snowflake identifier: {value!r}")
    return f'"{value.upper()}"'


def qualified_table(database: str, schema: str, table: str) -> str:
    return ".".join(quote_identifier(x) for x in (database, schema, table))


def create_table_sql(database: str, schema: str, spec: TableSpec) -> str:
    columns = ",\n  ".join(
        f"{quote_identifier(column.name)} {column.snowflake_type}" for column in spec.columns
    )
    return f"CREATE TABLE IF NOT EXISTS {qualified_table(database, schema, spec.name)} (\n  {columns}\n)"


def create_temp_table_sql(database: str, schema: str, spec: TableSpec, temp_name: str) -> str:
    target = qualified_table(database, schema, spec.name)
    temp = quote_identifier(temp_name)
    return f"CREATE TEMP TABLE {temp} LIKE {target}"


def merge_sql(database: str, schema: str, spec: TableSpec, temp_name: str) -> str:
    target = qualified_table(database, schema, spec.name)
    temp = quote_identifier(temp_name)
    on_clause = " AND ".join(
        f't.{quote_identifier(key)} = s.{quote_identifier(key)}' for key in spec.key_columns
    )
    non_keys = [column.name for column in spec.columns if column.name not in spec.key_columns]
    updates = ",\n    ".join(
        f'{quote_identifier(name)} = s.{quote_identifier(name)}' for name in non_keys
    )
    column_names = ", ".join(quote_identifier(column.name) for column in spec.columns)
    source_names = ", ".join(f's.{quote_identifier(column.name)}' for column in spec.columns)
    return f"""MERGE INTO {target} t
USING {temp} s
ON {on_clause}
WHEN MATCHED THEN UPDATE SET
    {updates}
WHEN NOT MATCHED THEN INSERT ({column_names})
VALUES ({source_names})"""
