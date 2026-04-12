from typing import TYPE_CHECKING

from pydantic import computed_field
from sqlmodel import Relationship, SQLModel

from app.models.base import BaseModel
from app.models.role_permissions import RolePermissionMapping

if TYPE_CHECKING:
    from app.models.roles import Role


class PermissionBase(SQLModel):
    subject: str
    action: str

    @computed_field
    @property
    def alias(self) -> str:
        return f'{self.subject}:{self.action}'


class PermissionPublic(BaseModel, PermissionBase):
    pass


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionPublic, table=True):
    roles: list['Role'] = Relationship(
        back_populates='permissions',
        link_model=RolePermissionMapping,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
