from typing import Optional

from decimal import Decimal
from pydantic import BaseModel

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class ItemRead(BaseReadSchema):
    category: str | None
    name: str
    description: str | None
    price: Decimal
    active: bool


class ItemCreate(BaseCreateSchema):
    category: str | None = None
    name: str
    description: str | None = None
    price: Decimal
    active: bool


class ItemCreateRequest(BaseModel):
    category: str | None = None
    name: str
    description: str | None = None
    price: Decimal
    active: bool


class ItemUpdate(BaseUpdateSchema):
    # Use self.model_dump(exclude_unset=True) to include only explicitly provided values.
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    active: Optional[bool] = None
