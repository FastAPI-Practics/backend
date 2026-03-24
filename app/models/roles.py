from typing import TYPE_CHECKING

from pydantic import computed_field
from sqlmodel import Relationship, SQLModel

from app.models.base import BaseModel
from app.models.role_permissions import RolePermissionMapping

if TYPE_CHECKING:
    from app.models.permissions import Permission
    from app.models.users import UserModel


class RoleBase(SQLModel):
    name: str


class RoleWithScopes(RoleBase):
    @computed_field
    @property
    def scopes(self) -> list[str]:
        return list(map(lambda permission: permission.alias, self.permissions))


class RolePublic(BaseModel, RoleWithScopes):
    pass


class RoleChange(RoleBase):
    scope_aliases: list[str] = []


class RoleCreate(RoleChange):
    pass


class RoleUpdate(RoleChange):
    pass


class Role(RolePublic, table=True):
    permissions: list['Permission'] = Relationship(
        back_populates='roles',
        link_model=RolePermissionMapping,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
    users: list['UserModel'] = Relationship(
        back_populates='role',
        cascade_delete=True,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
