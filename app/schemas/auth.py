from pydantic import BaseModel, SecretStr


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
