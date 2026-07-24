import logging

from psycopg import Connection
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from pypika import Table

from db.query_builder import PGQuery
from db.exceptions import DatabaseError, UsernameAlreadyTakenError
from models.user import UserCreate, UserCreateResponse

logger = logging.getLogger(__name__)


def insert_user(db: Connection, data: UserCreate) -> UserCreateResponse:
    users = Table("users")
    fields, values = zip(*data.model_dump().items())
    response_fields = UserCreateResponse.model_fields.keys()
    query = (
        PGQuery.into(users).columns(*fields).insert(*values).returning(*response_fields)
    )

    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()
            db.commit()
            return UserCreateResponse(**result)

    except UniqueViolation:
        logger.info(f"Failed to create user '{data.username}': username already taken.")
        raise UsernameAlreadyTakenError

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error("Error adding user to database.")
        raise DatabaseError(str(e))
