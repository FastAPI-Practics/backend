from typing import Annotated

from fastapi import Depends

from app.dependencies.session import SessionDep
from app.models.email import EmailNotification
from app.models.permissions import Permission
from app.models.pets import PetModel
from app.models.refresh import RefreshSession
from app.models.roles import Role
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


async def get_role_repository(session: SessionDep):
    yield Repository[Role](session)


type RoleRepository = Repository[Role]
RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]


async def get_permission_repository(session: SessionDep):
    yield Repository[Permission](session)


type PermissionRepository = Repository[Permission]
PermissionRepositoryDep = Annotated[
    PermissionRepository, Depends(get_permission_repository)
]


async def get_email_notification_repository(session: SessionDep):
    yield Repository[EmailNotification](session)


type EmailNotificationRepository = Repository[EmailNotification]
EmailNotificationRepositoryDep = Annotated[
    EmailNotificationRepository, Depends(get_email_notification_repository)
]
