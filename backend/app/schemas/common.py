"""Shared schema building blocks used across every resource."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMBase(BaseModel):
    """Base for *Read schemas — lets Pydantic build them straight from
    SQLAlchemy model instances instead of requiring a dict first."""

    model_config = ConfigDict(from_attributes=True)


class Page(ORMBase, Generic[T]):
    """Generic paginated envelope returned by every list endpoint."""

    items: list[T]
    total: int
    page: int
    page_size: int
