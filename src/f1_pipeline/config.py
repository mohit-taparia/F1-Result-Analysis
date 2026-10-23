from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    base_url: str = "https://api.jolpi.ca/ergast/f1"
    user_agent: str = "F1ModernDataPlatform/0.1.0"
    timeout_seconds: float = 20.0
    page_size: int = 100
    max_retries: int = 3
    backoff_factor: float = 0.75
