from typing import Literal, List, Optional

from pydantic import BaseModel

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema
from models.order_item import OrderItemRead

OrderStatus = Literal["pending", "ready", "withdrawn", "cancelled"]


class OrderRead(BaseReadSchema):
    user_id: int
    status: OrderStatus


class OrderCreate(BaseCreateSchema):
    user_id: int
    status: OrderStatus = "pending"


class OrderUpdate(BaseUpdateSchema):
    status: Optional[OrderStatus] = None


class OrderExtended(BaseModel):
    order: OrderRead
    order_items: List[OrderItemRead]
