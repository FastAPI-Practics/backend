from typing import Optional, Sequence

from fastapi import APIRouter, Security

from app.core.responses import auth_responses
from app.dependencies.auth import get_current_user
from app.dependencies.services import PermissionServiceDep
from app.models.permissions import PermissionCreate, PermissionPublic

router = APIRouter(prefix='/permissions', tags=['permission'], responses=auth_responses)


@router.get(
    path='/', dependencies=[Security(get_current_user, scopes=['permissions:list'])]
)
async def get_permissions(
    permission_service: PermissionServiceDep,
) -> Sequence[PermissionPublic]:
    return await permission_service.get_permissions()


@router.post(
    path='/', dependencies=[Security(get_current_user, scopes=['permissions:create'])]
)
async def create_permission(
    permission_service: PermissionServiceDep,
    permission_data: PermissionCreate,
) -> Optional[PermissionPublic]:
    return await permission_service.create_permission(permission_data)
