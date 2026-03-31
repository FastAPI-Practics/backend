from typing import Optional

from app.dependencies.repositories import (
    PermissionRepository,
    PermissionRepositoryDep,
    RoleRepository,
    RoleRepositoryDep,
)
from app.models.roles import Role, RoleCreate, RolePublic
from app.schemas.roles import RoleFilters
from app.utils.pagination import ListResponse


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

    async def get_roles(self, filters: RoleFilters) -> ListResponse[RolePublic]:
        return await self.__role_repository.fetch_with_pagination_data(filters)

    async def get_by_name(self, name: str) -> Optional[RolePublic]:
        roles = await self.__role_repository.fetch(RoleFilters(name=name))
        if len(roles) != 1:
            return None
        return roles[0]

    async def create_role(self, role_create: RoleCreate) -> Optional[RolePublic]:
        role_create_data = role_create.model_dump()
        scopes = role_create_data.pop('scope_aliases')
        all_permissions = await self.__permission_repository.fetch()
        permissions = [
            permission if permission.alias == scope else None
            for permission in all_permissions
            for scope in scopes
        ]
        permissions_filtered = list(
            filter(lambda permission: permission is not None, permissions)
        )
        instance = Role(**role_create_data)
        instance = await self.__role_repository.save(instance)
        instance.permissions = permissions_filtered
        return await self.__role_repository.save(instance)

    async def create_role_if_not_exists(
        self, role_create: RoleCreate
    ) -> Optional[RolePublic]:
        role_list = await self.__role_repository.fetch(
            RoleFilters(name=role_create.name)
        )
        if len(role_list) == 1:
            return role_list[0]
        return await self.create_role(role_create)

    async def save_role(self, role: Role) -> Role:
        return await self.__role_repository.save(role)
