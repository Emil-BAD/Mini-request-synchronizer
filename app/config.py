import os
from dataclasses import dataclass

DEFAULT_ORDERS_SOURCE_URL = "https://test.ooobs.ru/api/orders"


@dataclass(frozen=True)
class Settings:
    orders_source_url: str = os.getenv("ORDERS_SOURCE_URL", DEFAULT_ORDERS_SOURCE_URL)
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "10"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
