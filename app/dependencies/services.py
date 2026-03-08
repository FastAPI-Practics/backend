from typing import Annotated

from fastapi.params import Depends

from app.services.users import UserService

UserServiceDep = Annotated[UserService, Depends(UserService)]
