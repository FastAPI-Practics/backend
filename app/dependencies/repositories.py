from typing import Annotated

from fastapi import Depends

from app.dependencies.session import SessionDep
from app.models.pets import PetModel
from app.models.refresh import RefreshSession
from app.models.users import UserModel
from app.utils.repository import Repository


async def get_user_repository(session: SessionDep):
    yield Repository[UserModel](session)


type UserRepository = Repository[UserModel]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_pet_repository(session: SessionDep):
    yield Repository[PetModel](session)


type PetRepository = Repository[PetModel]
PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]


async def get_refresh_session_repository(session: SessionDep):
    yield Repository[RefreshSession](session)


type RefreshSessionRepository = Repository[RefreshSession]
RefreshSessionRepositoryDep = Annotated[
    RefreshSessionRepository, Depends(get_refresh_session_repository)
]
