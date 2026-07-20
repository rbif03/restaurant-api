from psycopg import Connection
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from pypika import Table

from db.query_builder import PGQuery
from db.exceptions import DatabaseError, UsernameAlreadyTakenError
from models.user import UserCreate, UserCreateResponse


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
        raise UsernameAlreadyTakenError

    except Exception as e:
        print(e)
        raise DatabaseError(str(e))
