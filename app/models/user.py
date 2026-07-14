import re
from typing import Annotated, Optional
from pydantic import AfterValidator, BaseModel, EmailStr

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


def validate_br_phone(v: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)]", "", v)
    cleaned = re.sub(r"^\+?55", "", cleaned)

    pattern = r"^([1-9][1-9])(9\d{8}|\d{8})$"
    if not re.fullmatch(pattern, cleaned):
        raise ValueError(
            "Invalid Brazilian phone number. Expected DDD + 8 or 9 digits, "
            "e.g. '11987654321' or '1133334444'"
        )

    return cleaned


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


class UserReadInternal(BaseReadSchema):
    # This class gets only the basic information about a user (id and admin)
    # Use this class as often as possible to avoid logging any user data
    admin: bool


class UserRead(UserReadInternal):
    email: EmailStr
    name: FullName
    phone: PhoneNumber
    hashed_password: str


class UserCreate(BaseCreateSchema):
    email: EmailStr
    name: FullName
    phone: PhoneNumber
    hashed_password: str
    # Shouldn't be possible to tell if the user is admin in user creation.


class UserCreateRequest(BaseModel):
    email: EmailStr
    name: FullName
    phone: PhoneNumber
    password: str
    # Shouldn't be possible to tell if the user is admin in user creation.


class UserUpdate(BaseUpdateSchema):
    email: Optional[EmailStr] = None
    name: Optional[FullName] = None
    phone: Optional[PhoneNumber] = None
    hashed_password: Optional[str]
    # Shouldn't be possible to tell if the user is admin in user creation.
