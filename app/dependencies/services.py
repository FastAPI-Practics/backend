from typing import Annotated

from fastapi.params import Depends

from app.services.email import EmailNotificationService
from app.services.permissions import PermissionService
from app.services.refresh import RefreshSessionService
from app.services.roles import RoleService
from app.services.users import UserService

UserServiceDep = Annotated[UserService, Depends(UserService)]

RefreshSessionServiceDep = Annotated[
    RefreshSessionService, Depends(RefreshSessionService)
]

PermissionServiceDep = Annotated[PermissionService, Depends(PermissionService)]

RoleServiceDep = Annotated[RoleService, Depends(RoleService)]

EmailNotificationServiceDep = Annotated[
    EmailNotificationService, Depends(EmailNotificationService)
]
