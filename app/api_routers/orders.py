from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from auth.auth import get_user_from_token
from db.connect import get_db_conn
from db.exceptions import DatabaseError, OrderNotFoundError
from db.queries.orders import get_user_orders, get_order_items_by_order_id
from models.order import OrderRead
from models.order_item import OrderItemReadExtended
from models.user import UserReadInternal

router = APIRouter()


@router.get("/")
def list_user_orders(
    db: Connection = Depends(get_db_conn),
    user: UserReadInternal = Depends(get_user_from_token),
) -> list[OrderRead]:
    try:
        user_orders = get_user_orders(db, user.id)
        return user_orders

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )


@router.get("/{order_id}")
def list_order_items_by_order_id(
    order_id: int,
    db: Connection = Depends(get_db_conn),
    user: UserReadInternal = Depends(get_user_from_token),
) -> List[OrderItemReadExtended]:

    try:
        return get_order_items_by_order_id(db, order_id, user.id, user.admin)

    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Order does not exist or does not belong to user.",
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )
