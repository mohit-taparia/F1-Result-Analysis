from datetime import datetime

import pytest

from f1_pipeline.warehouse.config import SnowflakeSettings
from f1_pipeline.warehouse.loader import _rows_for_load, load_records
from f1_pipeline.warehouse.specs import TABLE_SPECS


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def execute(self, sql):
        self.connection.statements.append(sql)
        if self.connection.fail_on_merge and sql.startswith("MERGE"):
            raise RuntimeError("merge failed")
        return self

    def executemany(self, sql, rows):
        self.connection.batch = (sql, rows)
        return self


class FakeConnection:
    def __init__(self, fail_on_merge=False):
        self.fail_on_merge = fail_on_merge
        self.statements = []
        self.batch = None
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def settings():
    return SnowflakeSettings(account="acct", user="user", warehouse="wh")


def test_rows_add_lineage_metadata_and_serialize_variant():
    spec = TABLE_SPECS["driver_standings"]
    records = [{
        "season": 2024, "round": 1, "driver_id": "verstappen", "driver_code": "VER",
        "position": 1, "position_text": "1", "points": 26.0, "wins": 1,
        "constructor_ids": ["red_bull"],
    }]
    rows = _rows_for_load(spec, records, "load-123", datetime(2026, 1, 1))
    assert '["red_bull"]' in rows[0]
    assert "load-123" in rows[0]
    assert "jolpica_ergast_compatible_api" in rows[0]


def test_variant_insert_parses_json_outside_values_clause():
    connection = FakeConnection()
    record = {
        "season": 2024, "round": 1, "driver_id": "verstappen", "driver_code": "VER",
        "position": 1, "position_text": "1", "points": 26.0, "wins": 1,
        "constructor_ids": ["red_bull"],
    }
    load_records(connection, settings(), "driver_standings", [record], load_id="fixed-load")
    insert_sql, _rows = connection.batch
    assert "PARSE_JSON(?)" not in insert_sql
    assert "PARSE_JSON(column9)" in insert_sql
    assert "FROM VALUES (" in insert_sql


def test_load_records_stages_merges_and_commits():
    connection = FakeConnection()
    record = {"season": 2024, "round": 1, "race_name": "Bahrain Grand Prix", "race_date": "2024-03-02",
              "circuit_id": "bahrain", "circuit_name": "Bahrain International Circuit"}
    load_id = load_records(connection, settings(), "races", [record], load_id="fixed-load")
    assert load_id == "fixed-load"
    assert connection.batch is not None
    assert any(statement.startswith("CREATE TEMP TABLE") for statement in connection.statements)
    assert any(statement.startswith("MERGE") for statement in connection.statements)
    assert connection.committed is True
    assert connection.rolled_back is False


def test_load_records_rolls_back_on_failure():
    connection = FakeConnection(fail_on_merge=True)
    record = {"season": 2024, "round": 1, "race_name": "Bahrain Grand Prix", "race_date": "2024-03-02",
              "circuit_id": "bahrain"}
    with pytest.raises(RuntimeError, match="merge failed"):
        load_records(connection, settings(), "races", [record], load_id="fixed-load")
    assert connection.committed is False
    assert connection.rolled_back is True


def test_load_records_rejects_empty_input():
    with pytest.raises(ValueError, match="empty dataset"):
        load_records(FakeConnection(), settings(), "races", [])
