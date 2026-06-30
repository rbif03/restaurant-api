from pydantic import PositiveInt

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class OrderItemRead(BaseReadSchema):
    order_id: int
    item_id: int
    ammount: PositiveInt


class OrderItemCreate(BaseCreateSchema):
    order_id: int
    item_id: int
    ammount: PositiveInt
