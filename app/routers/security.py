from typing import Annotated, Optional

from fastapi import APIRouter
from fastapi.params import Depends

from app.core.security import create_access_token
from app.dependencies.security import AuthenticatedUserDep, CurrentUserFromRefreshDep
from app.schemas.security import AuthData, TokenData

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/login')
async def login(
    authenticated_user: AuthenticatedUserDep,
) -> Optional[TokenData]:
    print(authenticated_user)
    if authenticated_user is None:
        return None
    access_token = create_access_token(authenticated_user)
    refresh_token = create_access_token(authenticated_user)
    return TokenData(
        refresh_token=refresh_token,
        access_token=access_token
    )

@router.post('/refresh')
async def refresh(
    authenticated_user: CurrentUserFromRefreshDep,
) -> Optional[TokenData]:
    if authenticated_user is None:
        return None
    access_token = create_access_token(authenticated_user)
    refresh_token = create_access_token(authenticated_user)
    return TokenData(
        refresh_token=refresh_token,
        access_token=access_token
    )
