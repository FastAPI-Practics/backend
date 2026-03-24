from typing import Optional, Sequence

from app.dependencies.repositories import PermissionRepository, PermissionRepositoryDep
from app.models.permissions import Permission, PermissionCreate, PermissionPublic


class PermissionService:
    __permission_repository: PermissionRepository

    def __init__(self, permission_repository: PermissionRepositoryDep):
        self.__permission_repository = permission_repository

    async def get_permissions(self) -> Sequence[PermissionPublic]:
        return await self.__permission_repository.fetch()

    async def get_by_scope(self, scope: str) -> Optional[PermissionPublic]:
        permissions = await self.__permission_repository.fetch()
        filtered = list(
            filter(lambda permission: permission.alias == scope, permissions)
        )
        if len(filtered) != 1:
            return None
        return filtered[0]

    async def create_permission(
        self, permission_create: PermissionCreate
    ) -> Optional[PermissionPublic]:
        instance = Permission(**permission_create.model_dump())
        return await self.__permission_repository.save(instance)

    async def create_permission_if_not_exists(
        self, permission_create: PermissionCreate
    ) -> Optional[PermissionPublic]:
        permission = await self.get_by_scope(permission_create.alias)
        if permission is not None:
            return permission
        return await self.create_permission(permission_create)
