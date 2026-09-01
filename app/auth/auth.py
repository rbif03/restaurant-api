import os
import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError
from pwdlib import PasswordHash
from psycopg import Connection
from psycopg.rows import dict_row
from pypika import Table
from starlette.requests import Request

from auth.exceptions import InvalidPasswordError, InvalidUserError, InvalidTokenPayload
from db.query_builder import PGQuery
from db.exceptions import DatabaseError
from models.user import UserRead, UserReadInternal
from services.ssm import ssm_get_parameter

logger = logging.getLogger(__name__)

class CustomHeaderOAuth2PasswordBearer(OAuth2PasswordBearer):
    # Update the header to use from "Authorization" to "API-Authorization"
    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("API-Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None
        return param

oauth2_scheme = CustomHeaderOAuth2PasswordBearer(tokenUrl="auth/signin")


def hash_password(plain_password: str) -> str:
    """
    Hashes a password for securely storing it in the database.
    This function should be used when creating or updating a user password so
    that the raw password is not saved directly. The returned hashed password
    value is suitable for saving to the database.
    """
    password_hasher = PasswordHash.recommended()
    return password_hasher.hash(plain_password)


def verify_password(plain: str, hashed: str) -> bool:
    password_hasher = PasswordHash.recommended()
    return password_hasher.verify(plain, hashed)


def get_user_from_db(
    db: Connection, username: str, username_field="username"
) -> UserRead:
    """Retrieve a user by their authentication identifier.

    OAuth2 always provides the identifier as `username`; `username_field` maps
    it to the corresponding database column (e.g. `"username"`, `"email"`).

    Raises:
        InvalidUserError: If no matching user exists.
        DatabaseError: If the user cannot be retrieved from the database.
    """
    users = Table("users")
    query = (
        PGQuery.from_(users)
        .select("*")
        .where(getattr(users, username_field) == username)
    )
    try:
        with db.cursor(row_factory=dict_row) as cur:
            result = cur.execute(str(query)).fetchone()

    except Exception as e:
        db.rollback()  # reset transaction state so it doesn't block subsequent requests
        logger.error(f"Unexpected db error when getting user id={username}.")
        raise DatabaseError("Unexpected database error happened.")

    if not result:
        raise InvalidUserError(f"{username_field} not found in db")

    return UserRead(**result)  # should never fail for a valid DB record


def authenticate_user(db: Connection, username: str, password: str) -> UserReadInternal:
    try:
        user = get_user_from_db(db, username)
    except Exception as e:
        # Don't log expected login failures; DB errors are logged separately.
        raise e

    if verify_password(password, user.hashed_password):
        return UserReadInternal(**user.model_dump())
    else:
        raise InvalidPasswordError(f"Ivalid password.")


def create_access_token(user: UserReadInternal) -> str:
    to_encode = {"sub": str(user.id), "admin": user.admin}  # Subject must be a string

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(ssm_get_parameter("/restaurant-api/jwt/expire-minutes"))
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        ssm_get_parameter("/restaurant-api/jwt/secret-key"),
        algorithm=ssm_get_parameter("/restaurant-api/jwt/algorithm"),
    )
    return encoded_jwt


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> UserReadInternal:
    # This function is called before the route code, so it's reasonable raise http exceptions
    try:
        payload = jwt.decode(
            token,
            ssm_get_parameter("/restaurant-api/jwt/secret-key"),
            algorithms=[ssm_get_parameter("/restaurant-api/jwt/algorithm")],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials: payload does not contain the 'sub' field.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserReadInternal(
            id=payload.get("sub"), admin=payload.get("admin", False)
        )

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail="Token expired, sign in again to obtain a new one: ExpiredSignatureError",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail="Token cannot be decoded because it failed validation: InvalidSignatureError",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials: InvalidTokenError",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_admin_user(admin_user: UserReadInternal = Depends(get_user_from_token)):
    if admin_user.admin == True:
        return admin_user
    else:
        raise HTTPException(
            status_code=403,
            detail="Must be an admin to access this endpoint.",
        )
