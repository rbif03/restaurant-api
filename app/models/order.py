from typing import Literal, Optional

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema

OrderStatus = Literal["pending", "ready", "withdrawn", "cancelled"]


class OrderRead(BaseReadSchema):
    id: int
    user_id: int
    status: OrderStatus


class OrderCreate(BaseCreateSchema):
    user_id: int
    status: OrderStatus = "pending"


class OrderUpdate(BaseUpdateSchema):
    status: Optional[OrderStatus] = None
