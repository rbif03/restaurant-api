from pydantic import PositiveInt

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class OrderItemRead(BaseReadSchema):
    order_id: int
    item_id: int
    amount: PositiveInt


class OrderItemCreate(BaseCreateSchema):
    order_id: int
    item_id: int
    amount: PositiveInt
