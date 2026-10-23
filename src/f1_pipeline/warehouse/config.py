import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SnowflakeSettings:
    account: str
    user: str
    warehouse: str
    database: str = "F1_ANALYTICS"
    schema: str = "RAW"
    role: str | None = None
    password: str | None = None

    @classmethod
    def from_env(cls) -> "SnowflakeSettings":
        required = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        }
        missing = [name.upper() for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing Snowflake environment settings: {', '.join(missing)}")
        return cls(
            **required,
            database=os.getenv("SNOWFLAKE_DATABASE", "F1_ANALYTICS"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
            role=os.getenv("SNOWFLAKE_ROLE"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
        )
