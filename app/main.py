import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.client import fetch_orders
from app.config import settings
from app.exceptions import OrdersSourceError
from app.schemas import SyncResponse
from app.service import process_orders

logging.basicConfig(level=settings.log_level.upper(), format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("order-sync")

app = FastAPI(title="Order Sync API", version="0.1.0")


@app.exception_handler(OrdersSourceError)
async def handle_orders_error(request, exc: OrdersSourceError):
    logger.warning("orders source error: %s (status=%s)", exc.message, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/")
async def root():
    return {"service": "Order Sync API", "status": "ok", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/clients", response_model=SyncResponse)
async def clients():
    raw_orders = await fetch_orders()
    result = process_orders(raw_orders)
    return result
