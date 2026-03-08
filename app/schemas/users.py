from typing import Optional

from app.models.users import UserStatus
from app.schemas.base import CommonListFilters


class UserFilters(CommonListFilters):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[UserStatus] = None
