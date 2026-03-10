from typing import Annotated, Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies.security import CurrentUserDep
from app.dependencies.services import UserServiceDep
from app.models.pets import PetModel
from app.models.users import UserCreate, UserPublic, UserUpdate
from app.schemas.users import UserFilters

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.get('/me')
async def get_profile(current_user: CurrentUserDep) -> Optional[UserPublic]:
    return current_user


@router.get('/')
async def get_users(
    user_service: UserServiceDep, filters: Annotated[UserFilters, Query()]
) -> Sequence[UserPublic]:
    return await user_service.get_users(filters)


@router.post('/')
async def create_user(
    user_create: UserCreate,
    user_service: UserServiceDep,
) -> UserPublic:
    return await user_service.create_user(user_create)


@router.get('/{user_id}')
async def get_user(user_service: UserServiceDep, user_id: UUID) -> Optional[UserPublic]:
    return await user_service.get_user(user_id)


@router.put('/{user_id}')
async def update_user(
    user_service: UserServiceDep, user_update: UserUpdate, user_id: UUID
) -> Optional[UserPublic]:
    return await user_service.update_user(user_update, user_id)


@router.delete('/{user_id}')
async def delete_user(
    user_service: UserServiceDep, user_id: UUID
) -> Optional[UserPublic]:
    return await user_service.delete_user(user_id)


@router.get('/{user_id}/pets')
async def get_user_pets(
    user_service: UserServiceDep, user_id: UUID
) -> Sequence[PetModel]:
    return await user_service.get_user_pets(user_id)
