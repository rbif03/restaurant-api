from typing import List

from pypika import Table

from db.query_builder import PGQuery, prefix_fields_with_table
from models.cart_item import CartItemCreate, CartItemUpdate, CartItemRead
from models.item import ItemRead
from models.order import OrderCreate
from models.order_item import OrderItemCreate


def get_insert_item_to_cart_query(data: CartItemCreate):
    cart_items = Table("cart_items")
    fields, values = zip(*data.model_dump())
    query = PGQuery.into(cart_items).columns(*fields).insert(*values).returning("*")
    return query


def get_update_item_in_cart_query(user_id: int, item_id: int, data: CartItemUpdate):
    cart_items = Table("cart_items")
    query = (
        PGQuery.update(cart_items)
        .setmany(data.model_dump(exclude_unset=True))
        .where((cart_items.user_id == user_id) & (cart_items.item_id == item_id))
        .returning("*")
    )
    return query


def get_select_all_cart_items_with_item_info_query(user_id: int):
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
    return query


def get_insert_new_pending_order_query(user_id: int):
    orders = Table("orders")
    data = OrderCreate(user_id=user_id, status="pending")
    fields, values = zip(*data.model_dump().items())
    query = PGQuery.into(orders).columns(fields).insert(values).returning("*")
    return query


def get_select_all_cart_items_query(user_id: int):
    cart_items = Table("cart_items")
    query = PGQuery.from_(cart_items).select("*").where(cart_items.user_id == user_id)
    return query


def get_add_items_in_cart_to_order_query(data: List[OrderItemCreate]):
    order_items = Table("order_items")
    fields = list(OrderItemCreate.model_fields.keys())
    insert_data = [tuple([getattr(obj, field) for field in fields]) for obj in data]
    query = PGQuery.into(order_items).columns(fields).insert(insert_data).returning("*")
    return query


def get_clean_users_cart_query(user_id: int):
    cart_items = Table("cart_items")
    query = PGQuery.from_(cart_items).delete().where(cart_items.user_id == user_id)
    return query
