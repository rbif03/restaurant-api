from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
from psycopg.rows import dict_row
from pypika import PostgreSQLQuery, Table

from db.connect import get_db_conn
from db.exceptions import DatabaseError, ItemNotFoundError
from db.queries.items import get_items, get_item_by_id
from models.item import ItemRead

router = APIRouter()


@router.get("/", status_code=200)
def list_items(category=None, db: Connection = Depends(get_db_conn)) -> list[ItemRead]:
    try:
        return get_items(db, category)

    except DatabaseError:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured.",
        )


@router.get("/{item_id}", status_code=200)
def list_item_by_id(item_id: int, db: Connection = Depends(get_db_conn)) -> ItemRead:
    try:
        return get_item_by_id(db, item_id)

    except ItemNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Item of id {item_id} not found in database."
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected database error occured.",
        )


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
