import logging

from fastapi import FastAPI
import psycopg

from api_routers.auth import router as auth_router
from api_routers.cart import router as cart_router
from api_routers.items import router as items_router
from api_routers.orders import router as orders_router
from services.db import get_connstr

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s() - %(message)s",
)
logger = logging.getLogger(__name__)


conn_str = get_connstr()
db_conn = psycopg.connect(conn_str)
logger.info("DB connection established.")


def handler(event, context, lambda_execution: bool = True):
    app = FastAPI()
    app.state.db_conn = db_conn
    app.include_router(auth_router, prefix="/auth")
    app.include_router(cart_router, prefix="/cart")
    app.include_router(items_router, prefix="/items")
    app.include_router(orders_router, prefix="/orders")

    if lambda_execution:
        from mangum import Mangum

        mangum_handler = Mangum(app)
        return mangum_handler(event, context)

    else:  # local execution
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    event = {}
    context = None
    handler(event, context, lambda_execution=False)
