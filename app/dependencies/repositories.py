from typing import Annotated

from fastapi import Depends

from app.dependencies.session import SessionDep
from app.models.pets import PetModel
from app.models.users import UserModel
from app.utils.repository import Repository


async def get_user_repository(session: SessionDep):
    yield Repository[UserModel](UserModel, session)


type UserRepository = Repository[UserModel]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_pet_repository(session: SessionDep):
    yield Repository[PetModel](PetModel, session)


type PetRepository = Repository[PetModel]
PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]
