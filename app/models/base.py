from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional
import time


class BaseReadSchema(BaseModel):
    id: int
    created_at: int  # unix timestamp
    updated_at: int  # unix timestamp


class BaseCreateSchema(BaseModel):
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))

    @model_validator(mode="before")
    @classmethod
    def _force_created_and_updated_at(cls, data):
        if isinstance(data, dict):
            data.pop("created_at", None)
            data.pop("updated_at", None)
        return data


class BaseUpdateSchema(BaseModel):
    updated_at: int = Field(default_factory=lambda: int(time.time()))

    @model_validator(mode="before")
    @classmethod
    def _force_updated_at(cls, data):
        if isinstance(data, dict):
            data.pop("updated_at", None)
        return data

    def model_dump(self, **kwargs):
        # Overrides model_dump so that the updated_at field is not ignored when exclude_unset is True
        data = super().model_dump(**kwargs)
        if kwargs.get("exclude_unset") and data:
            data["updated_at"] = self.updated_at
        return data
