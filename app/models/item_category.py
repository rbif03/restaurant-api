from typing import Optional

from models.base import BaseReadSchema, BaseCreateSchema, BaseUpdateSchema


class ItemCategoryRead(BaseReadSchema):
    name: str


class ItemCategoryCreate(BaseCreateSchema):
    name: str


class ItemCategoryUpdate(BaseUpdateSchema):
    name: Optional[str] = None
