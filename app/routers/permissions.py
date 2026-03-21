from typing import Optional, Sequence

from fastapi import APIRouter

from app.dependencies.services import PermissionServiceDep
from app.models.permissions import PermissionCreate, PermissionPublic

router = APIRouter(
    prefix='/permissions',
    tags=['permission'],
)


@router.get('/')
async def get_permissions(
    permission_service: PermissionServiceDep,
) -> Sequence[PermissionPublic]:
    return await permission_service.get_permissions()


@router.post('/')
async def create_permission(
    permission_service: PermissionServiceDep,
    permission_data: PermissionCreate,
) -> Optional[PermissionPublic]:
    return await permission_service.create_permission(permission_data)
