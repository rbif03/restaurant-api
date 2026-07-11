from fastapi import APIRouter, Depends
from psycopg import Connection
from psycopg.rows import dict_row
from pypika import PostgreSQLQuery, Table

from db.connect import get_db_conn
from models.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter()


@router.get("/", status_code=200)
def list_items(
    category=None, db_conn: Connection = Depends(get_db_conn)
) -> list[ItemRead]:
    items = Table("items")
    query = (
        PostgreSQLQuery.from_(items)
        .select("*")
        .where((items.category == None) | (items.category == category))
    )

    with db_conn.cursor(row_factory=dict_row) as cur:
        r = cur.execute(query).fetchall()

    return r


@router.get("/{item_id}", status_code=200)
def get_item_by_id(
    item_id: int, db_conn: Connection = Depends(get_db_conn)
) -> ItemRead:
    items = Table("items")
    query = PostgreSQLQuery.from_(items).select("*").where(items.id == item_id)

    with db_conn.cursor(row_factory=dict_row) as cur:
        r = cur.execute(query).fetchone()

    return r


# The routes below can be created later, for now will add items directly to the db
"""@router.post("/", status_code=201)
def add_item(body: ItemCreate) -> ItemRead:
    # database logic
    return


@router.patch("/{product_id}")
def update_item(product_id: int, body: ItemUpdate) -> ItemRead:
    fields_to_update = body.model_dump(exclude_unset=True)
    # database logic
    return"""
