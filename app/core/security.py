from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer

from app.core.settings import settings
from app.models.users import UserModel

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login', refreshUrl='/api/v1/auth/refresh'
)


def create_access_token(user: UserModel, expires_delta: timedelta | None = None) -> str:
    to_encode: dict[str, str | datetime] = {'sub': str(user.id)}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            seconds=settings.auth.access_token_lifetime_seconds
        )
    to_encode['exp'] = expire
    return jwt.encode(
        to_encode, settings.auth.secret, algorithm=settings.auth.token_algorithm
    )


def create_refresh_token(
    user: UserModel, access_token: str, expires_delta: timedelta | None = None
) -> str:
    to_encode: dict[str, str | datetime] = {'sub': str(user.id)}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            seconds=settings.auth.refresh_token_lifetime_seconds
        )
    to_encode['exp'] = expire
    to_encode['token'] = access_token
    return jwt.encode(
        to_encode, settings.auth.secret, algorithm=settings.auth.token_algorithm
    )
