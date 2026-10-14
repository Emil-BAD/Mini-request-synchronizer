import httpx
import pytest

from app.client import fetch_orders
from app.exceptions import OrdersSourceError


def test_handle_orders_error_raises_for_network_failure():
    err = OrdersSourceError("Upstream unavailable", status_code=503)
    with pytest.raises(OrdersSourceError):
        raise err


def test_fetch_orders_raises_for_http_error():
    async def fake_get(*args, **kwargs):
        raise httpx.HTTPError("bad network")

    with pytest.raises(OrdersSourceError):
        import app.client as client_module

        original = client_module.httpx.AsyncClient.get
        client_module.httpx.AsyncClient.get = fake_get
        try:
            import asyncio
            asyncio.run(fetch_orders())
        finally:
            client_module.httpx.AsyncClient.get = original
