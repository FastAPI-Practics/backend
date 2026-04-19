from pydantic.generics import GenericModel
from sqlmodel import SQLModel

from app.models.base import BaseModel


class PaginationInfo(SQLModel):
    page: int
    pages_num: int
    total: int


class ListResponse[T: BaseModel](GenericModel):
    info: PaginationInfo
    items: list[T]
