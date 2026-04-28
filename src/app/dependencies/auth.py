from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import SecurityScopes

from app.core.auth import Authenticator
from app.core.security import AccessTokenDep
from app.models.users import UserModel

AuthenticatorDep = Annotated[Authenticator, Depends(Authenticator)]

type CurrentUser = Optional[UserModel]


async def get_current_user(
    authenticator: AuthenticatorDep,
    access_token: AccessTokenDep,
    security_scopes: SecurityScopes,
):
    yield await authenticator.authenticate_user(access_token, security_scopes)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
