from typing import Optional, Sequence

from fastapi import APIRouter, Security

from app.core.responses import auth_responses
from app.dependencies.auth import get_current_user
from app.dependencies.services import RoleServiceDep
from app.models.roles import RoleCreate, RolePublic

router = APIRouter(prefix='/roles', tags=['roles'], responses=auth_responses)


@router.get(path='/', dependencies=[Security(get_current_user, scopes=['roles:list'])])
async def get_roles(
    role_service: RoleServiceDep,
) -> Sequence[RolePublic]:
    return await role_service.get_roles()


@router.post(
    path='/', dependencies=[Security(get_current_user, scopes=['roles:create'])]
)
async def create_role(
    role_create: RoleCreate,
    role_service: RoleServiceDep,
) -> Optional[RolePublic]:
    return await role_service.create_role(role_create)
