from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation
from pypika import Table

from db.connect import get_db_conn
from db.query_builder import PGQuery, prefix_fields_with_table
from models.cart_item import (
    CartItemCreate,
    CartItemCreateRequest,
    CartItemRead,
    CartItemReadWithItem,
    CartItemUpdate,
    CartItemUpdateRequest,
)
from models.item import ItemRead
from models.order import OrderCreate, OrderRead
from models.order_item import OrderItemCreate

router = APIRouter()


@router.post("/{user_id}", status_code=201)
def add_item_to_cart(
    body: CartItemCreateRequest,
    user_id: int,
    db_conn: Connection = Depends(get_db_conn),
) -> CartItemRead:
    cart_item_data = CartItemCreate(user_id=user_id, **body.model_dump()).model_dump()
    cols, vals = zip(*cart_item_data.items())

    cart_items = Table("cart_items")
    query = PGQuery.into(cart_items).columns(*cols).insert(*vals).returning("*")

    try:
        with db_conn.cursor(row_factory=dict_row) as cur:
            r = cur.execute(str(query)).fetchone()
            db_conn.commit()

    except UniqueViolation as e:
        raise HTTPException(
            status_code=409,
            detail=f"Item already exists in user's cart. Use PATCH /cart to update quantity.",
        )

    return CartItemRead(**r)


@router.patch("/{user_id}", status_code=200)
def update_cart_item(
    body: CartItemUpdateRequest,
    user_id: int,
    db_conn: Connection = Depends(get_db_conn),
):
    update_data = CartItemUpdate(user_id=user_id, **body.model_dump()).model_dump()
    cart_items = Table("cart_items")
    query = (
        PGQuery.update(cart_items)
        .setmany(update_data)
        .where((cart_items.user_id == user_id) & (cart_items.item_id == body.item_id))
        .returning("*")
    )

    with db_conn.cursor(row_factory=dict_row) as cur:
        r = cur.execute(str(query)).fetchone()
        db_conn.commit()

    if r is None:
        raise HTTPException(
            status_code=404,
            detail=f"Item {body.item_id} was not found in user's cart.",
        )
    return r


@router.post("/checkout/{user_id}")
def checkout_cart(user_id: int, db_conn: Connection = Depends(get_db_conn)):
    # Create a new order for the user
    orders = Table("orders")
    order_data = OrderCreate(user_id=user_id, status="pending").model_dump()
    order_cols, order_vals = zip(*order_data.items())
    create_order_query = (
        PGQuery.into(orders).columns(*order_cols).insert(*order_vals).returning("*")
    )
    with db_conn.cursor(row_factory=dict_row) as cur:
        create_order_r = cur.execute(str(create_order_query)).fetchone()
        order_obj = OrderRead(**create_order_r)

    # Insert items from the cart into the order_items table
    cart_items = Table("cart_items")
    order_items = Table("order_items")
    order_items_fields = OrderItemCreate.model_fields.keys()


@router.get("/{user_id}", status_code=200)
def list_cart_items(
    user_id: int, db_conn: Connection = Depends(get_db_conn)
) -> List[CartItemReadWithItem]:
    # cart_items_fields examples: 'cart_items.id', 'cart_items.item_id'
    cart_items = Table("cart_items")
    cart_items_fields = prefix_fields_with_table(cart_items, CartItemRead.model_fields)

    # items_fields examples: 'items.id', 'items.name'
    items = Table("items")
    items_fields = prefix_fields_with_table(items, ItemRead.model_fields)

    # Rows returned by the query below will have both the info of cart_items and items
    query = (
        PGQuery.from_(cart_items)
        .select(*cart_items_fields, *items_fields)
        .left_join(items)
        .on(cart_items.item_id == items.id)
        .where(cart_items.user_id == user_id)
    )

    with db_conn.cursor(row_factory=dict_row) as cur:
        r = cur.execute(str(query)).fetchall()

    if not r:
        return []

    result = []
    for row in r:
        result.append(CartItemReadWithItem.from_prefixed_row(row))

    return result
