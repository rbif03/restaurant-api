from typing import Optional

from pydantic import BaseModel, PositiveInt

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class CartItemRead(BaseReadSchema):
    user_id: int
    item_id: int
    amount: PositiveInt


class CartItemCreate(BaseCreateSchema):
    user_id: int
    item_id: int
    amount: PositiveInt


class CartItemCreateRequest(BaseModel):
    item_id: int
    amount: PositiveInt


class CartItemUpdate(BaseUpdateSchema):
    # Updating a cart item requires removing it first, then adding the new item.
    amount: Optional[PositiveInt] = None


class CartItemUpdateRequest(BaseModel):
    # Updating a cart item requires removing it first, then adding the new item.
    item_id: int
    amount: PositiveInt
