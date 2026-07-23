from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from auth.auth import get_user_from_token
from db.exceptions import (
    DatabaseError,
    EmptyCartError,
    ItemAlreadyInCartError,
    ItemNotInCartError,
    NonExistingItemError,
)
from db.queries.cart import (
    insert_item_to_cart,
    update_cart_item,
    get_cart_items,
    create_new_pending_order,
    attribute_items_to_order,
    clear_cart,
    get_cart_items_with_item_data,
)
from models.cart_item import (
    CartItemCreate,
    CartItemCreateRequest,
    CartItemRead,
    CartItemReadWithItem,
    CartItemUpdate,
    CartItemUpdateRequest,
)
from models.order import OrderExtended
from models.order_item import OrderItemCreate
from models.user import UserReadInternal
from services.db import get_db_conn

router = APIRouter()


@router.post("/", status_code=201)
def add_item_to_cart(
    body: CartItemCreateRequest,
    user: UserReadInternal = Depends(get_user_from_token),
    db: Connection = Depends(get_db_conn),
) -> CartItemRead:

    cart_item_data = CartItemCreate(user_id=user.id, **body.model_dump())
    try:
        result = insert_item_to_cart(db, cart_item_data)
        return result

    except ItemAlreadyInCartError:
        raise HTTPException(
            status_code=409,
            detail=f"Item already exists in user's cart. Use PATCH /cart to update quantity.",
        )

    except NonExistingItemError:
        raise HTTPException(
            status_code=404,
            detail=f"Couldn't add item to cart: item not found.",
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )


@router.patch("/", status_code=200)
def patch_cart_item(
    body: CartItemUpdateRequest,
    user: UserReadInternal = Depends(get_user_from_token),
    db: Connection = Depends(get_db_conn),
) -> CartItemRead:
    update_data = CartItemUpdate(**body.model_dump())
    item_id = body.item_id

    try:
        result = update_cart_item(db, user.id, item_id, update_data)
        return result

    except ItemNotInCartError:
        raise HTTPException(
            status_code=409,
            detail=f"Item with id={item_id} is not in user's cart, therefore can't be patched.",
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )


@router.post("/checkout/")
def checkout_cart(
    user: UserReadInternal = Depends(get_user_from_token),
    db: Connection = Depends(get_db_conn),
) -> OrderExtended:
    try:
        cart_items = get_cart_items(db, user.id)
        if not cart_items:
            raise EmptyCartError

        order = create_new_pending_order(db, user.id)
        order_items = [
            OrderItemCreate(order_id=order.id, item_id=item.item_id, amount=item.amount)
            for item in cart_items
        ]

        new_order_items = attribute_items_to_order(db, order_items)
        clear_cart(db, user.id)
        db.commit()
        return OrderExtended(order=order, order_items=new_order_items)

    except EmptyCartError as e:
        raise HTTPException(status_code=409, detail="Can't checkout an empty cart.")

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occured (probably when commiting db changes). More information: {e}",
        )


@router.get("/", status_code=200)
def list_cart_items(
    user: UserReadInternal = Depends(get_user_from_token),
    db: Connection = Depends(get_db_conn),
) -> List[CartItemReadWithItem]:
    try:
        result = get_cart_items_with_item_data(db, user.id)
        return result

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )
