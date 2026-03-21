from typing import Optional, Sequence

from fastapi import APIRouter

from app.dependencies.services import RoleServiceDep
from app.models.roles import RoleCreate, RolePublic

router = APIRouter(
    prefix='/roles',
    tags=['roles'],
)


@router.get('/')
async def get_roles(role_service: RoleServiceDep) -> Sequence[RolePublic]:
    return await role_service.get_roles()


@router.post('/')
async def create_role(
    role_create: RoleCreate, role_service: RoleServiceDep
) -> Optional[RolePublic]:
    return await role_service.create_role(role_create)
