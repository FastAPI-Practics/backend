from typing import Optional

from pydantic import Field, PrivateAttr
from sqlmodel import SQLModel

from app.core.errors import (
    ForbiddenError,
    InternalServerError,
    LoginError,
    NotFoundError,
    RegisterError,
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
    detail: None = None


class ForbiddenErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = ForbiddenError
    message: str = ForbiddenError.message


class LoginErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = LoginError
    message: str = LoginError.message
    detail: None = None


class RegisterErrorSchema(ErrorSchema):
    _error_cls: type[Exception] = RegisterError
    message: str = RegisterError.message
    detail: None = None


class OkSchema(SQLModel):
    message: str = 'Success'
