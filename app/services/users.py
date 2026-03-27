from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import UserRepository, UserRepositoryDep
from app.models.pets import PetModel
from app.models.users import UserCreate, UserModel, UserUpdate
from app.schemas.users import UserFilters
from app.utils.hasher import Hasher


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

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        users = await self.__user_repository.fetch(
            filters=UserFilters(email=email),
        )
        if len(users) != 1:
            return None
        return users[0]

    async def create_user(self, user_create: UserCreate) -> UserModel:
        user_dump = user_create.model_dump()
        password = str(user_dump.pop('password'))
        password_hash = Hasher.get_password_hash(password)
        user = UserModel(**user_dump, password_hash=password_hash)
        return await self.__user_repository.save(user)

    async def save_user(self, user: UserModel) -> UserModel:
        return await self.__user_repository.save(user)

    async def create_user_if_not_exists(self, user_create: UserCreate) -> UserModel:
        user = await self.get_user_by_email(user_create.email)
        if user is not None:
            return user
        return await self.create_user(user_create)

    async def get_user(self, user_id: UUID) -> Optional[UserModel]:
        return await self.__user_repository.get(user_id)

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        users = await self.__user_repository.fetch(UserFilters(username=username))
        if len(users) != 1:
            return None
        return users[0]

    async def update_user(
        self, user_update: UserUpdate, user_id: UUID
    ) -> Optional[UserModel]:
        return await self.__user_repository.update(user_id, user_update)

    async def delete_user(self, user_id: UUID) -> Optional[UserModel]:
        return await self.__user_repository.delete(user_id)

    async def get_user_pets(self, user_id: UUID) -> Sequence[PetModel]:
        user = await self.__user_repository.get(user_id)
        if user is None:
            return None
        return user.pets
