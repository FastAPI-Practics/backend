from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.rbac import PERMISSION_DESCRIPTIONS

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login',
    refreshUrl='/api/v1/auth/refresh',
    scopes=PERMISSION_DESCRIPTIONS,
)

AccessTokenDep = Annotated[str, Depends(oauth2_scheme)]
