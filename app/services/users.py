from base64 import b64encode
from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import UserRepository, UserRepositoryDep
from app.models.pets import PetModel
from app.models.users import UserCreate, UserModel, UserUpdate
from app.schemas.users import UserFilters


class UserService:
    __user_repository: UserRepository

    def __init__(self, user_repository: UserRepositoryDep):
        self.__user_repository = user_repository

    async def get_users(self, filters: UserFilters) -> Sequence[UserModel]:
        return await self.__user_repository.fetch(
            filters=filters,
            offset=filters.offset,
            limit=filters.limit,
        )

    async def create_user(self, user_create: UserCreate) -> UserModel:
        user_dump = user_create.model_dump()
        password = str(user_dump.pop('password'))
        password_bytes = password.encode()
        password_hash_bytes = b64encode(password_bytes)
        password_hash = password_hash_bytes.decode()
        user = UserModel(**user_dump, password_hash=password_hash)
        return await self.__user_repository.save(user)

    async def get_user(self, user_id: UUID) -> Optional[UserModel]:
        return await self.__user_repository.get(user_id)

    async def update_user(
        self, user_update: UserUpdate, user_id: UUID
    ) -> Optional[UserModel]:
        return await self.__user_repository.update(user_id, user_update)

    async def delete_user(self, user_id: UUID) -> Optional[UserModel]:
        return await self.__user_repository.delete(user_id)

    async def get_user_pets(self, user_id: UUID) -> Sequence[PetModel]:
        user = await self.__user_repository.get(user_id)
        if user is None:
            return []
        return user.pets
