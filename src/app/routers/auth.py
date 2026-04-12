from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Query, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.core.responses import (
    login_responses,
    ok_responses,
    register_responses,
    unauthorized_responses,
)
from app.dependencies.auth import AuthenticatorDep
from app.models.users import UserCreate
from app.schemas.auth import AuthTokenData, ChangePasswordData
from app.schemas.errors import OkSchema

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
):
    response.set_cookie('refresh_token', None, expires=-1)
    await authenticator.logout(refresh_token)
    return OkSchema()


@router.post(path='/register', responses=register_responses)
async def register(
    user_create: UserCreate,
    authenticator: AuthenticatorDep,
):
    return await authenticator.register(user_create)


@router.get(path='/user/{user_id}/verify')
async def verify_account(
    user_id: UUID,
    code: Annotated[str, Query()],
    authenticator: AuthenticatorDep,
):
    return await authenticator.verify_account(user_id, code)


@router.get(path='/user/{user_id}/password-reset/send-code')
async def confirm_password_send_code(
    user_id: UUID,
    authenticator: AuthenticatorDep,
):
    return await authenticator.send_password_reset_notification(user_id)


@router.post(path='/user/{user_id}/password-reset/confirm')
async def confirm_password_reset(
    user_id: UUID,
    change_data: ChangePasswordData,
    authenticator: AuthenticatorDep,
):
    return await authenticator.change_password(user_id, change_data)
