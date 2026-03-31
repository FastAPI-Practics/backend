from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, SQLModel

from app.models.base import BaseModel


class EmailSendData(SQLModel):
    subject: str
    email_to: EmailStr
    body: dict
    template_name: str


class EmailAction(int, Enum):
    VERIFY_ACCOUNT = 0
    CHANGE_PASSWORD = 1


class WithCode(SQLModel):
    code: UUID = Field(default_factory=uuid4)


class WithUserId(SQLModel):
    user_id: UUID = Field(foreign_key='usermodel.id')


class EmailVerificationData(WithUserId, WithCode):
    pass


class EmailNotificationCreate(WithUserId):
    action: EmailAction


class EmailNotification(BaseModel, EmailNotificationCreate, WithCode, table=True):
    expired_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
    )
    is_used: bool = False
