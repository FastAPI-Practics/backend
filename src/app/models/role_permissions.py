from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class RolePermissionMapping(BaseModel, table=True):
    role_id: UUID = Field(foreign_key='role.id', primary_key=True)
    permission_id: UUID = Field(foreign_key='permission.id', primary_key=True)
