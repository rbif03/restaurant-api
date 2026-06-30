from typing import Optional

from pydantic import PositiveInt

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class CartItemRead(BaseReadSchema):
    user_id: int
    item_id: int
    ammount: PositiveInt


class CartItemCreate(BaseCreateSchema):
    user_id: int
    item_id: int
    ammount: PositiveInt


class CartItemUpdate(BaseUpdateSchema):
    # Updating a cart item requires removing it first, then adding the new item.
    ammount: Optional[PositiveInt] = None
