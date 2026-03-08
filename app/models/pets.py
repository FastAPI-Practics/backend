from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.users import UserModel


class PetType(str, Enum):
    CAT = 'cat',
    DOG = 'dog',
    PARROT = 'parrot'


class PetModel(BaseModel, table=True):
    name: str
    type: PetType = Field(default=PetType.CAT)
    owner_id: UUID = Field(default=None, foreign_key="usermodel.id", index=True)
    owner: "UserModel" = Relationship(
        back_populates="pets",
        sa_relationship_kwargs={'lazy': 'selectin'}
    )
