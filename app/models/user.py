import re
from typing import Annotated, Optional
from pydantic import AfterValidator, BaseModel, EmailStr

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


def validate_full_name(value: str) -> str:
    # 1. Strip accidental leading/trailing whitespace
    cleaned_name = value.strip()

    # 2. Check for at least two words (First Name + Last Name)
    name_parts = cleaned_name.split()
    if len(name_parts) < 2:
        raise ValueError("Full name must include both a first and last name.")

    # 3. Ensure the name only contains letters, spaces, hyphens, or apostrophes
    # This allows names like "Mary-Jane" or "O'Connor"
    for char in cleaned_name:
        if not (char.isalpha() or char in "-' "):
            raise ValueError(
                f"Full name contains invalid characters. Invalid character: '{char}'"
            )

    # 4. Format nicely (Capitalize each word)
    return " ".join(part.capitalize() for part in name_parts)


PhoneNumber = Annotated[str, AfterValidator(validate_br_phone)]
FullName = Annotated[str, AfterValidator(validate_full_name)]


class UserReadInternal(BaseModel):
    id: int
    admin: bool


class UserRead(BaseReadSchema):
    admin: bool
    username: str
    name: FullName
    hashed_password: str


class UserCreate(BaseCreateSchema):
    username: str
    name: FullName
    hashed_password: str
    # Shouldn't be possible to tell if the user is admin in user creation.


class UserCreateRequest(BaseModel):
    username: str
    name: FullName
    password: str
    # Shouldn't be possible to tell if the user is admin in user creation.


class UserUpdate(BaseUpdateSchema):
    username: str
    name: Optional[FullName] = None
    hashed_password: Optional[str]
    # Shouldn't be possible to tell if the user is admin in user creation.
