from typing import Annotated, Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Query, Security

from app.core.errors import NotFoundError
from app.core.responses import auth_responses, detail_responses
from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.services import UserServiceDep
from app.models.pets import PetModel
from app.models.users import UserPublic, UserUpdate
from app.schemas.users import UserFilters

router = APIRouter(prefix='/users', tags=['users'], responses=auth_responses)


@router.get('/me')
async def get_profile(
    current_user: Annotated[
        CurrentUser, Security(get_current_user, scopes=['users:me'])
    ],
) -> Optional[UserPublic]:
    return current_user


@router.get(
    path='/',
    dependencies=[Security(get_current_user, scopes=['users:list'])],
)
async def get_users(
    user_service: UserServiceDep,
    filters: Annotated[UserFilters, Query()],
) -> Sequence[UserPublic]:
    return await user_service.get_users(filters)


@router.get(
    path='/{user_id}',
    responses={
        **auth_responses,
        **detail_responses,
    },
    dependencies=[Security(get_current_user, scopes=['users:detail'])],
)
async def get_user(
    user_service: UserServiceDep,
    user_id: UUID,
) -> UserPublic:
    user = await user_service.get_user(user_id)
    if user is None:
        raise NotFoundError()
    return user


@router.put(
    path='/{user_id}',
    dependencies=[Security(get_current_user, scopes=['users:update'])],
)
async def update_user(
    user_service: UserServiceDep,
    user_update: UserUpdate,
    user_id: UUID,
) -> UserPublic:
    updated = await user_service.update_user(user_update, user_id)
    if updated is None:
        raise NotFoundError()
    return updated


@router.delete(
    path='/{user_id}',
    dependencies=[Security(get_current_user, scopes=['users:update'])],
)
async def delete_user(
    user_service: UserServiceDep,
    user_id: UUID,
) -> UserPublic:
    deleted = await user_service.delete_user(user_id)
    if deleted is None:
        raise NotFoundError()
    return deleted


@router.get(
    path='/{user_id}/pets',
    dependencies=[Security(get_current_user, scopes=['users:detail', 'pets:list'])],
)
async def get_user_pets(
    user_service: UserServiceDep,
    user_id: UUID,
) -> Sequence[PetModel]:
    pets = await user_service.get_user_pets(user_id)
    if pets is None:
        raise NotFoundError()
    return pets
