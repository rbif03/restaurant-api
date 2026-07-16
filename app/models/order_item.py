from pydantic import PositiveInt

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema
from models.item import ItemRead


class OrderItemRead(BaseReadSchema):
    order_id: int
    item_id: int
    amount: PositiveInt


class OrderItemReadExtended(OrderItemRead):
    item: ItemRead

    @classmethod
    def from_prefixed_row(cls, row: dict) -> "OrderItemReadExtended":
        order_item_data = {}
        item_data = {}

        for key, value in row.items():
            table_name, column = key.split(".")
            if table_name == "order_items":
                order_item_data[column] = value
            elif table_name == "items":
                item_data[column] = value

        return cls(**order_item_data, item=ItemRead(**item_data))


class OrderItemCreate(BaseCreateSchema):
    order_id: int
    item_id: int
    amount: PositiveInt
