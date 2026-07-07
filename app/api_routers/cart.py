from fastapi import APIRouter, Depends
from psycopg import AsyncConnection

from dependencies.db import get_db
from models.cart_item import (
    CartItemCreate,
    CartItemCreateRequest,
    CartItemRead,
    CartItemUpdate,
    CartItemUpdateRequest,
)

router = APIRouter()


@router.post("/additem/{user_id}", status_code=201)
async def add_item_to_cart(
    body: CartItemCreateRequest, user_id: int, db: AsyncConnection = Depends(get_db)
) -> CartItemCreate:
    async with db.cursor() as cursor:
        await cursor.execute("""SELECT now()""")
        query_results = await cursor.fetchall()

    print(query_results)
    # user_id will have to be given by an auth flow later
    # check if item is not in cart already
    cart_item = CartItemCreate(user_id=user_id, **body.model_dump())
    return cart_item


@router.post("/updateamount/{user_id}")
def update_cart_item(body: CartItemUpdateRequest, user_id: int, status_code=200):
    # check if body.item_id is in user's cart
    # get the cart_item id
    cart_item_updated_fields = CartItemUpdate(**body)
    return


@router.post("/checkout/{user_id}")
def checkout_cart(user_id: int):
    # check if user has items in cart
    # create an order
    # add cart items to order items
    # delete user's cart items
    return


@router.get("/{user_id}", status_code=200)
def list_cart_items(user_id: int) -> CartItemRead:
    # user_id will have to be given by an auth flow later
    return
