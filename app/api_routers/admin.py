from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
from pydantic import PositiveInt

from auth.auth import get_admin_user
from db.exceptions import DatabaseError, NonExistingOrderError
from db.queries.orders import get_orders_by_status, update_order_status
from models.order import OrderRead, OrderStatus, OrderUpdate
from models.user import UserReadInternal
from services.db import get_db_conn

router = APIRouter()


@router.get("/orders")
def list_orders_by_status(
    status: OrderStatus,
    hours_ago: Optional[PositiveInt] = None,
    db: Connection = Depends(get_db_conn),
    admin_user: UserReadInternal = Depends(get_admin_user),
) -> List[OrderRead]:
    """
    Retrieve orders filtered by status, optionally within a recent time window.

    Restricted to admin users; the 'admin_user' dependency isn't used directly
    but enforces that only authenticated admins can access this endpoint.

    Args:
        status: The order status to filter by.
        hours_ago: If provided, limits results to orders created within the last
            `hours_ago` hours. If omitted, no time filtering is applied.
        db: Database connection, injected via dependency.
        admin_user: Authenticated admin user, injected for access control only.

    Returns:
        A list of orders matching the given status and time window.

    Raises:
        HTTPException: 500 if an unexpected database error occurs.
    """
    try:
        return get_orders_by_status(db, status, hours_ago)

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )


@router.patch("/orders/{order_id}")
def change_order_status(
    order_id: int,
    body: OrderUpdate,
    db: Connection = Depends(get_db_conn),
    admin_user: UserReadInternal = Depends(get_admin_user),
) -> OrderRead:
    try:
        return update_order_status(db, order_id, body.status)

    except NonExistingOrderError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Order not found.",
        )

    except DatabaseError:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured. More information: {e}",
        )
