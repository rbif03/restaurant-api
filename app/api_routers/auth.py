from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import Connection
from pydantic import BaseModel

import auth.auth as auth
from auth.exceptions import InvalidPasswordError, InvalidUserError
from db.exceptions import DatabaseError, UsernameAlreadyTakenError
from db.queries.users import insert_user
from models.user import UserCreate, UserCreateRequest, UserCreateResponse
from services.db import get_db_conn

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/signin")
def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Connection = Depends(get_db_conn),
) -> Token:
    try:
        user = auth.authenticate_user(db, form_data.username, form_data.password)
        token = auth.create_access_token(user)
        return Token(access_token=token, token_type="bearer")

    except (InvalidPasswordError, InvalidUserError) as e:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Unexpected error when signing in.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/signup")
def signup(
    body: UserCreateRequest, db: Connection = Depends(get_db_conn)
) -> UserCreateResponse:
    user_create = UserCreate(
        username=body.username,
        name=body.name,
        hashed_password=auth.hash_password(body.password),
    )
    try:
        return insert_user(db, user_create)

    except UsernameAlreadyTakenError:
        raise HTTPException(
            status_code=409,
            detail=f"Username already taken, try another one.",
        )

    except DatabaseError as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected database error occured.",
        )
