from typing import Optional

from decimal import Decimal

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class ItemRead(BaseReadSchema):
    category_id: int | None
    name: str
    description: str | None
    price: Decimal
    active: bool


class ItemCreate(BaseCreateSchema):
    category_id: int | None = None
    name: str
    description: str | None = None
    price: Decimal
    active: bool


class ItemUpdate(BaseUpdateSchema):
    # Use self.model_dump(exclude_unset=True) to include only explicitly provided values.
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    active: Optional[bool] = None
