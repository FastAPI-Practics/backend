from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import AccessTokenDep
from app.dependencies.auth import AuthenticatorDep
from app.schemas.auth import AuthTokenData

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/login')
async def login(
    auth_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    authenticator: AuthenticatorDep,
    response: Response,
) -> Optional[AuthTokenData]:
    tokens = await authenticator.create_tokens(auth_data)
    response.set_cookie('refresh_token', tokens.refresh_token, httponly=True)
    return tokens


@router.post('/refresh')
async def refresh(
    refresh_token: Annotated[str, Cookie()],
    authenticator: AuthenticatorDep,
    response: Response,
) -> Optional[AuthTokenData]:
    tokens = await authenticator.refresh_tokens(refresh_token)
    response.set_cookie('refresh_token', tokens.refresh_token, httponly=True)
    return tokens


@router.delete('/logout')
async def logout(
    token: AccessTokenDep,
    authenticator: AuthenticatorDep,
    response: Response,
) -> Optional[bool]:
    response.set_cookie('refresh_token', None, expires=-1)
    return await authenticator.logout(token)
