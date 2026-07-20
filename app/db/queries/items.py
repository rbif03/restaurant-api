from typing import List

from psycopg import Connection
from psycopg.rows import dict_row
from pypika import Table

from db.query_builder import PGQuery
from db.exceptions import DatabaseError, ItemNotFoundError
from models.item import ItemRead


def get_items(db: Connection, category) -> List[ItemRead]:
    items = Table("items")
    query = PGQuery.from_(items).select("*")
    if category is not None:
        query = query.where(items.category == category)

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
            result = cur.execute(str(query)).fetchone()
            if not result:
                raise ItemNotFoundError
            return ItemRead(**result)

    except ItemNotFoundError as e:
        raise e

    except Exception as e:
        raise DatabaseError(str(e))
