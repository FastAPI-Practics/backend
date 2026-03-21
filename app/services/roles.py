from typing import Optional, Sequence

from app.dependencies.repositories import (
    PermissionRepository,
    PermissionRepositoryDep,
    RoleRepository,
    RoleRepositoryDep,
)
from app.models.permissions import PermissionPublic
from app.models.roles import Role, RoleCreate, RolePublic


class RoleService:
    __role_repository: RoleRepository
    __permission_repository: PermissionRepository

    def __init__(
        self,
        role_repository: RoleRepositoryDep,
        permission_repository: PermissionRepositoryDep,
    ):
        self.__role_repository = role_repository
        self.__permission_repository = permission_repository

    async def get_roles(self) -> Sequence[RolePublic]:
        return await self.__role_repository.fetch()

    async def __get_permission_by_scope(self, scope: str) -> Optional[PermissionPublic]:
        permissions = await self.__permission_repository.fetch()
        filtered = list(
            filter(lambda permission: permission.alias == scope, permissions)
        )
        if len(filtered) != 1:
            return None
        return filtered[0]

    async def create_role(self, role_create: RoleCreate) -> Optional[RolePublic]:
        role_create_data = role_create.model_dump()
        print(role_create_data)
        scopes = role_create_data.pop('scope_aliases')
        permissions = [await self.__get_permission_by_scope(scope) for scope in scopes]
        permissions_filtered = list(
            filter(lambda permission: permission is not None, permissions)
        )
        instance = Role(**role_create_data, permissions=permissions_filtered)
        return await self.__role_repository.save(instance)
