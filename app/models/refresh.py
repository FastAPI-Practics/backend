from datetime import datetime, timezone
from uuid import UUID

from pydantic import computed_field
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field

from app.models.base import BaseModel


class RefreshSessionCreate(BaseModel):
    access_token_id: UUID
    refresh_token_id: UUID
    expires_at: datetime = Field(
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
    )
    user_id: UUID = Field(foreign_key='usermodel.id')


class RefreshSession(RefreshSessionCreate, table=True):
    is_invalidated: bool = Field(default=False)

    @computed_field
    @property
    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        expired = now > self.expires_at
        is_invalid = expired or self.is_invalidated
        return not is_invalid
