import pytest

from f1_pipeline.warehouse.specs import TABLE_SPECS
from f1_pipeline.warehouse.sql import create_table_sql, merge_sql, quote_identifier


def test_identifier_validation_rejects_sql_fragments():
    with pytest.raises(ValueError, match="Unsafe Snowflake identifier"):
        quote_identifier("RAW; DROP DATABASE F1")


def test_create_results_table_contains_operational_metadata():
    sql = create_table_sql("F1_ANALYTICS", "RAW", TABLE_SPECS["results"])
    assert '"F1_ANALYTICS"."RAW"."RESULTS"' in sql
    assert '"LOAD_ID" VARCHAR NOT NULL' in sql
    assert '"SOURCE" VARCHAR NOT NULL' in sql
    assert '"LOADED_AT" TIMESTAMP_TZ NOT NULL' in sql


def test_merge_uses_results_business_key_and_upsert():
    sql = merge_sql("F1_ANALYTICS", "RAW", TABLE_SPECS["results"], "tmp_results_abc")
    assert 't."SEASON" = s."SEASON"' in sql
    assert 't."ROUND" = s."ROUND"' in sql
    assert 't."DRIVER_ID" = s."DRIVER_ID"' in sql
    assert "WHEN MATCHED THEN UPDATE" in sql
    assert "WHEN NOT MATCHED THEN INSERT" in sql
