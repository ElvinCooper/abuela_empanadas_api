from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


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
