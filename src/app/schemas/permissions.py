from typing import Optional

from app.schemas.base import CommonListFilters


class PermissionFilters(CommonListFilters):
    subject: Optional[str] = None
    action: Optional[str] = None
