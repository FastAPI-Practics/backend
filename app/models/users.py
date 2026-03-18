from enum import Enum
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Column, Field, Relationship, SQLModel, String

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.pets import PetModel


class UserStatus(str, Enum):
    CREATED = 'created'
    CONFIRMED = 'confirmed'
    BANNED = 'banned'


class UserBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr = Field(sa_column=Column(String, unique=True, nullable=True))
    username: str


class UserPublic(BaseModel, UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserCreate(UserBase):
    password: str


class UserModel(UserPublic, table=True):
    password_hash: str
    status: UserStatus = Field(default=UserStatus.CREATED)
    pets: list['PetModel'] = Relationship(
        back_populates='owner',
        cascade_delete=True,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
