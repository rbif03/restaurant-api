import logging
from datetime import datetime
from typing import List, Optional

from psycopg import Connection
from psycopg.rows import dict_row
from pydantic import PositiveInt
from pypika import Table
from pypika import Order as SortOrder
from pypika.terms import ValueWrapper

from db.query_builder import PGQuery, prefix_fields_with_table
from db.exceptions import DatabaseError, OrderNotFoundError
from models.item import ItemRead
from models.order import OrderRead, OrderUpdate
from models.order_item import OrderItemRead, OrderItemReadExtended

logger = logging.getLogger(__name__)


def get_user_orders(db: Connection, user_id: int) -> List[OrderRead]:
    orders = Table("orders")
    query = (
        PGQuery.from_(orders)
        .select("*")
        .where(orders.user_id == user_id)
        .orderby(orders.created_at, order=SortOrder.desc)
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            return [OrderRead(**order) for order in result]

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))


def get_orders_by_status(
    db: Connection, status: OrderStatus, hours_ago: Optional[PositiveInt]
) -> List[OrderRead]:
    base_time = 0 if hours_ago is None else int(datetime.now()) - 3600 * hours_ago
    orders = Table("orders")
    query = (
        PGQuery.from_(orders)
        .select("*")
        .where((orders.status == status) & (orders.created_at >= base_time))
        .orderby(orders.created_at, order=SortOrder.asc)
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            return [OrderRead(**order) for order in result]

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))


def update_order_status(
    db: Connection, order_id: int, order_update: OrderUpdate
) -> OrderRead:
    """
    This function is supposed to be used by admin routes only, since it doesn't validate the owner of the order.

    Raises:
        OrderNotFoundError: if the order id passed is not in the database.
        DatabaseError: if an unexpected database error happens.
    """
    orders = Table("orders")
    query = (
        PGQuery.update(orders)
        .setmany(
            {
                orders.status: order_update.status, 
                orders.updated_at: order_update.updated_at
            }
        )
        .where(orders.id == order_id)
        .returning("*")
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()
            
        if not result:
            raise OrderNotFoundError(f"Order {order_id} not found.")

        db.commit()

        return OrderRead(**result)

    except Exception as e:
        logger.error(str(e))
        raise DatabaseError(str(e))


def get_order_items_by_order_id(
    db: Connection, order_id: int, user_id: int, user_admin: bool
) -> List[OrderItemReadExtended]:
    order_items = Table("order_items")
    order_items_fields = prefix_fields_with_table(
        order_items, OrderItemRead.model_fields.keys()
    )
    items = Table("items")
    items_fields = prefix_fields_with_table(items, ItemRead.model_fields.keys())
    orders = Table("orders")
    query = (
        PGQuery.from_(order_items)
        .select(*order_items_fields, *items_fields)
        .left_join(items)
        .on(order_items.item_id == items.id)
        .left_join(orders)
        .on(order_items.order_id == orders.id)
        .where(
            (order_items.order_id == order_id)
            & ((orders.user_id == user_id) | ValueWrapper(user_admin))
        )
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            if not result:
                raise OrderNotFoundError("Order not found or doesn't belong to user.")
            return [
                OrderItemReadExtended.from_prefixed_row(order_item)
                for order_item in result
            ]

    except OrderNotFoundError as e:
        raise e

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))
