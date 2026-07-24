import logging
from typing import List

from psycopg import Connection
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from psycopg.rows import dict_row
from pypika import Table

from db.query_builder import PGQuery, prefix_fields_with_table
from db.exceptions import (
    DatabaseError,
    ItemAlreadyInCartError,
    ItemNotInCartError,
    NonExistingItemError,
)
from models.cart_item import (
    CartItemCreate,
    CartItemUpdate,
    CartItemRead,
    CartItemReadWithItem,
)
from models.item import ItemRead
from models.order import OrderCreate, OrderRead
from models.order_item import OrderItemCreate, OrderItemRead

logger = logging.getLogger(__name__)


def insert_item_to_cart(db: Connection, data: CartItemCreate) -> CartItemRead:
    cart_items = Table("cart_items")

    fields, values = zip(*data.model_dump().items())
    query = PGQuery.into(cart_items).columns(*fields).insert(*values).returning("*")

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()
            db.commit()
            return CartItemRead(**result)

    except UniqueViolation as e:
        db.rollback()
        logger.info(
            f"Failed to add item to cart: {str(e)}. Rolling back transaction and raising ItemAlreadyInCartError."
        )
        raise ItemAlreadyInCartError(str(e))

    except ForeignKeyViolation as e:
        # This exception can occur if a non-existent user or item is provided.
        # However, the authentication schema validates that the user exists,
        # so this should only be raised when a non-existent item is passed.
        db.rollback()
        logger.info(
            f"Failed to add item to cart: {str(e)}. Rolling back transaction and raising NonExistingItemError."
        )
        raise NonExistingItemError(str(e))

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(e)


def update_cart_item(
    db: Connection, user_id: int, item_id: int, data: CartItemUpdate
) -> CartItemRead:
    cart_items = Table("cart_items")
    query = (
        PGQuery.update(cart_items)
        .setmany(data.model_dump(exclude_unset=True))
        .where((cart_items.user_id == user_id) & (cart_items.item_id == item_id))
        .returning("*")
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()
            db.commit()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))

    if not result:
        # By testing, this doesn't need a rollback
        raise ItemNotInCartError("")

    return CartItemRead(**result)


def get_cart_items_with_item_data(
    db: Connection, user_id: int
) -> List[CartItemReadWithItem]:
    cart_items = Table("cart_items")
    cart_items_fields = prefix_fields_with_table(
        cart_items, CartItemRead.model_fields.keys()
    )

    # items_fields examples: 'items.id', 'items.name'
    items = Table("items")
    items_fields = prefix_fields_with_table(items, ItemRead.model_fields.keys())

    # Rows returned by the query below will have both the info of cart_items and items
    query = (
        PGQuery.from_(cart_items)
        .select(*cart_items_fields, *items_fields)
        .left_join(items)
        .on(cart_items.item_id == items.id)
        .where(cart_items.user_id == user_id)
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))

    return [CartItemReadWithItem.from_prefixed_row(row) for row in result]


def create_new_pending_order(
    db: Connection, user_id: int, commit: bool = False
) -> OrderRead:
    orders = Table("orders")
    data = OrderCreate(user_id=user_id, status="pending")
    fields, values = zip(*data.model_dump().items())
    query = PGQuery.into(orders).columns(fields).insert(values).returning("*")

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()
            if commit:
                db.commit()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))

    return OrderRead(**result)


def get_cart_items(db: Connection, user_id: int) -> List[CartItemRead]:
    cart_items = Table("cart_items")
    query = PGQuery.from_(cart_items).select("*").where(cart_items.user_id == user_id)

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))

    return [CartItemRead(**row) for row in result]


def attribute_items_to_order(
    db: Connection, data: List[OrderItemCreate], commit: bool = False
) -> List[OrderItemRead]:
    order_items = Table("order_items")
    fields = list(OrderItemCreate.model_fields.keys())
    insert_data = [tuple([getattr(obj, field) for field in fields]) for obj in data]
    query = (
        PGQuery.into(order_items).columns(fields).insert(*insert_data).returning("*")
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            if commit:
                db.commit()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))

    return [OrderItemRead(**row) for row in result]


def clear_cart(db: Connection, user_id: int, commit: bool = False):
    cart_items = Table("cart_items")
    query = (
        PGQuery.from_(cart_items)
        .delete()
        .where(cart_items.user_id == user_id)
        .returning("*")
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            if commit:
                db.commit()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(str(e))
        raise DatabaseError(str(e))

    return
