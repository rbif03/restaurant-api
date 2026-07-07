from fastapi import FastAPI

from api_routers.cart import router as cart_router


def handler(event, context):
    app = FastAPI()
    app.include_router(cart_router, prefix="/cart")

    import uvicorn

    # Pass the import string path rather than the raw object when using reload=True
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    event = {}
    context = None
    handler(event, context)
