from pydantic import BaseModel, SecretStr
from sqlmodel import SQLModel


class ChangePasswordData(SQLModel):
    old_password: SecretStr
    new_password: SecretStr
    verification_code: str


class AuthData(BaseModel):
    username: str
    password: SecretStr


class RefreshTokenData(BaseModel):
    refresh_token: str


class AuthTokenData(RefreshTokenData):
    access_token: str
    type: str = 'Bearer'


class TokenData(BaseModel):
    token: str
