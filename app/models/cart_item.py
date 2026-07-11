from typing import Optional

from pydantic import BaseModel, PositiveInt

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema
from models.item import ItemRead


class CartItemRead(BaseReadSchema):
    user_id: int
    item_id: int
    amount: PositiveInt


class CartItemReadWithItem(CartItemRead):
    item: ItemRead

    @classmethod
    def from_prefixed_row(cls, row: dict) -> "CartItemReadWithItem":
        cart_data = {}
        item_data = {}

        for key, value in row.items():
            table_name, column = key.split(".")
            if table_name == "cart_items":
                cart_data[column] = value
            elif table_name == "items":
                item_data[column] = value

        return cls(**cart_data, item=ItemRead(**item_data))


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
