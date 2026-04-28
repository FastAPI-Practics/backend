from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RefreshSessionFilters(BaseModel):
    user_id: Optional[UUID] = None
