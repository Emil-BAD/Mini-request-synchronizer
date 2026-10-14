import logging

import httpx

from app.config import settings
from app.exceptions import OrdersSourceError

logger = logging.getLogger(__name__)


def handle_orders_error(message: str, status_code: int = 503):
    return OrdersSourceError(message=message, status_code=status_code)


async def fetch_orders() -> list[dict]:
    last_error: Exception | None = None

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                response = await client.get(settings.orders_source_url)

                if response.status_code >= 500:
                    raise OrdersSourceError(
                        "Orders source is temporarily unavailable",
                        status_code=503,
                    )
                if response.status_code >= 400:
                    raise OrdersSourceError(
                        f"Orders source returned HTTP {response.status_code}",
                        status_code=502,
                    )

                try:
                    payload = response.json()
                except ValueError as exc:  # pragma: no cover - exercised via server error tests
                    raise OrdersSourceError("Orders source returned invalid JSON", status_code=502) from exc

                if not isinstance(payload, list):
                    raise OrdersSourceError("Orders source returned unexpected JSON shape", status_code=502)

                return payload
        except OrdersSourceError:
            raise
        except httpx.TimeoutException as exc:
            logger.warning("Orders source request timed out: attempt=%s", attempt + 1)
            last_error = exc
        except httpx.HTTPError as exc:
            logger.warning("Orders source request failed: attempt=%s; error=%s", attempt + 1, type(exc).__name__)
            last_error = exc

    raise OrdersSourceError("Orders source is unavailable", status_code=503) from last_error
