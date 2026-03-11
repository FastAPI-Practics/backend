from typing import Annotated, Optional

import jwt
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import oauth2_scheme
from app.core.settings import settings
from app.dependencies.services import UserServiceDep
from app.models.users import UserModel
from app.schemas.security import RefreshData
from app.utils.hashing import verify_password

type AuthenticatedUser = Optional[UserModel]


async def autheticate_user(
    auth_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserServiceDep,
) -> AuthenticatedUser:
    email = auth_data.username
    user = await user_service.get_user_by_email(email)
    if user is None:
        return None
    password = auth_data.password
    is_passwords_matched = verify_password(password, user.password_hash)
    if is_passwords_matched:
        return user
    return None


AuthenticatedUserDep = Annotated[AuthenticatedUser, Depends(autheticate_user)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserServiceDep,
) -> AuthenticatedUser:
    payload = jwt.decode(
        token, settings.auth.secret, algorithms=settings.auth.token_algorithm
    )
    user_id = payload.get('sub')
    if user_id is None:
        return None
    return await user_service.get_user(user_id)


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


async def get_current_user_from_refresh_token(
    refresh_token_data: RefreshData,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserServiceDep,
):
    refresh_token = refresh_token_data.refresh_token
    refresh_token_payload = jwt.decode(
        refresh_token, settings.auth.secret, algorithms=settings.auth.token_algorithm
    )
    access_token = refresh_token_payload.get('token')
    if token == access_token:
        return await get_current_user(refresh_token, user_service)
    return None


CurrentUserFromRefreshDep = Annotated[
    AuthenticatedUser, Depends(get_current_user_from_refresh_token)
]
