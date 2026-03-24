from itertools import product

from app.core.rbac import INITIAL_ACTIONS, INITIAL_PERMISSION_SCHEMA, INITIAL_SUBJECTS
from app.core.settings import settings
from app.models.permissions import PermissionCreate
from app.models.roles import RoleCreate
from app.models.users import UserCreate
from app.services.permissions import PermissionService
from app.services.roles import RoleService
from app.services.users import UserService


class Bootstraper:
    __user_service: UserService
    __role_service: RoleService
    __permission_service: PermissionService

    def __init__(
        self,
        user_service: UserService,
        role_service: RoleService,
        permission_service: PermissionService,
    ):
        self.__user_service = user_service
        self.__role_service = role_service
        self.__permission_service = permission_service

    async def bootstrap_app(self):
        admin_role_data = RoleCreate(name=settings.rbac.admin_role)

        permission_cartesian_product = product(INITIAL_SUBJECTS, INITIAL_ACTIONS)
        for subject, action in permission_cartesian_product:
            await self.__permission_service.create_permission_if_not_exists(
                PermissionCreate(subject=subject, action=action)
            )
            scope = f'{subject}:{action}'
            admin_role_data.scope_aliases.append(scope)

        admin_permissions = INITIAL_PERMISSION_SCHEMA.pop(settings.rbac.admin_role, [])
        admin_permissions.remove('*')
        for scope in admin_permissions:
            subject, action = scope.split(':')
            await self.__permission_service.create_permission_if_not_exists(
                PermissionCreate(subject=subject, action=action)
            )
            admin_role_data.scope_aliases.append(scope)

        admin_role = await self.__role_service.create_role_if_not_exists(
            admin_role_data
        )

        admin_user_data = UserCreate(
            first_name='',
            last_name='',
            email=settings.rbac.admin_email,
            username='admin',
            password=settings.rbac.admin_password,
        )

        admin_user = await self.__user_service.create_user_if_not_exists(
            admin_user_data
        )
        admin_user.role_id = admin_role.id
        await self.__user_service.save_user(admin_user)

        for role, scopes in INITIAL_PERMISSION_SCHEMA.items():
            for scope in scopes:
                subject, action = scope.split(':')
                await self.__permission_service.create_permission_if_not_exists(
                    PermissionCreate(subject=subject, action=action)
                )
            role_create_data = RoleCreate(name=role, scope_aliases=scopes)
            await self.__role_service.create_role_if_not_exists(role_create_data)
