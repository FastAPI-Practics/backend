from typing import Optional

from app.schemas.base import CommonListFilters


class RoleFilters(CommonListFilters):
    name: Optional[str] = None
