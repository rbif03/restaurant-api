from typing import List

from psycopg import Connection
from psycopg.rows import dict_row
from pypika import Table
from pypika import Order as SortOrder

from db.query_builder import PGQuery, prefix_fields_with_table
from db.exceptions import DatabaseError, OrderAccessDeniedError
from models.item import ItemRead
from models.order import OrderRead, OrderStatus
from models.order_item import OrderItemRead, OrderItemReadExtended


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
        raise DatabaseError(str(e))


def get_orders_by_status(db: Connection, status: OrderStatus) -> List[OrderRead]:
    orders = Table("orders")
    query = (
        PGQuery.from_(orders)
        .select("*")
        .where(orders.status == status)
        .orderby(orders.created_at, order=SortOrder.desc)
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            return [OrderRead(**order) for order in result]

    except Exception as e:
        raise DatabaseError(str(e))


def validate_order_owner(db: Connection, order_id: int, user_id: int) -> bool:
    orders = Table("orders")
    query = PGQuery.from_(orders).select("*").where(orders.id == order_id)
    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()
            order = OrderRead(**result)

    except Exception as e:
        raise DatabaseError(str(e))

    # TODO: once auth is setup, all the user_id will be replaced by a UserReadObj
    if order.user_id != user_id:
        raise OrderAccessDeniedError("Order doesn't belong to user.")

    return True


def get_order_items_by_order_id(
    db: Connection, user_id: int, order_id: int, admin=False
) -> List[OrderItemReadExtended]:
    # Validation: does the order belong to the user
    user_allowed = validate_order_owner(db, order_id, user_id)
    order_items = Table("order_items")
    order_items_fields = prefix_fields_with_table(
        order_items, OrderItemRead.model_fields.keys()
    )
    items = Table("items")
    items_fields = prefix_fields_with_table(items, ItemRead.model_fields.keys())

    query = (
        PGQuery.from_(order_items)
        .select(*order_items_fields, *items_fields)
        .left_join(items)
        .on(order_items.item_id == items.id)
        .where(order_items.order_id == order_id)
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            return [OrderItemReadExtended(**order_item) for order_item in result]

    except Exception as e:
        raise DatabaseError(str(e))
