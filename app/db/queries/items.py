from typing import List

from psycopg import Connection
from psycopg.rows import dict_row
from pypika import Table

from db.query_builder import PGQuery
from db.exceptions import DatabaseError
from models.item import ItemRead


def get_items(db: Connection, category) -> List[ItemRead]:
    items = Table("items")
    query = (
        PGQuery.from_(items)
        .select("*")
        .where((items.category == None) | (items.category == category))
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchall()
            return [ItemRead(**item) for item in result]

    except Exception as e:
        raise DatabaseError(str(e))


def get_item_by_id(db: Connection, item_id) -> ItemRead:
    items = Table("items")
    query = PGQuery.from_(items).select("*").where(items.id == item_id)

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(query).fetchone()
            return ItemRead(**result)

    except Exception as e:
        raise DatabaseError(str(e))
