from typing import Annotated

from fastapi.params import Depends

from app.services.refresh import RefreshSessionService
from app.services.users import UserService

UserServiceDep = Annotated[UserService, Depends(UserService)]

RefreshSessionServiceDep = Annotated[
    RefreshSessionService, Depends(RefreshSessionService)
]
