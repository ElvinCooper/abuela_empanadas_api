from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict, model_validator

T = TypeVar("T")

_LOWERCASE_FIELDS = {"username", "password"}


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 100


class ErrorResponse(BaseModel):
    error: str
    code: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_strings(cls, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.strip()
                    if key in _LOWERCASE_FIELDS:
                        data[key] = data[key].lower()
        return data
