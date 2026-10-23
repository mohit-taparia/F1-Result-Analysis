from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    name: str
    snowflake_type: str


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: tuple[Column, ...]
    key_columns: tuple[str, ...]


METADATA_COLUMNS = (
    Column("load_id", "VARCHAR NOT NULL"),
    Column("source", "VARCHAR NOT NULL"),
    Column("loaded_at", "TIMESTAMP_TZ NOT NULL"),
)

TABLE_SPECS = {
    "races": TableSpec(
        name="races",
        columns=(
            Column("season", "NUMBER(4,0) NOT NULL"),
            Column("round", "NUMBER(3,0) NOT NULL"),
            Column("race_name", "VARCHAR"),
            Column("race_date", "DATE"),
            Column("race_time_utc", "VARCHAR"),
            Column("source_url", "VARCHAR"),
            Column("circuit_id", "VARCHAR NOT NULL"),
            Column("circuit_name", "VARCHAR"),
            Column("locality", "VARCHAR"),
            Column("country", "VARCHAR"),
            Column("latitude", "FLOAT"),
            Column("longitude", "FLOAT"),
        ) + METADATA_COLUMNS,
        key_columns=("season", "round"),
    ),
    "results": TableSpec(
        name="results",
        columns=(
            Column("season", "NUMBER(4,0) NOT NULL"),
            Column("round", "NUMBER(3,0) NOT NULL"),
            Column("race_name", "VARCHAR"),
            Column("race_date", "DATE"),
            Column("circuit_id", "VARCHAR"),
            Column("driver_id", "VARCHAR NOT NULL"),
            Column("driver_code", "VARCHAR"),
            Column("driver_given_name", "VARCHAR"),
            Column("driver_family_name", "VARCHAR"),
            Column("driver_date_of_birth", "DATE"),
            Column("driver_nationality", "VARCHAR"),
            Column("constructor_id", "VARCHAR"),
            Column("constructor_name", "VARCHAR"),
            Column("car_number", "VARCHAR"),
            Column("grid_position", "NUMBER(3,0)"),
            Column("finish_position", "NUMBER(3,0)"),
            Column("position_text", "VARCHAR"),
            Column("points", "FLOAT"),
            Column("laps", "NUMBER(4,0)"),
            Column("status", "VARCHAR"),
            Column("finish_time_millis", "NUMBER(18,0)"),
            Column("fastest_lap_rank", "NUMBER(3,0)"),
            Column("fastest_lap_number", "NUMBER(4,0)"),
            Column("fastest_lap_time", "VARCHAR"),
            Column("fastest_lap_avg_speed", "FLOAT"),
            Column("fastest_lap_avg_speed_units", "VARCHAR"),
        ) + METADATA_COLUMNS,
        key_columns=("season", "round", "driver_id"),
    ),
    "qualifying": TableSpec(
        name="qualifying",
        columns=(
            Column("season", "NUMBER(4,0) NOT NULL"),
            Column("round", "NUMBER(3,0) NOT NULL"),
            Column("race_name", "VARCHAR"),
            Column("race_date", "DATE"),
            Column("circuit_id", "VARCHAR"),
            Column("driver_id", "VARCHAR NOT NULL"),
            Column("driver_code", "VARCHAR"),
            Column("constructor_id", "VARCHAR"),
            Column("constructor_name", "VARCHAR"),
            Column("car_number", "VARCHAR"),
            Column("qualifying_position", "NUMBER(3,0)"),
            Column("q1", "VARCHAR"),
            Column("q2", "VARCHAR"),
            Column("q3", "VARCHAR"),
        ) + METADATA_COLUMNS,
        key_columns=("season", "round", "driver_id"),
    ),
    "driver_standings": TableSpec(
        name="driver_standings",
        columns=(
            Column("season", "NUMBER(4,0) NOT NULL"),
            Column("round", "NUMBER(3,0) NOT NULL"),
            Column("driver_id", "VARCHAR NOT NULL"),
            Column("driver_code", "VARCHAR"),
            Column("position", "NUMBER(3,0)"),
            Column("position_text", "VARCHAR"),
            Column("points", "FLOAT"),
            Column("wins", "NUMBER(3,0)"),
            Column("constructor_ids", "VARIANT"),
        ) + METADATA_COLUMNS,
        key_columns=("season", "round", "driver_id"),
    ),
    "constructor_standings": TableSpec(
        name="constructor_standings",
        columns=(
            Column("season", "NUMBER(4,0) NOT NULL"),
            Column("round", "NUMBER(3,0) NOT NULL"),
            Column("constructor_id", "VARCHAR NOT NULL"),
            Column("constructor_name", "VARCHAR"),
            Column("position", "NUMBER(3,0)"),
            Column("position_text", "VARCHAR"),
            Column("points", "FLOAT"),
            Column("wins", "NUMBER(3,0)"),
        ) + METADATA_COLUMNS,
        key_columns=("season", "round", "constructor_id"),
    ),
}
