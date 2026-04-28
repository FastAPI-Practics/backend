import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from app.dependencies.repositories import (
    get_permission_repository,
    get_role_repository,
    get_user_repository,
)
from app.dependencies.session import get_session
from app.services.permissions import PermissionService
from app.services.roles import RoleService
from app.services.users import UserService
from app.utils.bootstrap import Bootstraper
from sqlmodel.ext.asyncio.session import AsyncSession


async def bootstrap_app(session: Optional[AsyncSession] = None):
    if session is None:
        get_async_session_context = asynccontextmanager(get_session)
        async with get_async_session_context() as postgres_session:
            await bootstrap_main(postgres_session)
    else:
        await bootstrap_main(session)

async def bootstrap_main(session: AsyncSession):
    get_async_role_repository_context = asynccontextmanager(get_role_repository)
    get_async_permission_repository_context = asynccontextmanager(
        get_permission_repository
    )
    get_async_user_repository_context = asynccontextmanager(get_user_repository)
    async with get_async_permission_repository_context(
        session
    ) as permission_repository:
        permission_service = PermissionService(permission_repository)
        async with get_async_role_repository_context(session) as role_repository:
            role_service = RoleService(role_repository, permission_repository)
            async with get_async_user_repository_context(
                session
            ) as user_repository:
                user_service = UserService(user_repository)
                bootstraper = Bootstraper(
                    user_service=user_service,
                    role_service=role_service,
                    permission_service=permission_service,
                )
                await bootstraper.bootstrap_app()

if __name__ == '__main__':
    asyncio.run(bootstrap_app())
