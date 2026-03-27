from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.core.responses import (
    login_responses,
    ok_responses,
    register_responses,
    unauthorized_responses,
)
from app.dependencies.auth import AuthenticatorDep
from app.models.users import UserCreate
from app.schemas.auth import AuthTokenData
from app.schemas.responses import OkSchema

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post(path='/login', responses=login_responses)
async def login(
    auth_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    authenticator: AuthenticatorDep,
    response: Response,
) -> Optional[AuthTokenData]:
    tokens = await authenticator.login(auth_data)
    if tokens is None:
        return None
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


@router.delete(
    path='/logout',
    responses={
        **unauthorized_responses,
        **ok_responses,
    },
)
async def logout(
    refresh_token: Annotated[str, Cookie()],
    authenticator: AuthenticatorDep,
    response: Response,
) -> Optional[bool]:
    response.set_cookie('refresh_token', None, expires=-1)
    await authenticator.logout(refresh_token)
    return OkSchema()


@router.post(path='/register', responses=register_responses)
async def register(
    user_create: UserCreate,
    authenticator: AuthenticatorDep,
) -> bool:
    return await authenticator.register(user_create)
