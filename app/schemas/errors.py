from typing import Optional

from pydantic import Field, PrivateAttr
from sqlmodel import SQLModel

from app.utils.errors import (
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
)


class ErrorSchema(SQLModel):
    detail: Optional[dict] = Field(default_factory=dict)
    message: str
    _error_cls: type[Exception] = PrivateAttr(default=Exception)

    @property
    def error_cls(self) -> type[Exception]:
        return self._error_cls


class NotFoundErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = NotFoundError
    message: str = NotFoundError.message


class InternalServerErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = InternalServerError
    message: str = InternalServerError.message


class UnauthorizedErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = UnauthorizedError
    message: str = UnauthorizedError.message


class ForbiddenErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = ForbiddenError
    message: str = ForbiddenError.message
