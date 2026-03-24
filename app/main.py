from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.dependencies.repositories import (
    get_permission_repository,
    get_role_repository,
    get_user_repository,
)
from app.dependencies.session import get_session
from app.routers import auth, permissions, pets, roles, users
from app.services.permissions import PermissionService
from app.services.roles import RoleService
from app.services.users import UserService
from app.utils.bootstrap import Bootstraper

api_prefix = '/api'


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_async_session_context = asynccontextmanager(get_session)
    async with get_async_session_context() as session:
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
                    yield


app = FastAPI(
    openapi_url=f'{api_prefix}/openapi.json',
    docs_url=f'{api_prefix}/docs',
    redoc_url=f'{api_prefix}/redoc',
    lifespan=lifespan,
)

app_router = APIRouter(prefix=f'{api_prefix}/v1')
app_router.include_router(users.router)
app_router.include_router(pets.router)
app_router.include_router(auth.router)
app_router.include_router(permissions.router)
app_router.include_router(roles.router)

app.include_router(app_router)
