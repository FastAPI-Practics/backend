from typing import Optional

from app.schemas.base import CommonListFilters


class PetFilters(CommonListFilters):
    name: Optional[str] = None
