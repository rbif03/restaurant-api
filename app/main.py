from dotenv import load_dotenv
from fastapi import FastAPI
import psycopg

from api_routers.cart import router as cart_router
from db.connect import get_connstr

load_dotenv()

conn_str = get_connstr()
db_conn = psycopg.connect(conn_str)
print("DB connection established.")


def handler(event, context):
    app = FastAPI()
    app.state.db_conn = db_conn
    app.include_router(cart_router, prefix="/cart")

    import uvicorn

    # Pass the import string path rather than the raw object when using reload=True
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    event = {}
    context = None
    handler(event, context)
