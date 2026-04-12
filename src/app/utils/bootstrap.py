from itertools import product

from app.core.rbac import INITIAL_ACTIONS, INITIAL_PERMISSION_SCHEMA, INITIAL_SUBJECTS
from app.core.settings import settings
from app.models.permissions import PermissionCreate
from app.models.roles import RoleCreate
from app.models.users import UserCreate, UserStatus
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

        initial_scopes = [
            f'{subject}:{action}'
            for subject, action in product(INITIAL_SUBJECTS, INITIAL_ACTIONS)
        ]

        permission_scopes = [*initial_scopes]
        for scopes in INITIAL_PERMISSION_SCHEMA.values():
            permission_scopes.extend(scopes)

        permission_scopes = list(set(permission_scopes))
        permission_scopes.remove('*')
        for scope in permission_scopes:
            subject, action = scope.split(':')
            await self.__permission_service.create_permission_if_not_exists(
                PermissionCreate(subject=subject, action=action)
            )

        admin_role_data.scope_aliases = permission_scopes

        for role, scopes in INITIAL_PERMISSION_SCHEMA.items():
            if role == settings.rbac.admin_role:
                continue
            role_create_data = RoleCreate(name=role, scope_aliases=scopes)
            await self.__role_service.create_role_if_not_exists(role_create_data)

        admin_role = await self.__role_service.create_role_if_not_exists(
            admin_role_data
        )

        admin_user_data = UserCreate(
            first_name='admin',
            last_name='admin',
            email=settings.rbac.admin_email,
            username='admin',
            password=settings.rbac.admin_password,
        )

        admin_user = await self.__user_service.create_user_if_not_exists(
            admin_user_data
        )
        admin_user.role_id = admin_role.id
        admin_user.status = UserStatus.CONFIRMED
        await self.__user_service.save_user(admin_user)
